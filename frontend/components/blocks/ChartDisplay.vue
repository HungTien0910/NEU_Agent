<template>
  <div class="chart-card">
    <div class="chart-header">
      <span class="chart-title">{{ title }}</span>
      <div class="chart-switch" v-if="switchable">
        <button
          v-for="item in chartTypes"
          :key="item"
          class="chart-switch__btn"
          :class="type === item ? 'chart-switch__btn--active' : ''"
          @click="$emit('update:type', item)"
        >
          {{ item.toUpperCase() }}
        </button>
      </div>
    </div>

    <div v-if="!hasData" class="chart-empty">
      Không có dữ liệu biểu đồ.
    </div>

    <div v-else-if="type === 'bar'" class="chart chart--bar">
      <div v-for="(value, idx) in safeValues" :key="idx" class="chart-bar">
        <span class="chart-bar__value">{{ formatValue(value) }}</span>
        <div class="chart-bar__track">
          <div class="chart-bar__fill" :style="{ height: `${barHeight(value)}%` }" />
        </div>
        <span class="chart-bar__label" :title="safeLabels[idx]">{{ safeLabels[idx] }}</span>
      </div>
    </div>

    <div v-else-if="type === 'line'" class="chart chart--line">
      <svg viewBox="0 0 100 40" preserveAspectRatio="none">
        <defs>
          <linearGradient id="line-fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stop-color="#2b6fc9" stop-opacity="0.35" />
            <stop offset="100%" stop-color="#2b6fc9" stop-opacity="0.02" />
          </linearGradient>
        </defs>
        <polyline :points="linePoints" fill="none" stroke="#2b6fc9" stroke-width="2" />
        <polygon :points="areaPoints" fill="url(#line-fill)" />
        <circle
          v-for="(point, idx) in linePointPairs"
          :key="idx"
          :cx="point.x"
          :cy="point.y"
          r="1.6"
          fill="#1b5ea8"
        />
      </svg>
      <div class="chart-line__labels">
        <span v-for="(label, idx) in safeLabels" :key="idx">{{ label }}</span>
      </div>
    </div>

    <div v-else class="chart chart--pie">
      <div class="chart-pie" :style="{ background: pieGradient }" />
      <ul class="chart-legend">
        <li v-for="(label, idx) in safeLabels" :key="idx">
          <span class="legend-dot" :style="{ background: pieColors[idx % pieColors.length] }" />
          {{ label }} ({{ formatValue(safeValues[idx]) }})
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    type: 'bar' | 'line' | 'pie';
    labels: any[];
    values: number[];
    title?: string;
    switchable?: boolean;
    colors?: string[];
  }>(),
  {
    labels: () => [],
    values: () => [],
    title: '',
    switchable: false,
    colors: () => []
  }
);

defineEmits<{ (e: 'update:type', value: 'bar' | 'line' | 'pie'): void }>();

const chartTypes: Array<'bar' | 'line' | 'pie'> = ['bar', 'line', 'pie'];
const safeLabels = computed(() => props.labels.map((label) => String(label)));
const safeValues = computed(() =>
  props.values.map((value) => {
    const num = typeof value === 'number' ? value : Number(value);
    return Number.isFinite(num) ? num : 0;
  })
);
const hasData = computed(() => safeValues.value.length > 0);
const maxValue = computed(() => Math.max(...safeValues.value, 1));

const formatValue = (value: number) => {
  if (Number.isInteger(value)) return value.toString();
  return value.toFixed(2);
};

const barHeight = (value: number) => {
  if (value <= 0) return 2;
  const raw = Math.round((value / maxValue.value) * 100);
  return Math.max(10, raw);
};

const linePointPairs = computed(() => {
  const step = safeValues.value.length > 1 ? 100 / (safeValues.value.length - 1) : 0;
  return safeValues.value.map((value, idx) => {
    const x = idx * step;
    const y = 40 - (value / maxValue.value) * 32 - 4;
    return { x, y };
  });
});

