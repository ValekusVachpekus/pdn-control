/* ===== ПДн Контроль — App orchestrator ===== */
import { useState, useEffect } from 'react';
import { Icon, AppShell } from './shared.jsx';
import { useTweaks, TweaksPanel, TweakSection, TweakToggle, TweakColor, TweakRadio } from './tweaks-panel.jsx';
import Landing from './Landing.jsx';
import Scanning from './Scanning.jsx';
import Report from './Report.jsx';
import History from './History.jsx';
import { REPORT } from './data.jsx';

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

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [screen, setScreen] = useState('landing'); // landing | scanning | app
  const [nav, setNav] = useState('report');
  const [domain, setDomain] = useState('klinika-zdorovie.ru');
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

  const startScan = (d, skip) => {
    setDomain(d);
    if (skip) { setScreen('app'); setNav('report'); return; }
    setScreen('scanning');
  };

  return (
    <>
      {screen === 'landing' && <Landing onStart={startScan} />}
      {screen === 'scanning' && <Scanning domain={domain} onDone={() => { setScreen('app'); setNav('report'); }} />}
      {screen === 'app' && (
        <AppShell nav={nav} setNav={setNav} detail={detail} theme={t.dark}
          onNewScan={() => setScreen('landing')}>
          {nav === 'report' && <Report r={REPORT} detail={detail} onToast={toast}
            onRescan={() => setScreen('scanning')} />}
          {nav === 'history' && <History onOpen={() => setNav('report')} onToast={toast} />}
        </AppShell>
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
