/* ===== ПДн Контроль — Report technical appendix ===== */
import { Icon } from './shared.jsx';

function ReportAppendix({ r, isSpec, onToast }) {
  const t = r.trackers;
  const aiVerdict = { partial: { c: 'chip-warn', l: 'Частично' }, bad: { c: 'chip-crit', l: 'Риск' }, good: { c: 'chip-ok', l: 'OK' } };

  return (
    <section style={{ marginTop: 34 }}>
      <div className="sec-head">
        <Icon name="code" size={18} style={{ color: 'var(--ink-2)' }} />
        <h2 className="sec-title">Техническое приложение</h2>
      </div>

      {/* documents */}
      <div className="card card-pad" style={{ marginBottom: 14 }}>
        <div className="label-eyebrow" style={{ marginBottom: 13 }}>Найденные документы</div>
        <div className="col" style={{ gap: 8 }}>
          {r.documents.map((d, i) => {
            const ok = d.status === 'found';
            return (
              <div key={i} className="row-center surface-tile" style={{ gap: 12, padding: '11px 13px', borderRadius: 10 }}>
                <Icon name={ok ? 'checkcircle' : 'xcircle'} size={19} stroke={2}
                  style={{ color: ok ? 'var(--accent)' : 'var(--crit)', flexShrink: 0 }} />
                <div className="flex-1">
                  <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)' }}>{d.name}</div>
                  {d.url && isSpec && <div className="mono" style={{ fontSize: 11.5, color: 'var(--faint)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{d.url}</div>}
                </div>
                <span className={`chip ${ok ? 'chip-ok' : 'chip-crit'}`}>{d.statusLabel}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {/* trackers */}
        <div className="card card-pad">
          <div className="label-eyebrow" style={{ marginBottom: 13 }}>Трекеры и сторонние скрипты</div>
          <div style={{ display: 'flex', gap: 18, marginBottom: 15 }}>
            <div><div style={{ fontSize: 26, fontWeight: 800, letterSpacing: '-.02em' }}>{t.total}</div><div style={{ fontSize: 11.5, color: 'var(--muted)' }}>всего</div></div>
            <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 18 }}><div style={{ fontSize: 26, fontWeight: 800, color: 'var(--accent)', letterSpacing: '-.02em' }}>{t.ru}</div><div style={{ fontSize: 11.5, color: 'var(--muted)' }}>российских</div></div>
            <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 18 }}><div style={{ fontSize: 26, fontWeight: 800, color: 'var(--crit)', letterSpacing: '-.02em' }}>{t.foreign}</div><div style={{ fontSize: 11.5, color: 'var(--muted)' }}>зарубежных</div></div>
          </div>
          <div className="col" style={{ gap: 7 }}>
            {t.list.map((tr, i) => (
              <div key={i} className="row-center surface-tile" style={{ gap: 10, padding: '9px 11px', borderRadius: 9 }}>
                <span style={{ width: 8, height: 8, borderRadius: 99, background: tr.origin === 'ru' ? 'var(--accent)' : 'var(--crit)', flexShrink: 0 }}></span>
                <div className="flex-1">
                  <div style={{ fontSize: 13.5, fontWeight: 600 }}>{tr.name}</div>
                  {isSpec && <div className="mono" style={{ fontSize: 11, color: 'var(--faint)' }}>{tr.host}</div>}
                </div>
                <span className="chip chip-neutral" style={{ fontSize: 11 }}>{tr.kind}</span>
              </div>
            ))}
          </div>
        </div>

        {/* collection points */}
        <div className="card card-pad">
          <div className="label-eyebrow" style={{ marginBottom: 13 }}>Точки сбора персональных данных</div>
          <div className="col" style={{ gap: 10 }}>
            {r.collectionPoints.map((c, i) => (
              <div key={i} className="surface-tile" style={{ padding: '12px 13px', borderRadius: 10 }}>
                <div className="row-center" style={{ gap: 8, marginBottom: 6 }}>
                  <Icon name="form" size={16} style={{ color: 'var(--ink-2)' }} />
                  <span style={{ fontSize: 13.5, fontWeight: 600 }}>{c.form}</span>
                </div>
                {/* Расположение формы — всем ролям, чтобы блок не выглядел пустым (issue #102) */}
                <div className="row-center" style={{ gap: 6, marginBottom: 8, fontSize: 12, color: 'var(--muted)' }}>
                  <Icon name="doc" size={13} style={{ color: 'var(--faint)' }} />
                  <span>{c.location}</span>
                </div>
                {isSpec && <div className="mono" style={{ fontSize: 11, color: 'var(--faint)', marginBottom: 8, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.page}</div>}
                <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
                  {c.fields.map((f, j) => <span key={j} className="kbd">{f}</span>)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI-анализ юридических текстов: показываем всем платным пользователям —
          это и есть «полный отчёт», ради которого они платят. Не привязываем
          к режиму «Специалист». */}
      {r.aiNotes.length > 0 && (
        <div className="card card-pad" style={{ marginTop: 14 }}>
          <div className="row-center" style={{ gap: 8, marginBottom: 6 }}>
            <Icon name="ai" size={16} style={{ color: 'var(--accent)' }} />
            <span className="label-eyebrow">AI-анализ юридических текстов</span>
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 14 }}>
            Разбор политик, согласий и cookie-уведомлений с привязкой к статьям 152-ФЗ
          </div>
          <div className="col" style={{ gap: 16 }}>
            {r.aiNotes.map((n, i) => {
              const vd = aiVerdict[n.verdict] || { c: '', l: '—' };
              return (
                <div key={i} style={{ padding: '16px 18px', background: 'var(--surface-2)',
                  border: '1px solid var(--border)', borderRadius: 12 }}>
                  {/* шапка карточки документа */}
                  <div className="row-center" style={{ gap: 10, marginBottom: 8 }}>
                    <span style={{ fontSize: 14.5, fontWeight: 700 }}>{n.doc}</span>
                    <span className={`chip ${vd.c}`} style={{ fontSize: 11 }}>{vd.l}</span>
                    {n.complianceScore != null && (
                      <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--muted)' }}>
                        Балл: <b style={{ color: 'var(--ink)' }}>{n.complianceScore}</b>/100
                      </span>
                    )}
                  </div>

                  {/* сводка */}
                  {n.text && (
                    <p style={{ margin: '0 0 10px', fontSize: 13.5, color: 'var(--ink-2)', lineHeight: 1.55 }}>
                      {n.text}
                    </p>
                  )}

                  {/* отсутствующие обязательные разделы */}
                  {n.missingSections?.length > 0 && (
                    <div style={{ marginTop: 8, padding: '10px 12px', borderRadius: 8,
                      background: 'var(--crit-soft)' }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--crit-ink)',
                        marginBottom: 4 }}>
                        Отсутствуют обязательные блоки 152-ФЗ:
                      </div>
                      <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12.5, color: 'var(--crit-ink)',
                        lineHeight: 1.5 }}>
                        {n.missingSections.map((m, j) => <li key={j}>{m}</li>)}
                      </ul>
                    </div>
                  )}

                  {/* конкретные проблемы с цитатами */}
                  {n.issues?.length > 0 && (
                    <div style={{ marginTop: 10 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--ink)', marginBottom: 6 }}>
                        Конкретные проблемы в тексте:
                      </div>
                      {n.issues.map((is, j) => (
                        <div key={j} style={{ marginBottom: 8, padding: '10px 12px',
                          borderRadius: 8, background: 'var(--warn-soft)',
                          borderLeft: '3px solid var(--warn)' }}>
                          {is.article && (
                            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--warn-ink)',
                              marginBottom: 4 }}>
                              {is.article}
                            </div>
                          )}
                          <div style={{ fontSize: 12.5, fontStyle: 'italic', color: 'var(--muted)',
                            marginBottom: 6, lineHeight: 1.5 }}>
                            «{is.quote}»
                          </div>
                          <div style={{ fontSize: 12.5, color: 'var(--ink-2)', lineHeight: 1.5 }}>
                            <b>Проблема:</b> {is.problem}
                          </div>
                          {is.fix && (
                            <div style={{ fontSize: 12.5, color: 'var(--info-ink, #1565c0)',
                              lineHeight: 1.5, marginTop: 3 }}>
                              <b>Как исправить:</b> {is.fix}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* что сделано правильно */}
                  {n.strengths?.length > 0 && (
                    <div style={{ marginTop: 8, padding: '8px 12px', borderRadius: 8,
                      background: 'var(--ok-soft)' }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--ok-ink)',
                        marginBottom: 4 }}>
                        Что сделано правильно:
                      </div>
                      <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12.5, color: 'var(--ok-ink)',
                        lineHeight: 1.5 }}>
                        {n.strengths.map((s, j) => <li key={j}>{s}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* meta footer */}
      <div className="row-between" style={{ marginTop: 22, paddingTop: 18,
        borderTop: '1px solid var(--border)', fontSize: 12, color: 'var(--faint)', flexWrap: 'wrap', gap: 10 }}>
        <span>{r.org} · проверено страниц: {r.pagesScanned} · длительность: {r.durationSec} с</span>
        {isSpec && <span className="mono">ID: {r.reportId} · сканер v{r.scannerVersion}</span>}
      </div>
    </section>
  );
}

export default ReportAppendix;
