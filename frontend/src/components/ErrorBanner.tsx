import React from 'react';

interface ErrorBannerProps {
  message: string;
  onDismiss: () => void;
}

const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss }) => {
  return (
    <div className="error-banner">
      <div className="error-content">
        <div className="error-icon">⚠</div>
        <div className="error-message">{message}</div>
        <button className="error-dismiss" onClick={onDismiss} aria-label="Dismiss error">
          ✕
        </button>
      </div>

      <style>{`
        .error-banner {
          background: #f44336;
          color: white;
          padding: 16px;
          margin-bottom: 20px;
          border-radius: 6px;
          box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .error-content {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .error-icon {
          font-size: 24px;
          flex-shrink: 0;
        }

        .error-message {
          flex: 1;
          font-size: 15px;
          line-height: 1.5;
          font-weight: 500;
        }

        .error-dismiss {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          cursor: pointer;
          font-size: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
          flex-shrink: 0;
        }

        .error-dismiss:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .error-dismiss:active {
          background: rgba(255, 255, 255, 0.4);
        }
      `}</style>
    </div>
  );
};

export default ErrorBanner;
