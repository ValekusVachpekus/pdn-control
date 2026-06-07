/* ===== ПДн Контроль — mock data ===== */

// Отчёт больше не хардкодится здесь: он приходит единым JSON (Контракт №2) и
// маппится в mapReport.js. Ниже — только UI-данные, не входящие в отчёт.
// scan steps for the live crawler
export const SCAN_STEPS = [
  { t: 0.5,  type: 'dns',    text: 'Резолвинг DNS klinika-zdorovie.ru → 104.21.34.117' },
  { t: 1.2,  type: 'geo',    text: 'Геолокация сервера: США (US), Cloudflare, Inc.', flag: 'crit' },
  { t: 2.0,  type: 'page',   text: 'Загрузка страницы / (главная)' },
  { t: 2.9,  type: 'form',   text: 'Найдена форма «Запись на приём»: name, phone, email, comment', flag: 'find' },
  { t: 3.6,  type: 'consent',text: 'Чекбокс согласия pre_checked=true — отмечен заранее', flag: 'crit' },
  { t: 4.4,  type: 'cookie', text: 'Cookie-баннер: has_reject_button=false', flag: 'warn' },
  { t: 5.1,  type: 'script', text: 'Сторонний скрипт: mc.yandex.ru (Яндекс.Метрика)' },
  { t: 5.7,  type: 'script', text: 'Сторонний скрипт: googletagmanager.com', flag: 'warn' },
  { t: 6.3,  type: 'script', text: 'Сторонний скрипт: jivosite.com (JivoSite)', flag: 'warn' },
  { t: 7.2,  type: 'page',   text: 'Загрузка страницы /contacts' },
  { t: 8.0,  type: 'form',   text: 'Найдена форма «Обратная связь»: name, phone — без согласия', flag: 'warn' },
  { t: 8.9,  type: 'page',   text: 'Загрузка страницы /privacy' },
  { t: 9.6,  type: 'doc',    text: 'Найдена политика конфиденциальности — отправка в AI-анализ', flag: 'find' },
  { t: 10.6, type: 'ai',     text: 'AI: проверка сроков хранения, целей, получателей данных…' },
  { t: 11.8, type: 'ai',     text: 'AI: сроки хранения ПДн в политике не указаны', flag: 'info' },
  { t: 12.6, type: 'rule',   text: 'Применение правил проверки: 11 правил' },
  { t: 13.4, type: 'done',   text: 'Сканирование завершено: 2 критичных, 3 предупреждения, 1 инфо' },
];

export const HISTORY = [
  { id: 'rep_01HZX9K3Q7M2', domain: 'klinika-zdorovie.ru', org: 'ООО «Клиника Здоровье»', date: '5 июня 2026, 15:05', score: 42, band: 'HIGH', critical: 2, warning: 3, current: true },
  { id: 'rep_01HZW7B1A4', domain: 'klinika-zdorovie.ru', org: 'ООО «Клиника Здоровье»', date: '12 мая 2026, 10:22', score: 35, band: 'HIGH', critical: 3, warning: 4 },
  { id: 'rep_01HZT5N9C2', domain: 'mebel-uyut.ru', org: 'ИП Соколова Е. В.', date: '28 апреля 2026, 18:40', score: 71, band: 'MEDIUM', critical: 0, warning: 3 },
  { id: 'rep_01HZQ2D8E7', domain: 'kofe-tochka.ru', org: 'ООО «Кофе Точка»', date: '15 апреля 2026, 09:14', score: 88, band: 'LOW', critical: 0, warning: 1 },
  { id: 'rep_01HZN0F6G3', domain: 'autoservice-profi.ru', org: 'ООО «Авто-Профи»', date: '2 апреля 2026, 14:55', score: 54, band: 'MEDIUM', critical: 1, warning: 5 },
];

export const RISK_BANDS = {
  CRITICAL: { label: 'Критический риск', color: 'var(--crit)', soft: 'var(--crit-soft)', ink: 'var(--crit-ink)' },
  HIGH:   { label: 'Высокий риск',  color: 'var(--crit)', soft: 'var(--crit-soft)', ink: 'var(--crit-ink)' },
  MEDIUM: { label: 'Средний риск',  color: 'var(--warn)', soft: 'var(--warn-soft)', ink: 'var(--warn-ink)' },
  LOW:    { label: 'Низкий риск',   color: 'var(--ok)',   soft: 'var(--ok-soft)',   ink: 'var(--ok-ink)' },
  SAFE:   { label: 'Соответствует', color: 'var(--ok)',   soft: 'var(--ok-soft)',   ink: 'var(--ok-ink)' },
};
