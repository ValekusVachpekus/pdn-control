/* ===== ПДн Контроль — App orchestrator ===== */
import { useState, useEffect } from 'react';
import { Icon, AppShell } from './shared.jsx';
import { useTweaks, TweaksPanel, TweakSection, TweakToggle, TweakColor, TweakRadio } from './tweaks-panel.jsx';
import Landing from './Landing.jsx';
import Scanning from './Scanning.jsx';
import Report from './Report.jsx';
import History from './History.jsx';
import { startScan as apiStartScan, fetchReport, reportPdfUrl, normalizeDomain, IS_MOCK } from './api.js';

const ACCENTS = {
  '#1F8A5B': { press: '#1A7A50', l: { soft: '#E7F3EC', ink: '#0F5235' }, d: { soft: 'rgba(40,160,105,.18)', ink: '#6FD9A6' } },
  '#2A6FDB': { press: '#2360C2', l: { soft: '#E8F0FC', ink: '#1B4C9E' }, d: { soft: 'rgba(70,130,230,.20)', ink: '#9CC0F5' } },
  '#5B4BD6': { press: '#4D3FC0', l: { soft: '#ECEAFB', ink: '#3A2E9E' }, d: { soft: 'rgba(110,90,230,.22)', ink: '#B7AEF5' } },
  '#0E3A5C': { press: '#0B2E49', l: { soft: '#E5EDF3', ink: '#0E3A5C' }, d: { soft: 'rgba(70,130,180,.22)', ink: '#8FB8D9' } },
};

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "dark": false,
  "accent": "#1F8A5B",
  "detail": "Владелец"
}/*EDITMODE-END*/;

function Toasts({ items }) {
  return (
    <div style={{ position: 'fixed', bottom: 22, left: '50%', transform: 'translateX(-50%)', zIndex: 9999,
      display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center', pointerEvents: 'none' }}>
      {items.map(t => (
        <div key={t.id} className="fade-up" style={{ display: 'flex', alignItems: 'center', gap: 10,
          background: 'var(--ink)', color: 'var(--surface)', padding: '11px 16px', borderRadius: 11,
          boxShadow: 'var(--shadow-lg)', fontSize: 13.5, fontWeight: 500 }}>
          <Icon name={t.kind === 'ok' ? 'checkcircle' : 'info'} size={17} stroke={2}
            style={{ color: t.kind === 'ok' ? 'var(--ok)' : 'var(--info)' }} />
          {t.text}
        </div>
      ))}
    </div>
  );
}

function ReportLoading() {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', gap: 14, color: 'var(--muted)', padding: 40 }}>
      <Icon name="scan" size={28} stroke={1.8} style={{ color: 'var(--accent)' }} />
      <div style={{ fontSize: 15, fontWeight: 500 }}>Загрузка отчёта…</div>
    </div>
  );
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [screen, setScreen] = useState('landing'); // landing | scanning | app
  const [nav, setNav] = useState('report');
  const [domain, setDomain] = useState('');
  const [reportId, setReportId] = useState(null);
  const [report, setReport] = useState(null); // модель UI из api.fetchReport
  const [toasts, setToasts] = useState([]);
  const detail = t.detail === 'Специалист' ? 'specialist' : 'owner';

  // apply theme + accent
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', t.dark ? 'dark' : 'light');
    const a = ACCENTS[t.accent] || ACCENTS['#1F8A5B'];
    const pal = t.dark ? a.d : a.l;
    root.style.setProperty('--accent', t.accent);
    root.style.setProperty('--accent-press', a.press);
    root.style.setProperty('--accent-soft', pal.soft);
    root.style.setProperty('--accent-ink', pal.ink);
    root.style.setProperty('--ring', pal.soft);
  }, [t.dark, t.accent]);

  const toast = (text, kind = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(x => [...x, { id, text, kind }]);
    setTimeout(() => setToasts(x => x.filter(i => i.id !== id)), 2800);
  };

  // загрузка отчёта по reportId (единый JSON Контракта №2 → модель UI)
  useEffect(() => {
    if (!reportId) return;
    let alive = true;
    setReport(null);
    fetchReport(reportId)
      .then(r => { if (alive) setReport(r); })
      .catch(() => { if (alive) toast('Не удалось загрузить отчёт', 'info'); });
    return () => { alive = false; };
  }, [reportId]);

  const startScan = (d, skip) => {
    const dom = normalizeDomain(d);
    setDomain(dom);
    apiStartScan(dom)
      .then(({ reportId }) => setReportId(reportId))
      .catch(() => toast('Не удалось запустить проверку', 'info'));
    if (skip) { setScreen('app'); setNav('report'); return; }
    setScreen('scanning');
  };

  const downloadPdf = () => {
    if (IS_MOCK || !reportId) { toast('Отчёт сформирован — PDF загружается', 'ok'); return; }
    window.open(reportPdfUrl(reportId), '_blank');
  };

  const toggleDark = () => setTweak('dark', !t.dark);

  return (
    <>
      {screen === 'landing' && <Landing onStart={startScan} />}
      {screen === 'scanning' && <Scanning domain={domain} onDone={() => { setScreen('app'); setNav('report'); }} />}
      {screen === 'app' && (
        <AppShell nav={nav} setNav={setNav} detail={detail} theme={t.dark}
          onToggleTheme={toggleDark} onNewScan={() => setScreen('landing')}>
          {nav === 'report' && (report
            ? <Report r={report} detail={detail} onToast={toast}
                onDownload={downloadPdf} onRescan={() => setScreen('scanning')} />
            : <ReportLoading />)}
          {nav === 'history' && <History onOpen={() => setNav('report')} onToast={toast} />}
        </AppShell>
      )}

      {screen !== 'app' && (
        <button onClick={toggleDark}
          title={t.dark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'}
          style={{ position: 'fixed', top: 16, right: 16, zIndex: 1000,
            width: 40, height: 40, borderRadius: 10, border: '1px solid var(--border-2)',
            background: 'var(--surface)', color: 'var(--ink-2)', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: 'var(--shadow-sm)', transition: 'all .16s' }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--surface-3)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'var(--surface)'; }}>
          <Icon name={t.dark ? 'sun' : 'moon'} size={18} stroke={1.8} />
        </button>
      )}

      <Toasts items={toasts} />

      <TweaksPanel>

        <TweakSection label="Тема" />
        <TweakToggle label="Тёмная тема" value={t.dark} onChange={v => setTweak('dark', v)} />
        <TweakColor label="Акцент" value={t.accent}
          options={['#1F8A5B', '#2A6FDB', '#5B4BD6', '#0E3A5C']}
          onChange={v => setTweak('accent', v)} />
        <TweakSection label="Подача" />
        <TweakRadio label="Уровень детализации" value={t.detail}
          options={['Владелец', 'Специалист']} onChange={v => setTweak('detail', v)} />
        <div style={{ fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.5, padding: '2px 2px 0' }}>
          «Владелец» — кратко и без жаргона. «Специалист» — статьи, селекторы, IP, AI-анализ текстов.
        </div>
      </TweaksPanel>
    </>
  );
}

export default App;
