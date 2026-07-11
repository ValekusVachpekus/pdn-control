/* OAuth-редирект в api.js (#129): в реальном (не MOCK) режиме loginWithProvider
 * уводит браузер на /api/auth/oauth/{provider}/start?consent=<0|1>, а не шлёт POST.
 * Подменяем window.location, чтобы перехватить href без реальной навигации jsdom. */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('loginWithProvider — реальный redirect-flow', () => {
  const orig = window.location;

  beforeEach(() => {
    vi.resetModules();          // перечитать api.js с новым IS_MOCK
    vi.stubEnv('VITE_USE_MOCK', 'false');
    Object.defineProperty(window, 'location', { writable: true, value: { href: '' } });
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    Object.defineProperty(window, 'location', { writable: true, value: orig });
  });

  it('согласие отмечено → consent=1', async () => {
    const { loginWithProvider } = await import('../app/api.js');
    loginWithProvider('yandex', true);
    expect(window.location.href).toBe('/api/auth/oauth/yandex/start?consent=1');
  });

  it('согласие не отмечено → consent=0', async () => {
    const { loginWithProvider } = await import('../app/api.js');
    loginWithProvider('vk', false);
    expect(window.location.href).toBe('/api/auth/oauth/vk/start?consent=0');
  });
});
