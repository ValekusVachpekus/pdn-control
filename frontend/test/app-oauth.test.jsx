/* Smoke: App разбирает возврат из OAuth-редиректа (#129) без падения.
 * MOCK-режим (по умолчанию) — fetchMe вернёт null; проверяем, что монтирование с
 * ?oauth=success/error не кидает и лендинг рендерится. */
import { describe, it, expect, afterEach } from 'vitest';
import { render, cleanup } from '@testing-library/react';
import App from '../app/App.jsx';

const origLocation = window.location;

function setSearch(search) {
  Object.defineProperty(window, 'location', {
    writable: true,
    value: { ...origLocation, search, pathname: '/', href: `http://localhost/${search}` },
  });
}

afterEach(() => {
  cleanup();
  Object.defineProperty(window, 'location', { writable: true, value: origLocation });
  sessionStorage.clear();
});

describe('App — возврат из OAuth', () => {
  it('монтируется с ?oauth=success без краша', () => {
    setSearch('?oauth=success');
    const { container } = render(<App />);
    expect(container).toBeTruthy();
    // остаёмся на лендинге (поле ввода адреса на месте)
    expect(container.querySelector('input')).toBeInTheDocument();
  });

  it('монтируется с ?oauth_error=denied без краша', () => {
    setSearch('?oauth_error=denied');
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });
});
