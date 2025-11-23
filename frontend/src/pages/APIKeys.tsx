/**
 * API Keys Management Page
 * Allows users to configure API keys for different model providers
 */

import { useState, useEffect } from 'react';
import styles from './APIKeys.module.css';

interface APIKeyConfig {
  provider: string;
  displayName: string;
  key: string;
  masked: boolean;
}

const PROVIDERS = [
  { id: 'openai', name: 'OpenAI', placeholder: 'sk-...', description: 'For GPT-4 and other OpenAI models' },
  { id: 'anthropic', name: 'Anthropic (Claude)', placeholder: 'sk-ant-...', description: 'For Claude 3 and 3.5 models' },
  { id: 'google', name: 'Google (Gemini)', placeholder: 'AIza...', description: 'For Gemini 1.5 models' },
  { id: 'cohere', name: 'Cohere', placeholder: '...', description: 'For Command R models' },
  { id: 'grok', name: 'Grok (xAI)', placeholder: 'xai-...', description: 'For Grok 2 models' },
  { id: 'deepseek', name: 'DeepSeek', placeholder: 'sk-...', description: 'For DeepSeek Chat and Reasoner models' },
  { id: 'qwen', name: 'Qwen (Alibaba)', placeholder: 'sk-...', description: 'For Qwen Plus, Max, and Turbo models' },
  { id: 'glm', name: 'GLM (ZhipuAI)', placeholder: '...', description: 'For GLM-4 and GLM-4-Plus models' },
];

