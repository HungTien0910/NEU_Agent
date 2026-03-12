<template>
  <label class="base-input">
    <span v-if="label" class="base-input__label">
      {{ label }}
      <span v-if="required" class="base-input__required">*</span>
    </span>
    <input
      :type="type"
      :name="name"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :disabled="disabled"
      :readonly="readonly"
      :value="modelValue"
      class="base-input__control"
      @input="onInput"
    />
    <span v-if="help" class="base-input__help">{{ help }}</span>
    <span v-if="error" class="base-input__error">{{ error }}</span>
  </label>
</template>

<script setup lang="ts">
type InputType = 'text' | 'password' | 'email' | 'date';

const props = withDefaults(
  defineProps<{
    modelValue: string;
    label?: string;
    placeholder?: string;
    name?: string;
    type?: InputType;
    autocomplete?: string;
    help?: string;
    error?: string;
    required?: boolean;
    disabled?: boolean;
    readonly?: boolean;
  }>(),
  {
    type: 'text',
    autocomplete: 'off',
    required: false,
    disabled: false,
    readonly: false
  }
);

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>();

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
};
</script>

<style scoped>
.base-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  color: var(--color-muted);
}

.base-input__label {
  font-weight: 500;
}

.base-input__required {
  color: var(--color-danger);
  margin-left: 4px;
}

.base-input__control {
  height: 46px;
  padding: 0 16px;
  border-radius: var(--radius-sm);
  border: 1px solid #d6e2f2;
  font-size: 15px;
  color: var(--color-text);
  background: #f8fbff;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.base-input__control:hover:not(:disabled):not(:read-only) {
  border-color: #c8d8ef;
  background: #ffffff;
}

.base-input__control:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(27, 94, 168, 0.14);
  background: #ffffff;
}

.base-input__control:focus-visible {
  outline: none;
}

.base-input__control:disabled {
  background: var(--color-surface-soft);
  color: var(--color-muted);
}

.base-input__control:read-only {
  background: #f4f7fd;
  color: var(--color-muted);
}

.base-input__help {
  font-size: 12px;
  color: var(--color-muted);
}

.base-input__error {
  font-size: 12px;
  color: var(--color-danger);
}
</style>
