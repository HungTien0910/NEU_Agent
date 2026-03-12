<template>
  <section class="admin-section">
    <h2 class="admin-title">{{ t('logs.title') }}</h2>
    <div class="admin-card">
      <div class="admin-toolbar admin-toolbar--start" style="margin-bottom: 12px">
        <BaseInput v-model="filters.from" :label="t('logs.from')" type="date" />
        <BaseInput v-model="filters.to" :label="t('logs.to')" type="date" />
      </div>

      <table class="admin-table">
        <thead>
          <tr>
            <th>{{ t('logs.time') }}</th>
            <th>{{ t('logs.actor') }}</th>
            <th>{{ t('logs.action') }}</th>
            <th>{{ t('logs.target') }}</th>
            <th>{{ t('logs.detail') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in logs" :key="item.detail">
            <td>{{ item.time }}</td>
            <td>{{ item.actor }}</td>
            <td>
              <span class="admin-tag" :class="item.tagClass">{{ item.action }}</span>
            </td>
            <td>{{ item.target }}</td>
            <td>{{ item.detail }}</td>
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
  </section>
</template>

<script setup lang="ts">
import { listLogs } from '@/services/api/admin';
import { useI18n } from '@/composables/useI18n';

definePageMeta({
  layout: 'admin'
});

const { t, locale } = useI18n();
const filters = reactive({
  from: '',
  to: ''
});

const logs = ref<
  {
    id: number;
    time: string;
    actor: string;
    action: string;
    target: string;
    detail: string;
    tagClass: string;
  }[]
>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(20);
const pageSizes = [10, 20, 50, 100, 200];

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

const mapTag = (action: string) => {
  const normalized = action.toLowerCase();
  if (normalized === 'thêm mới' || normalized === 'create') return 'admin-tag--success';
  if (normalized === 'xóa' || normalized === 'delete') return 'admin-tag--danger';
  if (normalized.includes('đăng') || normalized.includes('sign')) {
    return 'admin-tag--warning';
  }
  return '';
};

const mapAction = (action: string) => {
  if (locale.value === 'en') {
    const map: Record<string, string> = {
      'Thêm mới': 'Create',
      'Chỉnh sửa': 'Update',
      'Xóa': 'Delete',
      'Đăng nhập': 'Sign in',
      'Đăng xuất': 'Sign out'
    };
    return map[action] || action;
  }
  return action;
};

const mapTarget = (target: string) => {
  if (locale.value === 'en') {
    const map: Record<string, string> = {
      'Tài khoản': 'Account',
      'Hệ thống': 'System',
      'Quyền': 'Permission'
    };
    return map[target] || target;
  }
  return target;
};

const mapDetail = (detail: string) => {
  if (locale.value !== 'en') return detail;
  const rules: Array<{ prefix: string; replace: string }> = [
    { prefix: 'Tạo tài khoản ', replace: 'Created account ' },
    { prefix: 'Cập nhật tài khoản ', replace: 'Updated account ' },
    { prefix: 'Xóa tài khoản ', replace: 'Deleted account ' },
    {
      prefix: 'Xóa toàn bộ dữ liệu trên hệ thống.',
      replace: 'Cleared all Neo4j and PostgreSQL data'
    },
    { prefix: 'Xóa toàn bộ dữ liệu Neo4j', replace: 'Cleared all Neo4j data' },
    { prefix: 'Đăng nhập vào hệ thống', replace: 'Signed into the system' },
    { prefix: 'Đăng xuất khỏi hệ thống', replace: 'Signed out of the system' }
  ];
  for (const rule of rules) {
    if (detail.startsWith(rule.prefix)) {
      return detail.replace(rule.prefix, rule.replace);
    }
  }
  return detail;
};

const loadLogs = async () => {
  const data = await listLogs(
    {
      from_date: filters.from,
      to_date: filters.to
    },
    pageSize.value,
    (page.value - 1) * pageSize.value
  );
  total.value = data.total || 0;
  logs.value = data.items.map((item) => ({
    id: item.id,
    time: new Date(item.time).toLocaleString(
      locale.value === 'en' ? 'en-US' : 'vi-VN'
    ),
    actor: item.actor,
    action: mapAction(item.action),
    target: mapTarget(item.target),
    detail: mapDetail(item.detail),
    tagClass: mapTag(item.action)
  }));
};

const changePageSize = () => {
  page.value = 1;
  loadLogs();
};

const prevPage = () => {
  if (page.value <= 1) return;
  page.value -= 1;
  loadLogs();
};

const nextPage = () => {
  if (page.value >= totalPages.value) return;
  page.value += 1;
  loadLogs();
};

watch(
  [filters, locale],
  () => {
    page.value = 1;
    loadLogs();
  },
  { deep: true }
);
onMounted(loadLogs);
</script>
