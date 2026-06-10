/* ===== ПДн Контроль — Report dashboard ===== */
import { useState } from 'react';
import { Icon, Badge, RiskGauge, Meter, SEV, FOR_ICON } from './shared.jsx';
import { RISK_BANDS } from './data.jsx';
import ReportAppendix from './ReportAppendix.jsx';

function StatTile({ severity, value, label }) {
  const s = SEV[severity];
  return (
    <div style={{ padding: '14px 14px', borderRadius: 12, background: s.soft, display: 'flex', alignItems: 'center', gap: 11 }}>
      <Icon name={s.icon} size={22} stroke={2} style={{ color: s.color }} />
      <div>
        <div style={{ fontSize: 22, fontWeight: 800, lineHeight: 1, color: s.ink, letterSpacing: '-.02em' }}>{value}</div>
        <div style={{ fontSize: 12, color: s.ink, opacity: .85, fontWeight: 500, marginTop: 3 }}>{label}</div>
      </div>
    </div>
  );
}

const formatFine = n => n.toLocaleString('ru-RU') + ' ₽';

function ViolationCard({ v, detail, open, onToggle }) {
  const s = SEV[v.severity];
  const isSpec = detail === 'specialist';
  return (
    <div className="card" style={{ overflow: 'hidden', borderColor: open ? s.color : 'var(--border)',
      transition: 'border-color .2s', boxShadow: open ? 'var(--shadow-md)' : 'var(--shadow-sm)' }}>
      <button onClick={onToggle} style={{ width: '100%', border: 0, background: 'transparent', cursor: 'pointer',
        font: 'inherit', textAlign: 'left', padding: '16px 18px', display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{ width: 38, height: 38, borderRadius: 10, background: s.soft, display: 'grid', placeItems: 'center', flexShrink: 0 }}>
          <Icon name={s.icon} size={21} stroke={2} style={{ color: s.color }} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, flexWrap: 'wrap', marginBottom: 3 }}>
            <span className="mono" style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--faint)' }}>{v.id}</span>
            <Badge severity={v.severity} size={11} />
          </div>
          <div style={{ fontSize: 15.5, fontWeight: 600, color: 'var(--ink)', letterSpacing: '-.01em', lineHeight: 1.3 }}>{v.title}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          <span className="chip chip-neutral" style={{ fontSize: 11.5 }}>
            <Icon name={FOR_ICON[v.for]} size={13} /> {v.for}
          </span>
          {isSpec && <span className="kbd">{v.articleShort}</span>}
          <Icon name="chevdown" size={18} style={{ color: 'var(--faint)', transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }} />
        </div>
      </button>
      {open && (
        <div className="fade-up" style={{ padding: '0 18px 18px 70px', animationDuration: '.3s' }}>
          <p style={{ margin: '0 0 14px', fontSize: 14, color: 'var(--ink-2)', lineHeight: 1.55 }}>{v.desc}</p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 14 }}>
            <span className="chip chip-neutral"><Icon name="doc" size={13} /> {v.article}</span>
            <span className="chip chip-neutral"><Icon name={FOR_ICON[v.for]} size={13} /> Адресовано: {v.for}</span>
          </div>
          {isSpec && (
            <div style={{ marginBottom: 14 }}>
              <div className="label-eyebrow" style={{ marginBottom: 7 }}>Где обнаружено</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {v.where.map((w, i) => (
                  <div key={i} className="mono" style={{ fontSize: 12, color: 'var(--ink-2)', background: 'var(--surface-2)',
                    border: '1px solid var(--border)', borderRadius: 8, padding: '7px 11px', display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                    <span style={{ color: 'var(--faint)', flexShrink: 0 }}>›</span>
                    <span style={{ wordBreak: 'break-word' }}>{w}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {v.fine_rub && (
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 12,
              padding: '10px 13px', background: 'var(--crit-soft)', borderRadius: 9 }}>
              <Icon name="alert" size={15} stroke={2} style={{ color: 'var(--crit-ink)', flexShrink: 0 }} />
              <span style={{ fontSize: 13, color: 'var(--crit-ink)' }}>
                <strong>Потенциальный штраф по КоАП РФ ст. 13.11:</strong> до {formatFine(v.fine_rub)}
              </span>
            </div>
          )}
          <div style={{ display: 'flex', gap: 11, background: 'var(--accent-soft)', borderRadius: 11, padding: '13px 15px' }}>
            <Icon name="bolt" size={18} stroke={2} style={{ color: 'var(--accent-ink)', flexShrink: 0, marginTop: 1 }} />
            <div>
              <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--accent-ink)', marginBottom: 3 }}>Рекомендация</div>
              <p style={{ margin: 0, fontSize: 13.5, color: 'var(--accent-ink)', lineHeight: 1.5 }}>{v.rec}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* Оверлей поверх заблюренных премиум-блоков на бесплатном тарифе.
 * Sticky-контейнер высотой во весь экран центрирует карточку по вертикали
 * вьюпорта, и она остаётся по центру при скролле в пределах заблюренной зоны. */
function LockedOverlay({ onUnlock }) {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 5, pointerEvents: 'none' }}>
      <div style={{ position: 'sticky', top: 0, height: '100vh', display: 'flex',
        alignItems: 'center', justifyContent: 'center' }}>
        <div className="card fade-up" style={{ pointerEvents: 'auto', maxWidth: 420, width: '90%',
          padding: '26px 26px 24px', textAlign: 'center', boxShadow: 'var(--shadow-lg)' }}>
          <div style={{ width: 52, height: 52, borderRadius: 14, margin: '0 auto 14px',
            background: 'var(--accent-soft)', display: 'grid', placeItems: 'center' }}>
            <Icon name="lock" size={26} stroke={2} style={{ color: 'var(--accent-ink)' }} />
          </div>
          <h3 style={{ margin: '0 0 8px', fontSize: 18, fontWeight: 700, letterSpacing: '-.01em' }}>
            Полный отчёт доступен после оплаты
          </h3>
          <p style={{ margin: '0 0 18px', fontSize: 13.5, color: 'var(--muted)', lineHeight: 1.5 }}>
            Детали нарушений, инфраструктура и геолокация, AI-анализ текстов,
            техническое приложение и PDF-отчёт — в полной версии.
          </p>
          <button className="btn btn-primary" style={{ height: 44, padding: '0 22px', justifyContent: 'center' }}
            onClick={onUnlock}>
            <Icon name="lock" size={17} stroke={2} /> Разблокировать отчёт
          </button>
        </div>
      </div>
    </div>
  );
}

function ScanFailedBanner({ r, onRescan }) {
  return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 }}>
      <div className="card fade-up" style={{ maxWidth: 560, padding: '32px 32px 28px', textAlign: 'center', boxShadow: 'var(--shadow-lg)' }}>
        <div style={{ width: 56, height: 56, borderRadius: 14, margin: '0 auto 16px',
          background: 'var(--warn-soft)', display: 'grid', placeItems: 'center' }}>
          <Icon name="alert" size={28} stroke={2} style={{ color: 'var(--warn-ink)' }} />
        </div>
        <h2 style={{ margin: '0 0 10px', fontSize: 19, fontWeight: 700, letterSpacing: '-.01em' }}>
          Не удалось проверить сайт
        </h2>
        <p style={{ margin: '0 0 8px', fontSize: 14, color: 'var(--ink-2)', lineHeight: 1.55 }}>
          {r.conclusionPlain || r.conclusion}
        </p>
        <p style={{ margin: '0 0 22px', fontSize: 13, color: 'var(--muted)', lineHeight: 1.5 }}>
          Это бывает, когда сайт защищён captcha/бот-детектором,
          требует JS-рендера или временно недоступен.
        </p>
        <button className="btn btn-primary" style={{ height: 44, padding: '0 22px',
          justifyContent: 'center' }} onClick={onRescan}>
          <Icon name="scan" size={17} stroke={2} /> Повторить проверку
        </button>
      </div>
    </div>
  );
}

