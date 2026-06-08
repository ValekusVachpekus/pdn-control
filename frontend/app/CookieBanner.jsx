/* ===== ПДн Контроль — cookie-баннер (152-ФЗ) =====
 * Информирует об использовании cookie и даёт выбор «Принять» / «Отклонить».
 * Кнопка отказа обязательна — наш же сканер штрафует баннеры без неё
 * (cookie_banner_has_reject=false). Выбор хранится в localStorage и больше
 * не показывается. Реальной загрузкой трекеров баннер пока не управляет —
 * на фронте сторонних трекеров нет; решение фиксируется для будущего бэкенда. */
import { useState } from 'react';
import { Icon } from './shared.jsx';

const STORAGE_KEY = 'pdn_cookie_consent'; // 'accepted' | 'rejected'

/* Хелперы согласия — экспортируются, чтобы при желании открыть «настройки
 * cookie» заново (сброс ключа возвращает баннер). */
export const getCookieConsent = () => {
  try { return localStorage.getItem(STORAGE_KEY); } catch { return null; }
};
export const setCookieConsent = (value) => {
  try { localStorage.setItem(STORAGE_KEY, value); } catch { /* приватный режим */ }
};
export const resetCookieConsent = () => {
  try { localStorage.removeItem(STORAGE_KEY); } catch { /* no-op */ }
};

function CookieBanner({ onOpenPolicy }) {
  // В dev баннер показываем при каждой перезагрузке (удобно тестировать);
  // в проде — читаем сохранённый выбор и больше не показываем.
  const [choice, setChoice] = useState(() => (import.meta.env.DEV ? null : getCookieConsent()));
  if (choice) return null;

  const decide = (value) => { setCookieConsent(value); setChoice(value); };

  return (
    <div className="fade-up" style={{ position: 'fixed', right: 18, bottom: 18,
      zIndex: 1800, width: 'calc(100% - 36px)', maxWidth: 360,
      background: 'var(--surface)', border: '1px solid var(--border-2)', borderRadius: 16,
      boxShadow: 'var(--shadow-lg)', padding: 20,
      display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
        <span style={{ width: 38, height: 38, borderRadius: 11, background: 'var(--accent-soft)',
          display: 'grid', placeItems: 'center', flexShrink: 0 }}>
          <Icon name="cookie" size={22} stroke={1.8} style={{ color: 'var(--accent)' }} />
        </span>
        <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--ink)' }}>Файлы cookie</div>
      </div>
      <div style={{ fontSize: 13.5, color: 'var(--muted)', lineHeight: 1.5 }}>
        Мы используем cookie для работы сайта и аналитики. Подробнее — в{' '}
        <button className="btn btn-quiet" onClick={onOpenPolicy}
          style={{ height: 'auto', padding: 0, fontSize: 13.5, color: 'var(--accent-ink)',
            textDecoration: 'underline', display: 'inline' }}>
          политике обработки ПДн
        </button>.
      </div>
      <div style={{ display: 'flex', gap: 9 }}>
        <button className="btn btn-ghost" style={{ flex: 1, height: 42, fontSize: 13.5, justifyContent: 'center' }}
          onClick={() => decide('rejected')}>
          Отклонить
        </button>
        <button className="btn btn-primary" style={{ flex: 1, height: 42, fontSize: 13.5, justifyContent: 'center' }}
          onClick={() => decide('accepted')}>
          Принять
        </button>
      </div>
    </div>
  );
}

export default CookieBanner;
