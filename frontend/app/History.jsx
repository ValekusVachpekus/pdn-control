/* ===== ПДн Контроль — History (реальная) =====
 * Берём список сканов с бэкенда (GET /api/scans). Клик по строке открывает
 * сохранённый отчёт без повторного скана — Report.jsx читает report_json
 * прямо из БД через GET /api/reports/:id.
 */
import { useEffect, useState } from 'react';
import { Icon } from './shared.jsx';
import { RISK_BANDS } from './data.jsx';
import { fetchHistory, IS_MOCK } from './api.js';

function ScorePill({ score, band }) {
  const b = RISK_BANDS[band] || RISK_BANDS.MEDIUM;
  if (score == null) {
    return (
      <span className="chip" style={{ background: 'var(--surface-3)', color: 'var(--muted)', fontSize: 11.5 }}>
        не определён
      </span>
    );
  }
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

function StatusBadge({ status, scanFailed }) {
  if (scanFailed) {
    return <span className="chip chip-warn" style={{ fontSize: 11 }}>сайт не открылся</span>;
  }
  if (status === 'done') return null; // успешный — без бейджа
  if (status === 'failed') return <span className="chip chip-crit" style={{ fontSize: 11 }}>ошибка</span>;
  if (status === 'running') return (
    <span className="chip" style={{ fontSize: 11, background: 'var(--info-soft)', color: 'var(--info-ink, #1565c0)', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
      <span style={{ width: 7, height: 7, borderRadius: 99, background: 'currentColor', animation: 'blink .9s infinite' }} />
      в процессе
    </span>
  );
  return <span className="chip" style={{ fontSize: 11, background: 'var(--surface-3)', color: 'var(--muted)' }}>в очереди</span>;
}

function formatDate(iso) {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
      + ', ' + d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  } catch { return iso; }
}

function History({ onOpen, onOpenScan, onToast, currentReportId }) {
  const [items, setItems] = useState(null);  // null = loading
  const [q, setQ] = useState('');

  // Подгружаем историю и, пока есть незавершённые сканы (pending/running),
  // периодически перезапрашиваем — чтобы «в процессе» сам сменился на результат.
  useEffect(() => {
    if (IS_MOCK) { setItems([]); return; }
    let alive = true;
    let timer;
    const load = async () => {
      try {
        const rows = await fetchHistory();
        if (!alive) return;
        setItems(rows);
        const inProgress = rows.some(r => r.status === 'pending' || r.status === 'running');
        if (inProgress) timer = setTimeout(load, 4000);
      } catch {
        if (alive) { setItems(prev => prev ?? []); onToast?.('Не удалось загрузить историю', 'info'); }
      }
    };
    load();
    return () => { alive = false; clearTimeout(timer); };
  }, []);

  const list = (items || []).filter(it => {
    const s = q.trim().toLowerCase();
    if (!s) return true;
    return (it.domain || '').toLowerCase().includes(s)
        || (it.organization || '').toLowerCase().includes(s);
  });

  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{ position: 'sticky', top: 0, zIndex: 10, background: 'color-mix(in oklch, var(--bg), transparent 8%)',
        backdropFilter: 'blur(8px)', borderBottom: '1px solid var(--border)', padding: '16px 32px' }}>
        <h1 style={{ margin: 0, fontSize: 19, fontWeight: 700, letterSpacing: '-.01em' }}>История проверок</h1>
        <div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 3 }}>Все ранее выполненные сканирования сайтов</div>
      </div>

      <div style={{ padding: '24px 32px 60px', maxWidth: 1000, margin: '0 auto' }}>
        <div className="field-wrap" style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'var(--surface)', border: '1px solid var(--border-2)',
          borderRadius: 11, padding: '0 14px', height: 44, maxWidth: 360, marginBottom: 20, transition: 'border-color .16s, box-shadow .16s' }}>
          <Icon name="search" size={18} style={{ color: 'var(--faint)' }} />
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="Поиск по домену или организации"
            style={{ flex: 1, border: 0, outline: 0, background: 'transparent', font: 'inherit', fontSize: 14, color: 'var(--ink)' }} />
        </div>

        {items === null && (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--muted)', fontSize: 14 }}>
            Загрузка истории…
          </div>
        )}

        {items !== null && items.length === 0 && (
          <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--muted)', fontSize: 14 }}>
            История пуста — запустите первую проверку сайта.
          </div>
        )}

        {list.length > 0 && (
          <div className="card" style={{ overflow: 'hidden' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr 1.2fr 1fr 40px', gap: 16, padding: '12px 20px',
              borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
              {['Сайт', 'Дата', 'Риск-скоринг', 'Проблемы', ''].map((h, i) => (
                <div key={i} className="label-eyebrow" style={{ fontSize: 11 }}>{h}</div>
              ))}
            </div>
            {list.map((it, i) => {
              const isCurrent = currentReportId && it.id === currentReportId;
              // Открываем done И failed (последний покажет банер «не выполнен»).
              // pending/running ещё идут — открываем экран скана (issue #50).
              const inProgress = it.status === 'pending' || it.status === 'running';
              const clickable = it.status === 'done' || it.status === 'failed' || inProgress;
              return (
                <button key={it.id} className="focus-inset"
                  onClick={() => inProgress
                    ? onOpenScan?.(it)
                    : clickable ? onOpen(it.id) : onToast?.('Отчёт ещё не готов', 'info')}
                  style={{ width: '100%', display: 'grid', gridTemplateColumns: '1.6fr 1fr 1.2fr 1fr 40px', gap: 16,
                    padding: '15px 20px', alignItems: 'center', border: 0,
                    borderBottom: i < list.length - 1 ? '1px solid var(--border)' : 0,
                    background: isCurrent ? 'var(--accent-soft)' : 'transparent',
                    cursor: clickable ? 'pointer' : 'default', font: 'inherit', textAlign: 'left',
                    transition: 'background .14s' }}
                  onMouseEnter={e => { if (!isCurrent && clickable) e.currentTarget.style.background = 'var(--surface-2)'; }}
                  onMouseLeave={e => { if (!isCurrent) e.currentTarget.style.background = 'transparent'; }}>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <span className="mono" style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)',
                        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{it.domain}</span>
                      {isCurrent && <span className="chip chip-ok" style={{ fontSize: 10.5 }}>текущий</span>}
                      {it.paid && <span className="chip chip-ok" style={{ fontSize: 10.5 }}>
                        <Icon name="checkcircle" size={11} stroke={2} /> оплачен
                      </span>}
                      <StatusBadge status={it.status} scanFailed={it.scan_failed} />
                    </div>
                    {it.organization && (
                      <div style={{ fontSize: 12.5, color: 'var(--muted)', overflow: 'hidden',
                        textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{it.organization}</div>
                    )}
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--ink-2)' }}>{formatDate(it.created_at)}</div>
                  <div>{clickable
                    ? <ScorePill score={it.score} band={it.risk_level} />
                    : <span style={{ color: 'var(--faint)', fontSize: 13 }}>—</span>}</div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {it.critical_count > 0 && <span className="chip chip-crit" style={{ fontSize: 11.5 }}>
                      <Icon name="xcircle" size={12} stroke={2} />{it.critical_count}
                    </span>}
                    {it.warning_count > 0 && <span className="chip chip-warn" style={{ fontSize: 11.5 }}>
                      <Icon name="alert" size={12} stroke={2} />{it.warning_count}
                    </span>}
                    {it.status === 'done' && !it.scan_failed && it.critical_count === 0 && it.warning_count === 0 &&
                      <span className="chip chip-ok" style={{ fontSize: 11.5 }}>чисто</span>}
                  </div>
                  <Icon name="chevron" size={17} style={{ color: 'var(--faint)', justifySelf: 'end' }} />
                </button>
              );
            })}
          </div>
        )}

        {items !== null && items.length > 0 && list.length === 0 && (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--muted)', fontSize: 14 }}>
            Ничего не найдено
          </div>
        )}
      </div>
    </div>
  );
}
export default History;
