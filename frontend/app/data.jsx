/* ===== ПДн Контроль — mock data ===== */

// Отчёт больше не хардкодится здесь: он приходит единым JSON (Контракт №2) и
// маппится в mapReport.js. Ниже — только UI-данные, не входящие в отчёт.
// Анимация лога сканирования. Это НЕ реальный поток событий от парсера —
// просто индикация прогресса для UX. {domain} подставляется в Scanning.jsx
// текущим доменом, чтобы не было захардкоженного «klinika-zdorovie.ru».
export const SCAN_STEPS = [
  { t: 0.5,  type: 'dns',    text: 'Резолвинг DNS {domain}' },
  { t: 1.2,  type: 'geo',    text: 'Определение страны размещения сервера' },
  { t: 2.0,  type: 'page',   text: 'Загрузка главной страницы' },
  { t: 2.9,  type: 'form',   text: 'Поиск форм сбора персональных данных', flag: 'find' },
  { t: 3.6,  type: 'consent',text: 'Проверка чекбоксов согласия на обработку ПДн' },
  { t: 4.4,  type: 'cookie', text: 'Анализ cookie-баннера и кнопок управления' },
  { t: 5.1,  type: 'script', text: 'Инвентаризация сторонних скриптов и трекеров' },
  { t: 5.7,  type: 'script', text: 'Проверка трансграничной передачи данных' },
  { t: 6.3,  type: 'page',   text: 'Обход внутренних страниц сайта' },
  { t: 7.2,  type: 'form',   text: 'Сопоставление полей форм с категориями ПДн' },
  { t: 8.0,  type: 'doc',    text: 'Поиск политики конфиденциальности и согласия', flag: 'find' },
  { t: 8.9,  type: 'ai',     text: 'AI-анализ текстов политик: цели обработки, сроки, передача' },
  { t: 9.6,  type: 'ai',     text: 'AI-анализ: оценка соответствия 152-ФЗ ст. 5, 9, 18' },
  { t: 10.6, type: 'rule',   text: 'Применение правил rule-engine' },
  { t: 11.8, type: 'rule',   text: 'Подсчёт скоринга и потенциального штрафа по КоАП 13.11' },
  { t: 12.6, type: 'done',   text: 'Формирование итогового отчёта' },
  { t: 13.4, type: 'done',   text: 'Сканирование завершено' },
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
