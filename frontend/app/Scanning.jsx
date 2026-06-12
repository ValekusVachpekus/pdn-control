/* ===== ПДн Контроль — Scanning (реальный прогресс) =====
 * Опрашивает GET /api/scans/:id/progress и показывает РЕАЛЬНЫЕ фазы конвейера
 * (очередь → обход → AI-анализ → сборка) с настоящими счётчиками от парсера.
 * Никакой фейковой анимации: прогресс-бар привязан к индексу текущей фазы,
 * длительность каждой фазы непредсказуема (зависит от сайта).
 */
import { useState, useEffect, useRef } from 'react';
import { Icon } from './shared.jsx';
import { fetchScanProgress } from './api.js';

// Человеческие подписи фаз. Порядок берём из ответа (поле phases), но саму
// последовательность отображаем без служебных queued/failed как отдельных строк.
const PHASE_META = {
  queued:    { label: 'В очереди',                        hint: 'Задача поставлена в очередь' },
  crawling:  { label: 'Обход страниц сайта',              hint: 'Парсер открывает публичные страницы' },
  analyzing: { label: 'AI-анализ на соответствие 152-ФЗ', hint: 'Модель оценивает риски по закону' },
  building:  { label: 'Формирование отчёта',              hint: 'Собираем итоговый документ' },
  done:      { label: 'Готово',                           hint: 'Отчёт сформирован' },
};
// Фазы, которые показываем как шаги (queued объединяем с crawling визуально).
const STEP_ORDER = ['crawling', 'analyzing', 'building'];

