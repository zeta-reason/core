/**
 * Left sidebar navigation
 */

import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import styles from './Sidebar.module.css';

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>⚡</span>
          <span className={styles.logoText}>Zeta Reason</span>
        </div>
        <button
          className={styles.themeToggle}
          onClick={toggleTheme}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
      </div>

      <nav className={styles.nav}>
        <Link
          to="/"
          className={`${styles.navItem} ${isActive('/') && !location.pathname.includes('/run') ? styles.active : ''}`}
        >
          <span className={styles.navIcon}>🏠</span>
          <span className={styles.navText}>Dashboard</span>
        </Link>

        <Link
          to="/api-keys"
          className={`${styles.navItem} ${isActive('/api-keys') ? styles.active : ''}`}
        >
          <span className={styles.navIcon}>🔑</span>
          <span className={styles.navText}>API Keys</span>
        </Link>
      </nav>

      <div className={styles.footer}>
        <div className={styles.version}>v1.0.0</div>
      </div>
    </div>
  );
};
