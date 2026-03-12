<template>
  <section class="auth-card">
    <div class="auth-card__brand">
      <slot name="logo">
        <div class="auth-card__logo">NEU</div>
      </slot>
      <div class="auth-card__titles">
        <h1 class="auth-card__title">{{ title }}</h1>
        <p class="auth-card__subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <div class="auth-card__body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="auth-card__footer">
      <slot name="footer" />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle: string;
}>();
</script>

<style scoped>
.auth-card {
  width: min(460px, 100%);
  background: rgba(10, 25, 55, 0.45);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 22px 50px rgba(7, 18, 38, 0.35);
  backdrop-filter: blur(12px);
  padding: 42px 38px 34px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  color: #f5f7ff;
}

.auth-card__brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.auth-card__logo {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.7);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
  letter-spacing: 1px;
  background: rgba(255, 255, 255, 0.12);
}

.auth-card__title {
  margin: 0;
  font-size: 18.5px;
  font-weight: 700;
  color: #ffffff;
  text-transform: uppercase;
}

.auth-card__subtitle {
  margin: 6px 0 0;
  font-size: 12.5px;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.7);
}

.auth-card__body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.auth-card__footer {
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 768px) {
  .auth-card {
    padding: 32px 24px 24px;
  }
}
</style>
