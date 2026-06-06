/* ===== ПДн Контроль — History ===== */
import { useState } from 'react';
import { Icon, Badge } from './shared.jsx';
import { HISTORY, RISK_BANDS } from './data.jsx';

function ScorePill({ score, band }) {
  const b = RISK_BANDS[band];
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
      <span style={{ position: 'relative', width: 34, height: 34, flexShrink: 0 }}>
        <svg width={34} height={34} viewBox="0 0 34 34" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="17" cy="17" r="14" fill="none" stroke="var(--surface-3)" strokeWidth="4" />
          <circle cx="17" cy="17" r="14" fill="none" stroke={b.color} strokeWidth="4" strokeLinecap="round"
            strokeDasharray={2 * Math.PI * 14} strokeDashoffset={2 * Math.PI * 14 * (1 - score / 100)} />
        </svg>
        <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', fontSize: 12, fontWeight: 700, color: b.ink }}>{score}</span>
      </span>
      <span className="chip" style={{ background: b.soft, color: b.ink, fontSize: 11.5 }}>{b.label}</span>
    </span>
  );
}

function History({ onOpen, onToast }) {
  const items = HISTORY;
  const [q, setQ] = useState('');
  const list = items.filter(i => i.domain.includes(q.toLowerCase()) || i.org.toLowerCase().includes(q.toLowerCase()));

  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{ position: 'sticky', top: 0, zIndex: 10, background: 'color-mix(in oklch, var(--bg), transparent 8%)',
        backdropFilter: 'blur(8px)', borderBottom: '1px solid var(--border)', padding: '16px 32px' }}>
        <h1 style={{ margin: 0, fontSize: 19, fontWeight: 700, letterSpacing: '-.01em' }}>История проверок</h1>
        <div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 3 }}>Все ранее выполненные сканирования сайтов</div>
      </div>

      <div style={{ padding: '24px 32px 60px', maxWidth: 1000, margin: '0 auto' }}>
        {/* search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'var(--surface)', border: '1px solid var(--border-2)',
          borderRadius: 11, padding: '0 14px', height: 44, maxWidth: 360, marginBottom: 20 }}>
          <Icon name="search" size={18} style={{ color: 'var(--faint)' }} />
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="Поиск по домену или организации"
            style={{ flex: 1, border: 0, outline: 0, background: 'transparent', font: 'inherit', fontSize: 14, color: 'var(--ink)' }} />
        </div>

        {/* table */}
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr 1.2fr 1fr 40px', gap: 16, padding: '12px 20px',
            borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
            {['Сайт', 'Дата', 'Риск-скоринг', 'Проблемы', ''].map((h, i) => (
              <div key={i} className="label-eyebrow" style={{ fontSize: 11 }}>{h}</div>
            ))}
          </div>
          {list.map((it, i) => (
            <button key={it.id} onClick={() => it.current ? onOpen() : onToast('В прототипе доступен только текущий отчёт', 'info')}
              style={{ width: '100%', display: 'grid', gridTemplateColumns: '1.6fr 1fr 1.2fr 1fr 40px', gap: 16,
                padding: '15px 20px', alignItems: 'center', border: 0, borderBottom: i < list.length - 1 ? '1px solid var(--border)' : 0,
                background: it.current ? 'var(--accent-soft)' : 'transparent', cursor: 'pointer', font: 'inherit', textAlign: 'left',
                transition: 'background .14s' }}
              onMouseEnter={e => { if (!it.current) e.currentTarget.style.background = 'var(--surface-2)'; }}
              onMouseLeave={e => { if (!it.current) e.currentTarget.style.background = 'transparent'; }}>
              <div style={{ minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="mono" style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{it.domain}</span>
                  {it.current && <span className="chip chip-ok" style={{ fontSize: 10.5 }}>текущий</span>}
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{it.org}</div>
              </div>
              <div style={{ fontSize: 13, color: 'var(--ink-2)' }}>{it.date}</div>
              <div><ScorePill score={it.score} band={it.band} /></div>
              <div style={{ display: 'flex', gap: 6 }}>
                {it.critical > 0 && <span className="chip chip-crit" style={{ fontSize: 11.5 }}><Icon name="xcircle" size={12} stroke={2} />{it.critical}</span>}
                {it.warning > 0 && <span className="chip chip-warn" style={{ fontSize: 11.5 }}><Icon name="alert" size={12} stroke={2} />{it.warning}</span>}
                {it.critical === 0 && it.warning === 0 && <span className="chip chip-ok" style={{ fontSize: 11.5 }}>чисто</span>}
              </div>
              <Icon name="chevron" size={17} style={{ color: 'var(--faint)', justifySelf: 'end' }} />
            </button>
          ))}
          {list.length === 0 && (
            <div style={{ padding: 40, textAlign: 'center', color: 'var(--muted)', fontSize: 14 }}>Ничего не найдено</div>
          )}
        </div>
      </div>
    </div>
  );
}
export default History;
