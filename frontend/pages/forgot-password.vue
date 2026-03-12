<template>
  <div class="forgot-page">
    <AuthCard
      :title="t('auth.forgotTitle')"
      :subtitle="t('auth.forgotSubtitle')"
    >
      <template #logo>
        <div class="forgot-logo">
          <img
            src="/media/neu-logo.webp"
            alt="Logo NEU"
            class="forgot-logo__img"
          />
        </div>
      </template>

      <form class="forgot-form" @submit.prevent="onSubmit">
        <BaseInput
          v-model="username"
          :label="t('auth.username')"
          :placeholder="t('auth.placeholderUsername')"
          name="username"
          type="text"
          autocomplete="username"
          :error="errors.username"
          required
        />

        <p v-if="errors.form" class="forgot-error">{{ errors.form }}</p>
        <p v-if="successMessage" class="forgot-success">
          {{ successMessage }}
        </p>

        <BaseButton
          type="submit"
          :loading="isSubmitting"
          :disabled="!canSubmit"
          full
        >
          {{ t('auth.sendLink') }}
        </BaseButton>

        <BaseButton variant="ghost" type="button" @click="goLogin" full>
          {{ t('auth.backToLogin') }}
        </BaseButton>
      </form>
    </AuthCard>
  </div>
</template>

<script setup lang="ts">
import { forgotPassword } from '@/services/api/auth';
import { useI18n } from '@/composables/useI18n';

definePageMeta({
  layout: 'auth'
});

const { t, locale, load } = useI18n();
const route = useRoute();
const username = ref('');
const isSubmitting = ref(false);
const successMessage = ref('');
const errors = ref({
  username: '',
  form: ''
});

const canSubmit = computed(() => Boolean(username.value.trim()));

const validate = () => {
  errors.value = { username: '', form: '' };

  if (!username.value.trim()) {
    errors.value.username = t('auth.errors.usernameRequired');
  }

  return !errors.value.username;
};

onMounted(() => {
  load();
  const fromQuery = String(route.query.username || '').trim();
  if (fromQuery) {
    username.value = fromQuery;
  }
});

const onSubmit = async () => {
  if (!validate()) return;
  isSubmitting.value = true;
  successMessage.value = '';

  try {
    const response = await forgotPassword({ username: username.value.trim() });
    if (locale.value === 'en') {
      const map: Record<string, string> = {
        'Nếu email tồn tại, hệ thống sẽ gửi liên kết đặt lại.': t('auth.messages.forgotUnknown'),
        'Đã gửi liên kết đặt lại mật khẩu qua email.': t('auth.messages.forgotCreated')
      };
      successMessage.value = map[response.message] || t('auth.messages.forgotUnknown');
    } else {
      successMessage.value = response.message;
    }
  } catch (error: any) {
    const detail = error?.data?.detail as string | undefined;
    if (!detail) {
      errors.value.form = t('auth.errors.forgotFailed');
    } else if (locale.value === 'en') {
      errors.value.form = t('auth.errors.forgotFailed');
    } else {
      errors.value.form = detail;
    }
  } finally {
    isSubmitting.value = false;
  }
};

const goLogin = async () => {
  await navigateTo('/login');
};
</script>

<style scoped>
.forgot-page {
  width: 100%;
  display: flex;
  justify-content: center;
}

.forgot-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.forgot-logo {
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

.forgot-logo__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.forgot-error {
  margin: 0;
  font-size: 13px;
  color: var(--color-danger);
}

.forgot-success {
  margin: 0;
  font-size: 13px;
  color: #c8e7ff;
}

.forgot-link {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
}

.forgot-page :deep(a) {
  font-weight: 600;
  color: #ffffff;
}

.forgot-page :deep(.base-input__label) {
  color: rgba(255, 255, 255, 0.85);
}

.forgot-page :deep(.base-input__control) {
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(255, 255, 255, 0.4);
}

.forgot-page :deep(.base-input__control::placeholder) {
  color: rgba(85, 98, 122, 0.8);
}

.forgot-page :deep(.base-button--ghost) {
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.4);
}
</style>
