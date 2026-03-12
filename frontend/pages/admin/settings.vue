<template>
  <section class="admin-section">
    <h2 class="admin-title">{{ t('settings.title') }}</h2>

    <div class="admin-grid admin-grid--2">
      <div class="admin-card">
        <h3 class="settings-title">{{ t('settings.region') }}</h3>
        <div class="admin-form-grid admin-form-grid--single">
          <BaseSelect
            v-model="draft.language"
            :label="t('settings.language')"
            :options="languages"
          />
          <BaseSelect
            v-model="draft.timezone"
            :label="t('settings.timezone')"
            :options="timezones"
          />
          <BaseInput v-model="draft.dateFormat" :label="t('settings.dateFormat')" />
        </div>
      </div>

      <div class="admin-card">
        <h3 class="settings-title">{{ t('settings.notify') }}</h3>
        <div class="settings-row">
          <span>{{ t('settings.emailSystem') }}</span>
          <div
            class="toggle"
            :class="draft.emailNotifications ? 'toggle--on' : ''"
            @click="draft.emailNotifications = !draft.emailNotifications"
          />
        </div>
        <div class="settings-row">
          <span>{{ t('settings.errorNotify') }}</span>
          <div
            class="toggle"
            :class="draft.errorNotifications ? 'toggle--on' : ''"
            @click="draft.errorNotifications = !draft.errorNotifications"
          />
        </div>
      </div>
    </div>

    <div class="admin-card">
      <h3 class="settings-title">{{ t('settings.security') }}</h3>
      <div class="settings-row">
        <span>{{ t('settings.rotate') }}</span>
        <span class="admin-tag">
          {{ draft.passwordRotationDays }} {{ t('common.day') }}
        </span>
      </div>
      <div class="settings-row">
        <span>{{ t('settings.mfa') }}</span>
        <span
          class="admin-tag"
          :class="draft.mfaEnabled ? 'admin-tag--success' : 'admin-tag--warning'"
        >
          {{ draft.mfaEnabled ? t('settings.on') : t('settings.off') }}
        </span>
      </div>
    </div>

    <div class="admin-footer-actions">
      <BaseButton style="min-width: 140px" :disabled="!dirty" @click="saveSettings">
        {{ t('settings.save') }}
      </BaseButton>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAppSettings } from '@/composables/useAppSettings';
import { useI18n } from '@/composables/useI18n';
import { useToast } from '@/composables/useToast';

definePageMeta({
  layout: 'admin'
});

const { settings, load, save } = useAppSettings();
const { t, locale } = useI18n();
const { push } = useToast();
const draft = reactive({
  language: 'vi',
  timezone: 'GMT+7',
  dateFormat: 'DD/MM/YYYY',
  emailNotifications: true,
  errorNotifications: true,
  passwordRotationDays: 90,
  mfaEnabled: false
});
const dirty = ref(false);
const syncing = ref(false);

const syncDraft = () => {
  syncing.value = true;
  Object.assign(draft, settings.value);
  dirty.value = false;
  syncing.value = false;
};

const languages = computed(() => [
  { label: t('settings.languageVi'), value: 'vi' },
  { label: t('settings.languageEn'), value: 'en' }
]);

const timezones = computed(() => {
  if (settings.value.language === 'en') {
    return [
      { label: t('settings.timezoneHanoi'), value: 'GMT+7' },
      { label: t('settings.timezoneUtc'), value: 'UTC' }
    ];
  }
  return [
    { label: t('settings.timezoneHanoi'), value: 'GMT+7' },
    { label: t('settings.timezoneUtc'), value: 'UTC' }
  ];
});

onMounted(async () => {
  await load();
  syncDraft();
});

watch(
  draft,
  () => {
    if (!syncing.value) {
      dirty.value = true;
    }
  },
  { deep: true, flush: 'sync' }
);

const saveSettings = async () => {
  if (!dirty.value) return;
  settings.value = { ...draft };
  try {
    await save();
    syncDraft();
    push(locale.value === 'en' ? 'Settings saved.' : 'Đã lưu cài đặt.', 'success');
  } catch (error: any) {
    push(error?.data?.detail || t('common.noData'), 'error');
  }
};
</script>

<style scoped>
.settings-title {
  margin: 0 0 14px;
  color: #1b2b44;
  font-size: 15px;
}

.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  color: #6c7e99;
  font-size: 14px;
}
</style>
