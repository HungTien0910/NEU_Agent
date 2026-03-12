<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-card">
      <h2 class="modal-title">{{ t('userDetail.title') }}</h2>
      <p class="modal-subtitle">{{ t('user.accountSubtitle') }}</p>

      <div class="profile-grid">
        <div class="profile-item">
          <span class="profile-label">{{ t('users.username') }}</span>
          <span class="profile-value">{{ user.username || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.fullName') }}</span>
          <span class="profile-value">{{ user.full_name || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.email') }}</span>
          <span class="profile-value">{{ user.email || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.phone') }}</span>
          <span class="profile-value">{{ user.phone || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.titleLabel') }}</span>
          <span class="profile-value">{{ user.title || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.birthDate') }}</span>
          <span class="profile-value">{{ user.birth_date || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.gender') }}</span>
          <span class="profile-value">{{ user.gender || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.department') }}</span>
          <span class="profile-value">{{ user.department || '-' }}</span>
        </div>
        <div class="profile-item profile-item--span">
          <span class="profile-label">{{ t('users.address') }}</span>
          <span class="profile-value">{{ user.address || '-' }}</span>
        </div>
        <div class="profile-item">
          <span class="profile-label">{{ t('users.status') }}</span>
          <span
            class="admin-tag"
            :class="user.is_active ? 'admin-tag--success' : 'admin-tag--warning'"
          >
            {{ user.is_active ? t('users.active') : t('users.locked') }}
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
import { getUser } from '@/services/api/admin';
import { useI18n } from '@/composables/useI18n';

definePageMeta({
  layout: 'admin'
});

const { t } = useI18n();

const route = useRoute();
const user = reactive({
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

const permissionLabels = computed(() => user.permissions.map((perm) => mapPermission(perm)));
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

onMounted(async () => {
  const id = Number(route.params.id);
  const detail = await getUser(id);
  Object.assign(user, {
    username: detail.username,
    full_name: detail.full_name,
    email: detail.email || '',
    phone: detail.phone || '',
    title: detail.title || '',
    department: detail.department || '',
    address: detail.address || '',
    birth_date: detail.birth_date || '',
    gender: detail.gender || 'Nam',
    permissions: detail.permissions || [],
    is_active: detail.is_active
  });
});

const closeModal = () => navigateTo('/admin/users');
</script>

<style scoped></style>
