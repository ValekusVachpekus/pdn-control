/* ===== ПДн Контроль — окно входа / регистрации =====
 * Три режима: login / register (e-mail + пароль) и code (passwordless —
 * одноразовый код на e-mail, issue #55). Вся сетевая логика — в api.js;
 * здесь UI, локальная валидация и состояния. После успеха — onAuth(user). */
import { useEffect, useState } from 'react';
import { Icon, Logo, Modal } from './shared.jsx';
import { login, register, loginWithProvider, requestCode, verifyCode } from './api.js';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const CODE_RE = /^\d{6}$/;
const RESEND_COOLDOWN = 60; // c — синхронно с backend otp_resend_cooldown_sec

/* Кнопка входа через внешнего провайдера (UI-only, мок). Бренд-марка —
 * цветной квадрат с буквой, чтобы не тащить внешние логотипы. */
function ProviderButton({ mark, color, label, disabled, onClick }) {
  return (
    <button className="btn btn-ghost" disabled={disabled} onClick={onClick}
      style={{ height: 46, justifyContent: 'center', gap: 10, fontSize: 14 }}>
      <span style={{ width: 22, height: 22, borderRadius: 6, background: color, color: '#fff',
        display: 'grid', placeItems: 'center', fontSize: 12, fontWeight: 800, flexShrink: 0 }}>{mark}</span>
      {label}
    </button>
  );
}

function Field({ icon, type = 'text', value, onChange, placeholder, autoComplete, onEnter, inputMode, maxLength }) {
  const [focus, setFocus] = useState(false);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, height: 46, padding: '0 14px',
      background: 'var(--surface-2)', borderRadius: 11,
      border: `1.5px solid ${focus ? 'var(--accent)' : 'var(--border-2)'}`,
      boxShadow: focus ? '0 0 0 4px var(--ring)' : 'none', transition: 'all .16s' }}>
      <Icon name={icon} size={18} style={{ color: 'var(--faint)' }} />
      <input type={type} value={value} autoComplete={autoComplete} inputMode={inputMode} maxLength={maxLength}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
        onKeyDown={e => e.key === 'Enter' && onEnter && onEnter()}
        placeholder={placeholder}
        style={{ flex: 1, border: 0, outline: 0, background: 'transparent', font: 'inherit',
          fontSize: 14.5, color: 'var(--ink)', minWidth: 0 }} />
    </div>
  );
}

/* Чекбокс согласия на обработку ПДн (152-ФЗ ст. 9) — переиспользуется в
 * register и в passwordless-регистрации. */
function ConsentBox({ consent, setConsent, onOpenPolicy }) {
  return (
    <label style={{ display: 'flex', alignItems: 'flex-start', gap: 9, marginTop: 4,
      fontSize: 13, color: 'var(--muted)', lineHeight: 1.45, cursor: 'pointer' }}>
      <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)}
        style={{ width: 17, height: 17, marginTop: 1, accentColor: 'var(--accent)', flexShrink: 0, cursor: 'pointer' }} />
      <span>
        Я даю согласие на обработку моих персональных данных и принимаю{' '}
        <button type="button" className="btn btn-quiet" onClick={onOpenPolicy}
          style={{ height: 'auto', padding: 0, fontSize: 13, color: 'var(--accent-ink)',
            textDecoration: 'underline', display: 'inline' }}>
          политику обработки ПДн
        </button>.
      </span>
    </label>
  );
}

function ErrorBox({ err }) {
  if (!err) return null;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 13,
      color: 'var(--crit-ink)', background: 'var(--crit-soft)', padding: '8px 11px', borderRadius: 9 }}>
      <Icon name="alert" size={15} stroke={2} /> {err}
    </div>
  );
}

