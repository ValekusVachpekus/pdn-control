/* ===== ПДн Контроль — корневой ErrorBoundary =====
 * Ловит ошибки рендера в поддереве, чтобы один сломанный компонент не ронял
 * весь UI в белый экран (issue #40). Показывает фолбэк в стиле дизайн-системы
 * с кнопкой перезагрузки. Логируем в консоль — позже сюда же можно повесить
 * отправку в Sentry/бэк. */
import { Component } from 'react';
import { Icon, Logo } from './shared.jsx';

class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // TODO: отправлять в Sentry/на бэк, когда появится сбор ошибок.
    console.error('ErrorBoundary поймал ошибку:', error, info);
  }

  handleReload = () => {
    // Сбрасываем флаг и перезагружаем страницу — гарантированно чистое состояние.
    this.setState({ hasError: false });
    location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center', padding: 20, background: 'var(--bg)' }}>
        <div className="card" style={{ maxWidth: 460, width: '100%', padding: '32px 30px',
          textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
          <Logo size={40} />
          <Icon name="alert" size={30} stroke={1.8} style={{ color: 'var(--crit)' }} />
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700, letterSpacing: '-.01em' }}>
            Что-то пошло не так
          </h1>
          <p style={{ margin: 0, fontSize: 14, color: 'var(--muted)', lineHeight: 1.5, maxWidth: 360 }}>
            Произошла ошибка в интерфейсе. Перезагрузите страницу — обычно это помогает.
            Если повторяется, сообщите нам.
          </p>
          <button className="btn btn-primary" style={{ height: 42, marginTop: 4 }}
            onClick={this.handleReload}>
            <Icon name="history" size={17} stroke={2} /> Перезагрузить
          </button>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
