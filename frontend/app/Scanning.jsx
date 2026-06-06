/* ===== ПДн Контроль — Scanning ===== */
function Scanning({ domain, onDone }) {
  const steps = window.SCAN_STEPS;
  const SPEED = 0.62; // time compression
  const total = steps[steps.length - 1].t;
  const [elapsed, setElapsed] = useState(0);
  const [revealed, setRevealed] = useState(0);
  const [finished, setFinished] = useState(false);
  const logRef = useRef(null);
  const startRef = useRef(null);

  useEffect(() => {
    let raf;
    const tick = (ts) => {
      if (startRef.current == null) startRef.current = ts;
      const e = (ts - startRef.current) / 1000 / SPEED;
      setElapsed(e);
      let n = 0;
      for (const s of steps) if (e >= s.t) n++;
      setRevealed(n);
      if (e >= total + 0.6) { setFinished(true); return; }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  useEffect(() => { if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight; }, [revealed]);
  useEffect(() => { if (finished) { const t = setTimeout(onDone, 1100); return () => clearTimeout(t); } }, [finished]);

  const shown = steps.slice(0, revealed);
  const pct = Math.min(100, Math.round((elapsed / total) * 100));
  const count = (type) => shown.filter(s => s.type === type).length;
  const stats = [
    { label: 'Страниц', value: Math.max(count('page'), shown.length ? 1 : 0), icon: 'doc' },
    { label: 'Форм', value: count('form'), icon: 'form' },
    { label: 'Скриптов', value: count('script'), icon: 'code' },
    { label: 'Документов', value: count('doc'), icon: 'shield' },
  ];
  const flagColor = { crit: 'var(--crit)', warn: 'var(--warn)', info: 'var(--info)', find: 'var(--accent)' };
  const flagBg = { crit: 'var(--crit-soft)', warn: 'var(--warn-soft)', info: 'var(--info-soft)', find: 'var(--accent-soft)' };

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24,
      background: 'radial-gradient(110% 70% at 50% 0%, var(--accent-soft) 0%, transparent 42%), var(--bg)' }}>
      <div className="card fade-up" style={{ width: '100%', maxWidth: 720, padding: 0, overflow: 'hidden', boxShadow: 'var(--shadow-lg)' }}>
        {/* header */}
        <div style={{ padding: '24px 28px 20px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ position: 'relative', width: 46, height: 46, flexShrink: 0 }}>
              <div style={{ position: 'absolute', inset: 0, borderRadius: 12, background: 'var(--accent-soft)' }}></div>
              {!finished && <div style={{ position: 'absolute', inset: -3, borderRadius: 14, border: '2px solid var(--accent)',
                borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }}></div>}
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
              <div className="mono" style={{ fontSize: 11.5, color: 'var(--faint)' }}>{elapsed.toFixed(1)} с</div>
            </div>
          </div>
          {/* progress bar */}
          <div style={{ height: 6, borderRadius: 99, background: 'var(--surface-3)', marginTop: 18, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${pct}%`, borderRadius: 99,
              background: finished ? 'var(--accent)' : 'linear-gradient(90deg, var(--accent), color-mix(in oklch, var(--accent), white 30%))',
              transition: 'width .2s linear' }}></div>
          </div>
        </div>

        {/* stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', borderBottom: '1px solid var(--border)' }}>
          {stats.map((s, i) => (
            <div key={i} style={{ padding: '14px 16px', borderLeft: i ? '1px solid var(--border)' : 0, textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 800, letterSpacing: '-.02em', color: 'var(--ink)' }}>{s.value}</div>
              <div style={{ fontSize: 11.5, color: 'var(--muted)', fontWeight: 500, marginTop: 1 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* live log */}
        <div ref={logRef} style={{ height: 252, overflowY: 'auto', padding: '8px 8px 14px', background: 'var(--surface-2)' }}>
          {shown.map((s, i) => (
            <div key={i} className="log-in" style={{ display: 'flex', alignItems: 'flex-start', gap: 11, padding: '7px 14px' }}>
              <span className="mono" style={{ fontSize: 11, color: 'var(--faint)', marginTop: 2, minWidth: 38 }}>{s.t.toFixed(1)}s</span>
              <span style={{ width: 8, height: 8, borderRadius: 99, marginTop: 6, flexShrink: 0,
                background: s.flag ? flagColor[s.flag] : 'var(--border-2)' }}></span>
              <span style={{ fontSize: 13.5, color: 'var(--ink-2)', lineHeight: 1.45, flex: 1 }}>
                {s.text}
                {s.flag && s.flag !== 'find' && (
                  <span className="chip" style={{ marginLeft: 8, padding: '1px 8px', fontSize: 10.5, background: flagBg[s.flag], color: flagColor[s.flag], verticalAlign: 'middle' }}>
                    {s.flag === 'crit' ? 'критично' : s.flag === 'warn' ? 'риск' : 'инфо'}
                  </span>
                )}
              </span>
            </div>
          ))}
          {!finished && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '7px 14px' }}>
              <span className="mono" style={{ fontSize: 11, color: 'var(--faint)', minWidth: 38 }}>{elapsed.toFixed(1)}s</span>
              <span style={{ width: 8, height: 8, borderRadius: 99, background: 'var(--accent)', animation: 'blink .9s infinite' }}></span>
              <span style={{ fontSize: 13.5, color: 'var(--muted)' }}>обработка…</span>
            </div>
          )}
        </div>

        {/* footer */}
        <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 12, color: 'var(--faint)' }}>
            {finished ? 'Открываем отчёт…' : 'Краулер обходит публичные страницы и применяет правила проверки'}
          </span>
          <button className="btn btn-primary" style={{ height: 38, opacity: finished ? 1 : .55 }} disabled={!finished} onClick={onDone}>
            Открыть отчёт <Icon name="arrow" size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
window.Scanning = Scanning;
