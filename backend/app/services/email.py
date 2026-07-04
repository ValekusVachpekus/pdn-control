"""Отправка писем через Resend (HTTP API, async).

DEV-фолбэк: если RESEND_API_KEY не задан — код печатается в лог, письмо не
уходит и запрос не падает. Чтобы включить реальную отправку, достаточно ЗАДАТЬ
ДАННЫЕ в окружении (RESEND_API_KEY + EMAIL_FROM на верифицированный домен) —
менять код не нужно. Resend — иностранный провайдер: для прода с ПДн граждан РФ
требуется юридическая оценка (152-ФЗ) либо РФ-провайдер; см. README.
"""
from __future__ import annotations

import logging

import httpx

from ..config import get_settings

log = logging.getLogger(__name__)


def _otp_html(code: str) -> str:
    return f"""\
<div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px;border:1px solid #eee;border-radius:10px">
  <h2 style="margin:0 0 8px;color:#1F8A5B">Код для входа</h2>
  <p style="color:#555;margin:0 0 16px">Введите этот код в ПДн Контроль для входа или регистрации:</p>
  <div style="font-size:30px;font-weight:700;letter-spacing:8px;color:#1F8A5B;text-align:center;background:#f6faf8;padding:14px;border-radius:8px">{code}</div>
  <p style="font-size:12px;color:#999;margin:16px 0 0">Код действует 10 минут. Если вы не запрашивали вход — просто проигнорируйте письмо.</p>
</div>"""


async def send_otp_email(email: str, code: str) -> None:
    """Шлёт OTP-код. В DEV-режиме (нет ключа) — логирует код, не отправляет.

    Никогда не возбуждает исключение наружу: эндпоинт request-code обязан
    отвечать 204 независимо от результата (анти-enumeration). Сбой провайдера
    логируем для разбора.
    """
    s = get_settings()
    if not s.email_configured:
        log.warning(
            "[DEV email] OTP для %s: %s (RESEND_API_KEY не задан — письмо НЕ отправлено)",
            email, code,
        )
        return

    payload = {
        "from": s.email_from,
        "to": [email],
        "subject": "Код для входа в ПДн Контроль",
        "html": _otp_html(code),
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{s.email_api_base}/emails",
                headers={"Authorization": f"Bearer {s.resend_api_key}"},
                json=payload,
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.error("Resend: не удалось отправить OTP на %s: %s", email, exc)
