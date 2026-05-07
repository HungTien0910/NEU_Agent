<template>
  <div class="admission-widget">
    <button class="admission-widget__fab" @click="open = !open" aria-label="Chatbot tuyển sinh">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 3a7 7 0 0 0-7 7v4a3 3 0 0 0 3 3h1l2.2 2.2a1 1 0 0 0 1.6-.8V17h3a3 3 0 0 0 3-3v-4a7 7 0 0 0-7-7Z" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="9.3" cy="10.5" r="1.1" fill="currentColor"/>
        <circle cx="14.7" cy="10.5" r="1.1" fill="currentColor"/>
        <path d="M9 14c.8.7 1.8 1 3 1s2.2-.3 3-1" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
      </svg>
    </button>

    <div v-if="open" class="admission-widget__panel">
      <div class="admission-widget__head">
        <strong>Chat tư vấn tuyển sinh</strong>
      </div>
      <div class="admission-widget__messages">
        <div
          v-for="(item, idx) in messages"
          :key="idx"
          class="admission-widget__bubble"
          :class="item.role === 'user' ? 'is-user' : 'is-bot'"
        >
          {{ item.text }}
        </div>
        <div v-if="loading" class="admission-widget__bubble is-bot admission-widget__typing">
          <span />
          <span />
          <span />
        </div>
      </div>
      <form class="admission-widget__input" @submit.prevent="ask">
        <input
          v-model="question"
          placeholder="Nhập câu hỏi tuyển sinh..."
          :disabled="loading"
        />
        <button type="submit" :disabled="!question.trim() || loading">
          {{ loading ? '...' : 'Gửi' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { queryAdmission } from '@/services/api/publicAdmission';

type Msg = { role: 'user' | 'bot'; text: string };

const open = ref(false);
const question = ref('');
const loading = ref(false);
const messages = ref<Msg[]>([
  {
    role: 'bot',
    text: 'Chào bạn, mình có thể tư vấn thông tin tuyển sinh dựa trên tài liệu đã import.'
  }
]);

const ask = async () => {
  const q = question.value.trim();
  if (!q || loading.value) return;
  messages.value.push({ role: 'user', text: q });
  question.value = '';
  loading.value = true;
  try {
    const res = await queryAdmission(q, 'vi');
    messages.value.push({ role: 'bot', text: res.answer });
  } catch (error: any) {
    messages.value.push({
      role: 'bot',
      text: error?.data?.detail || 'Hiện chưa trả lời được. Vui lòng thử lại.'
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.admission-widget {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 12;
}

.admission-widget__fab {
  border: none;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(145deg, #0f5ea8, #2a78c9);
  color: #fff;
  display: grid;
  place-items: center;
  box-shadow: 0 12px 28px rgba(17, 56, 102, 0.4);
  cursor: pointer;
}

.admission-widget__fab svg {
  width: 28px;
  height: 28px;
}

.admission-widget__panel {
  width: min(360px, calc(100vw - 24px));
  height: 460px;
  margin-top: 10px;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 18px 48px rgba(17, 34, 68, 0.28);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admission-widget__head {
  padding: 12px;
  background: #f0f6ff;
  border-bottom: 1px solid #dbe7f8;
}

.admission-widget__messages {
  padding: 12px;
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.admission-widget__bubble {
  max-width: 88%;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 13px;
  line-height: 1.35;
  white-space: pre-wrap;
}

.admission-widget__bubble.is-user {
  align-self: flex-end;
  background: #0f5ea8;
  color: #fff;
}

.admission-widget__bubble.is-bot {
  align-self: flex-start;
  background: #f3f6fb;
  color: #20324f;
}

.admission-widget__typing {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 44px;
}

.admission-widget__typing span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #7d90af;
  animation: admission-dot 0.9s ease-in-out infinite;
}

.admission-widget__typing span:nth-child(2) {
  animation-delay: 0.15s;
}

.admission-widget__typing span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes admission-dot {
  0%,
  80%,
  100% {
    transform: scale(0.7);
    opacity: 0.45;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.admission-widget__input {
  display: flex;
  gap: 8px;
  padding: 10px;
  border-top: 1px solid #dbe7f8;
}

.admission-widget__input input {
  flex: 1;
  border: 1px solid #c5d5ea;
  border-radius: 10px;
  padding: 8px 10px;
}

.admission-widget__input button {
  border: none;
  border-radius: 10px;
  background: #0f5ea8;
  color: #fff;
  padding: 8px 12px;
  cursor: pointer;
}
</style>
