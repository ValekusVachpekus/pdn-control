/* ===== ПДн Контроль — shared UI ===== */
import { useState, useEffect, useRef } from 'react';
import { RISK_BANDS } from './data.jsx';

/* ---------- icon set (simple line icons) ---------- */
const ICON_PATHS = {
  shield: 'M12 3l7 3v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z',
  scan: 'M4 8V5a1 1 0 011-1h3M16 4h3a1 1 0 011 1v3M20 16v3a1 1 0 01-1 1h-3M8 20H5a1 1 0 01-1-1v-3 M4 12h16',
  history: 'M3 12a9 9 0 109-9 9 9 0 00-7.5 4M3 4v4h4 M12 8v4l3 2',
  rules: 'M4 6h10 M18 6h2 M4 12h4 M12 12h8 M4 18h12 M16 18h4 M16 4v4 M10 10v4 M14 16v4',
  doc: 'M6 3h7l5 5v13a0 0 0 01 0 0H6a0 0 0 010 0V3z M13 3v5h5 M9 13h6 M9 17h6',
  alert: 'M12 4l9 16H3l9-16z M12 10v4 M12 17.5v.01',
  xcircle: 'M12 3a9 9 0 100 18 9 9 0 000-18z M15 9l-6 6 M9 9l6 6',
  info: 'M12 3a9 9 0 100 18 9 9 0 000-18z M12 11v5 M12 7.5v.01',
  check: 'M5 12l5 5L20 7',
  checkcircle: 'M12 3a9 9 0 100 18 9 9 0 000-18z M8.5 12l2.5 2.5 4.5-5',
  chevron: 'M9 6l6 6-6 6',
  chevdown: 'M6 9l6 6 6-6',
  external: 'M14 5h5v5 M19 5l-8 8 M19 13v6H5V5h6',
  download: 'M12 4v11 M7 11l5 5 5-5 M5 20h14',
  globe: 'M12 3a9 9 0 100 18 9 9 0 000-18z M3 12h18 M12 3c2.5 2.5 2.5 15 0 18 M12 3c-2.5 2.5-2.5 15 0 18',
  server: 'M4 5h16v5H4z M4 14h16v5H4z M7.5 7.5v.01 M7.5 16.5v.01',
  cookie: 'M12 3a9 9 0 109 9 4 4 0 01-4-4 4 4 0 01-4-4 9 9 0 00-1-1z M9 13v.01 M13 16v.01 M15 11v.01',
  form: 'M4 4h16v16H4z M8 9h8 M8 13h8 M8 17h4',
  code: 'M9 8l-4 4 4 4 M15 8l4 4-4 4',
  ai: 'M12 3l1.8 4.7L18.5 9 13.8 10.3 12 15l-1.8-4.7L5.5 9l4.7-1.3L12 3z M18 15l.7 1.8L20.5 17.5l-1.8.7L18 20l-.7-1.8L15.5 17.5l1.8-.7L18 15z',
  arrow: 'M5 12h14 M13 6l6 6-6 6',
  lock: 'M6 11h12v9H6z M9 11V8a3 3 0 016 0v3',
  building: 'M5 21V4a1 1 0 011-1h7a1 1 0 011 1v17 M14 9h4a1 1 0 011 1v11 M8 7h3 M8 11h3 M8 15h3',
  search: 'M11 4a7 7 0 100 14 7 7 0 000-14z M20 20l-4-4',
  clock: 'M12 3a9 9 0 100 18 9 9 0 000-18z M12 7v5l3 2',
  user: 'M12 12a4 4 0 100-8 4 4 0 000 8z M5 20a7 7 0 0114 0',
  sun: 'M12 5a7 7 0 100 14 7 7 0 000-14z M12 1v2 M12 21v2 M4 4l1.5 1.5 M18.5 18.5L20 20 M1 12h2 M21 12h2 M4 20l1.5-1.5 M18.5 5.5L20 4',
  bolt: 'M13 3L5 13h6l-1 8 8-10h-6l1-8z',
  filter: 'M4 5h16l-6 7v6l-4 2v-8L4 5z',
  copy: 'M9 9h11v11H9z M5 15H4V4h11v1',
  moon: 'M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z',
};

function Icon({ name, size = 20, stroke = 1.7, className = '', style = {} }) {
  const d = ICON_PATHS[name] || '';
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round"
      className={className} style={{ flexShrink: 0, ...style }} aria-hidden="true">
      {d.split(' M').map((seg, i) => <path key={i} d={(i === 0 ? seg : 'M' + seg)} />)}
    </svg>
  );
}

