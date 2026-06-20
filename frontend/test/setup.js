// Vitest setup: матчеры jest-dom (toBeInTheDocument и пр.) для всех тестов.
import '@testing-library/jest-dom/vitest';

// jsdom не всегда даёт requestAnimationFrame — RiskGauge/Meter анимируют через него.
if (typeof globalThis.requestAnimationFrame !== 'function') {
  globalThis.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 0);
  globalThis.cancelAnimationFrame = (id) => clearTimeout(id);
}
