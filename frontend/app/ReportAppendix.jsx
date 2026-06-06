/* ===== ПДн Контроль — Report technical appendix ===== */
function ReportAppendix({ r, isSpec, onToast }) {
  const t = r.trackers;
  const aiVerdict = { partial: { c: 'chip-warn', l: 'Частично' }, bad: { c: 'chip-crit', l: 'Риск' }, good: { c: 'chip-ok', l: 'OK' } };

  return (
    <section style={{ marginTop: 34 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 16 }}>
        <Icon name="code" size={18} style={{ color: 'var(--ink-2)' }} />
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, letterSpacing: '-.01em' }}>Техническое приложение</h2>
      </div>

      {/* documents */}
      <div className="card" style={{ padding: 20, marginBottom: 14 }}>
        <div className="label-eyebrow" style={{ marginBottom: 13 }}>Найденные документы</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {r.documents.map((d, i) => {
            const ok = d.status === 'found';
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 13px',
                background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10 }}>
                <Icon name={ok ? 'checkcircle' : 'xcircle'} size={19} stroke={2}
                  style={{ color: ok ? 'var(--accent)' : 'var(--crit)', flexShrink: 0 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
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
        <div className="card" style={{ padding: 20 }}>
          <div className="label-eyebrow" style={{ marginBottom: 13 }}>Трекеры и сторонние скрипты</div>
          <div style={{ display: 'flex', gap: 18, marginBottom: 15 }}>
            <div><div style={{ fontSize: 26, fontWeight: 800, letterSpacing: '-.02em' }}>{t.total}</div><div style={{ fontSize: 11.5, color: 'var(--muted)' }}>всего</div></div>
            <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 18 }}><div style={{ fontSize: 26, fontWeight: 800, color: 'var(--accent)', letterSpacing: '-.02em' }}>{t.ru}</div><div style={{ fontSize: 11.5, color: 'var(--muted)' }}>российских</div></div>
            <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 18 }}><div style={{ fontSize: 26, fontWeight: 800, color: 'var(--crit)', letterSpacing: '-.02em' }}>{t.foreign}</div><div style={{ fontSize: 11.5, color: 'var(--muted)' }}>зарубежных</div></div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
            {t.list.map((tr, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 11px', background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 9 }}>
                <span style={{ width: 8, height: 8, borderRadius: 99, background: tr.origin === 'ru' ? 'var(--accent)' : 'var(--crit)', flexShrink: 0 }}></span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13.5, fontWeight: 600 }}>{tr.name}</div>
                  {isSpec && <div className="mono" style={{ fontSize: 11, color: 'var(--faint)' }}>{tr.host}</div>}
                </div>
                <span className="chip chip-neutral" style={{ fontSize: 11 }}>{tr.kind}</span>
              </div>
            ))}
          </div>
        </div>

        {/* collection points */}
        <div className="card" style={{ padding: 20 }}>
          <div className="label-eyebrow" style={{ marginBottom: 13 }}>Точки сбора персональных данных</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {r.collectionPoints.map((c, i) => (
              <div key={i} style={{ padding: '12px 13px', background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <Icon name="form" size={16} style={{ color: 'var(--ink-2)' }} />
                  <span style={{ fontSize: 13.5, fontWeight: 600 }}>{c.form}</span>
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

      {/* AI analysis — specialist only */}
      {isSpec && (
        <div className="card" style={{ padding: 20, marginTop: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 13 }}>
            <Icon name="ai" size={16} style={{ color: 'var(--accent)' }} />
            <span className="label-eyebrow">AI-анализ текстов</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {r.aiNotes.map((n, i) => {
              const vd = aiVerdict[n.verdict];
              return (
                <div key={i} style={{ padding: '13px 15px', background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 6 }}>
                    <span style={{ fontSize: 13.5, fontWeight: 600 }}>{n.doc}</span>
                    <span className={`chip ${vd.c}`} style={{ fontSize: 11 }}>{vd.l}</span>
                  </div>
                  <p style={{ margin: 0, fontSize: 13, color: 'var(--ink-2)', lineHeight: 1.55 }}>{n.text}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* meta footer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 22, paddingTop: 18,
        borderTop: '1px solid var(--border)', fontSize: 12, color: 'var(--faint)', flexWrap: 'wrap', gap: 10 }}>
        <span>{r.org} · проверено страниц: {r.pagesScanned} · длительность: {r.durationSec} с</span>
        {isSpec && <span className="mono">ID: {r.reportId} · сканер v{r.scannerVersion}</span>}
      </div>
    </section>
  );
}

window.ReportAppendix = ReportAppendix;
