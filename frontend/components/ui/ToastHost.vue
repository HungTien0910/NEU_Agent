<template>
  <div class="toast-host">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast-item"
      :class="`toast-item--${toast.type}`"
    >
      <span>{{ toast.message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast';

const { toasts, remove } = useToast();

watch(
  toasts,
  (items) => {
    items.forEach((toast) => {
      if ((toast as any)._timer) return;
      (toast as any)._timer = setTimeout(() => remove(toast.id), toast.duration);
    });
  },
  { deep: true }
);
</script>
