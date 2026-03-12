<template>
  <div class="user-shell">
    <aside class="user-sidebar">
      <NuxtLink to="/user/overview" class="user-logo">
        <img src="/media/neu-logo.webp" alt="NEU" class="user-logo__img" />
        <div class="user-logo__text">
          <span v-for="(line, idx) in brandLines" :key="idx">{{ line }}</span>
        </div>
      </NuxtLink>
      <nav class="user-nav">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="user-nav__item"
          :class="isActive(item.to) ? 'user-nav__item--active' : ''"
        >
          <span class="admin-nav__icon" :class="`admin-nav__icon--${item.icon}`" />
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>
    </aside>

    <div class="user-main">
      <header class="user-header">
        <div class="user-header__title">{{ t('header.title') }}</div>
        <div class="user-header__right" @mouseenter="openMenu" @mouseleave="scheduleClose">
          <div class="user-header__pill">
            {{ t('header.hello') }}, {{ userName }}
          </div>
          <div
            v-if="menuOpen"
            class="user-dropdown"
            @mouseenter="openMenu"
            @mouseleave="scheduleClose"
          >
            <NuxtLink to="/user/profile" class="user-dropdown__item">
              {{ t('header.account') }}
            </NuxtLink>
            <button class="user-dropdown__item" @click="logout">
              {{ t('header.logout') }}
            </button>
          </div>
        </div>
      </header>
      <main class="user-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCurrentUser } from '@/composables/useCurrentUser';
import { useI18n } from '@/composables/useI18n';

const route = useRoute();
const { t, load } = useI18n();
const { user, load: loadUser, clear } = useCurrentUser();

const menuOpen = ref(false);
const userName = computed(() => user.value?.full_name || 'User');
const brandLines = computed(() => t('header.brand').split('\n'));
let closeTimer: ReturnType<typeof setTimeout> | null = null;

const navItems = computed(() => [
  { label: t('nav.overview'), to: '/user/overview', icon: 'overview' },
  { label: t('nav.query'), to: '/user/query', icon: 'query' },
  { label: t('nav.history'), to: '/user/history', icon: 'logs' }
]);

const isActive = (path: string) => route.path.startsWith(path);

const openMenu = () => {
  if (closeTimer) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
  menuOpen.value = true;
};

const scheduleClose = () => {
  if (closeTimer) {
    clearTimeout(closeTimer);
  }
  closeTimer = setTimeout(() => {
    menuOpen.value = false;
  }, 180);
};

const logout = async () => {
  clear();
  menuOpen.value = false;
  await navigateTo('/login');
};

onMounted(() => {
  load();
  loadUser();
});

onBeforeUnmount(() => {
  if (closeTimer) {
    clearTimeout(closeTimer);
  }
});
</script>
