/* ===== ПДн Контроль — адаптер Контракта №2 (JSON) → модель UI =====
 *
 * Единый JSON (PDFreport/example.json и бэкенд → PDF-микросервис) приводится
 * к плоской форме, которую рендерят компоненты отчёта. Вся логика переименований
 * и вычислений живёт здесь — компоненты остаются без захардкоженных данных.
 */

const ROLE_RU = { developer: 'Разработчик', lawyer: 'Юрист', marketer: 'Маркетолог' };

// код страны (ISO-3166-1 alpha-2) → эмодзи-флаг (любой код → 🌐)
const FLAGS = { US: '🇺🇸', RU: '🇷🇺', DE: '🇩🇪', NL: '🇳🇱', FR: '🇫🇷', GB: '🇬🇧', IE: '🇮🇪', SG: '🇸🇬' };

function flag(code) {
  if (!code) return '🌐';
  return FLAGS[code] ?? '🌐';
}

function dateHuman(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit',
    timeZone: 'Europe/Moscow',
  });
}

// "ст. 9 (согласие)" → "ст. 9"
function articleShort(article) {
  if (!article) return '';
  return article.split(' (')[0].trim();
}

export function mapReport(j) {
  const m = j.document_meta ?? {};
  const s = j.scoring ?? {};
  const es = j.executive_summary ?? {};
  const stats = es.stats ?? {};
  const ig = j.infrastructure_and_geo ?? {};
  const ta = j.technical_appendix ?? {};
  const tr = ta.trackers_summary ?? {};

  return {
    org: m.organization_name,
    url: m.target_url,
    domain: m.domain,
    date: m.generated_at,
    dateHuman: dateHuman(m.generated_at),
    pagesScanned: m.pages_scanned,
    durationSec: m.scan_duration_sec,
    reportId: m.report_id,
    scannerVersion: m.scanner_version,

    score: s.overall_score,
    band: s.risk_level,        // CRITICAL|HIGH|MEDIUM|LOW|SAFE
    legalScore: s.legal_score,
    techScore: s.technical_score,

    counts: {
      critical: stats.critical_count ?? 0,
      warning: stats.warning_count ?? 0,
      info: stats.info_count ?? 0,
      passed: stats.passed_count ?? 0,
    },
    totalFine: es.total_fine_rub ?? 0,
    conclusion: es.verdict,
    conclusionPlain: es.verdict_plain ?? es.verdict,

    infra: {
      ip: ig.server_ip,
      country: `${ig.server_country_ru ?? ''}${ig.server_country ? ` (${ig.server_country})` : ''}`.trim(),
      countryFlag: flag(ig.server_country),
      hosting: ig.hosting_provider,
      // tri-state: compliant | non_compliant | unknown. Старое поле bool оставляем
      // как fallback для отчётов, сгенерированных до перехода на tri-state.
      localizationStatus: ig.localization_status ?? (ig.localization_compliant ? 'compliant' : 'unknown'),
      note: ig.localization_note,
    },

    // Маркер: парсер не смог получить страницы — фронт скроет «премиум»-секции
    // и покажет заглушку «не удалось проверить».
    scanFailed: !!j._scan_failed,
    // Оплачен ли этот конкретный отчёт (источник истины — бэкенд).
    paid: !!j._paid,

    violations: (j.violations ?? []).map(v => ({
      id: v.id,
      severity: v.severity,
      for: ROLE_RU[v.target_role] ?? v.target_role,
      title: v.title,
      article: v.article_152fz,
      articleShort: articleShort(v.article_152fz),
      desc: v.description,
      where: v.evidence ?? [],
      rec: v.recommendation,
      fine_rub: v.fine_rub,
    })),

    passed: (es.passed_checks ?? []).map(p => ({ title: p.title, detail: p.detail })),

    documents: (ta.documents_found ?? []).map(d => ({
      name: d.name,
      url: d.url,
      status: d.url ? 'found' : 'missing',
      statusLabel: d.status,
    })),

    trackers: {
      total: tr.total ?? 0,
      ru: tr.russian ?? 0,
      foreign: tr.foreign ?? 0,
      list: (tr.list ?? []).map(t => ({
        name: t.name,
        host: t.host,
        origin: t.origin,
        kind: t.kind,
      })),
    },

    collectionPoints: (ta.data_collection_points ?? []).map(c => ({
      page: c.url,
      form: c.form_name,
      fields: c.fields ?? [],
    })),

    aiNotes: (ta.ai_analysis ?? []).map(a => ({
      doc: a.doc,
      verdict: a.verdict,
      text: a.summary || a.text,
      complianceScore: a.compliance_score ?? null,
      missingSections: a.missing_sections ?? [],
      issues: (a.issues ?? []).map(is => ({
        quote: is.quote,
        article: is.article,
        problem: is.problem,
        fix: is.fix,
      })),
      strengths: a.strengths ?? [],
    })),
  };
}
