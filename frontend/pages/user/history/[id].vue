<template>
  <section class="user-section">
    <div class="user-card">
      <div class="detail-header">
        <div>
          <h2 class="user-title">{{ t('user.detailTitle') }}</h2>
          <p class="user-subtitle">{{ detail?.question }}</p>
        </div>
        <BaseButton variant="outline" @click="goBack">
          {{ t('user.backToHistory') }}
        </BaseButton>
      </div>

      <div v-if="detail?.summary" class="detail-summary">
        {{ detail.summary }}
      </div>

      <div v-if="detail?.columns?.length" class="detail-table">
        <table class="admin-table">
          <thead>
            <tr>
              <th v-for="col in detail.columns" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in detail.rows" :key="idx">
              <td v-for="(cell, cIdx) in row" :key="cIdx">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="canExport" class="export-row">
          <BaseButton variant="outline" @click="exportDetail">
            {{ t('user.export') }}
          </BaseButton>
        </div>
      </div>

      <ChartDisplay
        v-if="detail?.chart"
        v-model:type="chartType"
        :labels="detail.chart.labels"
        :values="detail.chart.values"
        :title="t('user.chart')"
        switchable
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '@/composables/useI18n';
import { useCurrentUser } from '@/composables/useCurrentUser';
import { exportExcel, getHistory } from '@/services/api/user';

definePageMeta({
  layout: 'user'
});

const { t } = useI18n();
const { user, load: loadUser } = useCurrentUser();
const route = useRoute();
const detail = ref<any>(null);
const chartType = ref<'bar' | 'line' | 'pie'>('bar');
const canExport = computed(() => (user.value?.permissions?.length || 0) > 0);

const loadDetail = async () => {
  if (!user.value?.username) return;
  const id = Number(route.params.id);
  const data = await getHistory(user.value.username, id);
  detail.value = data;
  if (data.chart?.type) {
    chartType.value = data.chart.type;
  }
};

const goBack = () => navigateTo('/user/history');

const exportDetail = async () => {
  if (!detail.value?.columns?.length || !detail.value?.rows?.length) return;
  if (!user.value?.username) return;
  await exportExcel({
    username: user.value.username,
    columns: detail.value.columns,
    rows: detail.value.rows,
    file_name: `neu_history_${detail.value.id}.xlsx`
  });
};

onMounted(() => {
  loadUser();
  loadDetail();
});
</script>

<style scoped>
.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-summary {
  margin: 12px 0 18px;
  font-size: 13px;
  color: #1b2b44;
  font-weight: 600;
}

.detail-table {
  margin-bottom: 18px;
}

.export-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>
