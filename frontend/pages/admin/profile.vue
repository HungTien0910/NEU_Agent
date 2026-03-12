<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-card">
      <h2 class="modal-title">{{ t('user.accountTitle') }}</h2>
      <p class="modal-subtitle">{{ t('user.accountSubtitle') }}</p>

      <div class="profile-grid">
        <div class="profile-item">
          <span class="profile-label">{{ t('users.username') }}</span>
          <span class="profile-value">{{ detail.username || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.fullName') }}</span>
          <span class="profile-value">{{ detail.full_name || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.email') }}</span>
          <span class="profile-value">{{ detail.email || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.phone') }}</span>
          <span class="profile-value">{{ detail.phone || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.titleLabel') }}</span>
          <span class="profile-value">{{ detail.title || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.birthDate') }}</span>
          <span class="profile-value">{{ detail.birth_date || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.gender') }}</span>
          <span class="profile-value">{{ detail.gender || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.department') }}</span>
          <span class="profile-value">{{ detail.department || '-' }}</span>
        </div>
        <div class="profile-item profile-item--span">
          <span class="profile-label">{{ t('users.address') }}</span>
          <span class="profile-value">{{ detail.address || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.status') }}</span>
          <span
            class="admin-tag"
            :class="detail.is_active ? 'admin-tag--success' : 'admin-tag--warning'"
          >
            {{ detail.is_active ? t('users.active') : t('users.locked') }}
          </span>
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
import { getUserByUsername } from '@/services/api/admin';
import { useCurrentUser } from '@/composables/useCurrentUser';
import { useI18n } from '@/composables/useI18n';

definePageMeta({
  layout: 'admin'
});

const { t } = useI18n();
const { user, load } = useCurrentUser();

const detail = reactive({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  title: '',
  department: '',
  address: '',
  birth_date: '',
  gender: 'Nam',
  password: '*****',
  permissions: [] as string[],
  is_active: true
});

const permissionLabels = computed(() =>
  detail.permissions.map((perm) => mapPermission(perm))
);
const permissionsLabel = computed(() =>
  permissionLabels.value.length ? permissionLabels.value.join(', ') : '-'
);

const mapPermission = (perm: string) => {
  const map: Record<string, string> = {
    'data:student': t('users.permStudent'),
    'data:course': t('users.permCourse'),
    'data:lecturer': t('users.permLecturer'),
    'data:academic': t('users.permAcademic')
  };
  return map[perm] || perm;
};

const closeModal = () => navigateTo('/admin/overview');

onMounted(async () => {
  load();
  const username = user.value?.username || 'admin';
  const info = await getUserByUsername(username);
  Object.assign(detail, {
    username: info.username,
    full_name: info.full_name,
    email: info.email || '',
    phone: info.phone || '',
    title: info.title || '',
    department: info.department || '',
    address: info.address || '',
    birth_date: info.birth_date || '',
    gender: info.gender || 'Nam',
    permissions: info.permissions || [],
    is_active: info.is_active
  });
});
</script>

<style scoped></style>
