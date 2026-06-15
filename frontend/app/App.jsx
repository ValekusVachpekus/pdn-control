/* ===== ПДн Контроль — App orchestrator ===== */
import { useState, useEffect, useRef, lazy, Suspense } from 'react';
import { Icon, AppShell } from './shared.jsx';
import { useTweaks } from './tweaks.js';
import Landing from './Landing.jsx';
import History from './History.jsx';
import Auth from './Auth.jsx';
import Policy from './Policy.jsx';
import CookieBanner from './CookieBanner.jsx';
// Тяжёлые экраны грузим по требованию — лендинг-чанк меньше (issue #44).
const Scanning = lazy(() => import('./Scanning.jsx'));
const Report = lazy(() => import('./Report.jsx'));
const Pricing = lazy(() => import('./Pricing.jsx'));
// Dev-панель твиков: только в dev и только лениво — в прод-бандл не попадает (issue #43).
const DevTweaks = import.meta.env.DEV ? lazy(() => import('./DevTweaks.jsx')) : null;
import { startScan as apiStartScan, fetchReport, reportPdfUrl, normalizeDomain, IS_MOCK,
  getStoredAuth, logout as apiLogout, getAuthHeader } from './api.js';

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

// Раздел «Отчёт» открыт, но отчёт не выбран (пустой аккаунт без проверок,
// issue #17) — не крутим вечный спиннер, а зовём запустить проверку.
function ReportEmpty({ onNewScan }) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', gap: 14, color: 'var(--muted)', padding: 40, textAlign: 'center' }}>
      <Icon name="doc" size={28} stroke={1.8} style={{ color: 'var(--faint)' }} />
      <div style={{ fontSize: 15, fontWeight: 500 }}>Отчётов пока нет</div>
      <div style={{ fontSize: 13.5, maxWidth: 340, lineHeight: 1.5 }}>
        Запустите проверку сайта — её результат появится здесь и в истории.
      </div>
      <button className="btn btn-primary" style={{ height: 38, marginTop: 4 }} onClick={onNewScan}>
        Запустить проверку <Icon name="arrow" size={16} />
      </button>
    </div>
  );
}

