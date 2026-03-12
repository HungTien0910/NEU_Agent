<template>
  <button
    class="base-button"
    :class="[
      `base-button--${variant}`,
      full ? 'base-button--full' : ''
    ]"
    :disabled="disabled || loading"
    :type="type"
  >
    <span v-if="loading" class="base-button__spinner" />
    <span class="base-button__content">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
type ButtonVariant = 'primary' | 'ghost' | 'outline' | 'danger';
type ButtonType = 'button' | 'submit' | 'reset';

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant;
    type?: ButtonType;
    full?: boolean;
    loading?: boolean;
    disabled?: boolean;
  }>(),
  {
    variant: 'primary',
    type: 'button',
    full: false,
    loading: false,
    disabled: false
  }
);
</script>

<style scoped>
.base-button {
  height: 48px;
  border-radius: var(--radius-sm);
  border: none;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease,
    color 0.18s ease, border-color 0.18s ease;
}

.base-button--full {
  width: 100%;
}

.base-button--primary {
  background: linear-gradient(135deg, #1b5ea8 0%, #1f6fbe 100%);
  color: #fff;
  box-shadow: 0 12px 20px rgba(26, 90, 166, 0.24);
}

.base-button--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #154f91 0%, #1b63aa 100%);
  transform: translateY(-1px);
}

.base-button--primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 8px 14px rgba(26, 90, 166, 0.2);
}

.base-button--ghost {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-border);
}

.base-button--ghost:hover:not(:disabled) {
  background: #f3f7ff;
  border-color: #c8d8ef;
}

.base-button--outline {
  background: #ffffff;
  color: var(--color-primary);
  border: 1px solid #d9e2ef;
}

.base-button--outline:hover:not(:disabled) {
  border-color: #c8d8ef;
  box-shadow: 0 10px 18px rgba(19, 55, 102, 0.12);
  transform: translateY(-1px);
}

.base-button--outline:active:not(:disabled) {
  transform: translateY(0);
}

.base-button--danger {
  background: #d32b2b;
  color: #fff;
  box-shadow: 0 12px 20px rgba(211, 43, 43, 0.25);
}

.base-button--danger:hover:not(:disabled) {
  background: #b92222;
  transform: translateY(-1px);
}

.base-button--danger:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 8px 14px rgba(211, 43, 43, 0.2);
}

.base-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.base-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(27, 94, 168, 0.18);
}

.base-button__spinner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

.base-button__content {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
