/* Юнит-тесты адаптера Контракта №2 → модель UI (mapReport).
 * Высокая ценность / низкая цена: чистая функция, ловит регрессии контракта. */
import { describe, it, expect } from 'vitest';
import { mapReport } from '../app/mapReport.js';
import example from '../app/example-report.json';

describe('mapReport — эталонная фикстура (example-report.json)', () => {
  const r = mapReport(example);

  it('переносит мету и скоринг', () => {
    expect(r.domain).toBe(example.document_meta.domain);
    expect(r.url).toBe(example.document_meta.target_url);
    expect(r.reportId).toBe(example.document_meta.report_id);
    expect(r.score).toBe(example.scoring.overall_score);
    expect(r.band).toBe(example.scoring.risk_level);
    expect(r.legalScore).toBe(example.scoring.legal_score);
    expect(r.techScore).toBe(example.scoring.technical_score);
  });

  it('считает счётчики из executive_summary.stats', () => {
    const st = example.executive_summary.stats;
    expect(r.counts).toEqual({
      critical: st.critical_count,
      warning: st.warning_count,
      info: st.info_count,
      passed: st.passed_count,
    });
  });

  it('маппит нарушения: роль рус., короткая статья, evidence → where', () => {
    expect(r.violations).toHaveLength(example.violations.length);
    const v0 = r.violations[0];
    const src = example.violations[0];
    expect(v0.id).toBe(src.id);
    expect(v0.severity).toBe(src.severity);
    expect(v0.title).toBe(src.title);
    expect(v0.where).toEqual(src.evidence ?? []);
    // target_role → русское имя
    expect(['Разработчик', 'Юрист', 'Маркетолог']).toContain(v0.for);
    // "ст. 9 (...)" → "ст. 9"
    expect(v0.articleShort).toBe(v0.article.split(' (')[0].trim());
  });

  it('маппит инфраструктуру и флаг страны', () => {
    expect(r.infra.ip).toBe(example.infrastructure_and_geo.server_ip);
    expect(r.infra.hosting).toBe(example.infrastructure_and_geo.hosting_provider);
    expect(typeof r.infra.countryFlag).toBe('string');
    expect(r.infra.localizationStatus).toMatch(/compliant|non_compliant|unknown/);
  });

  it('маппит трекеры списком объектов', () => {
    const tr = example.technical_appendix.trackers_summary;
    expect(r.trackers.total).toBe(tr.total ?? 0);
    expect(r.trackers.list).toHaveLength((tr.list ?? []).length);
    if (r.trackers.list.length) {
      expect(r.trackers.list[0]).toHaveProperty('name');
      expect(r.trackers.list[0]).toHaveProperty('origin');
    }
  });

  it('даёт человекочитаемую дату', () => {
    expect(typeof r.dateHuman).toBe('string');
    expect(r.dateHuman.length).toBeGreaterThan(0);
  });
});

describe('mapReport — крайние случаи', () => {
  it('пустой объект → дефолты без падения', () => {
    const r = mapReport({});
    expect(r.counts).toEqual({ critical: 0, warning: 0, info: 0, passed: 0 });
    expect(r.violations).toEqual([]);
    expect(r.passed).toEqual([]);
    expect(r.trackers.list).toEqual([]);
    expect(r.collectionPoints).toEqual([]);
    expect(r.aiNotes).toEqual([]);
    expect(r.totalFine).toBe(0);
    expect(r.paid).toBe(false);
    expect(r.scanFailed).toBe(false);
  });

  it('нет total_fine_rub → 0', () => {
    const r = mapReport({ executive_summary: { verdict: 'ок' } });
    expect(r.totalFine).toBe(0);
    expect(r.conclusion).toBe('ок');
    // verdict_plain отсутствует → fallback на verdict
    expect(r.conclusionPlain).toBe('ок');
  });

  it('пустые violations → пустой массив', () => {
    const r = mapReport({ violations: [] });
    expect(r.violations).toEqual([]);
  });

  it('флаги _scan_failed / _paid пробрасываются', () => {
    const r = mapReport({ _scan_failed: true, _paid: true });
    expect(r.scanFailed).toBe(true);
    expect(r.paid).toBe(true);
  });

  it('localization_compliant (старый bool) → tri-state fallback', () => {
    expect(mapReport({ infrastructure_and_geo: { localization_compliant: true } })
      .infra.localizationStatus).toBe('compliant');
    expect(mapReport({ infrastructure_and_geo: { localization_compliant: false } })
      .infra.localizationStatus).toBe('unknown');
  });

  // issue #102: расположение формы — человекочитаемая метка для всех ролей.
  it('точки сбора: location из URL + fallback имени формы', () => {
    const r = mapReport({ technical_appendix: { data_collection_points: [
      { url: 'https://x.ru/', form_name: 'Запись на приём', fields: ['name'] },
      { url: 'https://x.ru/contacts', form_name: 'Обратная связь' },
      { url: 'https://x.ru/about?x=1#y' },
    ] } });
    expect(r.collectionPoints[0].location).toBe('Главная страница');
    expect(r.collectionPoints[1].location).toBe('/contacts');
    expect(r.collectionPoints[2].location).toBe('/about');
    // нет form_name → плейсхолдер
    expect(r.collectionPoints[2].form).toBe('Форма');
    // fields по умолчанию пустой массив
    expect(r.collectionPoints[1].fields).toEqual([]);
  });
});
