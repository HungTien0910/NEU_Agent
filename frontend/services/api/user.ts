import { useApiFetch } from '@/services/api/client';

export type QueryPayload = {
  username: string;
  question: string;
  language?: string;
};

export type QueryResponse = {
  id: number;
  columns: string[];
  rows: Array<Array<any>>;
  chart?: { type: string; labels: any[]; values: any[] } | null;
  summary: string;
  cypher?: string | null;
  is_stat?: boolean | null;
};

export type HistoryItem = {
  id: number;
  question: string;
  summary?: string | null;
  chart_type?: string | null;
  is_data?: boolean;
  created_at: string;
};

export type HistoryListResponse = {
  total: number;
  items: HistoryItem[];
};

export type HistoryDetail = {
  id: number;
  question: string;
  summary?: string | null;
  columns: string[];
  rows: Array<Array<any>>;
  chart?: { type: string; labels: any[]; values: any[] } | null;
  cypher?: string | null;
  created_at: string;
};

export type UserProfile = {
  id: number;
  username: string;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  title?: string | null;
  birth_date?: string | null;
  gender?: string | null;
  address?: string | null;
  department?: string | null;
  role: string;
  permissions: string[];
  is_active: boolean;
};

export const queryData = async (payload: QueryPayload) => {
  const api = useApiFetch();
  return await api<QueryResponse>('/query', { method: 'POST', body: payload });
};

export const streamQuery = async (
  payload: QueryPayload,
  handlers: {
    onSummary?: (text: string) => void;
    onResult?: (data: QueryResponse) => void;
    onError?: (detail: string) => void;
  }
) => {
  const config = useRuntimeConfig();
  const response = await fetch(`${config.public.apiBase}/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok || !response.body) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.detail || 'Stream failed');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf('\n\n');
    while (boundary !== -1) {
      const raw = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const lines = raw.split('\n');
      let event = 'message';
      let data = '';
      for (const line of lines) {
        if (line.startsWith('event:')) {
          event = line.replace('event:', '').trim();
        }
        if (line.startsWith('data:')) {
          data += line.replace('data:', '').trim();
        }
      }
      if (data) {
        try {
          const json = JSON.parse(data);
          if (event === 'summary') {
            handlers.onSummary?.(json.text || '');
          } else if (event === 'result') {
            handlers.onResult?.(json as QueryResponse);
          } else if (event === 'error') {
            handlers.onError?.(json.detail || 'Stream error');
          }
        } catch {
          handlers.onError?.('Stream parse error');
        }
      }
      boundary = buffer.indexOf('\n\n');
    }
  }
};

export const listHistory = async (username: string, limit = 20, skip = 0) => {
  const api = useApiFetch();
  return await api<HistoryListResponse>('/history', {
    params: { username, limit, skip }
  });
};

export const getHistory = async (username: string, id: number) => {
  const api = useApiFetch();
  return await api<HistoryDetail>(`/history/${id}`, {
    params: { username }
  });
};

export const getUserProfile = async (username: string) => {
  const api = useApiFetch();
  return await api<UserProfile>(`/users/by-username/${username}`);
};

export const exportExcel = async (payload: {
  username: string;
  history_id?: number;
  columns?: string[];
  rows?: Array<Array<any>>;
  file_name?: string;
}) => {
  const config = useRuntimeConfig();
  const response = await fetch(`${config.public.apiBase}/export/excel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.detail || 'Export failed');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = payload.file_name || 'neu_export.xlsx';
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
