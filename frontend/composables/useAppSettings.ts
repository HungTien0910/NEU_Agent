import { getSettings, updateSettings } from '@/services/api/admin';

type SettingsState = {
  language: string;
  timezone: string;
  dateFormat: string;
  emailNotifications: boolean;
  errorNotifications: boolean;
  passwordRotationDays: number;
  mfaEnabled: boolean;
};

const defaultSettings: SettingsState = {
  language: 'vi',
  timezone: 'GMT+7',
  dateFormat: 'DD/MM/YYYY',
  emailNotifications: true,
  errorNotifications: true,
  passwordRotationDays: 90,
  mfaEnabled: false
};

export const useAppSettings = () => {
  const settings = useState<SettingsState>('app-settings', () => ({
    ...defaultSettings
  }));
  const loaded = useState('app-settings-loaded', () => false);

  const load = async () => {
    if (loaded.value) return;
    try {
      const data = await getSettings();
      settings.value = {
        language: data.language,
        timezone: data.timezone,
        dateFormat: data.date_format,
        emailNotifications: data.email_notifications,
        errorNotifications: data.error_notifications,
        passwordRotationDays: data.password_rotation_days,
        mfaEnabled: data.mfa_enabled
      };
      loaded.value = true;
    } catch {
      loaded.value = true;
    }
  };

  const save = async () => {
    const data = await updateSettings({
      language: settings.value.language,
      timezone: settings.value.timezone,
      date_format: settings.value.dateFormat,
      email_notifications: settings.value.emailNotifications,
      error_notifications: settings.value.errorNotifications,
      password_rotation_days: settings.value.passwordRotationDays,
      mfa_enabled: settings.value.mfaEnabled
    });
    settings.value = {
      language: data.language,
      timezone: data.timezone,
      dateFormat: data.date_format,
      emailNotifications: data.email_notifications,
      errorNotifications: data.error_notifications,
      passwordRotationDays: data.password_rotation_days,
      mfaEnabled: data.mfa_enabled
    };
  };

  return { settings, load, save };
};