/* ---------- severity helpers ---------- */
const SEV = {
  critical: { chip: 'chip-crit', icon: 'xcircle', label: 'Критично', color: 'var(--crit)', soft: 'var(--crit-soft)', ink: 'var(--crit-ink)' },
  warning:  { chip: 'chip-warn', icon: 'alert',   label: 'Предупреждение', color: 'var(--warn)', soft: 'var(--warn-soft)', ink: 'var(--warn-ink)' },
  info:     { chip: 'chip-info', icon: 'info',    label: 'Инфо', color: 'var(--info)', soft: 'var(--info-soft)', ink: 'var(--info-ink)' },
  ok:       { chip: 'chip-ok',   icon: 'checkcircle', label: 'Пройдено', color: 'var(--ok)', soft: 'var(--ok-soft)', ink: 'var(--ok-ink)' },
};
const FOR_ICON = { 'Разработчик': 'code', 'Юрист': 'doc', 'Маркетолог': 'bolt' };

function Badge({ severity, withLabel = true, size = 13 }) {
  const s = SEV[severity];
  return (
    <span className={`chip ${s.chip}`} style={{ fontSize: size - 1 }}>
      <Icon name={s.icon} size={size + 1} stroke={2} />
      {withLabel && s.label}
    </span>
  );
}

