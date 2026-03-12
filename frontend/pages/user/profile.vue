<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-card">
      <h2 class="modal-title">{{ t('user.accountTitle') }}</h2>
      <p class="modal-subtitle">{{ t('user.accountSubtitle') }}</p>

      <div class="profile-grid">
        <div class="profile-item">
          <span class="profile-label">{{ t('users.username') }}</span>
          <span class="profile-value">{{ profile.username }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.fullName') }}</span>
          <span class="profile-value">{{ profile.full_name }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.email') }}</span>
          <span class="profile-value">{{ profile.email }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.phone') }}</span>
          <span class="profile-value">{{ profile.phone }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.titleLabel') }}</span>
          <span class="profile-value">{{ profile.title }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.birthDate') }}</span>
          <span class="profile-value">{{ profile.birth_date }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.gender') }}</span>
          <span class="profile-value">{{ profile.gender }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.department') }}</span>
          <span class="profile-value">{{ profile.department }}</span>
        </div>
        <div class="profile-item profile-item--span">
          <span class="profile-label">{{ t('users.address') }}</span>
          <span class="profile-value">{{ profile.address }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('user.roleLabel') }}</span>
          <span class="profile-value">{{ roleLabel }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.status') }}</span>
          <span class="profile-value">{{ statusLabel }}</span>
        </div>
        <div class="profile-item profile-item--span">
          <span class="profile-label">{{ t('users.permissions') }}</span>
          <span class="profile-value">{{ permissionsLabel }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCurrentUser } from '@/composables/useCurrentUser';
import { useI18n } from '@/composables/useI18n';
import { getUserProfile } from '@/services/api/user';

definePageMeta({
  layout: 'user'
});

const { t, locale, load } = useI18n();
const { user, load: loadUser } = useCurrentUser();

const profile = reactive({
  username: '-',
  full_name: '-',
  email: '-',
  phone: '-',
  title: '-',
  birth_date: '-',
  gender: '-',
  address: '-',
  department: '-',
  role: 'user',
  permissions: [] as string[],
  is_active: true
});

const roleLabel = computed(() => {
  if (profile.role === 'admin') {
    return locale.value === 'en' ? 'Administrator' : 'Quản trị viên';
  }
  return locale.value === 'en' ? 'User' : 'Cán bộ';
});

const permissionsLabel = computed(() => {
  if (!profile.permissions.length) return '-';
  const map: Record<string, string> = {
    'data:student': t('users.permStudent'),
    'data:course': t('users.permCourse'),
    'data:lecturer': t('users.permLecturer'),
    'data:academic': t('users.permAcademic')
  };
  return profile.permissions.map((perm) => map[perm] || perm).join(', ');
});

const statusLabel = computed(() => {
  if (profile.is_active) {
    return locale.value === 'en' ? t('users.active') : t('users.active');
  }
  return locale.value === 'en' ? t('users.locked') : t('users.locked');
});

const closeModal = () => navigateTo('/user/overview');

const loadProfile = async () => {
  if (!user.value?.username) return;
  try {
    const data = await getUserProfile(user.value.username);
    Object.assign(profile, {
      username: data.username || '-',
      full_name: data.full_name || '-',
      email: data.email || '-',
      phone: data.phone || '-',
      title: data.title || '-',
      birth_date: data.birth_date || '-',
      gender: data.gender || '-',
      address: data.address || '-',
      department: data.department || '-',
      role: data.role || 'user',
      permissions: data.permissions || [],
      is_active: data.is_active ?? true
    });
  } catch (error) {
    Object.assign(profile, {
      username: user.value?.username || '-',
      full_name: user.value?.full_name || '-'
    });
  }
};

onMounted(async () => {
  load();
  loadUser();
  await loadProfile();
});
</script>
