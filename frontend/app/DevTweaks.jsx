/* ===== ПДн Контроль — dev-обёртка панели твиков =====
 * Изолирует весь импорт tweaks-panel.jsx (542 стр.) за одной точкой, которую
 * App.jsx подгружает через React.lazy ТОЛЬКО при import.meta.env.DEV. За счёт
 * этого панель и её стили выпадают из прод-чанка (issue #43). */
import { TweaksPanel, TweakSection, TweakToggle, TweakColor, TweakRadio } from './tweaks-panel.jsx';

export default function DevTweaks({ t, setTweak }) {
  return (
    <TweaksPanel>
      <TweakSection label="Тема" />
      <TweakToggle label="Тёмная тема" value={t.dark} onChange={v => setTweak('dark', v)} />
      <TweakColor label="Акцент" value={t.accent}
        options={['#1F8A5B', '#2A6FDB', '#5B4BD6', '#0E3A5C']}
        onChange={v => setTweak('accent', v)} />
      <TweakSection label="Подача" />
      <TweakRadio label="Уровень детализации" value={t.detail}
        options={['Владелец', 'Специалист']} onChange={v => setTweak('detail', v)} />
      <div style={{ fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.5, padding: '2px 2px 0' }}>
        «Владелец» — кратко и без жаргона. «Специалист» — статьи, селекторы, IP, AI-анализ текстов.
      </div>
    </TweaksPanel>
  );
}
