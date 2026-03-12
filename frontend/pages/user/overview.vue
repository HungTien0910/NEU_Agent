<template>
  <section class="user-section">
    <div>
      <h2 class="user-title">{{ t('user.overviewTitle') }}</h2>
      <p class="user-subtitle">{{ t('user.overviewSubtitle') }}</p>
    </div>

    <div class="user-hero">
      <div class="hero-content">
        <div class="hero-badge">NEU</div>
        <div>
          <h3 class="hero-title">
            {{ t('user.overviewGreeting') }} {{ displayName }}
          </h3>
          <p class="hero-text">{{ t('user.overviewHint') }}</p>
        </div>
      </div>
      <div class="hero-stats">
        <div class="hero-stat">
          <span class="stat-label">{{ t('user.totalQueries') }}</span>
          <strong class="stat-value">{{ totalQueries }}</strong>
        </div>
        <div class="hero-stat">
          <span class="stat-label">{{ t('user.lastQuery') }}</span>
          <strong class="stat-value stat-value--sm stat-value--truncate" :title="lastQuery">
            {{ lastQuery }}
          </strong>
          <span class="stat-meta">{{ lastQueryTime }}</span>
        </div>
      </div>
    </div>

    <div class="user-charts user-grid user-grid--2">
      <template v-if="isClient">
        <ChartDisplay
          :type="'bar'"
          :labels="activityLabels"
          :values="activityValues"
          :title="t('user.overviewActivityChart')"
        />
        <ChartDisplay
          :type="'pie'"
          :labels="chartTypeLabels"
          :values="chartTypeValues"
          :colors="['#2b6fc9', '#f4b256']"
          :title="t('user.overviewChartType')"
        />
      </template>
      <template v-else>
        <div class="user-card chart-skeleton" />
        <div class="user-card chart-skeleton" />
      </template>
    </div>

    <div class="user-grid user-grid--2">
      <div class="user-card history-card">
        <div class="card-title">{{ t('user.historyTitle') }}</div>
        <ul v-if="history.length" class="history-list">
          <li v-for="item in history" :key="item.id">
            <strong>{{ item.question }}</strong>
            <span>{{ formatDate(item.created_at) }}</span>
          </li>
        </ul>
        <p v-else class="history-empty">{{ t('user.historyEmpty') }}</p>
      </div>
      <div class="user-card permission-card">
        <div class="card-title">{{ t('user.permissionsTitle') }}</div>
        <div v-if="permissionLabels.length" class="perm-list">
          <span v-for="perm in permissionLabels" :key="perm" class="perm-chip">
            {{ perm }}
          </span>
        </div>
        <p v-else class="history-empty">{{ t('user.permissionsEmpty') }}</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '@/composables/useI18n';
import { useCurrentUser } from '@/composables/useCurrentUser';
import { listHistory } from '@/services/api/user';
import ChartDisplay from '@/components/blocks/ChartDisplay.vue';

definePageMeta({
  layout: 'user'
});

const { t, locale } = useI18n();
const { user, load: loadUser } = useCurrentUser();
const isClient = ref(false);
const history = ref<
  {
    id: number;
    question: string;
    created_at: string;
    chart_type?: string | null;
    is_data?: boolean;
  }[]
>([]);
const recentHistory = ref<
  {
    id: number;
    question: string;
    created_at: string;
    chart_type?: string | null;
    is_data?: boolean;
  }[]
>([]);
const totalQueries = ref(0);
const lastQuery = ref('—');
const lastQueryTime = ref('—');

const displayName = computed(() => user.value?.full_name || user.value?.username || '—');
const permissionLabels = computed(() => {
  if (user.value?.role === 'admin') {
    return [t('user.permissionsAll')];
  }
  const map: Record<string, string> = {
    'data:student': t('users.permStudent'),
    'data:course': t('users.permCourse'),
    'data:lecturer': t('users.permLecturer'),
    'data:academic': t('users.permAcademic')
  };
  return (user.value?.permissions || []).map((perm) => map[perm] || perm);
});

