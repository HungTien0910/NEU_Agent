<template>
  <div class="admin-shell" :class="isCollapsed ? 'admin-shell--collapsed' : ''">
    <aside
      class="admin-sidebar"
      @mouseenter="handleSidebarEnter"
      @mouseleave="handleSidebarLeave"
    >
      <NuxtLink to="/admin/overview" class="admin-logo">
        <img src="/media/neu-logo.webp" alt="NEU" class="admin-logo__img" />
        <div class="admin-logo__text">
          <span v-for="(line, idx) in brandLines" :key="idx">{{ line }}</span>
        </div>
      </NuxtLink>
      <nav class="admin-nav">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="admin-nav__item"
          :class="isActive(item.to) ? 'admin-nav__item--active' : ''"
        >
          <span class="admin-nav__icon" :class="`admin-nav__icon--${item.icon}`" />
          <span class="admin-nav__text">{{ item.label }}</span>
        </NuxtLink>
      </nav>
    </aside>

    <div class="admin-main">
      <header class="admin-header">
        <div class="admin-header__title">{{ t('header.title') }}</div>
        <div
          class="admin-header__right"
          @mouseenter="openMenu"
          @mouseleave="scheduleClose"
        >
          <div class="admin-header__pill">
            {{ t('header.hello') }}, {{ userName }}
          </div>
          <div
            v-if="menuOpen"
            class="admin-dropdown"
            @mouseenter="openMenu"
            @mouseleave="scheduleClose"
          >
            <NuxtLink to="/admin/profile" class="admin-dropdown__item">
              {{ t('header.account') }}
            </NuxtLink>
            <button class="admin-dropdown__item" @click="logout">
              {{ t('header.logout') }}
            </button>
          </div>
        </div>
      </header>
      <main class="admin-content">
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
const isCollapsed = ref(true);
const hoverEnabled = ref(true);
const userName = computed(() => user.value?.full_name || 'Admin');
const brandLines = computed(() => t('header.brand').split('\n'));
let closeTimer: ReturnType<typeof setTimeout> | null = null;

const navItems = computed(() => [
  { label: t('nav.overview'), to: '/admin/overview', icon: 'overview' },
  { label: t('nav.query'), to: '/admin/query', icon: 'query' },
  { label: t('nav.import'), to: '/admin/import', icon: 'import' },
  { label: t('nav.data'), to: '/admin/data', icon: 'data' },
  { label: t('nav.users'), to: '/admin/users', icon: 'users' },
  { label: t('nav.logs'), to: '/admin/logs', icon: 'logs' },
  { label: t('nav.settings'), to: '/admin/settings', icon: 'settings' }
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

const updateHoverMode = () => {
  if (typeof window === 'undefined') return;
  hoverEnabled.value = window.innerWidth > 960;
  if (!hoverEnabled.value) {
    isCollapsed.value = false;
  }
};

const handleSidebarEnter = () => {
  if (hoverEnabled.value) {
    isCollapsed.value = false;
  }
};

const handleSidebarLeave = () => {
  if (hoverEnabled.value) {
    isCollapsed.value = true;
  }
};

const logout = async () => {
  clear();
  menuOpen.value = false;
  await navigateTo('/login');
};

onMounted(() => {
  load();
  loadUser();
  updateHoverMode();
  window.addEventListener('resize', updateHoverMode);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateHoverMode);
  if (closeTimer) {
    clearTimeout(closeTimer);
  }
});
</script>
