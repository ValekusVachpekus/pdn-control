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
 *   POST /api/auth/register { email, password, consent } -> { token, user }
 * Токен хранить в httpOnly-cookie (выставляет бэкенд) либо здесь в памяти —
 * НЕ кладите JWT в localStorage. В MOCK возвращаем фиктивного пользователя.
 *
 * 152-ФЗ (ст. 9): при регистрации передаётся флаг `consent` — бэкенд ОБЯЗАН
 * зафиксировать факт согласия на обработку ПДн (timestamp + версия политики),
 * чтобы суметь его доказать. Фронтовая галочка — лишь UX, источник истины —
 * запись на сервере. При отсутствии consent сервер должен ответить 4xx. */
export async function login({ email, password }) {
  if (IS_MOCK) return { token: 'mock', user: { email } };
  const res = await http('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function register({ email, password, consent }) {
  if (IS_MOCK) return { token: 'mock', user: { email } };
  const res = await http('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, consent }),
  });
  return res.json();
}

/* Вход / регистрация через внешнего провайдера (Яндекс / ВКонтакте) — ТОЛЬКО UI/мок.
 * В проде это OAuth: фронт открывает /api/auth/oauth/:provider (redirect на
 * провайдера), бэкенд обрабатывает callback, ставит сессию (httpOnly-cookie)
 * и возвращает user. Реальный обмен токенами и проверка — на бэкенде.
 * `consent` передаётся при регистрации через провайдера — бэкенд должен
 * зафиксировать согласие так же, как при обычной регистрации (ст. 9). */
export async function loginWithProvider(provider, consent) {
  if (IS_MOCK) {
    const email = provider === 'yandex' ? 'user@yandex.ru' : 'user@vk.com';
    return { token: 'mock', user: { email, provider } };
  }
  const res = await http(`/api/auth/oauth/${provider}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ consent }),
  });
  return res.json();
}

/* ===== Billing (шаблон — подключить к CloudPayments через бэкенд) =====
 *
 * Подписок НЕТ. Два продукта с РАЗОВОЙ оплатой: бесплатный отчёт (тизер) и
 * полный отчёт (разблокирует один текущий отчёт). Каталог — ВИТРИНА: в MOCK
 * отдаётся дефолт ниже, в проде заменяется ответом бэкенда (GET /api/billing/plans),
 * чтобы цены/фичи не были захардкожены во фронте. Источник истины по сумме и
 * проверке оплаты — бэкенд. */
const MOCK_PLANS = [
  { id: 'free', name: 'Бесплатный отчёт', price: 0, highlight: false,
    features: ['Риск-скоринг сайта', 'Число нарушений по категориям', 'Краткое заключение'] },
  { id: 'paid', name: 'Полный отчёт', price: 990, highlight: true,
    features: ['Все нарушения с деталями и пруфами', 'Инфраструктура и геолокация (ст. 18 ч. 5)',
      'AI-анализ текстов политик и согласий', 'Техническое приложение: трекеры и формы', 'Скачивание PDF-отчёта'] },
];

/* Получить каталог продуктов. Предполагаемый эндпоинт: GET /api/billing/plans -> Plan[] */
export async function fetchPlans() {
  if (IS_MOCK) return MOCK_PLANS;
  const res = await http('/api/billing/plans');
  return res.json();
}

/* Создать сессию разовой оплаты в CloudPayments.
 * Предполагаемый эндпоинт: POST /api/billing/checkout { plan, report_id } -> { checkout_url }
 * Фронт лишь редиректит на checkout_url (виджет/страница CloudPayments);
 * сумма, ключи и подтверждение оплаты — на бэкенде. В MOCK оплата имитируется. */
export async function createCheckout(plan) {
  if (IS_MOCK) return { checkout_url: null };
  const res = await http('/api/billing/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plan }),
  });
  return res.json();
}
