/* ===== ПДн Контроль — Политика обработки персональных данных =====
 * Отдельный экран (ст. 18.1 ч. 2 152-ФЗ — политика в свободном доступе).
 * ЗАГЛУШКА: вставьте реальный текст политики между маркерами
 * POLICY-TEXT-BEGIN / POLICY-TEXT-END ниже. */
import { Icon, Logo } from './shared.jsx';

function Policy({ onBack }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      {/* top bar */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '20px 32px', maxWidth: 860, margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
          <Logo size={32} />
          <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: '-.01em' }}>ПДн Контроль</div>
        </div>
        <button className="btn btn-ghost" style={{ height: 38 }} onClick={onBack}>
          <Icon name="arrow" size={16} style={{ transform: 'scaleX(-1)' }} /> Назад
        </button>
      </header>

      {/* content */}
      <div style={{ flex: 1, width: '100%', maxWidth: 760, margin: '0 auto', padding: '20px 24px 72px' }}>
        <h1 style={{ margin: '0 0 8px', fontSize: 'clamp(26px,3.4vw,34px)', fontWeight: 600,
          letterSpacing: '-.018em', color: 'var(--ink)' }}>
          Политика обработки персональных данных
        </h1>
        <p style={{ margin: '0 0 28px', fontSize: 14, color: 'var(--faint)' }}>
          Документ публикуется в соответствии со ст. 18.1 Федерального закона № 152-ФЗ.
        </p>

        {/* POLICY-TEXT-BEGIN — замените блок ниже реальным текстом политики */}
        <div style={{ border: '1.5px dashed var(--border-2)', borderRadius: 14, padding: '28px 24px',
          background: 'var(--surface-2)', color: 'var(--muted)', fontSize: 14.5, lineHeight: 1.6,
          display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'center', textAlign: 'center' }}>
          <Icon name="doc" size={26} stroke={1.6} style={{ color: 'var(--faint)' }} />
          <strong style={{ color: 'var(--ink-2)', fontWeight: 600 }}>
            Текст политики обработки персональных данных будет размещён здесь.
          </strong>
          <span>Замените содержимое блока между маркерами POLICY-TEXT в файле <code>Policy.jsx</code>.</span>
        </div>
        {/* POLICY-TEXT-END */}
      </div>
    </div>
  );
}

export default Policy;