/* ---------- Risk gauge (semicircle arc) ---------- */
function RiskGauge({ score, band, size = 260 }) {
  const bands = RISK_BANDS[band];
  const [shown, setShown] = useState(0);
  useEffect(() => {
    let raf, start;
    const dur = 900;
    const tick = (ts) => {
      if (!start) start = ts;
      const p = Math.min(1, (ts - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setShown(Math.round(score * eased));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [score]);

  const w = size, h = size * 0.62;
  const cx = w / 2, cy = h * 0.94, r = w * 0.40, sw = w * 0.072;
  const circ = Math.PI * r;
  const frac = shown / 100;
  const arc = (cxx, cyy, rr) => `M ${cxx - rr} ${cyy} A ${rr} ${rr} 0 0 1 ${cxx + rr} ${cyy}`;
  // tick marks at 0,25,50,75,100
  return (
    <div style={{ position: 'relative', width: w, height: h + 6 }}>
      <svg width={w} height={h + 6} viewBox={`0 0 ${w} ${h + 6}`}>
        <path d={arc(cx, cy, r)} fill="none" stroke="var(--surface-3)" strokeWidth={sw} strokeLinecap="round" />
        <path d={arc(cx, cy, r)} fill="none" stroke={bands.color} strokeWidth={sw} strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={circ * (1 - frac)}
          style={{ transition: 'stroke .4s' }} />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'flex-end', paddingBottom: h * 0.03 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
          <span style={{ fontSize: w * 0.19, fontWeight: 800, lineHeight: 1, letterSpacing: '-.03em', color: bands.color }}>{shown}</span>
          <span style={{ fontSize: w * 0.072, fontWeight: 600, color: 'var(--faint)' }}>/ 100</span>
        </div>
        <span className="chip" style={{ marginTop: 8, background: bands.soft, color: bands.ink, fontSize: 12.5, padding: '5px 12px' }}>
          <span style={{ width: 7, height: 7, borderRadius: 99, background: bands.color, display: 'inline-block' }}></span>
          {bands.label}
        </span>
      </div>
    </div>
  );
}

/* ---------- mini meter bar ---------- */
function Meter({ label, value, color }) {
  const [w, setW] = useState(0);
  useEffect(() => { const t = setTimeout(() => setW(value), 120); return () => clearTimeout(t); }, [value]);
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7 }}>
        <span style={{ fontSize: 13.5, color: 'var(--ink-2)', fontWeight: 500 }}>{label}</span>
        <span className="mono" style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink)' }}>{value}</span>
      </div>
      <div style={{ height: 8, borderRadius: 99, background: 'var(--surface-3)', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${w}%`, background: color || 'var(--accent)', borderRadius: 99, transition: 'width .9s cubic-bezier(.2,.7,.2,1)' }}></div>
      </div>
    </div>
  );
}

/* ---------- App shell (sidebar + topbar) ---------- */
function AppShell({ nav, setNav, children, onNewScan, detail, theme, onToggleTheme }) {
  const items = [
    { id: 'report', icon: 'shield', label: 'Отчёт' },
    { id: 'history', icon: 'history', label: 'История' },
  ];
  return (
    <div className="app-layout" style={{ display: 'flex', minHeight: '100vh' }}>
      <aside className="sidebar" style={{ width: 248, flexShrink: 0, background: 'var(--surface)', borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', position: 'sticky', top: 0, height: '100vh' }}>
        <div className="sidebar-logo" style={{ padding: '20px 20px 16px', display: 'flex', alignItems: 'center', gap: 11 }}>
          <Logo size={30} />
          <div style={{ lineHeight: 1.1 }}>
            <div style={{ fontWeight: 700, fontSize: 15.5, letterSpacing: '-.01em' }}>ПДн Контроль</div>
            <div style={{ fontSize: 11, color: 'var(--faint)', fontWeight: 500 }}>аудит 152-ФЗ</div>
          </div>
        </div>
        <button className="btn btn-primary sidebar-new-scan" style={{ margin: '4px 16px 14px', height: 42 }} onClick={onNewScan}>
          <Icon name="scan" size={18} /> Новая проверка
        </button>
        <nav className="sidebar-nav" style={{ display: 'flex', flexDirection: 'column', gap: 2, padding: '0 12px' }}>
          {items.map(it => (
            <button key={it.id} onClick={() => !it.soon && setNav(it.id)} disabled={it.soon}
              style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '10px 12px', borderRadius: 10,
                border: 0, cursor: it.soon ? 'default' : 'pointer', textAlign: 'left', width: '100%',
                font: 'inherit', fontSize: 14, fontWeight: 600,
                background: nav === it.id ? 'var(--accent-soft)' : 'transparent',
                color: it.soon ? 'var(--faint)' : nav === it.id ? 'var(--accent-ink)' : 'var(--ink-2)',
                transition: 'all .14s' }}
              onMouseEnter={e => { if (nav !== it.id && !it.soon) e.currentTarget.style.background = 'var(--surface-3)'; }}
              onMouseLeave={e => { if (nav !== it.id) e.currentTarget.style.background = 'transparent'; }}>
              <Icon name={it.icon} size={19} stroke={nav === it.id ? 2 : 1.7} />
              {it.label}
              {it.soon && <span className="kbd" style={{ marginLeft: 'auto', fontSize: 9.5 }}>скоро</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer" style={{ marginTop: 'auto', padding: '0 16px 16px' }}>
          <button
            className="btn btn-ghost"
            onClick={onToggleTheme}
            title={theme ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'}
            style={{ width: '100%', justifyContent: 'flex-start', height: 40, marginBottom: 10,
              gap: 9, color: 'var(--ink-2)', fontSize: 13.5 }}>
            <Icon name={theme ? 'sun' : 'moon'} size={17} stroke={1.8} />
            {theme ? 'Светлая тема' : 'Тёмная тема'}
          </button>
          <div className="card" style={{ padding: '12px 13px', background: 'var(--surface-2)', borderRadius: 12, display: 'flex', gap: 10, alignItems: 'flex-start' }}>
            <Icon name="info" size={17} style={{ color: 'var(--faint)', marginTop: 1 }} />
            <p style={{ margin: 0, fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.45 }}>
              Предварительный технический аудит. Не является юридическим заключением.
            </p>
          </div>
        </div>
      </aside>
      <main style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        {children}
      </main>
    </div>
  );
}

/* ---------- Modal (overlay + centered card, ESC/backdrop to close) ---------- */
function Modal({ open, onClose, children, width = 440 }) {
  useEffect(() => {
    if (!open) return;
    const onKey = e => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => { window.removeEventListener('keydown', onKey); document.body.style.overflow = ''; };
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div onMouseDown={onClose}
      style={{ position: 'fixed', inset: 0, zIndex: 2000, display: 'flex', alignItems: 'center',
        justifyContent: 'center', padding: 20, background: 'rgba(15,20,28,.55)', backdropFilter: 'blur(3px)' }}>
      <div className="card fade-up" onMouseDown={e => e.stopPropagation()}
        style={{ width: '100%', maxWidth: width, boxShadow: 'var(--shadow-lg)', position: 'relative',
          maxHeight: '90vh', overflowY: 'auto' }}>
        <button onClick={onClose} aria-label="Закрыть"
          style={{ position: 'absolute', top: 14, right: 14, width: 32, height: 32, borderRadius: 8,
            border: 0, background: 'transparent', color: 'var(--faint)', cursor: 'pointer',
            display: 'grid', placeItems: 'center', transition: 'all .14s' }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--surface-3)'; e.currentTarget.style.color = 'var(--ink)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--faint)'; }}>
          <Icon name="xcircle" size={20} />
        </button>
        {children}
      </div>
    </div>
  );
}

/* ---------- Logo mark ---------- */
function Logo({ size = 32 }) {
  return (
    <div style={{ width: size, height: size, borderRadius: size * 0.28, background: 'var(--accent)',
      display: 'grid', placeItems: 'center', flexShrink: 0, boxShadow: '0 2px 6px rgba(31,138,91,.35)' }}>
      <Icon name="shield" size={size * 0.62} stroke={2} style={{ color: '#fff' }} />
    </div>
  );
}

export { Icon, Badge, RiskGauge, Meter, AppShell, Logo, Modal, SEV, FOR_ICON };
