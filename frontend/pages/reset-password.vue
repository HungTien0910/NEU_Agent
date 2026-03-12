<template>
  <div class="reset-page">
    <AuthCard :title="t('auth.resetTitle')" :subtitle="t('auth.resetSubtitle')">
      <template #logo>
        <div class="reset-logo">
          <img
            src="/media/neu-logo.webp"
            alt="Logo NEU"
            class="reset-logo__img"
          />
        </div>
      </template>

      <form class="reset-form" @submit.prevent="onSubmit">
        <BaseInput
          v-model="newPassword"
          :label="t('auth.newPassword')"
          :placeholder="t('auth.placeholderNewPassword')"
          name="newPassword"
          type="password"
          autocomplete="new-password"
          :error="errors.newPassword"
          required
        />
        <BaseInput
          v-model="confirmPassword"
          :label="t('auth.confirmPassword')"
          :placeholder="t('auth.placeholderConfirmPassword')"
          name="confirmPassword"
          type="password"
          autocomplete="new-password"
          :error="errors.confirmPassword"
          required
        />

        <p v-if="errors.form" class="reset-error">{{ errors.form }}</p>
        <p v-if="successMessage" class="reset-success">
          {{ successMessage }}
        </p>

        <BaseButton
          type="submit"
          :loading="isSubmitting"
          :disabled="!canSubmit"
          full
        >
          {{ t('auth.update') }}
        </BaseButton>
      </form>
    </AuthCard>
  </div>
</template>

<script setup lang="ts">
import { resetPassword } from '@/services/api/auth';
import { useI18n } from '@/composables/useI18n';

definePageMeta({
  layout: 'auth'
});

const { t, locale, load } = useI18n();
const route = useRoute();
const token = computed(() => String(route.query.token || '').trim());
const newPassword = ref('');
const confirmPassword = ref('');
const isSubmitting = ref(false);
const successMessage = ref('');
const errors = ref({
  newPassword: '',
  confirmPassword: '',
  form: ''
});

const canSubmit = computed(() =>
  Boolean(newPassword.value.trim() && confirmPassword.value.trim())
);

const validate = () => {
  errors.value = { newPassword: '', confirmPassword: '', form: '' };

  if (!token.value) {
    errors.value.form = t('auth.errors.missingToken');
  }

  if (!newPassword.value.trim()) {
    errors.value.newPassword = t('auth.errors.passwordRequired');
  }

  if (!confirmPassword.value.trim()) {
    errors.value.confirmPassword = t('auth.errors.confirmRequired');
  }

  if (
    newPassword.value.trim() &&
    confirmPassword.value.trim() &&
    newPassword.value !== confirmPassword.value
  ) {
    errors.value.confirmPassword = t('auth.errors.mismatch');
  }

  return !errors.value.newPassword && !errors.value.confirmPassword && !errors.value.form;
};

onMounted(load);

const onSubmit = async () => {
  if (!validate()) return;
  isSubmitting.value = true;
  successMessage.value = '';

  try {
    const response = await resetPassword({
      token: token.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value
    });
    if (locale.value === 'en') {
      const map: Record<string, string> = {
        'Đặt lại mật khẩu thành công.': t('auth.messages.resetSuccess')
      };
      successMessage.value = map[response.message] || t('auth.messages.resetSuccess');
    } else {
      successMessage.value = response.message;
    }
    setTimeout(() => navigateTo('/login'), 1200);
  } catch (error: any) {
    const detail = error?.data?.detail as string | undefined;
    if (!detail) {
      errors.value.form = t('auth.errors.resetFailed');
    } else if (locale.value === 'en') {
      const map: Record<string, string> = {
        'Mật khẩu xác nhận không khớp.': t('auth.errors.mismatch'),
        'Liên kết đặt lại không hợp lệ.': t('auth.errors.invalidToken'),
        'Liên kết đặt lại đã hết hạn.': t('auth.errors.expiredToken')
      };
      errors.value.form = map[detail] || t('auth.errors.resetFailed');
    } else {
      errors.value.form = detail;
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.reset-page {
  width: 100%;
  display: flex;
  justify-content: center;
}

.reset-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reset-logo {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.12);
  display: grid;
  place-items: center;
  overflow: hidden;
  box-shadow: 0 10px 18px rgba(7, 18, 38, 0.35);
}

.reset-logo__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reset-error {
  margin: 0;
  font-size: 13px;
  color: var(--color-danger);
}

.reset-success {
  margin: 0;
  font-size: 13px;
  color: #c8e7ff;
}

.reset-page :deep(.base-input__label) {
  color: rgba(255, 255, 255, 0.85);
}

.reset-page :deep(.base-input__control) {
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(255, 255, 255, 0.4);
}

.reset-page :deep(.base-input__control::placeholder) {
  color: rgba(85, 98, 122, 0.8);
}
</style>