const linePoints = computed(() => linePointPairs.value.map((p) => `${p.x},${p.y}`).join(' '));
const areaPoints = computed(() => {
  if (!linePointPairs.value.length) return '';
  const first = linePointPairs.value[0];
  const last = linePointPairs.value[linePointPairs.value.length - 1];
  return `${first.x},40 ${linePoints.value} ${last.x},40`;
});

const defaultPieColors = ['#2b6fc9', '#5fa2f2', '#f4b256', '#ef6b6b', '#7ed4a2'];
const pieColors = computed(() =>
  props.colors && props.colors.length > 0 ? props.colors : defaultPieColors
);
const pieGradient = computed(() => {
  const total = safeValues.value.reduce((sum, value) => sum + value, 0);
  if (total === 0) {
    return 'conic-gradient(#e9eef7 0% 100%)';
  }
  let acc = 0;
  return `conic-gradient(${safeValues.value
    .map((value, idx) => {
      const start = (acc / total) * 100;
      acc += value;
      const end = (acc / total) * 100;
      return `${pieColors.value[idx % pieColors.value.length]} ${start}% ${end}%`;
    })
    .join(', ')})`;
});
</script>

<style scoped>
.chart-card {
  border-radius: 18px;
  border: 1px solid #e2e9fb;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  padding: 18px;
  box-shadow: 0 12px 30px rgba(27, 46, 88, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-title {
  font-weight: 600;
  color: #1b2b44;
  font-size: 14px;
}

.chart-switch {
  display: flex;
  gap: 6px;
}

.chart-switch__btn {
  border: 1px solid #d9e2ef;
  background: #f6f9ff;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  color: #6c7e99;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-switch__btn--active {
  background: #1b5ea8;
  color: #fff;
  border-color: transparent;
}

.chart {
  display: grid;
  gap: 12px;
}

.chart--bar {
  grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
  align-items: end;
  min-height: 190px;
}

.chart-bar {
  display: grid;
  grid-template-rows: auto 1fr auto;
  align-items: end;
  gap: 6px;
  justify-items: center;
}

.chart-bar__track {
  width: 26px;
  height: 120px;
  border-radius: 12px;
  background: #eef3fb;
  border: 1px solid #e1eaf7;
  display: flex;
  align-items: flex-end;
  padding: 4px;
}

.chart-bar__fill {
  width: 100%;
  border-radius: 10px 10px 0 0;
  background: linear-gradient(180deg, #2b6fc9, #7ab0f2);
  animation: bar-rise 0.6s ease;
}

.chart-bar__label {
  font-size: 11px;
  color: #7b8cab;
  max-width: 70px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.chart-bar__value {
  font-size: 11px;
  color: #1b2b44;
  font-weight: 600;
}

.chart--line svg {
  width: 100%;
  height: 140px;
  background: repeating-linear-gradient(
    0deg,
    #f8fbff 0px,
    #f8fbff 16px,
    #f0f5ff 16px,
    #f0f5ff 17px
  );
  border-radius: 12px;
  padding: 10px;
}

.chart-line__labels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
  font-size: 11px;
  color: #7b8cab;
}

.chart--pie {
  grid-template-columns: 160px 1fr;
  align-items: center;
}

.chart-pie {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  box-shadow: 0 10px 20px rgba(27, 46, 88, 0.12);
}

.chart-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: #6c7e99;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

@media (max-width: 720px) {
  .chart--pie {
    grid-template-columns: 1fr;
    justify-items: center;
  }
}

.chart-empty {
  padding: 16px;
  border-radius: 12px;
  background: #f5f8ff;
  color: #7b8cab;
  font-size: 12px;
  text-align: center;
}

@keyframes bar-rise {
  from {
    height: 0%;
  }
  to {
    height: 100%;
  }
}
</style>
