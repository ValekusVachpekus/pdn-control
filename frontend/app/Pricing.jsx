/* ===== ПДн Контроль — покупка платной версии (Pro) =====
 * ШАБЛОН для подключения биллинга. Каталог тарифов приходит из api.fetchPlans()
 * (в MOCK — дефолт, в проде — бэкенд), цены/фичи во фронте НЕ захардкожены.
 * createCheckout(plan) возвращает checkout_url платёжного провайдера —
 * фронт лишь редиректит на него. Проверка оплаты — на бэкенде. */
import { useState, useEffect } from 'react';
import { Icon, Modal } from './shared.jsx';
import { fetchPlans, createCheckout } from './api.js';

const CTA = { free: 'Текущий план', pro: 'Перейти на Pro', team: 'Подключить Team' };

function fmtPrice(p) {
  return new Intl.NumberFormat('ru-RU').format(p ?? 0);
}

function PlanCard({ plan, current, busy, onPick }) {
  const hi = plan.highlight;
  const isCurrent = plan.id === current;
  return (
    <div className="card" style={{ flex: '1 1 220px', minWidth: 220, padding: '20px 20px 22px',
      position: 'relative', borderColor: hi ? 'var(--accent)' : 'var(--border)',
      boxShadow: hi ? '0 0 0 1px var(--accent), var(--shadow-md)' : 'var(--shadow-sm)' }}>
      {hi && !isCurrent && (
        <span className="chip" style={{ position: 'absolute', top: -11, left: 20,
          background: 'var(--accent)', color: '#fff', fontSize: 11 }}>Популярный</span>
      )}
      {isCurrent && (
        <span className="chip chip-ok" style={{ position: 'absolute', top: -11, left: 20, fontSize: 11 }}>
          <Icon name="checkcircle" size={13} stroke={2.2} /> Активен
        </span>
      )}
      <div style={{ fontSize: 15, fontWeight: 700 }}>{plan.name}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, margin: '8px 0 16px' }}>
        <span style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-.02em' }}>{fmtPrice(plan.price)} ₽</span>
        {plan.period && <span style={{ fontSize: 13, color: 'var(--faint)' }}>{plan.period}</span>}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 9, marginBottom: 18 }}>
        {plan.features.map((f, i) => (
          <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'flex-start', fontSize: 13.5, color: 'var(--ink-2)' }}>
            <Icon name="check" size={16} stroke={2.2} style={{ color: 'var(--ok)', marginTop: 1 }} /> {f}
          </div>
        ))}
      </div>
      <button className={`btn ${isCurrent ? 'btn-pro' : hi ? 'btn-primary' : 'btn-ghost'}`}
        disabled={isCurrent || plan.id === 'free' || busy}
        style={{ width: '100%', justifyContent: 'center', height: 42 }}
        onClick={() => onPick(plan.id)}>
        {isCurrent ? 'Подписка активна' : busy === plan.id ? 'Переход к оплате…' : (CTA[plan.id] || 'Выбрать')}
      </button>
    </div>
  );
}

function Pricing({ open, onClose, onToast, currentPlan = 'free', onSubscribed, user, onRequireAuth }) {
  const [plans, setPlans] = useState(null);
  const [busy, setBusy] = useState(null);

  useEffect(() => {
    if (!open) return;
    let alive = true;
    setPlans(null);
    fetchPlans()
      .then(p => { if (alive) setPlans(p); })
      .catch(() => { if (alive) { setPlans([]); onToast && onToast('Не удалось загрузить тарифы', 'info'); } });
    return () => { alive = false; };
  }, [open]);

  const pick = async (planId) => {
    // UX-гейт: оплата только для авторизованных. Это НЕ замена защите —
    // бэкенд обязан сам отклонять /api/billing/checkout без сессии (401).
    if (!user) {
      onToast && onToast('Войдите, чтобы оформить подписку', 'info');
      onRequireAuth && onRequireAuth();
      return;
    }
    setBusy(planId);
    try {
      const { checkout_url } = await createCheckout(planId);
      if (checkout_url) { window.location.href = checkout_url; return; } // прод: переход к оплате
      // MOCK/демо: оплаты нет — имитируем активацию подписки локально
      onSubscribed && onSubscribed(planId);
      onToast && onToast('Демо: подписка Pro активирована', 'ok');
      onClose();
    } catch {
      onToast && onToast('Не удалось перейти к оплате', 'info');
    } finally {
      setBusy(null);
    }
  };

  return (
    <Modal open={open} onClose={onClose} width={780}>
      <div style={{ padding: '32px 30px 30px' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div className="label-eyebrow" style={{ marginBottom: 8 }}>Тарифы</div>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700, letterSpacing: '-.01em' }}>
            Больше проверок и полные отчёты
          </h2>
          <p style={{ margin: '8px auto 0', fontSize: 14, color: 'var(--muted)', maxWidth: 480 }}>
            Откройте PDF-отчёты, AI-анализ политик и безлимит проверок. Отмена в любой момент.
          </p>
        </div>

        {plans === null ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--muted)', fontSize: 14 }}>
            Загрузка тарифов…
          </div>
        ) : (
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
            {plans.map(p => <PlanCard key={p.id} plan={p} current={currentPlan} busy={busy} onPick={pick} />)}
          </div>
        )}

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 12, color: 'var(--faint)' }}>
          Тарифы и оплата настраиваются на стороне бэкенда. В демо-режиме оплата имитируется.
        </p>
      </div>
    </Modal>
  );
}

export default Pricing;
