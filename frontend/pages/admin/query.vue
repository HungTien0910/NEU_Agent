<template>
  <section class="admin-section">
    <div>
      <h2 class="admin-title">{{ t('query.title') }}</h2>
      <p class="admin-subtitle">{{ t('user.askSubtitle') }}</p>
    </div>

    <div class="admin-card chat-card">
      <div class="chat-messages">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="chat-bubble"
          :class="msg.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--bot'"
        >
          <p v-if="msg.text" class="chat-text">{{ msg.text }}</p>

          <div v-if="msg.summary" class="chat-summary">{{ msg.summary }}</div>

          <div v-if="msg.columns?.length" class="chat-result">
            <div class="result-header">
              <span>{{ t('user.result') }}</span>
            </div>
            <table class="admin-table">
              <thead>
                <tr>
                  <th v-for="col in msg.columns" :key="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in msg.rows" :key="idx">
                  <td v-for="(cell, cIdx) in row" :key="cIdx">{{ cell }}</td>
                </tr>
              </tbody>
            </table>
            <div v-if="canExport && msg.isStat" class="export-row">
              <BaseButton variant="outline" @click="exportResult(msg)">
                {{ t('user.export') }}
              </BaseButton>
            </div>
          </div>

          <ChartDisplay
            v-if="msg.chart"
            v-model:type="msg.chart.type"
            :labels="msg.chart.labels"
            :values="msg.chart.values"
            :title="t('user.chart')"
            switchable
          />

          <div v-if="msg.loading" class="chat-loading">
            <span class="chat-dot" />
            <span class="chat-dot" />
            <span class="chat-dot" />
          </div>
        </div>
      </div>

      <div class="chat-input">
        <textarea
          v-model="input"
          rows="1"
          :placeholder="t('query.placeholder')"
          @keydown="handleKeydown"
        />
        <button
          class="send-btn"
          :disabled="!input.trim() || loading"
          :aria-label="t('common.send')"
          @click="send"
        >
          <svg class="send-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M2.2 11.5l19-8.1c.6-.3 1.2.3.9.9l-8.1 19c-.2.6-1 .6-1.3.1l-3-6.1-6.1-3c-.5-.3-.5-1.1.1-1.3z"
              fill="currentColor"
            />
            <path
              d="M11.3 12.7l7.5-6.2-6.2 7.5-3.1-1.6 1.8-1.7z"
              fill="rgba(0,0,0,0.25)"
            />
          </svg>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '@/composables/useI18n';
import { useCurrentUser } from '@/composables/useCurrentUser';
import { exportExcel, streamQuery } from '@/services/api/user';
import ChartDisplay from '@/components/blocks/ChartDisplay.vue';

definePageMeta({
  layout: 'admin'
});

const { t, locale } = useI18n();
const { user, load: loadUser } = useCurrentUser();

type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  text?: string;
  summary?: string;
  columns?: string[];
  rows?: Array<Array<any>>;
  chart?: { type: 'bar' | 'line' | 'pie'; labels: any[]; values: number[] };
  isStat?: boolean;
  loading?: boolean;
};

const canExport = computed(() => {
  if (user.value?.role === 'admin') return true;
  return (user.value?.permissions?.length || 0) > 0;
});
const input = ref('');
const messages = ref<ChatMessage[]>([]);
const loading = ref(false);

const send = async () => {
  if (!input.value.trim() || !user.value?.username) return;
  const question = input.value.trim();
  input.value = '';
  const userMsg: ChatMessage = {
    id: `${Date.now()}-u`,
    role: 'user',
    text: question
  };
  const botId = `${Date.now()}-b`;
  const botMsg: ChatMessage = {
    id: botId,
    role: 'assistant',
    loading: true
  };
  messages.value.push(userMsg, botMsg);
  loading.value = true;

  try {
    await streamQuery(
      {
        username: user.value.username,
        question,
        language: locale.value
      },
      {
        onSummary: (text) => {
          const target = messages.value.find((msg) => msg.id === botId);
          if (!target) return;
          if (target.loading) target.loading = false;
          target.summary = target.summary ? `${target.summary} ${text}` : text;
        },
        onResult: (response) => {
          const target = messages.value.find((msg) => msg.id === botId);
          if (!target) return;
          Object.assign(target, {
            loading: false,
            summary: response.summary || target.summary,
            columns: response.columns,
            rows: response.rows,
            isStat: response.is_stat ?? false,
            chart: response.chart
              ? { ...response.chart, type: response.chart.type as any }
              : undefined
          });
        },
        onError: (detail) => {
          const target = messages.value.find((msg) => msg.id === botId);
          if (!target) return;
          Object.assign(target, {
            loading: false,
            summary: detail || t('common.noData')
          });
        }
      }
    );
  } finally {
    loading.value = false;
  }
};

const exportResult = async (item: ChatMessage) => {
  if (!item.columns?.length || !item.rows?.length || !user.value?.username) return;
  await exportExcel({
    username: user.value.username,
    columns: item.columns,
    rows: item.rows,
    file_name: 'neu_query.xlsx'
  });
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (!loading.value) {
      send();
    }
  }
};

onMounted(() => {
  loadUser();
});
</script>
