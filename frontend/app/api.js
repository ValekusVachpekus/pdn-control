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