const activityLabels = computed(() => {
  if (!isClient.value) return [];
  const labels: string[] = [];
  const today = new Date();
  for (let i = 6; i >= 0; i -= 1) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    labels.push(
      date.toLocaleDateString(locale.value === 'en' ? 'en-US' : 'vi-VN', {
        day: '2-digit',
        month: '2-digit'
      })
    );
  }
  return labels;
});

const activityValues = computed(() => {
  if (!isClient.value) return [];
  const counts: number[] = Array(7).fill(0);
  const today = new Date();
  const dayKeys = Array.from({ length: 7 }, (_, idx) => {
    const date = new Date(today);
    date.setDate(today.getDate() - (6 - idx));
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  });
  recentHistory.value.forEach((item) => {
    const date = new Date(item.created_at);
    const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
    const index = dayKeys.indexOf(key);
    if (index !== -1) counts[index] += 1;
  });
  return counts;
});

const chartTypeLabels = computed(() => [
  t('user.overviewChartData'),
  t('user.overviewChartChat')
]);

const chartTypeValues = computed(() => {
  if (!isClient.value) return [];
  let dataCount = 0;
  let chatCount = 0;
  recentHistory.value.forEach((item) => {
    if (item.is_data) {
      dataCount += 1;
    } else {
      chatCount += 1;
    }
  });
  return [dataCount, chatCount];
});

const formatDate = (value: string) => {
  const date = new Date(value);
  return date.toLocaleString(locale.value === 'en' ? 'en-US' : 'vi-VN');
};

const loadOverview = async () => {
  if (!user.value?.username) return;
  const data = await listHistory(user.value.username, 200, 0);
  totalQueries.value = data.total;
  recentHistory.value = data.items;
  history.value = data.items.slice(0, 5);
  if (data.items.length > 0) {
    lastQuery.value = data.items[0].question;
    lastQueryTime.value = formatDate(data.items[0].created_at);
  }
};

onMounted(() => {
  isClient.value = true;
  loadUser();
  loadOverview();
});
</script>

<style scoped>
.user-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-hero {
  margin-top: 18px;
  padding: 20px 22px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f2f7ff 0%, #e7f1ff 100%);
  border: 1px solid #dbe7fb;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-skeleton {
  min-height: 220px;
  border-radius: 16px;
  border: 1px dashed #d7e2f5;
  background: linear-gradient(135deg, #f4f7fd 0%, #eef3fb 100%);
}

.hero-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hero-badge {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: #1b5ea8;
  color: #ffffff;
  display: grid;
  place-items: center;
  font-weight: 700;
  letter-spacing: 1px;
  box-shadow: 0 12px 24px rgba(27, 94, 168, 0.2);
}

.hero-title {
  margin: 0;
  font-size: 20px;
  color: #1b2b44;
}

.hero-text {
  margin: 6px 0 0;
  font-size: 13px;
  color: #6c7e99;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}

.hero-stat {
  background: #ffffff;
  border: 1px solid #e1eaf7;
  border-radius: 14px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-meta {
  font-size: 12px;
  color: #8a9bb5;
}

.stat-label {
  color: #7b8cab;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.stat-value {
  margin-top: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #1b2b44;
}

.stat-value--sm {
  font-size: 14px;
  font-weight: 600;
  color: #2a5fa7;
  margin-top: 0;
}

.stat-value--truncate {
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-grid {
  margin-top: 18px;
}

.card-title {
  font-weight: 600;
  color: #1b2b44;
}

.history-card,
.permission-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  color: #6c7e99;
  font-size: 13px;
}

.history-list strong {
  color: #1b2b44;
  font-weight: 600;
  display: block;
}

.history-empty {
  margin: 0;
  font-size: 13px;
  color: #7b8cab;
}

.perm-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.perm-chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f3f7ff;
  border: 1px solid #dbe7fb;
  font-size: 12px;
  color: #2a5fa7;
  font-weight: 600;
}

.user-charts {
  margin-top: 18px;
  align-items: stretch;
}

:deep(.chart-card) {
  height: 100%;
}

@media (max-width: 640px) {
  .user-hero {
    padding: 16px;
  }

  .hero-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
