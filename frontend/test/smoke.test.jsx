/* Smoke-рендеры ключевых экранов: проверяем, что компоненты монтируются без
 * падений на реальной форме данных (mapReport(example)). Не проверяют пиксели —
 * только что рендер не кидает (issue #49). */
import { describe, it, expect, afterEach, vi } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import Landing from '../app/Landing.jsx';
import Report from '../app/Report.jsx';
import { mapReport } from '../app/mapReport.js';
import example from '../app/example-report.json';

afterEach(cleanup);

const noop = () => {};

describe('Landing', () => {
  it('рендерится без падений', () => {
    const { container } = render(
      <Landing onStart={noop} onLogin={noop} onLogout={noop} onUpgrade={noop}
        onOpenHistory={noop} onOpenPolicy={noop} user={null} />
    );
    expect(container).toBeTruthy();
    // на лендинге есть поле ввода адреса сайта
    expect(container.querySelector('input')).toBeInTheDocument();
  });
});

describe('Report', () => {
  const r = mapReport(example);

  it('рендерит дашборд с mock-данными (оплачен)', () => {
    render(
      <Report r={r} detail="owner" onToast={noop} onRescan={noop}
        onDownload={noop} paid={true} onUnlock={noop} />
    );
    expect(screen.getByText('Отчёт о проверке')).toBeInTheDocument();
    expect(screen.getByText('Выявленные нарушения')).toBeInTheDocument();
  });

  it('режим «Специалист» не падает', () => {
    const { container } = render(
      <Report r={r} detail="specialist" onToast={noop} onRescan={noop}
        onDownload={noop} paid={true} onUnlock={noop} />
    );
    expect(container).toBeTruthy();
  });

  it('показывает заглушку при scanFailed вместо краша', () => {
    const failed = { ...r, scanFailed: true };
    const onRescan = vi.fn();
    render(
      <Report r={failed} detail="owner" onToast={noop} onRescan={onRescan}
        onDownload={noop} paid={true} onUnlock={noop} />
    );
    expect(screen.getByText('Не удалось проверить сайт')).toBeInTheDocument();
  });
});