// Навигация переживает reload (issue #15): храним текущий экран в sessionStorage
// (per-tab, чистится при закрытии вкладки). paid/user сюда НЕ кладём — paid
// приходит от бэка при re-fetch отчёта, user восстанавливается из getStoredAuth().
const NAV_KEY = 'pdn_nav';
function readStoredNav() {
  try {
    const raw = sessionStorage.getItem(NAV_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const storedNav = readStoredNav();
  const [screen, setScreen] = useState(storedNav?.screen || 'landing'); // landing | scanning | app | policy
  const [prevScreen, setPrevScreen] = useState('landing'); // куда вернуться с экрана политики
  const [nav, setNav] = useState(storedNav?.nav || 'report');
  const [domain, setDomain] = useState(storedNav?.domain || '');
  const [reportId, setReportId] = useState(storedNav?.reportId ?? null);
  const [report, setReport] = useState(null); // модель UI из api.fetchReport
  const [toasts, setToasts] = useState([]);
  const [modal, setModal] = useState(null); // null | 'auth' | 'pricing'
  // user восстанавливаем из localStorage при загрузке — иначе токен в api.js есть,
  // а UI считает, что пользователь не залогинен (и шлёт его на форму входа).
  const [user, setUser] = useState(() => getStoredAuth()?.user || null);
  const [paid, setPaid] = useState(false);  // оплачен ли ТЕКУЩИЙ отчёт (разовая оплата, per-report)
  const detail = t.detail === 'Специалист' ? 'specialist' : 'owner';

  const handleLogout = () => {
    apiLogout();
    setUser(null);
    setReportId(null);
    setReport(null);
    setScreen('landing');
    toast('Вы вышли из аккаунта', 'ok');
  };

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

  // Сохраняем навигацию для переживания reload (issue #15).
  useEffect(() => {
    try {
      sessionStorage.setItem(NAV_KEY, JSON.stringify({ screen, nav, domain, reportId }));
    } catch {}
  }, [screen, nav, domain, reportId]);

  // Тост-таймеры держим в ref и чистим при unmount — иначе setState после
  // размонтирования (предупреждение React) и утечка таймеров (issue #48).
  const toastTimers = useRef([]);
  useEffect(() => () => { toastTimers.current.forEach(clearTimeout); }, []);

  const toast = (text, kind = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(x => [...x, { id, text, kind }]);
    const timer = setTimeout(() => {
      setToasts(x => x.filter(i => i.id !== id));
      toastTimers.current = toastTimers.current.filter(t => t !== timer);
    }, 2800);
    toastTimers.current.push(timer);
  };

  // Загрузка отчёта с polling'ом: пока скан ещё не завершён, бэк отвечает 409
  // (status=pending/running). Подождём — таймаут 3 минуты, шаг 2 секунды.
  useEffect(() => {
    if (!reportId) return;
    let alive = true;
    let attempts = 0;
    let timer;
    const ctrl = new AbortController(); // отменяем in-flight при unmount/смене reportId
    const MAX_ATTEMPTS = 45; // 45 × 2с = 1.5 мин; failed-сканы бэк теперь отдаёт сразу
    setReport(null);

    const tick = async () => {
      if (!alive) return;
      try {
        const r = await fetchReport(reportId, { signal: ctrl.signal });
        if (alive) {
          setReport(r);
          // Отчёт мог быть открыт из истории (domain не выставлен) — берём из
          // самого отчёта, иначе кнопка «Повторить» окажется без домена (issue #30).
          if (r.domain) setDomain(r.domain);
          // Источник истины по оплате — бэкенд (_paid из mapReport).
          if (r.paid) setPaid(true);
        }
      } catch (err) {
        if (!alive || err.isAbort) return; // отмена при unmount — молча выходим
        attempts++;
        // 409 (скан ещё идёт) и таймаут запроса — ретраим до лимита.
        if ((err.status === 409 || err.isTimeout) && attempts < MAX_ATTEMPTS) {
          timer = setTimeout(tick, 2000);
        } else if (alive) {
          const msg = err.isTimeout ? 'Сервер не отвечает — попробуйте позже' :
                      err.status === 401 ? 'Войдите в аккаунт' :
                      err.status === 404 ? 'Отчёт не найден' :
                      'Не удалось загрузить отчёт';
          toast(msg, 'info');
        }
      }
    };
    tick();
    return () => { alive = false; clearTimeout(timer); ctrl.abort(); };
  }, [reportId]);

  const startScan = (d, skip) => {
    const dom = normalizeDomain(d);
    setDomain(dom);
    setPaid(false); // новый отчёт — снова бесплатный тизер до оплаты
    // ВАЖНО: сбрасываем reportId/report ДО запуска. setReportId(newId) стоит в
    // .then() (асинхронно), а setScreen('scanning') — синхронный и сработает
    // раньше. На ПОВТОРНОЙ проверке того же сайта без сброса экран прогресса
    // смонтируется со СТАРЫМ (уже done) reportId → опрос прогресса сразу вернёт
    // 100%, а новый обход пойдёт «под» загрузкой отчёта. Сброс в null заставляет
    // Scanning ждать настоящий новый id.
    setReportId(null);
    setReport(null);
    apiStartScan(dom)
      .then(({ reportId }) => setReportId(reportId))
      .catch(() => toast('Не удалось запустить проверку', 'info'));
    if (skip) { setScreen('app'); setNav('report'); return; }
    setScreen('scanning');
  };

  // PDF: window.open() не передаёт Authorization-заголовок, поэтому качаем
  // fetch'ем с Bearer и инициируем скачивание через blob.
  const downloadPdf = async () => {
    if (IS_MOCK || !reportId) { toast('Отчёт сформирован — PDF загружается', 'ok'); return; }
    try {
      const res = await fetch(reportPdfUrl(reportId), { headers: getAuthHeader() });
      if (!res.ok) {
        if (res.status === 402) { toast('Сначала оплатите отчёт', 'info'); return; }
        if (res.status === 401) { toast('Войдите в аккаунт', 'info'); return; }
        toast('Не удалось скачать PDF', 'info'); return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      toast('PDF скачан', 'ok');
    } catch {
      toast('Не удалось скачать PDF', 'info');
    }
  };

  // После оплаты — перезагружаем отчёт с бэка, чтобы получить полные данные
  // (детали нарушений, инфраструктура, AI-анализ были скрыты на free-режиме).
  const handlePaid = async () => {
    setPaid(true);
    if (!reportId || IS_MOCK) return;
    try {
      const r = await fetchReport(reportId);
      setReport(r);
    } catch { /* отчёт обновится при следующем рендере */ }
  };

  const toggleDark = () => setTweak('dark', !t.dark);

  // открыть экран политики обработки ПДн (запоминаем, откуда пришли, и закрываем модалку)
  const openPolicy = () => {
    setPrevScreen(s => (screen === 'policy' ? s : screen));
    setScreen('policy');
    setModal(null);
  };

  return (
    <>
      {screen === 'landing' && <Landing onStart={startScan} user={user}
        onLogin={() => setModal('auth')} onLogout={handleLogout}
        onUpgrade={() => setModal('pricing')} onOpenPolicy={openPolicy}
        onOpenHistory={() => { setNav('history'); setScreen('app'); }} />}
      {screen === 'scanning' && (
        <Suspense fallback={<ReportLoading />}>
          <Scanning domain={domain} reportId={reportId} isMock={IS_MOCK}
            onDone={() => { setScreen('app'); setNav('report'); }}
            onError={(msg) => { toast(msg || 'Не удалось проверить сайт', 'info'); setScreen('landing'); }}
            onBackground={() => { toast('Проверка продолжается в фоне — результат появится в истории', 'info'); setScreen('landing'); }} />
        </Suspense>
      )}
      {screen === 'policy' && <Policy onBack={() => setScreen(prevScreen || 'landing')} />}
      {screen === 'app' && (
        <AppShell nav={nav} setNav={setNav} detail={detail} theme={t.dark}
          paid={paid} onUpgrade={() => setModal('pricing')}
          onToggleTheme={toggleDark} onNewScan={() => setScreen('landing')}>
          {nav === 'report' && (report
            ? <Suspense fallback={<ReportLoading />}>
                <Report r={report} detail={detail} onToast={toast} paid={paid}
                  onUnlock={() => setModal('pricing')}
                  onDownload={downloadPdf}
                  onRescan={() => {
                  const d = domain || report?.domain;
                  if (d) startScan(d);
                  else toast('Не удалось определить адрес сайта для повтора', 'info');
                }} />
              </Suspense>
            : reportId
              ? <ReportLoading />
              : <ReportEmpty onNewScan={() => setScreen('landing')} />)}
          {nav === 'history' && <History
            currentReportId={reportId}
            onToast={toast}
            onOpenScan={(it) => {
              // Идущая проверка (pending/running) — открываем экран её хода (issue #50).
              // Новый скан НЕ запускаем (apiStartScan не дёргаем), только навигация на
              // существующий reportId; Scanning сам поллит прогресс на маунте.
              setPaid(false);
              setDomain(it.domain || '');
              setReportId(it.id);
              setScreen('scanning');
            }}
            onOpen={(id) => {
              if (id && id !== reportId) {
                // Открываем выбранный из истории отчёт. paid не знаем,
                // setPaid(false) — фронт перезагрузит отчёт; если оплачен,
                // бэк отдаст полные данные.
                setPaid(false);
                setReportId(id);
              }
              setNav('report');
            }} />}
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

      <Auth open={modal === 'auth'} onClose={() => setModal(null)}
        onAuth={setUser} onToast={toast} onOpenPolicy={openPolicy} />
      {modal === 'pricing' && (
        <Suspense fallback={null}>
          <Pricing open onClose={() => setModal(null)} onToast={toast}
            paid={paid} onPaid={handlePaid} user={user} reportId={reportId}
            onRequireAuth={() => setModal('auth')} />
        </Suspense>
      )}

      <Toasts items={toasts} />
      <CookieBanner onOpenPolicy={openPolicy} />

      {DevTweaks && (
        <Suspense fallback={null}>
          <DevTweaks t={t} setTweak={setTweak} />
        </Suspense>
      )}
    </>
  );
}

export default App;
