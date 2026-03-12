<template>
  <section class="admin-section">
    <div class="admin-toolbar">
      <div>
        <h2 class="admin-title">{{ t('users.title') }}</h2>
        <p class="admin-subtitle">{{ t('users.listTitle') }}</p>
      </div>
      <BaseButton @click="openCreate" style="width: 140px">
        {{ t('users.create') }}
      </BaseButton>
    </div>

    <div class="admin-card">
      <table class="admin-table">
        <thead>
          <tr>
            <th>{{ t('common.no') }}</th>
            <th>{{ t('users.username') }}</th>
            <th>{{ t('users.fullName') }}</th>
            <th>{{ t('users.email') }}</th>
            <th>{{ t('users.phone') }}</th>
            <th>{{ t('users.titleLabel') }}</th>
            <th>{{ t('users.status') }}</th>
            <th>{{ t('users.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in users" :key="user.id">
            <td>{{ (page - 1) * pageSize + index + 1 }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.full_name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.phone }}</td>
            <td>{{ user.title }}</td>
            <td>
              <span
                class="admin-tag"
                :class="user.is_active ? 'admin-tag--success' : 'admin-tag--warning'"
              >
                {{ user.is_active ? t('users.active') : t('users.locked') }}
              </span>
            </td>
            <td>
              <div class="admin-actions">
                <button class="icon-btn" @click="goDetail(user.id)" :title="t('common.view')">
                  👁
                </button>
                <button class="icon-btn" @click="openEdit(user)" :title="t('common.edit')">
                  ✎
                </button>
                <button
                  class="icon-btn icon-btn--danger"
                  @click="openDelete(user)"
                  :title="t('common.delete')"
                >
                  🗑
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pager">
        <span>{{ t('common.page') }} {{ page }} / {{ totalPages }}</span>
        <div class="pager-actions">
          <select v-model.number="pageSize" class="pager-select" @change="changePageSize">
            <option v-for="size in pageSizes" :key="size" :value="size">
              {{ size }}
            </option>
          </select>
          <button class="icon-btn" :disabled="page === 1" @click="prevPage">‹</button>
          <button class="icon-btn" :disabled="page === totalPages" @click="nextPage">
            ›
          </button>
        </div>
      </div>
    </div>

    <div v-if="showFormModal" class="admin-modal">
      <div class="admin-modal__card">
        <div class="admin-modal__header">
          <h3 class="admin-modal__title">
            {{ isEditMode ? t('users.modalEdit') : t('users.modalCreate') }}
          </h3>
          <button class="admin-modal__close" @click="closeForm">×</button>
        </div>

        <div class="admin-form-grid">
          <BaseInput v-model="form.username" :label="`${t('users.username')}*`" />
          <BaseInput v-model="form.full_name" :label="`${t('users.fullName')}*`" />
          <BaseInput v-model="form.title" :label="`${t('users.titleLabel')}*`" />
          <BaseInput v-model="form.birth_date" :label="t('users.birthDate')" type="date" />
          <div class="admin-form-field">
            <span class="admin-form-label">{{ t('users.gender') }}</span>
            <div class="admin-pill-group">
              <label class="admin-radio">
                <input v-model="form.gender" type="radio" value="Nữ" />
                <span>{{ t('users.female') }}</span>
              </label>
              <label class="admin-radio">
                <input v-model="form.gender" type="radio" value="Nam" />
                <span>{{ t('users.male') }}</span>
              </label>
            </div>
          </div>
          <BaseInput v-model="form.email" :label="`${t('users.email')}*`" />
          <BaseInput v-model="form.phone" :label="`${t('users.phone')}*`" />
          <BaseInput
            v-model="form.password"
            :label="`${t('users.password')}*`"
            type="password"
          />
          <BaseInput v-model="form.address" :label="t('users.address')" />
          <BaseSelect v-model="form.department" :label="t('users.department')" :options="departments" />
          <div class="admin-form-field admin-span-2">
            <span class="admin-form-label">{{ t('users.permissions') }}</span>
            <div class="admin-pill-group">
              <span
                v-for="perm in permissionOptions"
                :key="perm.code"
                class="admin-pill"
                :class="selectedPermissions.includes(perm.code) ? 'admin-pill--active' : ''"
                @click="togglePermission(perm.code)"
              >
                {{ perm.label }}
              </span>
            </div>
          </div>
          <div v-if="isEditMode" class="admin-form-field admin-span-2">
            <span class="admin-form-label">{{ t('users.status') }}</span>
            <div class="admin-toggle-row">
              <span>{{ t('users.activate') }}</span>
              <div
                class="toggle"
                :class="form.is_active ? 'toggle--on' : ''"
                @click="form.is_active = !form.is_active"
              />
            </div>
          </div>
        </div>

        <div class="admin-footer-actions">
          <BaseButton variant="outline" @click="closeForm">
            {{ t('common.close') }}
          </BaseButton>
          <BaseButton
            style="min-width: 120px"
            :disabled="isEditMode && !canSave"
            @click="submitForm"
          >
            {{ t('common.save') }}
          </BaseButton>
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="admin-modal">
      <div class="admin-modal__card" style="max-width: min(520px, 90vw)">
        <div class="admin-alert">
          <div class="admin-alert__icon">!</div>
          <div>
            <h4 style="margin: 0 0 6px; color: #1b2b44">
              {{ t('users.confirmDelete') }}
            </h4>
            <p style="margin: 0; color: #6c7e99">
              {{ t('users.confirmDeleteDetail') }} {{ selectedUser?.username }}?
              {{ t('users.deleteWarning') }}
            </p>
          </div>
        </div>
        <div class="admin-footer-actions" style="margin-top: 20px">
          <BaseButton variant="outline" @click="closeDelete">
            {{ t('common.cancel') }}
          </BaseButton>
          <BaseButton variant="danger" @click="confirmDelete">
            {{ t('common.delete') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import {
  createUser,
  deleteUser,
  getUser,
  listUsers,
  updateUser
} from '@/services/api/admin';
import { useI18n } from '@/composables/useI18n';
import { useToast } from '@/composables/useToast';

definePageMeta({
  layout: 'admin'
});

const { t, locale } = useI18n();
const { push } = useToast();

const users = ref<any[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const pageSizes = [10, 20, 50, 100, 200];

const departments = computed(() => {
  if (locale.value === 'en') {
    return [
      { label: 'Accounting', value: 'Kế toán' },
      { label: 'Information Technology', value: 'CNTT' },
      { label: 'Economics', value: 'Kinh tế' }
    ];
  }
  return [
    { label: 'Kế toán', value: 'Kế toán' },
    { label: 'CNTT', value: 'CNTT' },
    { label: 'Kinh tế', value: 'Kinh tế' }
  ];
});

const permissionOptions = computed(() => [
  { code: 'data:student', label: t('users.permStudent') },
  { code: 'data:course', label: t('users.permCourse') },
  { code: 'data:lecturer', label: t('users.permLecturer') },
  { code: 'data:academic', label: t('users.permAcademic') }
]);

const showFormModal = ref(false);
const showDeleteModal = ref(false);
const isEditMode = ref(false);
const selectedUser = ref<typeof users.value[0] | null>(null);
const selectedPermissions = ref<string[]>([]);
const originalSnapshot = ref<any>(null);

const form = reactive({
  username: '',
  full_name: '',
  title: '',
  birth_date: '',
  gender: 'Nữ',
  email: '',
  phone: '',
  password: '',
  address: '',
  department: 'Kế toán',
  is_active: true
});

const openCreate = () => {
  isEditMode.value = false;
  selectedPermissions.value = [];
  Object.assign(form, {
    username: '',
    full_name: '',
    title: '',
    birth_date: '',
    gender: 'Nữ',
    email: '',
    phone: '',
    password: '',
    address: '',
    department: 'Kế toán',
    is_active: true
  });
  showFormModal.value = true;
};

const openEdit = async (user: (typeof users.value)[0]) => {
  isEditMode.value = true;
  selectedUser.value = user;
  const detail = await getUser(user.id);
  selectedPermissions.value = detail.permissions || [];
  originalSnapshot.value = {
    username: detail.username,
    full_name: detail.full_name,
    title: detail.title || '',
    birth_date: detail.birth_date || '',
    gender: detail.gender || '',
    email: detail.email || '',
    phone: detail.phone || '',
    address: detail.address || '',
    department: detail.department || '',
    permissions: detail.permissions || [],
    is_active: detail.is_active
  };
  Object.assign(form, {
    username: detail.username,
    full_name: detail.full_name,
    title: detail.title || '',
    birth_date: detail.birth_date || '',
    gender: detail.gender || 'Nam',
    email: detail.email || '',
    phone: detail.phone || '',
    password: '',
    address: detail.address || '',
    department: detail.department || 'Kế toán',
    is_active: detail.is_active
  });
  showFormModal.value = true;
};

const openDelete = (user: (typeof users.value)[0]) => {
  selectedUser.value = user;
  showDeleteModal.value = true;
};

const closeForm = () => {
  showFormModal.value = false;
};

const closeDelete = () => {
  showDeleteModal.value = false;
};

const goDetail = (id: number) => navigateTo(`/admin/users/${id}`);

const togglePermission = (perm: string) => {
  if (selectedPermissions.value.includes(perm)) {
    selectedPermissions.value = selectedPermissions.value.filter((p) => p !== perm);
    return;
  }
  selectedPermissions.value.push(perm);
};

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

const loadUsers = async () => {
  const skip = (page.value - 1) * pageSize.value;
  const data = await listUsers('', pageSize.value, skip);
  users.value = data.items || [];
  total.value = data.total || 0;
  if (page.value > totalPages.value) {
    page.value = totalPages.value;
  }
};

const nextPage = async () => {
  if (page.value < totalPages.value) {
    page.value += 1;
    await loadUsers();
  }
};

const prevPage = async () => {
  if (page.value > 1) {
    page.value -= 1;
    await loadUsers();
  }
};

const changePageSize = async () => {
  page.value = 1;
  await loadUsers();
};

const submitForm = async () => {
  const payload = buildPayload();

  if (!payload.password) {
    delete (payload as any).password;
  }

  try {
    if (isEditMode.value && selectedUser.value) {
      const changedFields = getChangedFields(payload);
      if (!changedFields.length) {
        return;
      }
      await updateUser(selectedUser.value.id, payload);
      const messages: string[] = [];
      if (originalSnapshot.value) {
        if (changedFields.length) {
          messages.push(
            locale.value === 'en'
              ? `Updated: ${changedFields.join(', ')}.`
              : `Đã cập nhật: ${changedFields.join(', ')}.`
          );
        }
      }

      if (messages.length === 0) {
        messages.push(
          locale.value === 'en' ? 'User updated.' : 'Cập nhật tài khoản thành công.'
        );
      }
      messages.forEach((msg) => push(msg, 'success'));
    } else {
      await createUser(payload);
      push(
        locale.value === 'en' ? 'User created.' : 'Tạo tài khoản thành công.',
        'success'
      );
    }
    closeForm();
    page.value = 1;
    await loadUsers();
  } catch (err: any) {
    const message =
      err?.data?.detail || err?.message || (locale.value === 'en' ? 'Save failed.' : 'Lưu thất bại.');
    push(message, 'error');
  }
};

const confirmDelete = async () => {
  if (selectedUser.value) {
    await deleteUser(selectedUser.value.id);
    push(locale.value === 'en' ? 'User deleted.' : 'Đã xóa tài khoản.', 'success');
  }
  closeDelete();
  page.value = 1;
  await loadUsers();
};

onMounted(loadUsers);

const buildPayload = () => {
  return {
    username: form.username,
    full_name: form.full_name,
    title: form.title,
    birth_date: form.birth_date || null,
    gender: form.gender,
    email: form.email,
    phone: form.phone,
    password: form.password || undefined,
    address: form.address,
    department: form.department,
    permissions: selectedPermissions.value,
    is_active: form.is_active,
    role: 'user'
  };
};

const getChangedFields = (payload: ReturnType<typeof buildPayload>) => {
  if (!originalSnapshot.value) return [];
  const normalize = (value: any) => (value ?? '').toString().trim();
  const normalizeArray = (value: string[] | undefined) =>
    (value || []).slice().sort().join('|');
  const labelMap: Record<string, string> = {
    username: t('users.username'),
    full_name: t('users.fullName'),
    title: t('users.titleLabel'),
    birth_date: t('users.birthDate'),
    gender: t('users.gender'),
    email: t('users.email'),
    phone: t('users.phone'),
    address: t('users.address'),
    department: t('users.department'),
    permissions: t('users.permissions'),
    is_active: t('users.status'),
    password: t('users.password')
  };

  const changedFields: string[] = [];
  if (normalize(originalSnapshot.value.username) !== normalize(payload.username)) {
    changedFields.push(labelMap.username);
  }
  if (normalize(originalSnapshot.value.full_name) !== normalize(payload.full_name)) {
    changedFields.push(labelMap.full_name);
  }
  if (normalize(originalSnapshot.value.title) !== normalize(payload.title)) {
    changedFields.push(labelMap.title);
  }
  if (normalize(originalSnapshot.value.birth_date) !== normalize(payload.birth_date)) {
    changedFields.push(labelMap.birth_date);
  }
  if (normalize(originalSnapshot.value.gender) !== normalize(payload.gender)) {
    changedFields.push(labelMap.gender);
  }
  if (normalize(originalSnapshot.value.email) !== normalize(payload.email)) {
    changedFields.push(labelMap.email);
  }
  if (normalize(originalSnapshot.value.phone) !== normalize(payload.phone)) {
    changedFields.push(labelMap.phone);
  }
  if (normalize(originalSnapshot.value.address) !== normalize(payload.address)) {
    changedFields.push(labelMap.address);
  }
  if (normalize(originalSnapshot.value.department) !== normalize(payload.department)) {
    changedFields.push(labelMap.department);
  }
  if (
    normalizeArray(originalSnapshot.value.permissions) !==
    normalizeArray(payload.permissions)
  ) {
    changedFields.push(labelMap.permissions);
  }
  if (originalSnapshot.value.is_active !== payload.is_active) {
    changedFields.push(labelMap.is_active);
  }
  if (payload.password) {
    changedFields.push(labelMap.password);
  }
  return changedFields;
};

const canSave = computed(() => {
  if (!isEditMode.value) return true;
  const payload = buildPayload();
  return getChangedFields(payload).length > 0;
});
</script>

<style scoped>
.admin-subtitle {
  margin: 6px 0 0;
  color: #7b8cab;
  font-size: 13px;
}

.admin-form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  color: #7b8cab;
}

.admin-form-label {
  font-weight: 600;
  color: #6c7e99;
}

.admin-radio {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #2a5fa7;
}

.admin-toggle-row {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #2a5fa7;
  font-weight: 600;
}

.admin-pill {
  cursor: pointer;
}

.admin-pill--active {
  background: #1b5ea8;
  color: #fff;
}

.pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  color: #7b8cab;
  font-size: 12px;
}

.pager-actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

.pager-select {
  border: 1px solid #d7e3f7;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  color: #1b2b44;
  background: #ffffff;
}
</style>