export const APIKeys: React.FC = () => {
  const [keys, setKeys] = useState<Record<string, APIKeyConfig>>({});
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [tempKey, setTempKey] = useState('');
  const [saveStatus, setSaveStatus] = useState<{ provider: string; success: boolean } | null>(null);

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = () => {
    // Load from localStorage
    const stored = localStorage.getItem('zeta_api_keys');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setKeys(parsed);
      } catch (e) {
        console.error('Failed to parse stored API keys:', e);
      }
    }
  };

  const saveKey = (provider: string) => {
    if (!tempKey.trim()) {
      // Remove key if empty
      const newKeys = { ...keys };
      delete newKeys[provider];
      setKeys(newKeys);
      localStorage.setItem('zeta_api_keys', JSON.stringify(newKeys));
    } else {
      // Save key
      const newKeys = {
        ...keys,
        [provider]: {
          provider,
          displayName: PROVIDERS.find(p => p.id === provider)?.name || provider,
          key: tempKey,
          masked: true,
        },
      };
      setKeys(newKeys);
      localStorage.setItem('zeta_api_keys', JSON.stringify(newKeys));
    }

    setEditingProvider(null);
    setTempKey('');
    setSaveStatus({ provider, success: true });
    setTimeout(() => setSaveStatus(null), 3000);
  };

  const startEditing = (provider: string) => {
    setEditingProvider(provider);
    setTempKey(keys[provider]?.key || '');
  };

  const cancelEditing = () => {
    setEditingProvider(null);
    setTempKey('');
  };

  const toggleMask = (provider: string) => {
    if (keys[provider]) {
      setKeys({
        ...keys,
        [provider]: {
          ...keys[provider],
          masked: !keys[provider].masked,
        },
      });
    }
  };

  const maskKey = (key: string): string => {
    if (key.length <= 8) return '••••••••';
    return key.substring(0, 7) + '•'.repeat(Math.min(key.length - 7, 20));
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>API Keys</h1>
        <p className={styles.subtitle}>
          Manage API keys for model providers. Keys are stored locally in your browser.
        </p>
      </div>

      <div className={styles.infoBox}>
        <div className={styles.infoIcon}>ℹ️</div>
        <div>
          <h3 className={styles.infoTitle}>Security Note</h3>
          <p className={styles.infoText}>
            API keys are stored in your browser's localStorage and sent to the backend only when running evaluations.
            For production use, consider using environment variables on the backend instead.
          </p>
        </div>
      </div>

      <div className={styles.providerList}>
        {PROVIDERS.map((provider) => {
          const hasKey = !!keys[provider.id];
          const isEditing = editingProvider === provider.id;
          const keyConfig = keys[provider.id];

          return (
            <div key={provider.id} className={styles.providerCard}>
              <div className={styles.providerHeader}>
                <div className={styles.providerInfo}>
                  <h3 className={styles.providerName}>{provider.name}</h3>
                  {hasKey && !isEditing && (
                    <span className={styles.statusBadge}>Configured</span>
                  )}
                </div>
                {!isEditing && (
                  <button
                    className={styles.editButton}
                    onClick={() => startEditing(provider.id)}
                  >
                    {hasKey ? 'Edit' : 'Add Key'}
                  </button>
                )}
              </div>

              {isEditing ? (
                <div className={styles.editForm}>
                  <input
                    type="text"
                    className={styles.keyInput}
                    value={tempKey}
                    onChange={(e) => setTempKey(e.target.value)}
                    placeholder={provider.placeholder}
                    autoFocus
                  />
                  <div className={styles.editActions}>
                    <button
                      className={styles.saveButton}
                      onClick={() => saveKey(provider.id)}
                    >
                      Save
                    </button>
                    <button
                      className={styles.cancelButton}
                      onClick={cancelEditing}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : hasKey ? (
                <div className={styles.keyDisplay}>
                  <code className={styles.keyValue}>
                    {keyConfig.masked ? maskKey(keyConfig.key) : keyConfig.key}
                  </code>
                  <button
                    className={styles.toggleButton}
                    onClick={() => toggleMask(provider.id)}
                  >
                    {keyConfig.masked ? '👁️ Show' : '🔒 Hide'}
                  </button>
                </div>
              ) : (
                <p className={styles.noKey}>No API key configured</p>
              )}

              {saveStatus?.provider === provider.id && (
                <div className={styles.saveSuccess}>
                  ✓ API key saved successfully
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className={styles.footer}>
        <h3 className={styles.footerTitle}>How to get API keys:</h3>
        <ul className={styles.linkList}>
          <li>
            <strong>OpenAI:</strong>{' '}
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              rel="noopener noreferrer"
            >
              platform.openai.com/api-keys
            </a>
          </li>
          <li>
            <strong>Anthropic:</strong>{' '}
            <a
              href="https://console.anthropic.com/settings/keys"
              target="_blank"
              rel="noopener noreferrer"
            >
              console.anthropic.com/settings/keys
            </a>
          </li>
          <li>
            <strong>Google (Gemini):</strong>{' '}
            <a
              href="https://makersuite.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
            >
              makersuite.google.com/app/apikey
            </a>
          </li>
          <li>
            <strong>Cohere:</strong>{' '}
            <a
              href="https://dashboard.cohere.com/api-keys"
              target="_blank"
              rel="noopener noreferrer"
            >
              dashboard.cohere.com/api-keys
            </a>
          </li>
          <li>
            <strong>Grok (xAI):</strong>{' '}
            <a
              href="https://x.ai/api"
              target="_blank"
              rel="noopener noreferrer"
            >
              x.ai/api
            </a>
          </li>
          <li>
            <strong>DeepSeek:</strong>{' '}
            <a
              href="https://platform.deepseek.com/"
              target="_blank"
              rel="noopener noreferrer"
            >
              platform.deepseek.com
            </a>
          </li>
          <li>
            <strong>Qwen (Alibaba):</strong>{' '}
            <a
              href="https://dashscope.aliyuncs.com/"
              target="_blank"
              rel="noopener noreferrer"
            >
              dashscope.aliyuncs.com
            </a>
          </li>
          <li>
            <strong>GLM (ZhipuAI):</strong>{' '}
            <a
              href="https://open.bigmodel.cn/"
              target="_blank"
              rel="noopener noreferrer"
            >
              open.bigmodel.cn
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
};