function Scanning({ domain, reportId, isMock = false, onDone, onError, onBackground }) {
  const [progress, setProgress] = useState({ phase: isMock ? 'done' : 'queued' });
  const [finished, setFinished] = useState(false);
  const finishedRef = useRef(false);

  // Polling реального прогресса до done/failed.
  useEffect(() => {
    if (!reportId && !isMock) return;
    let alive = true;
    let timer;
    const poll = async () => {
      try {
        const p = await fetchScanProgress(reportId);
        if (!alive) return;
        setProgress(p);
        if (p.status === 'failed' || p.phase === 'failed') {
          onError?.(p.error || 'Проверка завершилась с ошибкой');
          return;
        }
        if (p.status === 'done' || p.phase === 'done') {
          finishedRef.current = true;
          setFinished(true);
          return; // финал
        }
      } catch { /* временная ошибка сети — повторим */ }
      if (alive) timer = setTimeout(poll, 1500);
    };
    poll();
    return () => { alive = false; clearTimeout(timer); };
  }, [reportId, isMock]);

  // После завершения — небольшая пауза и открываем отчёт.
  useEffect(() => {
    if (finished) { const t = setTimeout(onDone, 900); return () => clearTimeout(t); }
  }, [finished]);

  const phase = finished ? 'done' : (progress.phase || 'queued');
  // Индекс текущей фазы в STEP_ORDER (queued → считаем как старт crawling).
  const curIdx = phase === 'queued' ? 0
    : phase === 'done' ? STEP_ORDER.length
    : Math.max(0, STEP_ORDER.indexOf(phase));
  // Прогресс-бар: доля пройденных фаз. queued=5%, done=100%.
  const pct = finished ? 100
    : phase === 'queued' ? 5
    : Math.round(((curIdx + 0.5) / STEP_ORDER.length) * 100);

  // Реальные счётчики (есть с фазы analyzing).
  const hasFacts = progress.pages != null;
  const facts = [
    { label: 'Страниц', value: progress.pages },
    { label: 'Форм', value: progress.forms },
    { label: 'Форм с ПДн', value: progress.forms_pii },
    { label: 'Трекеров', value: progress.trackers },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24,
      background: 'radial-gradient(110% 70% at 50% 0%, var(--accent-soft) 0%, transparent 42%), var(--bg)' }}>
      <div className="card fade-up" style={{ width: '100%', maxWidth: 620, padding: 0, overflow: 'hidden', boxShadow: 'var(--shadow-lg)' }}>
        {/* header */}
        <div style={{ padding: '24px 28px 20px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ position: 'relative', width: 46, height: 46, flexShrink: 0 }}>
              <div style={{ position: 'absolute', inset: 0, borderRadius: 12, background: 'var(--accent-soft)' }}></div>
              {!finished && (
                <svg style={{ position: 'absolute', inset: 0, width: 46, height: 46 }} viewBox="0 0 46 46">
                  <rect x="1" y="1" width="44" height="44" rx="11" ry="11"
                    fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round"
                    strokeDasharray="39 118"
                    style={{ animation: 'tracePerimeter 1.1s linear infinite' }} />
                </svg>
              )}
              <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: 'var(--accent-ink)' }}>
                <Icon name={finished ? 'checkcircle' : 'scan'} size={22} stroke={2} />
              </div>
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, color: 'var(--muted)', fontWeight: 500 }}>
                {finished ? 'Проверка завершена' : 'Проверяем сайт'}
              </div>
              <div className="mono" style={{ fontSize: 17, fontWeight: 600, color: 'var(--ink)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {domain}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 26, fontWeight: 800, letterSpacing: '-.02em', color: finished ? 'var(--accent)' : 'var(--ink)' }}>{pct}%</div>
            </div>
          </div>
          {/* progress bar */}
          <div style={{ height: 6, borderRadius: 99, background: 'var(--surface-3)', marginTop: 18, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${pct}%`, borderRadius: 99,
              background: finished ? 'var(--accent)' : 'linear-gradient(90deg, var(--accent), color-mix(in oklch, var(--accent), white 30%))',
              transition: 'width .4s ease' }}></div>
          </div>
        </div>

        {/* phases */}
        <div style={{ padding: '20px 28px', background: 'var(--surface-2)' }}>
          {STEP_ORDER.map((ph, i) => {
            const meta = PHASE_META[ph];
            const state = finished || i < curIdx ? 'done' : i === curIdx ? 'active' : 'pending';
            return (
              <div key={ph} style={{ display: 'flex', alignItems: 'flex-start', gap: 13, padding: '10px 0',
                opacity: state === 'pending' ? 0.45 : 1, transition: 'opacity .3s' }}>
                {/* icon */}
                <div style={{ width: 26, height: 26, flexShrink: 0, borderRadius: 99, display: 'grid', placeItems: 'center',
                  background: state === 'done' ? 'var(--accent-soft)' : state === 'active' ? 'var(--accent-soft)' : 'var(--surface-3)' }}>
                  {state === 'done'
                    ? <Icon name="check" size={15} stroke={2.5} style={{ color: 'var(--accent-ink)' }} />
                    : state === 'active'
                      ? <span style={{ width: 9, height: 9, borderRadius: 99, background: 'var(--accent)', animation: 'blink .9s infinite' }}></span>
                      : <span style={{ width: 7, height: 7, borderRadius: 99, background: 'var(--faint)' }}></span>}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14.5, fontWeight: 600,
                    color: state === 'pending' ? 'var(--muted)' : 'var(--ink)' }}>{meta.label}</div>
                  {/* реальные счётчики под фазой analyzing */}
                  {ph === 'analyzing' && state !== 'pending' && hasFacts ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 14px', marginTop: 6 }}>
                      {facts.filter(f => f.value != null).map((f, j) => (
                        <span key={j} style={{ fontSize: 12.5, color: 'var(--ink-2)' }}>
                          {f.label}: <b>{f.value}</b>
                        </span>
                      ))}
                      {progress.server_ip && (
                        <span className="mono" style={{ fontSize: 12, color: 'var(--muted)' }}>
                          IP: {progress.server_ip}
                        </span>
                      )}
                    </div>
                  ) : (
                    <div style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 2 }}>{meta.hint}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* footer */}
        <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <span style={{ fontSize: 12, color: 'var(--faint)' }}>
            {finished ? 'Открываем отчёт…'
              : 'Проверка может занять 1-2 минуты — можно свернуть, скан идёт на сервере'}
          </span>
          {finished ? (
            <button className="btn btn-primary" style={{ height: 38, flexShrink: 0 }} onClick={onDone}>
              Открыть отчёт <Icon name="arrow" size={16} />
            </button>
          ) : (
            <button className="btn btn-ghost" style={{ height: 38, flexShrink: 0 }} onClick={onBackground}>
              В главное меню
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
export default Scanning;
