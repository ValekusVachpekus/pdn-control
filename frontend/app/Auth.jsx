/* ===== ПДн Контроль — окно входа / регистрации =====
 * ШАБЛОН для подключения бэкенда. Вся сетевая логика — в api.js
 * (login / register). Здесь только UI, локальная валидация и состояния.
 * При интеграции: после успеха пробросить user наверх через onAuth(user). */
import { useState } from 'react';
import { Icon, Logo, Modal } from './shared.jsx';
import { login, register } from './api.js';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

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

function Auth({ open, onClose, onAuth, onToast }) {
  const [mode, setMode] = useState('login'); // login | register
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const isRegister = mode === 'register';

  const submit = async () => {
    setErr('');
    if (!EMAIL_RE.test(email.trim())) { setErr('Введите корректный e-mail'); return; }
    if (password.length < 8) { setErr('Пароль — минимум 8 символов'); return; }
    setBusy(true);
    try {
      const fn = isRegister ? register : login;
      const { user } = await fn({ email: email.trim(), password });
      onToast && onToast(isRegister ? 'Аккаунт создан' : 'Вы вошли', 'ok');
      onAuth && onAuth(user);
      onClose();
    } catch {
      setErr(isRegister ? 'Не удалось зарегистрироваться' : 'Неверный e-mail или пароль');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} width={420}>
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

          <button className="btn btn-primary" disabled={busy}
            style={{ height: 46, marginTop: 4, justifyContent: 'center' }} onClick={submit}>
            {busy ? 'Подождите…' : isRegister ? 'Зарегистрироваться' : 'Войти'}
            {!busy && <Icon name="arrow" size={18} />}
          </button>
        </div>

        <div style={{ textAlign: 'center', marginTop: 18, fontSize: 13.5, color: 'var(--muted)' }}>
          {isRegister ? 'Уже есть аккаунт?' : 'Нет аккаунта?'}{' '}
          <button className="btn btn-quiet" style={{ height: 26, padding: '0 6px', fontSize: 13.5, color: 'var(--accent-ink)' }}
            onClick={() => { setMode(isRegister ? 'login' : 'register'); setErr(''); }}>
            {isRegister ? 'Войти' : 'Создать'}
          </button>
        </div>
      </div>
    </Modal>
  );
}

export default Auth;
