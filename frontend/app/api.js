/* ===== ПДн Контроль — слой доступа к данным (единственный шов с бэкендом) =====
 *
 * Пока бэкенда нет — режим MOCK: отчёт берётся из example-report.json.
 * Для интеграции достаточно изменений ТОЛЬКО в этом файле / через env:
 *   VITE_USE_MOCK=false   — включить реальные запросы;
 *   VITE_API_BASE=<url>   — базовый адрес API (пусто = тот же origin, nginx-прокси /api/).
 *
 * С бэкенда приходит единый JSON Контракта №2 (тот же, что у PDF-микросервиса),
 * который приводится к модели UI через mapReport().
 */
import { mapReport } from './mapReport.js';
import exampleReport from './example-report.json';

const BASE = import.meta.env.VITE_API_BASE ?? '';
export const IS_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') !== 'false';

// нормализация введённого пользователем адреса: example.com/ → example.com
export function normalizeDomain(url) {
  return String(url).trim().replace(/^https?:\/\//, '').replace(/\/$/, '');
}

/* Валидация домена (defense-in-depth на фронте; источник истины — бэкенд).
 * Пропускаем только корректные имена хостов: метки [a-z0-9-], TLD из букв,
 * опционально порт/путь. Этого достаточно, чтобы отсечь служебные символы
 * SQL/командных инъекций (' " ; -- < > пробел и т.п.) ещё до отправки. */
export function isValidDomain(url) {
  const host = normalizeDomain(url).split(/[/?#]/)[0];
  return /^([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}(?::\d{1,5})?$/i.test(host);
}

async function http(path, opts) {
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res;
}

/* Запустить проверку сайта.
 * Предполагаемый эндпоинт бэкенда: POST /api/scans { url } -> { report_id }
 * Возвращает { reportId }. В MOCK — фиктивный id. */
export async function startScan(url) {
  if (IS_MOCK) return { reportId: 'mock' };
  const res = await http('/api/scans', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  const data = await res.json();
  return { reportId: data.report_id };
}

/* Получить готовый отчёт (единый JSON Контракта №2) и привести к модели UI.
 * Предполагаемый эндпоинт: GET /api/reports/:id -> JSON Контракта №2 */
export async function fetchReport(reportId) {
  if (IS_MOCK) return mapReport(exampleReport);
  const res = await http(`/api/reports/${reportId}`);
  return mapReport(await res.json());
}

/* URL для скачивания PDF (через бэкенд-прокси к PDF-микросервису, Контракт №2 → /render).
 * Предполагаемый эндпоинт: GET /api/reports/:id/pdf -> application/pdf */
export function reportPdfUrl(reportId) {
  return `${BASE}/api/reports/${reportId}/pdf`;
}

/* ===== Auth (шаблон — подключить к бэкенду) =====
 * Предполагаемые эндпоинты:
 *   POST /api/auth/login    { email, password } -> { token, user }
 *   POST /api/auth/register { email, password } -> { token, user }
 * Токен хранить в httpOnly-cookie (выставляет бэкенд) либо здесь в памяти —
 * НЕ кладите JWT в localStorage. В MOCK возвращаем фиктивного пользователя. */
export async function login({ email, password }) {
  if (IS_MOCK) return { token: 'mock', user: { email, plan: 'free' } };
  const res = await http('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function register({ email, password }) {
  if (IS_MOCK) return { token: 'mock', user: { email, plan: 'free' } };
  const res = await http('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

/* ===== Billing (шаблон — подключить к платёжному провайдеру через бэкенд) =====
 *
 * Каталог тарифов — ВИТРИНА. В MOCK отдаётся дефолт ниже; в проде заменяется
 * ответом бэкенда (GET /api/billing/plans), чтобы цены/фичи/лимиты не были
 * захардкожены во фронте. Источник истины по суммам и проверке оплаты — бэкенд. */
const MOCK_PLANS = [
  { id: 'free', name: 'Бесплатно', price: 0, period: '', highlight: false,
    features: ['1 проверка сайта', 'Риск-скоринг и нарушения', 'Отчёт в браузере'] },
  { id: 'pro', name: 'Pro', price: 1490, period: '/ мес', highlight: true,
    features: ['Безлимит проверок', 'PDF-отчёты', 'AI-анализ текстов политик',
      'История и повторные проверки', 'Приоритеты для юриста/маркетолога/разработчика'] },
  { id: 'team', name: 'Team', price: 4900, period: '/ мес', highlight: false,
    features: ['Всё из Pro', 'До 10 пользователей', 'Мониторинг сайтов по расписанию', 'Экспорт и API-доступ'] },
];

/* Получить каталог тарифов. Предполагаемый эндпоинт: GET /api/billing/plans -> Plan[] */
export async function fetchPlans() {
  if (IS_MOCK) return MOCK_PLANS;
  const res = await http('/api/billing/plans');
  return res.json();
}

/* Создать сессию оплаты.
 * Предполагаемый эндпоинт: POST /api/billing/checkout { plan } -> { checkout_url }
 * Фронт лишь редиректит на checkout_url; ключи/цены/проверки — на бэкенде. */
export async function createCheckout(plan) {
  if (IS_MOCK) return { checkout_url: null };
  const res = await http('/api/billing/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plan }),
  });
  return res.json();
}
