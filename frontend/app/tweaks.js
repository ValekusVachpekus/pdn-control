/* ===== ПДн Контроль — состояние твиков (без UI) =====
 * useTweaks вынесен из dev-панели (issue #43): хук нужен всегда (тема/акцент/
 * детализация), а тяжёлая панель (tweaks-panel.jsx) подгружается лениво только
 * в dev. Так панель полностью выпадает из прод-бандла. */
import { useState, useCallback } from 'react';

export function useTweaks(defaults) {
  const [values, setValues] = useState(defaults);
  // Принимает setTweak('key', value) ИЛИ setTweak({ key: value }) — чтобы
  // useState-style вызов не записал ключ "[object Object]".
  const setTweak = useCallback((keyOrEdits, val) => {
    const edits = typeof keyOrEdits === 'object' && keyOrEdits !== null
      ? keyOrEdits : { [keyOrEdits]: val };
    setValues((prev) => ({ ...prev, ...edits }));
    // Сигналы для dev-хоста/панели — в проде без подписчиков это no-op.
    try {
      window.parent.postMessage({ type: '__edit_mode_set_keys', edits }, '*');
      window.dispatchEvent(new CustomEvent('tweakchange', { detail: edits }));
    } catch {}
  }, []);
  return [values, setTweak];
}
