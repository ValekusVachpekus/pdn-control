/* ===== ПДн Контроль — слой доступа к данным (единственный шов с бэкендом) =====
 *
 * VITE_USE_MOCK=false — реальные запросы; VITE_API_BASE=<url> — базовый адрес
 * (пусто = тот же origin, nginx-прокси /api/). С бэкенда приходит JSON
 * Контракта №2, mapReport() приводит его к UI-модели.
 *
 * Токен JWT хранится в localStorage под ключом 'pdn_auth' и автоматически
 * подставляется в Authorization-заголовок ко всем защищённым запросам.
 * Это упрощение MVP — для прода правильнее httpOnly-cookie, чтобы JWT не был
 * доступен JS (защита от XSS).
 */
import { mapReport } from './mapReport.js';
import exampleReport from './example-report.json';

const BASE = import.meta.env.VITE_API_BASE ?? '';
export const IS_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') !== 'false';

const STORAGE_KEY = 'pdn_auth';

// ── токен и юзер: in-memory + localStorage ──────────────────────────────────
let _auth = readStoredAuth();

function readStoredAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function writeAuth(auth) {
  _auth = auth;
  try {
    if (auth) localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
    else localStorage.removeItem(STORAGE_KEY);
  } catch {}
}

export function getStoredAuth() { return _auth; }
export function isAuthenticated() { return !!(_auth && _auth.token); }
export function logout() { writeAuth(null); }
export function getAuthHeader() {
  return _auth?.token ? { Authorization: `Bearer ${_auth.token}` } : {};
}

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

async function http(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  // Автоматически подставляем JWT, если он есть.
  if (_auth?.token) headers['Authorization'] = `Bearer ${_auth.token}`;
  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (res.status === 401) {
    // Токен протух/невалиден — сносим, чтобы фронт перевёл юзера на логин.
    writeAuth(null);
  }
  if (!res.ok) {
    let detail = '';
    try { detail = (await res.json())?.detail || ''; } catch {}
    const err = new Error(`API ${path} → ${res.status}${detail ? `: ${detail}` : ''}`);
    err.status = res.status;
    throw err;
  }
  return res;
}

/* Запустить проверку сайта. POST /api/scans { url } -> { report_id }. */
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

/* Опрос статуса проверки. GET /api/scans/:id/status -> { status, error, ... }. */
export async function fetchScanStatus(reportId) {
  if (IS_MOCK) return { status: 'done' };
  const res = await http(`/api/scans/${reportId}/status`);
  return res.json();
}

/* Реальный прогресс скана для экрана ожидания.
 * GET /api/scans/:id/progress -> { phase, status, phases[], pages, forms, trackers, server_ip, ... }
 * Фазы: queued → crawling → analyzing → building → done|failed.
 * Счётчики (pages/forms/trackers/...) появляются с фазы analyzing. */
export async function fetchScanProgress(reportId) {
  if (IS_MOCK) return { phase: 'done', status: 'done', phases: ['queued','crawling','analyzing','building','done','failed'] };
  const res = await http(`/api/scans/${reportId}/progress`);
  return res.json();
}

/* История сканов пользователя. GET /api/scans?limit=&offset= -> ScanRow[]. */
export async function fetchHistory({ limit = 50, offset = 0 } = {}) {
  if (IS_MOCK) return [];
  const res = await http(`/api/scans?limit=${limit}&offset=${offset}`);
  return res.json();
}

/* Получить готовый отчёт (Контракт №2) и привести к модели UI. */
export async function fetchReport(reportId) {
  if (IS_MOCK) return mapReport(exampleReport);
  const res = await http(`/api/reports/${reportId}`);
  return mapReport(await res.json());
}

/* URL для скачивания PDF — бэкенд проксирует Контракт №2 → PDFreport. */
export function reportPdfUrl(reportId) {
  return `${BASE}/api/reports/${reportId}/pdf`;
}

/* ===== Auth =================================================================
 * POST /api/auth/login    { email, password }            -> { token, user }
 * POST /api/auth/register { email, password, consent }   -> { token, user }
 * 152-ФЗ ст. 9: consent=true обязателен при регистрации; без него бэк вернёт 400.
 */
export async function login({ email, password }) {
  if (IS_MOCK) {
    const auth = { token: 'mock', user: { email } };
    writeAuth(auth);
    return auth;
  }
  const res = await http('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const auth = await res.json();
  writeAuth(auth);
  return auth;
}

export async function register({ email, password, consent }) {
  if (IS_MOCK) {
    const auth = { token: 'mock', user: { email } };
    writeAuth(auth);
    return auth;
  }
  const res = await http('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, consent }),
  });
  const auth = await res.json();
  writeAuth(auth);
  return auth;
}

/* Вход через Яндекс/ВК. На бэке сейчас 501 — UI-кнопки видны, но реальный
 * OAuth-flow пока не реализован (см. backend/app/routers/auth.py). */
export async function loginWithProvider(provider, consent) {
  if (IS_MOCK) {
    const email = provider === 'yandex' ? 'user@yandex.ru' : 'user@vk.com';
    const auth = { token: 'mock', user: { email, provider } };
    writeAuth(auth);
    return auth;
  }
  const res = await http(`/api/auth/oauth/${provider}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ consent }),
  });
  const auth = await res.json();
  writeAuth(auth);
  return auth;
}

/* ===== Billing (CloudPayments, пока заглушка на бэке) ===================== */
const MOCK_PLANS = [
  { id: 'free', name: 'Бесплатный отчёт', price: 0, highlight: false,
    features: ['Риск-скоринг сайта', 'Число нарушений по категориям', 'Краткое заключение'] },
  { id: 'paid', name: 'Полный отчёт', price: 990, highlight: true,
    features: ['Все нарушения с деталями и пруфами', 'Инфраструктура и геолокация (ст. 18 ч. 5)',
      'AI-анализ текстов политик и согласий', 'Техническое приложение: трекеры и формы', 'Скачивание PDF-отчёта'] },
];

export async function fetchPlans() {
  if (IS_MOCK) return MOCK_PLANS;
  const res = await http('/api/billing/plans');
  return res.json();
}

/* Разблокировать ОДИН конкретный отчёт. В dev-режиме бэк сразу помечает
 * scan.paid=True, в проде вернёт checkout_url виджета CloudPayments. */
export async function createCheckout(plan, reportId) {
  if (IS_MOCK) return { checkout_url: null, paid: true };
  const res = await http('/api/billing/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plan, report_id: reportId }),
  });
  return res.json();
}
