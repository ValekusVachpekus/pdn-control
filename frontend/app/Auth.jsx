/* ===== ПДн Контроль — окно входа / регистрации =====
 * ШАБЛОН для подключения бэкенда. Вся сетевая логика — в api.js
 * (login / register). Здесь только UI, локальная валидация и состояния.
 * При интеграции: после успеха пробросить user наверх через onAuth(user). */
import { useState } from 'react';
import { Icon, Logo, Modal } from './shared.jsx';
import { login, register, loginWithProvider } from './api.js';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

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

function Field({ icon, type = 'text', value, onChange, placeholder, autoComplete, onEnter }) {
  const [focus, setFocus] = useState(false);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, height: 46, padding: '0 14px',
      background: 'var(--surface-2)', borderRadius: 11,
      border: `1.5px solid ${focus ? 'var(--accent)' : 'var(--border-2)'}`,
      boxShadow: focus ? '0 0 0 4px var(--ring)' : 'none', transition: 'all .16s' }}>
      <Icon name={icon} size={18} style={{ color: 'var(--faint)' }} />
      <input type={type} value={value} autoComplete={autoComplete}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
        onKeyDown={e => e.key === 'Enter' && onEnter && onEnter()}
        placeholder={placeholder}
        style={{ flex: 1, border: 0, outline: 0, background: 'transparent', font: 'inherit',
          fontSize: 14.5, color: 'var(--ink)', minWidth: 0 }} />
    </div>
  );
}

function Auth({ open, onClose, onAuth, onToast, onOpenPolicy }) {
  const [mode, setMode] = useState('login'); // login | register
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [consent, setConsent] = useState(false); // согласие на обработку ПДн — снято по умолчанию (ст. 9)
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const isRegister = mode === 'register';

  // Auth остаётся смонтированным между открытиями — чистим состояние при закрытии,
  // чтобы галочка согласия и ошибки не «протекали» в следующую сессию (ст. 9: по умолчанию снято).
  const handleClose = () => {
    setErr('');
    setConsent(false);
    setPassword('');
    onClose();
  };

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

  const oauth = async (provider) => {
    setErr('');
    if (isRegister && !consent) { setErr('Подтвердите согласие на обработку персональных данных'); return; }
    setBusy(true);
    try {
      const { user } = await loginWithProvider(provider, isRegister ? consent : undefined);
      onToast && onToast('Вы вошли', 'ok');
      onAuth && onAuth(user);
      handleClose();
    } catch {
      setErr('Не удалось войти через провайдера');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal open={open} onClose={handleClose} width={420}>
      <div style={{ padding: '32px 30px 28px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, marginBottom: 22 }}>
          <Logo size={40} />
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, letterSpacing: '-.01em' }}>
              {isRegister ? 'Создать аккаунт' : 'Вход в ПДн Контроль'}
            </h2>
            <p style={{ margin: '6px 0 0', fontSize: 13.5, color: 'var(--muted)' }}>
              {isRegister ? 'История проверок и доступ к Pro' : 'Доступ к истории и сохранённым отчётам'}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
          <Field icon="user" type="email" value={email} onChange={setEmail}
            placeholder="you@company.ru" autoComplete="email" onEnter={submit} />
          <Field icon="lock" type="password" value={password} onChange={setPassword}
            placeholder="Пароль" autoComplete={isRegister ? 'new-password' : 'current-password'} onEnter={submit} />

          {err && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 13,
              color: 'var(--crit-ink)', background: 'var(--crit-soft)', padding: '8px 11px', borderRadius: 9 }}>
              <Icon name="alert" size={15} stroke={2} /> {err}
            </div>
          )}

          {isRegister && (
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
          )}

          <button className="btn btn-primary" disabled={busy}
            style={{ height: 46, marginTop: 4, justifyContent: 'center' }} onClick={submit}>
            {busy ? 'Подождите…' : isRegister ? 'Зарегистрироваться' : 'Войти'}
            {!busy && <Icon name="arrow" size={18} />}
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
        </div>

        <div style={{ textAlign: 'center', marginTop: 18, fontSize: 13.5, color: 'var(--muted)' }}>
          {isRegister ? 'Уже есть аккаунт?' : 'Нет аккаунта?'}{' '}
          <button className="btn btn-quiet" style={{ height: 26, padding: '0 6px', fontSize: 13.5, color: 'var(--accent-ink)' }}
            onClick={() => { setMode(isRegister ? 'login' : 'register'); setErr(''); setConsent(false); }}>
            {isRegister ? 'Войти' : 'Создать'}
          </button>
        </div>
      </div>
    </Modal>
  );
}

export default Auth;