function Report({ r, detail, onToast, onRescan, onDownload, paid = true, onUnlock }) {
  // Сначала отлавливаем «парсер не зашёл на сайт» — не нужно рисовать обычный отчёт
  // с фейковым score и пустыми блоками. Чистая заглушка с приглашением повторить.
  // Доп. защита: если бэк не проставил _scan_failed, но score/band не распознаны
  // (UNKNOWN risk_level), всё равно показываем баннер вместо краша при RISK_BANDS[r.band].
  const bands = RISK_BANDS[r.band];
  if (r.scanFailed || !bands || r.score == null) {
    return <ScanFailedBanner r={r} onRescan={onRescan} />;
  }
  const isSpec = detail === 'specialist';
  const [sev, setSev] = useState('all');
  const [role, setRole] = useState('all');
  const [open, setOpen] = useState({ 'ERR-001': true });
  const [showPassed, setShowPassed] = useState(false);

  const order = { critical: 0, warning: 1, info: 2 };
  const filtered = r.violations
    .filter(v => sev === 'all' || v.severity === sev)
    .filter(v => role === 'all' || v.for === role)
    .sort((a, b) => order[a.severity] - order[b.severity]);

  const sevFilters = [
    { id: 'all', label: 'Все', n: r.violations.length },
    { id: 'critical', label: 'Критичные', n: r.counts.critical },
    { id: 'warning', label: 'Предупреждения', n: r.counts.warning },
    { id: 'info', label: 'Инфо', n: r.counts.info },
  ];
  const roles = ['all', 'Разработчик', 'Юрист', 'Маркетолог'];

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
      {/* sticky header */}
      <div className="report-header" style={{ position: 'sticky', top: 0, zIndex: 10, background: 'color-mix(in oklch, var(--bg), transparent 8%)',
        backdropFilter: 'blur(8px)', borderBottom: '1px solid var(--border)', padding: '16px 32px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <h1 style={{ margin: 0, fontSize: 19, fontWeight: 700, letterSpacing: '-.01em' }}>Отчёт о проверке</h1>
            <span className="chip" style={{ background: bands.soft, color: bands.ink }}>
              <span style={{ width: 6, height: 6, borderRadius: 99, background: bands.color }}></span>{bands.label}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4, fontSize: 13, color: 'var(--muted)' }}>
            <span className="mono" style={{ color: 'var(--ink-2)' }}>{r.domain}</span>
            <span style={{ color: 'var(--border-2)' }}>·</span>
            <span>{r.dateHuman}</span>
            {isSpec && <><span style={{ color: 'var(--border-2)' }}>·</span><span className="mono" style={{ fontSize: 12 }}>{r.reportId}</span></>}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          <button className="btn btn-ghost" style={{ height: 40 }} onClick={onRescan}>
            <Icon name="scan" size={17} /> Повторить
          </button>
          {paid ? (
            <button className="btn btn-primary" style={{ height: 40 }}
              onClick={onDownload || (() => onToast('Отчёт сформирован — PDF загружается', 'ok'))}>
              <Icon name="download" size={17} /> Скачать PDF
            </button>
          ) : (
            <button className="btn btn-primary" style={{ height: 40 }} onClick={onUnlock}>
              <Icon name="lock" size={17} stroke={2} /> Разблокировать PDF
            </button>
          )}
        </div>
      </div>

      {/* body */}
      <div className="report-body" style={{ padding: '26px 32px 60px', maxWidth: 1000, width: '100%', margin: '0 auto' }}>
        {/* score overview */}
        <div className="fade-up card score-overview" style={{ padding: 24, display: 'grid', gridTemplateColumns: '300px 1fr', gap: 28, alignItems: 'center' }}>
          <div className="score-gauge-col" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', borderRight: '1px solid var(--border)', paddingRight: 8 }}>
            <RiskGauge score={r.score} band={r.band} size={250} />
            <div style={{ marginTop: 4, fontSize: 12.5, color: 'var(--muted)', textAlign: 'center' }}>
              Оценка рисков · {isSpec ? `сканер v${r.scannerVersion}` : 'чем ниже — тем выше риск'}
            </div>
          </div>
          <div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginBottom: 18 }}>
              <Meter label="Юридическая часть" value={r.legalScore} color="var(--info)" />
              <Meter label="Техническая часть" value={r.techScore} color="var(--accent)" />
            </div>
            <div className="stat-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 10 }}>
              <StatTile severity="critical" value={r.counts.critical} label="Критичных" />
              <StatTile severity="warning" value={r.counts.warning} label="Предупреждений" />
              <StatTile severity="info" value={r.counts.info} label="Информационных" />
              <StatTile severity="ok" value={r.counts.passed} label="Пройдено" />
            </div>
            {r.totalFine > 0 && (
              <div style={{ marginTop: 10, padding: '12px 15px', background: 'var(--crit-soft)',
                borderRadius: 10, display: 'flex', alignItems: 'center', gap: 12 }}>
                <Icon name="alert" size={20} stroke={2} style={{ color: 'var(--crit-ink)', flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--crit-ink)', opacity: .75,
                    textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 2 }}>
                    Суммарный потенциальный штраф
                  </div>
                  <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--crit-ink)', letterSpacing: '-.02em', lineHeight: 1.1 }}>
                    до {formatFine(r.totalFine)}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--crit-ink)', opacity: .65, marginTop: 1 }}>
                    по КоАП РФ ст. 13.11
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* disclaimer + AI-источник */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', margin: '14px 2px 0', fontSize: 12.5, color: 'var(--muted)' }}>
          <Icon name="ai" size={15} style={{ marginTop: 1, flexShrink: 0, color: 'var(--accent)' }} />
          <span>
            <b style={{ color: 'var(--ink-2)' }}>Оценка и нарушения сформированы AI</b> на основании
            152-ФЗ (ред. от 24.06.2025) и КоАП РФ ст. 13.11 (ред. с 30.05.2025).
            Это предварительный аудит, а не юридическое заключение — не заменяет консультацию юриста.
          </span>
        </div>

        {/* conclusion */}
        <section className="fade-up card" style={{ padding: 22, marginTop: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 12 }}>
            <Icon name="ai" size={18} style={{ color: 'var(--accent)' }} />
            <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>Заключение</h2>
            <span className="chip chip-ok" style={{ fontSize: 11 }}>AI</span>
          </div>
          <p style={{ margin: 0, fontSize: isSpec ? 14.5 : 15.5, color: 'var(--ink-2)', lineHeight: 1.62 }}>
            {isSpec ? r.conclusion : r.conclusionPlain}
          </p>
        </section>

        {/* премиум-блоки: на бесплатном тарифе заблюрены под оверлеем */}
        <div style={{ position: 'relative' }}>
        <div style={paid ? undefined : { filter: 'blur(6px)', pointerEvents: 'none', userSelect: 'none', opacity: .9 }}>
        {/* infrastructure */}
        <InfraCard r={r} isSpec={isSpec} />

        {/* violations */}
        <section style={{ marginTop: 30 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 12 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, letterSpacing: '-.01em' }}>Выявленные нарушения</h2>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {sevFilters.map(f => (
                <button key={f.id} onClick={() => setSev(f.id)} className="btn"
                  style={{ height: 34, padding: '0 13px', fontSize: 13, borderRadius: 9,
                    background: sev === f.id ? 'var(--ink)' : 'var(--surface)', color: sev === f.id ? 'var(--surface)' : 'var(--ink-2)',
                    border: '1px solid', borderColor: sev === f.id ? 'var(--ink)' : 'var(--border-2)' }}>
                  {f.label} <span style={{ opacity: .6, fontWeight: 700 }}>{f.n}</span>
                </button>
              ))}
            </div>
          </div>
          {/* role filter */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12.5, color: 'var(--faint)', marginRight: 2 }}>Кому:</span>
            {roles.map(rr => (
              <button key={rr} onClick={() => setRole(rr)} className="btn"
                style={{ height: 30, padding: '0 11px', fontSize: 12.5, borderRadius: 99, fontWeight: 600,
                  background: role === rr ? 'var(--accent-soft)' : 'transparent', color: role === rr ? 'var(--accent-ink)' : 'var(--muted)',
                  border: '1px solid', borderColor: role === rr ? 'transparent' : 'var(--border)' }}>
                {rr === 'all' ? 'Все роли' : rr}
              </button>
            ))}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
            {filtered.map(v => (
              <ViolationCard key={v.id} v={v} detail={detail} open={!!open[v.id]}
                onToggle={() => setOpen(o => ({ ...o, [v.id]: !o[v.id] }))} />
            ))}
            {filtered.length === 0 && (
              <div className="card" style={{ padding: 28, textAlign: 'center', color: 'var(--muted)', fontSize: 14 }}>
                Нет нарушений по выбранному фильтру
              </div>
            )}
          </div>
        </section>

        {/* passed checks */}
        <section style={{ marginTop: 26 }}>
          <button onClick={() => setShowPassed(p => !p)} className="card" style={{ width: '100%', border: '1px solid var(--border)',
            cursor: 'pointer', font: 'inherit', textAlign: 'left', padding: '15px 18px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <Icon name="checkcircle" size={21} stroke={2} style={{ color: 'var(--accent)' }} />
            <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--ink)' }}>Пройдено проверок</span>
            <span className="chip chip-ok">{r.passed.length}</span>
            <Icon name="chevdown" size={18} style={{ marginLeft: 'auto', color: 'var(--faint)', transform: showPassed ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }} />
          </button>
          {showPassed && (
            <div className="fade-up" style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
              {r.passed.map((p, i) => (
                <div key={i} className="card" style={{ padding: '13px 16px', display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                  <Icon name="check" size={18} stroke={2.4} style={{ color: 'var(--accent)', marginTop: 1, flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)' }}>{p.title}</div>
                    {isSpec && <div style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 2 }}>{p.detail}</div>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* technical appendix */}
        <ReportAppendix r={r} isSpec={isSpec} onToast={onToast} />
        </div>
        {!paid && <LockedOverlay onUnlock={onUnlock} />}
        </div>
      </div>
    </div>
  );
}

function InfraCard({ r, isSpec }) {
  // Какие поля показывать: IP — только для «специалиста», страна/хостинг — всем.
  // Пустые значения рисуем как «—», чтобы карточка не зияла.
  const rows = [
    { icon: 'server', label: 'IP сервера', value: r.infra.ip || '—', mono: true, hideOwner: true },
    { icon: 'globe', label: 'Страна сервера',
      value: r.infra.country ? `${r.infra.countryFlag} ${r.infra.country}`.trim() : '—' },
    { icon: 'building', label: 'Хостинг-провайдер', value: r.infra.hosting || '—' },
  ];

  // Три состояния локализации задают и chip в шапке, и цвет рамки/полоски с примечанием.
  const STATES = {
    compliant:     { chip: 'chip-ok',   text: 'Соответствует', border: 'var(--ok)',
                     bg: 'var(--ok-soft)',   ink: 'var(--ok-ink)',   icon: 'checkcircle' },
    non_compliant: { chip: 'chip-crit', text: 'Нарушение',     border: 'var(--crit)',
                     bg: 'var(--crit-soft)', ink: 'var(--crit-ink)', icon: 'xcircle' },
    unknown:       { chip: 'chip-warn', text: 'Не определено', border: 'var(--warn)',
                     bg: 'var(--warn-soft)', ink: 'var(--warn-ink)', icon: 'alert' },
  };
  const st = STATES[r.infra.localizationStatus] || STATES.unknown;

  return (
    <section className="fade-up card" style={{ padding: 22, marginTop: 20, borderColor: st.border }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 16 }}>
        <Icon name="server" size={18} style={{ color: 'var(--ink-2)' }} />
        <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>Инфраструктура и геолокация</h2>
        <span className={`chip ${st.chip}`} style={{ marginLeft: 'auto' }}>
          <Icon name={st.icon} size={13} stroke={2} /> {st.text}
        </span>
      </div>
      <div className="infra-grid" style={{ display: 'grid',
        gridTemplateColumns: `repeat(${rows.filter(row => isSpec || !row.hideOwner).length},1fr)`,
        gap: 1, background: 'var(--border)',
        borderRadius: 11, overflow: 'hidden', border: '1px solid var(--border)' }}>
        {rows.filter(row => isSpec || !row.hideOwner).map((row, i) => (
          <div key={i} style={{ background: 'var(--surface-2)', padding: '13px 15px' }}>
            <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>{row.label}</div>
            <div className={row.mono ? 'mono' : ''}
              style={{ fontSize: 14.5, fontWeight: 600, color: 'var(--ink)' }}>{row.value}</div>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 10, marginTop: 14, padding: '12px 14px',
        background: st.bg, borderRadius: 10 }}>
        <Icon name={st.icon} size={17} stroke={2}
          style={{ color: st.ink, flexShrink: 0, marginTop: 1 }} />
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color: st.ink, marginBottom: 2 }}>
            Локализация ПДн в РФ (ст. 18 ч. 5)
          </div>
          <p style={{ margin: 0, fontSize: 13, color: st.ink, lineHeight: 1.5, opacity: .92 }}>
            {r.infra.note}
          </p>
        </div>
      </div>
    </section>
  );
}

export default Report;
