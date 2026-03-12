<template>
  <div class="login-page">
    <AuthCard
      :title="t('auth.title')"
      :subtitle="t('auth.subtitle')"
    >
      <template #logo>
        <div class="login-logo">
          <img
            src="/media/neu-logo.webp"
            alt="Logo NEU"
            class="login-logo__img"
          />
        </div>
      </template>

      <form class="login-form" @submit.prevent="onSubmit">
        <BaseInput
          v-model="username"
          :label="t('auth.username')"
          :placeholder="t('auth.placeholderUsername')"
          name="username"
          autocomplete="username"
          :error="errors.username"
          required
        />
        <BaseInput
          v-model="password"
          :label="t('auth.password')"
          :placeholder="t('auth.placeholderPassword')"
          name="password"
          type="password"
          autocomplete="current-password"
          :error="errors.password"
          required
        />

        <p v-if="errors.form" class="login-error">{{ errors.form }}</p>

        <BaseButton
          type="submit"
          :loading="isSubmitting"
          :disabled="!canSubmit"
          full
        >
          {{ t('auth.login') }}
        </BaseButton>
      </form>

      <template #footer>
        <NuxtLink
          v-if="showForgot"
          :to="`/forgot-password?username=${encodeURIComponent(username.trim())}`"
        >
          {{ t('auth.forgot') }}
        </NuxtLink>
      </template>
    </AuthCard>
  </div>
</template>

<script setup lang="ts">
import { login } from '@/services/api/auth';
import { useCurrentUser } from '@/composables/useCurrentUser';
import { useI18n } from '@/composables/useI18n';
import { useToast } from '@/composables/useToast';

definePageMeta({
  layout: 'auth'
});

const { t, locale, load } = useI18n();
const { push } = useToast();
const username = ref('');
const password = ref('');
const isSubmitting = ref(false);
const showForgot = ref(false);
const errors = ref({
  username: '',
  password: '',
  form: ''
});

const canSubmit = computed(() =>
  Boolean(username.value.trim() && password.value.trim())
);

const validate = () => {
  errors.value = { username: '', password: '', form: '' };

  if (!username.value.trim()) {
    errors.value.username = t('auth.errors.usernameRequired');
  }

  if (!password.value.trim()) {
    errors.value.password = t('auth.errors.passwordRequired');
  }

  return !errors.value.username && !errors.value.password;
};

onMounted(load);

const onSubmit = async () => {
  if (!validate()) return;
  isSubmitting.value = true;
  showForgot.value = false;

  try {
    const response = await login({
      username: username.value.trim(),
      password: password.value
    });

    const { save } = useCurrentUser();
    save({
      id: response.user.id,
      username: response.user.username,
      full_name: response.user.full_name,
      role: response.user.role,
      permissions: response.user.permissions || []
    });
    push(locale.value === 'en' ? 'Login successful.' : 'Đăng nhập thành công.', 'success');

    if (response.user.role === 'admin') {
      await navigateTo('/admin/overview');
    } else {
      await navigateTo('/user/overview');
    }
  } catch (error: any) {
    const detail = error?.data?.detail as string | undefined;
    const isInvalidCredentials =
      detail === 'Tên đăng nhập hoặc mật khẩu không đúng.';
    showForgot.value = isInvalidCredentials && Boolean(username.value.trim());
    if (!detail) {
      errors.value.form = t('auth.errors.loginFailed');
    } else if (locale.value === 'en') {
      const map: Record<string, string> = {
        'Tên đăng nhập hoặc mật khẩu không đúng.': t('auth.errors.invalidCredentials'),
        'Tài khoản đang bị khóa.': t('auth.errors.accountLocked')
      };
      errors.value.form = map[detail] || t('auth.errors.loginFailed');
    } else {
      errors.value.form = detail;
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.login-page {
  width: 100%;
  display: flex;
  justify-content: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-logo {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  border: 2px solid var(--color-primary);
  background: #fff;
  display: grid;
  place-items: center;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.login-logo__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.login-error {
  margin: 0;
  font-size: 13px;
  color: var(--color-danger);
}

.login-page :deep(a) {
  font-weight: 600;
  color: #ffffff;
}

.login-page :deep(.base-input__label) {
  color: rgba(255, 255, 255, 0.85);
}

.login-page :deep(.base-input__control) {
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(255, 255, 255, 0.4);
}

.login-page :deep(.base-input__control::placeholder) {
  color: rgba(85, 98, 122, 0.8);
}
</style>
