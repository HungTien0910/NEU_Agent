<template>
  <section class="user-section">
    <div>
      <h2 class="user-title">{{ t('user.historyTitle') }}</h2>
      <p class="user-subtitle">{{ t('user.historySubtitle') }}</p>
    </div>

    <div class="user-card" style="margin-top: 12px">
      <table v-if="history.length" class="admin-table">
        <thead>
          <tr>
            <th>#</th>
            <th>{{ t('user.question') }}</th>
            <th>{{ t('user.summary') }}</th>
            <th>{{ t('user.time') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in history" :key="item.id">
            <td>{{ (page - 1) * pageSize + idx + 1 }}</td>
            <td>
              <NuxtLink :to="`/user/history/${item.id}`" class="history-link">
                {{ item.question }}
              </NuxtLink>
            </td>
            <td>{{ item.summary || '—' }}</td>
            <td>{{ formatDate(item.created_at) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="history-empty">{{ t('user.historyEmpty') }}</p>
      <div v-if="history.length" class="pager">
        <span>{{ t('common.page') }} {{ page }} / {{ totalPages }}</span>
        <div class="pager-actions">
          <select v-model.number="pageSize" class="pager-select" @change="changePageSize">
            <option v-for="size in pageSizes" :key="size" :value="size">
              {{ size }}
            </option>
          </select>
          <button class="icon-btn" :disabled="page === 1" @click="prevPage">‹</button>
          <button class="icon-btn" :disabled="page === totalPages" @click="nextPage">›</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '@/composables/useI18n';
import { useCurrentUser } from '@/composables/useCurrentUser';
import { listHistory } from '@/services/api/user';

definePageMeta({
  layout: 'user'
});

const { t, locale } = useI18n();
const { user, load: loadUser } = useCurrentUser();
const history = ref<{ id: number; question: string; summary?: string; created_at: string }[]>(
  []
);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const pageSizes = [10, 20, 50, 100, 200];

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

const formatDate = (value: string) => {
  const date = new Date(value);
  return date.toLocaleString(locale.value === 'en' ? 'en-US' : 'vi-VN');
};

const loadHistory = async () => {
  if (!user.value?.username) return;
  const skip = (page.value - 1) * pageSize.value;
  const data = await listHistory(user.value.username, pageSize.value, skip);
  history.value = data.items;
  total.value = data.total || 0;
  if (page.value > totalPages.value) page.value = totalPages.value;
};

const changePageSize = async () => {
  page.value = 1;
  await loadHistory();
};

const prevPage = async () => {
  if (page.value <= 1) return;
  page.value -= 1;
  await loadHistory();
};

const nextPage = async () => {
  if (page.value >= totalPages.value) return;
  page.value += 1;
  await loadHistory();
};

onMounted(() => {
  loadUser();
  loadHistory();
});
</script>

<style scoped>
.history-link {
  color: #1b5ea8;
  font-weight: 600;
}

.history-empty {
  margin: 0;
  padding: 12px;
  color: #7b8cab;
  font-size: 13px;
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
