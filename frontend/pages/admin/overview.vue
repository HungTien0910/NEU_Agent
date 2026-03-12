<template>
  <section class="admin-section">
    <h2 class="admin-title">{{ t('overview.title') }}</h2>

    <div class="admin-grid admin-grid--4">
      <div class="admin-card stat-card">
        <div class="stat-card__label">{{ t('overview.totalUsers') }}</div>
        <div class="stat-card__value">{{ overview.stats.total_users }}</div>
      </div>
      <div class="admin-card stat-card">
        <div class="stat-card__label">{{ t('overview.activeUsers') }}</div>
        <div class="stat-card__value">{{ overview.stats.active_users }}</div>
      </div>
      <div class="admin-card stat-card">
        <div class="stat-card__label">{{ t('overview.lockedUsers') }}</div>
        <div class="stat-card__value">{{ overview.stats.locked_users }}</div>
      </div>
      <div class="admin-card stat-card">
        <div class="stat-card__label">{{ t('overview.admins') }}</div>
        <div class="stat-card__value">{{ overview.stats.admin_users }}</div>
      </div>
    </div>

    <div class="admin-grid admin-grid--2">
      <div class="admin-card weekly-card">
        <div class="weekly-header">
          <div>
            <div class="stat-card__label weekly-title">
              {{ t('overview.weekly') }}
            </div>
            <p class="weekly-subtitle">{{ t('overview.weeklyHint') }}</p>
          </div>
          <div class="weekly-summary">
            <div>
              <span>{{ t('overview.weeklyTotal') }}</span>
              <strong>{{ weeklyTotal }}</strong>
            </div>
            <div>
              <span>{{ t('overview.weeklyAvg') }}</span>
              <strong>{{ weeklyAvg }}</strong>
            </div>
            <div>
              <span>{{ t('overview.weeklyPeak') }}</span>
              <strong>{{ weeklyPeak }}</strong>
            </div>
          </div>
        </div>
        <div class="weekly-legend">
          <span class="legend-item"><i class="dot dot--create" />{{ t('overview.weeklyCreate') }}</span>
          <span class="legend-item"><i class="dot dot--update" />{{ t('overview.weeklyUpdate') }}</span>
          <span class="legend-item"><i class="dot dot--delete" />{{ t('overview.weeklyDelete') }}</span>
        </div>
        <div v-if="weeklyBars.length" class="weekly-chart">
          <div v-for="bar in weeklyBars" :key="bar.label" class="weekly-bar">
            <div class="weekly-stack" :title="bar.tooltip">
              <span class="bar-seg bar-create" :style="{ height: bar.createdPct + '%' }" />
              <span class="bar-seg bar-update" :style="{ height: bar.updatedPct + '%' }" />
              <span class="bar-seg bar-delete" :style="{ height: bar.deletedPct + '%' }" />
            </div>
            <span class="bar-label">{{ bar.label }}</span>
          </div>
        </div>
        <div v-else class="weekly-empty">{{ t('overview.weeklyEmpty') }}</div>
      </div>
      <div class="admin-card">
        <div class="stat-card__label" style="font-weight: 600; color: #1b2b44">
          {{ t('overview.recent') }}
        </div>
        <ul class="activity-list">
          <li v-for="item in overview.activities" :key="item.title">
            <strong>{{ item.title }}</strong>
            <span>{{ item.date }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="admin-card admin-card--soft">
      <div class="stat-card__label" style="font-weight: 600; color: #1b2b44">
        {{ t('overview.quick') }}
      </div>
      <div class="quick-stats">
        <div>
          <span>{{ t('overview.reset') }}</span>
          <strong>{{ overview.quick_stats.password_reset_requests }}</strong>
        </div>
        <div>
          <span>{{ t('overview.newUsers') }}</span>
          <strong>{{ overview.quick_stats.new_users_this_week }}</strong>
        </div>
        <div>
          <span>{{ t('overview.statusChanges') }}</span>
          <strong>{{ overview.quick_stats.status_changes }}</strong>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { getOverview } from '@/services/api/admin';
import { useI18n } from '@/composables/useI18n';

definePageMeta({
  layout: 'admin'
});

const { t, locale } = useI18n();
const overview = reactive({
  stats: {
    total_users: 0,
    active_users: 0,
    locked_users: 0,
    admin_users: 0
  },
  activities: [] as { title: string; date: string }[],
  quick_stats: {
    password_reset_requests: 0,
    new_users_this_week: 0,
    status_changes: 0
  },
  weekly: {
    labels: [],
    created: [],
    updated: [],
    deleted: [],
    total: []
  }
});
const rawActivities = ref<{ title: string; date: string }[]>([]);

const weeklyBars = computed(() => {
  const labels = overview.weekly?.labels || [];
  const created = overview.weekly?.created || [];
  const updated = overview.weekly?.updated || [];
  const deleted = overview.weekly?.deleted || [];
  const totals = overview.weekly?.total || [];
  const maxTotal = Math.max(...totals, 1);
  return labels.map((label, idx) => {
    const c = created[idx] || 0;
    const u = updated[idx] || 0;
    const d = deleted[idx] || 0;
    const total = totals[idx] ?? c + u + d;
    return {
      label,
      created: c,
      updated: u,
      deleted: d,
      total,
      createdPct: (c / maxTotal) * 100,
      updatedPct: (u / maxTotal) * 100,
      deletedPct: (d / maxTotal) * 100,
      tooltip: `${label} • ${t('overview.weeklyCreate')}: ${c}, ${t('overview.weeklyUpdate')}: ${u}, ${t('overview.weeklyDelete')}: ${d}`
    };
  });
});

const weeklyTotal = computed(() => {
  const totals = overview.weekly?.total || [];
  return totals.reduce((sum, value) => sum + value, 0);
});

const weeklyAvg = computed(() => {
  if (!weeklyBars.value.length) return 0;
  return Math.round(weeklyTotal.value / weeklyBars.value.length);
});

const weeklyPeak = computed(() => {
  if (!weeklyBars.value.length) return '—';
  let peakIdx = 0;
  weeklyBars.value.forEach((bar, idx) => {
    if (bar.total > weeklyBars.value[peakIdx].total) peakIdx = idx;
  });
  return `${weeklyBars.value[peakIdx].label} • ${weeklyBars.value[peakIdx].total}`;
});

const mapActivities = () => {
  const mapDetail = (detail: string) => {
    if (locale.value !== 'en') return detail;
    const rules: Array<{ prefix: string; replace: string }> = [
      { prefix: 'Tạo tài khoản ', replace: 'Created account ' },
      { prefix: 'Cập nhật tài khoản ', replace: 'Updated account ' },
      { prefix: 'Xóa tài khoản ', replace: 'Deleted account ' },
      { prefix: 'Cập nhật cài đặt', replace: 'Updated settings' },
      {
        prefix: 'Xóa toàn bộ dữ liệu trên hệ thống.',
        replace: 'Cleared all Neo4j and PostgreSQL data'
      },
      { prefix: 'Xóa toàn bộ dữ liệu Neo4j', replace: 'Cleared all Neo4j data' }
    ];
    for (const rule of rules) {
      if (detail.startsWith(rule.prefix)) {
        return detail.replace(rule.prefix, rule.replace);
      }
    }
    return detail;
  };

  const formatDate = (value: string) => {
    if (locale.value !== 'en') return value;
    const parts = value.split('/');
    if (parts.length !== 3) return value;
    const [day, month, year] = parts.map((part) => Number(part));
    const date = new Date(year, month - 1, day);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString('en-US');
  };

  overview.activities = rawActivities.value.map((item) => {
    const title = item.title.replace(/^#\\d+\\s*/, '');
    const prefix = item.title.match(/^#\\d+\\s*/) || [''];
    return {
      ...item,
      title: `${prefix[0]}${mapDetail(title)}`,
      date: formatDate(item.date)
    };
  });
};

onMounted(async () => {
  const data = await getOverview();
  rawActivities.value = data.activities;
  Object.assign(overview, data);
  mapActivities();
});

watch(locale, mapActivities);
</script>

<style scoped>
.chart-placeholder {
  margin-top: 18px;
  height: 180px;
  border-radius: 12px;
  background: #f4f7fd;
  display: grid;
  place-items: center;
}

.chart-line {
  width: 80%;
  height: 2px;
  background: linear-gradient(90deg, #1b5ea8 0%, #6ea6ef 100%);
  position: relative;
}

.chart-line::after {
  content: '';
  position: absolute;
  right: 0;
  top: -3px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1b5ea8;
}

.weekly-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weekly-header {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
}

.weekly-title {
  font-weight: 600;
  color: #1b2b44;
}

.weekly-subtitle {
  margin: 6px 0 0;
  font-size: 12px;
  color: #7b8cab;
}

.weekly-summary {
  display: flex;
  gap: 16px;
  background: #f6f9ff;
  border: 1px solid #e1eaf7;
  padding: 10px 14px;
  border-radius: 14px;
  color: #1b2b44;
}

.weekly-summary span {
  font-size: 11px;
  color: #7b8cab;
}

.weekly-summary strong {
  display: block;
  margin-top: 4px;
  font-size: 16px;
}

.weekly-legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  color: #7b8cab;
  font-size: 12px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot--create {
  background: #3e8fe6;
}

.dot--update {
  background: #6ec1a8;
}

.dot--delete {
  background: #ef8b8b;
}

.weekly-chart {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(42px, 1fr));
  gap: 12px;
  align-items: end;
  min-height: 190px;
  padding: 14px;
  border-radius: 16px;
  background: linear-gradient(180deg, #f9fbff 0%, #f1f6ff 100%);
  border: 1px solid #e6eef9;
  position: relative;
}

.weekly-chart::after {
  content: '';
  position: absolute;
  inset: 16px;
  border-radius: 12px;
  border: 1px dashed #dfe8f7;
  pointer-events: none;
}

.weekly-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  z-index: 1;
}

.weekly-stack {
  width: 18px;
  height: 120px;
  display: flex;
  flex-direction: column-reverse;
  gap: 2px;
  border-radius: 10px;
  padding: 4px;
  background: #ffffff;
  border: 1px solid #e3ebf7;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.6);
}

.bar-seg {
  width: 100%;
  border-radius: 6px;
  transition: height 0.2s ease;
}

.bar-create {
  background: linear-gradient(180deg, #4a98f0 0%, #2876d6 100%);
}

.bar-update {
  background: linear-gradient(180deg, #7ad6b8 0%, #4fb495 100%);
}

.bar-delete {
  background: linear-gradient(180deg, #f3a1a1 0%, #e57676 100%);
}

.bar-label {
  font-size: 11px;
  color: #7b8cab;
}

.weekly-empty {
  padding: 18px;
  border-radius: 12px;
  border: 1px dashed #d6e2f2;
  color: #8a9bb5;
  font-size: 13px;
  background: #f8fbff;
}

.activity-list {
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-list li {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 13px;
  color: #6c7e99;
}

.activity-list strong {
  color: #1b2b44;
  font-weight: 600;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 18px;
  margin-top: 12px;
}

.quick-stats span {
  color: #7b8cab;
  font-size: 13px;
}

.quick-stats strong {
  display: block;
  margin-top: 8px;
  font-size: 20px;
  color: #1b2b44;
}
</style>
