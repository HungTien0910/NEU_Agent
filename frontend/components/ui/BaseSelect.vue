<template>
  <label class="base-select">
    <span v-if="label" class="base-select__label">
      {{ label }}
      <span v-if="required" class="base-select__required">*</span>
    </span>
    <select
      :name="name"
      :disabled="disabled"
      :value="modelValue"
      class="base-select__control"
      @change="onChange"
    >
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <span v-if="error" class="base-select__error">{{ error }}</span>
  </label>
</template>

<script setup lang="ts">
type Option = { label: string; value: string };

const props = withDefaults(
  defineProps<{
    modelValue: string;
    label?: string;
    name?: string;
    required?: boolean;
    disabled?: boolean;
    error?: string;
    options: Option[];
  }>(),
  {
    required: false,
    disabled: false
  }
);

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>();

const onChange = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  emit('update:modelValue', target.value);
};
</script>

<style scoped>
.base-select {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  color: var(--color-muted);
}

.base-select__label {
  font-weight: 500;
}

.base-select__required {
  color: var(--color-danger);
  margin-left: 4px;
}

.base-select__control {
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

.base-select__control:hover:not(:disabled) {
  border-color: #c8d8ef;
  background: #ffffff;
}

.base-select__control:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(27, 94, 168, 0.14);
  background: #ffffff;
}

.base-select__control:focus-visible {
  outline: none;
}

.base-select__error {
  font-size: 12px;
  color: var(--color-danger);
}
</style>
