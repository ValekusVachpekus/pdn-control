/* ===== ПДн Контроль — Landing ===== */
import { useState, useRef, useEffect } from 'react';
import { Icon, Logo } from './shared.jsx';
import { isValidDomain, normalizeDomain } from './api.js';

function Landing({ onStart, onLogin, onLogout, onUpgrade, onOpenHistory, user, onOpenPolicy }) {
  const [url, setUrl] = useState('');
  const [focus, setFocus] = useState(false);
  const [err, setErr] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const inputRef = useRef(null);
  const menuRef = useRef(null);

  // Закрываем меню профиля при клике снаружи.
  useEffect(() => {
    if (!menuOpen) return;
    const onClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, [menuOpen]);

  const submit = () => {
    const raw = url.trim();
    // Пустой ввод → подсветить ошибку, не отправлять заглушечный домен.
    if (!raw) { setErr(true); inputRef.current?.focus(); return; }
    if (!isValidDomain(raw)) { setErr(true); return; }
    onStart(normalizeDomain(raw));
  };

  const checks = [
    { icon: 'form', t: 'Формы и согласия', d: 'Чекбоксы, pre-checked, объединённые согласия' },
    { icon: 'cookie', t: 'Cookie-баннеры', d: 'Кнопка отказа, состав cookie' },
    { icon: 'code', t: 'Сторонние скрипты', d: 'Метрики, CRM, чат-виджеты, трекеры' },
    { icon: 'doc', t: 'Политики и документы', d: 'Политика ПДн, сроки хранения' },
    { icon: 'server', t: 'Локализация ПДн', d: 'Геолокация сервера, ст. 18 ч. 5' },
    { icon: 'ai', t: 'AI-анализ текстов', d: 'Согласия, cookie-уведомления, политика' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      {/* top bar */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '20px 32px', maxWidth: 1180, margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
          <Logo size={32} />
          <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: '-.01em' }}>ПДн Контроль</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <button className="btn btn-quiet" style={{ height: 38 }}
            onClick={() => user ? onOpenHistory?.() : onLogin?.()}>
            <Icon name="history" size={17} /> История
          </button>
          <button className="btn btn-quiet" style={{ height: 38 }} onClick={onUpgrade}>
            <Icon name="bolt" size={17} /> Тарифы
          </button>
          {user ? (
            <div ref={menuRef} style={{ position: 'relative' }}>
              <button className="btn btn-ghost" style={{ height: 38 }}
                onClick={() => setMenuOpen(o => !o)}>
                <Icon name="user" size={16} /> {user.email}
              </button>
              {menuOpen && (
                <div className="card fade-up" style={{ position: 'absolute', top: 'calc(100% + 6px)',
                  right: 0, minWidth: 200, padding: 6, boxShadow: 'var(--shadow-lg)', zIndex: 100 }}>
                  <div style={{ padding: '8px 12px', fontSize: 12, color: 'var(--muted)',
                    borderBottom: '1px solid var(--border)', marginBottom: 4 }}>
                    {user.email}
                  </div>
                  <button className="btn btn-quiet" style={{ width: '100%', height: 36,
                    justifyContent: 'flex-start' }}
                    onClick={() => { setMenuOpen(false); onLogout?.(); }}>
                    <Icon name="arrow" size={15} style={{ transform: 'rotate(180deg)' }} /> Выйти
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button className="btn btn-ghost" style={{ height: 38 }} onClick={onLogin}>
              Войти
            </button>
          )}
        </div>
      </header>

      {/* hero */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '24px 24px 56px', textAlign: 'center', maxWidth: 880, margin: '0 auto', width: '100%' }}>
        <h1 className="fade-up" style={{ margin: 0, fontSize: 'clamp(32px, 4.4vw, 48px)', fontWeight: 600,
          letterSpacing: '-.018em', lineHeight: 1.12, color: 'var(--ink)' }}>
          Узнайте, чем рискует ваш сайт по закону о персональных данных
        </h1>
        <p className="fade-up" style={{ margin: '20px auto 0', fontSize: 'clamp(16px,2vw,19px)', color: 'var(--muted)',
          maxWidth: 600, lineHeight: 1.5, animationDelay: '.05s' }}>
          Введите адрес сайта — за минуту проверим на соответствие <strong>152-ФЗ</strong>: формы, согласия, cookie, трекеры и политику.
          Покажем риск-скоринг, нарушения, потенциальные штрафы и что исправить в первую очередь.
        </p>

        {/* URL input */}
        <div className="fade-up" style={{ width: '100%', maxWidth: 620, marginTop: 34, animationDelay: '.1s' }}>
          <div style={{ display: 'flex', gap: 10, alignItems: 'stretch',
            background: 'var(--surface)', borderRadius: 14, padding: 8,
            border: `1.5px solid ${err ? 'var(--crit)' : focus ? 'var(--accent)' : 'var(--border-2)'}`,
            boxShadow: focus ? `0 0 0 4px var(--ring), var(--shadow-md)` : 'var(--shadow-md)', transition: 'all .18s' }}>
            <div style={{ display: 'flex', alignItems: 'center', paddingLeft: 12, color: 'var(--faint)' }}>
              <Icon name="globe" size={20} />
            </div>
            <input ref={inputRef} value={url}
              onChange={e => { setUrl(e.target.value); setErr(false); }}
              onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
              onKeyDown={e => e.key === 'Enter' && submit()}
              placeholder="example.ru"
              style={{ flex: 1, border: 0, outline: 0, background: 'transparent', font: 'inherit',
                fontSize: 17, color: 'var(--ink)', padding: '0 6px', minWidth: 0 }} />
            <button className="btn btn-primary" style={{ height: 48, padding: '0 22px', fontSize: 15 }} onClick={submit}>
              Проверить сайт <Icon name="arrow" size={18} />
            </button>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12, padding: '0 4px' }}>
            <span style={{ fontSize: 13, color: err ? 'var(--crit)' : 'var(--faint)',
              display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              {err
                ? 'Введите корректный адрес сайта'
                : 'Проверка бесплатно · полный отчёт — разовая оплата'}
            </span>
            <button className="btn btn-quiet" style={{ height: 30, padding: '0 8px', fontSize: 13, color: 'var(--accent-ink)' }}
              onClick={() => { setUrl('klinika-zdorovie.ru'); inputRef.current && inputRef.current.focus(); }}>
              Заполнить примером
            </button>
          </div>
        </div>

        {/* what we check */}
        <div className="fade-up" style={{ width: '100%', marginTop: 56, textAlign: 'left', animationDelay: '.16s' }}>
          <div className="label-eyebrow" style={{ marginBottom: 6 }}>Что проверяем</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', columnGap: 48 }}>
            {checks.map((c, i) => (
              <div key={i} style={{ display: 'flex', gap: 14, alignItems: 'baseline',
                padding: '15px 0', borderTop: '1px solid var(--border)' }}>
                <span className="mono" style={{ fontSize: 12, color: 'var(--faint)', minWidth: 20 }}>{String(i + 1).padStart(2, '0')}</span>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--ink)' }}>{c.t}</div>
                  <div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2, lineHeight: 1.45 }}>{c.d}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p style={{ marginTop: 34, fontSize: 12.5, color: 'var(--faint)', maxWidth: 560, lineHeight: 1.5 }}>
          ПДн Контроль выполняет предварительный технический аудит и помогает снизить типовые риски.
          Сервис не гарантирует полное соответствие 152-ФЗ и не заменяет консультацию юриста.
        </p>
        <button className="btn btn-quiet" onClick={onOpenPolicy}
          style={{ marginTop: 14, height: 30, padding: '0 8px', fontSize: 13, color: 'var(--accent-ink)' }}>
          Политика обработки персональных данных
        </button>
      </div>
    </div>
  );
}
export default Landing;