function Auth({ open, onClose, onAuth, onToast, onOpenPolicy }) {
  const [mode, setMode] = useState('login'); // login | register | code
  const [step, setStep] = useState(1);       // для code: 1 = e-mail, 2 = код
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [consent, setConsent] = useState(false); // снято по умолчанию (ст. 9)
  const [cooldown, setCooldown] = useState(0);    // c до повторной отправки кода
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const isRegister = mode === 'register';
  const isCode = mode === 'code';

  // Тикаем кулдаун повторной отправки кода.
  useEffect(() => {
    if (cooldown <= 0) return undefined;
    const t = setTimeout(() => setCooldown(c => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const resetTransient = () => {
    setErr(''); setConsent(false); setPassword(''); setCode(''); setStep(1); setCooldown(0);
  };

  // Auth остаётся смонтированным между открытиями — чистим состояние при закрытии,
  // чтобы согласие/код/ошибки не «протекали» в следующую сессию.
  const handleClose = () => { resetTransient(); onClose(); };

  const switchMode = (next) => { setMode(next); resetTransient(); };

  // ── e-mail + пароль ────────────────────────────────────────────────────
  const submit = async () => {
    setErr('');
    if (!EMAIL_RE.test(email.trim())) { setErr('Введите корректный e-mail'); return; }
    if (password.length < 8) { setErr('Пароль — минимум 8 символов'); return; }
    if (isRegister && !consent) { setErr('Подтвердите согласие на обработку персональных данных'); return; }
    setBusy(true);
    try {
      const { user } = isRegister
        ? await register({ email: email.trim(), password, consent })
        : await login({ email: email.trim(), password });
      onToast && onToast(isRegister ? 'Аккаунт создан' : 'Вы вошли', 'ok');
      onAuth && onAuth(user);
      handleClose();
    } catch {
      setErr(isRegister ? 'Не удалось зарегистрироваться' : 'Неверный e-mail или пароль');
    } finally {
      setBusy(false);
    }
  };

  // ── passwordless: шаг 1 — запросить код ─────────────────────────────────
  const sendCode = async () => {
    setErr('');
    if (!EMAIL_RE.test(email.trim())) { setErr('Введите корректный e-mail'); return; }
    setBusy(true);
    try {
      await requestCode({ email: email.trim() });
      // Бэкенд всегда 204 (анти-enumeration) — переходим к вводу кода.
      setStep(2); setCode(''); setCooldown(RESEND_COOLDOWN);
    } catch {
      setErr('Не удалось отправить код, попробуйте позже');
    } finally {
      setBusy(false);
    }
  };

  // ── passwordless: шаг 2 — проверить код ─────────────────────────────────
  const submitCode = async () => {
    setErr('');
    if (!CODE_RE.test(code.trim())) { setErr('Код — 6 цифр'); return; }
    setBusy(true);
    try {
      const { user } = await verifyCode({ email: email.trim(), code: code.trim(), consent });
      onToast && onToast('Вы вошли', 'ok');
      onAuth && onAuth(user);
      handleClose();
    } catch (e) {
      // Новому пользователю нужен consent (ст. 9) — бэк отдаёт 400 с detail про consent.
      setErr(/consent/i.test(e?.message || '')
        ? 'Подтвердите согласие на обработку персональных данных'
        : 'Неверный или просроченный код');
    } finally {
      setBusy(false);
    }
  };

  const oauth = async (provider) => {
    setErr('');
    if (isRegister && !consent) { setErr('Подтвердите согласие на обработку персональных данных'); return; }
    setBusy(true);
    try {
      // В проде loginWithProvider уводит браузер на провайдера и НЕ резолвится —
      // код ниже отработает только в MOCK-режиме (вернёт готового user). Возврат из
      // реального redirect-flow (?oauth=success/error) разбирает App.jsx.
      const res = await loginWithProvider(provider, isRegister ? consent : false);
      if (res?.user) {
        setBusy(false);
        onToast && onToast('Вы вошли', 'ok');
        onAuth && onAuth(res.user);
        handleClose();
      }
      // real-режим: страница уже уходит на провайдера — busy оставляем true.
    } catch {
      setErr('Не удалось войти через провайдера');
      setBusy(false);
    }
  };

  const title = isCode ? 'Вход по коду' : isRegister ? 'Создать аккаунт' : 'Вход в ПДн Контроль';
  const subtitle = isCode
    ? (step === 1 ? 'Пришлём одноразовый код на e-mail' : `Код отправлен на ${email.trim()}`)
    : isRegister ? 'История проверок и доступ к Pro' : 'Доступ к истории и сохранённым отчётам';

  return (
    <Modal open={open} onClose={handleClose} width={420} labelId="auth-title">
      <div style={{ padding: '32px 30px 28px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, marginBottom: 22 }}>
          <Logo size={40} />
          <div style={{ textAlign: 'center' }}>
            <h2 id="auth-title" style={{ margin: 0, fontSize: 20, fontWeight: 700, letterSpacing: '-.01em' }}>
              {title}
            </h2>
            <p style={{ margin: '6px 0 0', fontSize: 13.5, color: 'var(--muted)' }}>{subtitle}</p>
          </div>
        </div>

        {/* ───────── passwordless (код на e-mail) ───────── */}
        {isCode ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
            {step === 1 ? (
              <>
                <Field icon="user" type="email" value={email} onChange={setEmail}
                  placeholder="you@company.ru" autoComplete="email" onEnter={sendCode} />
                <ErrorBox err={err} />
                <button className="btn btn-primary" disabled={busy}
                  style={{ height: 46, marginTop: 4, justifyContent: 'center' }} onClick={sendCode}>
                  {busy ? 'Отправляем…' : 'Получить код'}
                  {!busy && <Icon name="arrow" size={18} />}
                </button>
              </>
            ) : (
              <>
                <Field icon="lock" type="text" value={code} onChange={setCode}
                  placeholder="6-значный код" autoComplete="one-time-code"
                  inputMode="numeric" maxLength={6} onEnter={submitCode} />
                <ConsentBox consent={consent} setConsent={setConsent} onOpenPolicy={onOpenPolicy} />
                <ErrorBox err={err} />
                <button className="btn btn-primary" disabled={busy}
                  style={{ height: 46, marginTop: 4, justifyContent: 'center' }} onClick={submitCode}>
                  {busy ? 'Подождите…' : 'Войти'}
                  {!busy && <Icon name="arrow" size={18} />}
                </button>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 2 }}>
                  <button className="btn btn-quiet" style={{ height: 28, padding: '0 4px', fontSize: 13, color: 'var(--muted)' }}
                    onClick={() => { setStep(1); setErr(''); setCode(''); }}>
                    ← Изменить e-mail
                  </button>
                  <button className="btn btn-quiet" disabled={cooldown > 0 || busy}
                    style={{ height: 28, padding: '0 4px', fontSize: 13, color: cooldown > 0 ? 'var(--faint)' : 'var(--accent-ink)' }}
                    onClick={sendCode}>
                    {cooldown > 0 ? `Повторить через ${cooldown} с` : 'Отправить код повторно'}
                  </button>
                </div>
              </>
            )}

            <div style={{ textAlign: 'center', marginTop: 14, fontSize: 13.5, color: 'var(--muted)' }}>
              <button className="btn btn-quiet" style={{ height: 26, padding: '0 6px', fontSize: 13.5, color: 'var(--accent-ink)' }}
                onClick={() => switchMode('login')}>
                Войти по паролю
              </button>
            </div>
          </div>
        ) : (
          /* ───────── e-mail + пароль (login / register) ───────── */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
            <Field icon="user" type="email" value={email} onChange={setEmail}
              placeholder="you@company.ru" autoComplete="email" onEnter={submit} />
            <Field icon="lock" type="password" value={password} onChange={setPassword}
              placeholder="Пароль" autoComplete={isRegister ? 'new-password' : 'current-password'} onEnter={submit} />

            <ErrorBox err={err} />

            {isRegister && <ConsentBox consent={consent} setConsent={setConsent} onOpenPolicy={onOpenPolicy} />}

            <button className="btn btn-primary" disabled={busy}
              style={{ height: 46, marginTop: 4, justifyContent: 'center' }} onClick={submit}>
              {busy ? 'Подождите…' : isRegister ? 'Зарегистрироваться' : 'Войти'}
              {!busy && <Icon name="arrow" size={18} />}
            </button>

            <button className="btn btn-ghost" disabled={busy}
              style={{ height: 44, justifyContent: 'center', gap: 8, fontSize: 14 }}
              onClick={() => switchMode('code')}>
              <Icon name="lock" size={17} /> Войти по коду на e-mail
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '6px 0 2px' }}>
              <div className="hairline" style={{ flex: 1 }} />
              <span style={{ fontSize: 12.5, color: 'var(--faint)' }}>{isRegister ? 'или зарегистрироваться через' : 'или войти через'}</span>
              <div className="hairline" style={{ flex: 1 }} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
              <ProviderButton mark="Я" color="#FC3F1D" label={`${isRegister ? 'Регистрация' : 'Войти'} через Яндекс`}
                disabled={busy} onClick={() => oauth('yandex')} />
              <ProviderButton mark="VK" color="#0077FF" label={`${isRegister ? 'Регистрация' : 'Войти'} через ВКонтакте`}
                disabled={busy} onClick={() => oauth('vk')} />
            </div>

            <div style={{ textAlign: 'center', marginTop: 18, fontSize: 13.5, color: 'var(--muted)' }}>
              {isRegister ? 'Уже есть аккаунт?' : 'Нет аккаунта?'}{' '}
              <button className="btn btn-quiet" style={{ height: 26, padding: '0 6px', fontSize: 13.5, color: 'var(--accent-ink)' }}
                onClick={() => switchMode(isRegister ? 'login' : 'register')}>
                {isRegister ? 'Войти' : 'Создать'}
              </button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

export default Auth;
