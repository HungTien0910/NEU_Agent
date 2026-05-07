import { useApiFetch } from '@/services/api/client';

export type OverviewResponse = {
  stats: {
    total_users: number;
    active_users: number;
    locked_users: number;
    admin_users: number;
  };
  activities: { title: string; date: string }[];
  quick_stats: {
    password_reset_requests: number;
    new_users_this_week: number;
    status_changes: number;
  };
  weekly: {
    labels: string[];
    created: number[];
    updated: number[];
    deleted: number[];
    total: number[];
  };
};

export type UserListItem = {
  id: number;
  username: string;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  title?: string | null;
  role: string;
  is_active: boolean;
};

export type UserListResponse = {
  items: UserListItem[];
  total: number;
  limit: number;
  skip: number;
};

export type UserDetail = {
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

export type UserCreate = Omit<UserDetail, 'id'> & { password: string };
export type UserUpdate = Partial<UserCreate>;

export type LogItem = {
  id: number;
  time: string;
  actor: string;
  action: string;
  target: string;
  detail: string;
};

export type LogListResponse = {
  total: number;
  items: LogItem[];
};

export type SettingsPayload = {
  language: string;
  timezone: string;
  date_format: string;
  email_notifications: boolean;
  error_notifications: boolean;
  password_rotation_days: number;
  mfa_enabled: boolean;
};

export type DataItemsResponse = {
  sheet: string;
  items: any[];
  total: number;
  limit: number;
  skip: number;
};

export const getOverview = async () => {
  const api = useApiFetch();
  return await api<OverviewResponse>('/admin/overview');
};

export const listUsers = async (search = '', limit = 20, skip = 0) => {
  const api = useApiFetch();
  return await api<UserListResponse>('/users', {
    params: { search: search || undefined, limit, skip }
  });
};

export const getUser = async (id: number) => {
  const api = useApiFetch();
  return await api<UserDetail>(`/users/${id}`);
};

export const getUserByUsername = async (username: string) => {
  const api = useApiFetch();
  return await api<UserDetail>(`/users/by-username/${username}`);
};

export const createUser = async (payload: UserCreate) => {
  const api = useApiFetch();
  return await api<UserDetail>('/users', { method: 'POST', body: payload });
};

export const updateUser = async (id: number, payload: UserUpdate) => {
  const api = useApiFetch();
  return await api<UserDetail>(`/users/${id}`, { method: 'PUT', body: payload });
};

export const deleteUser = async (id: number) => {
  const api = useApiFetch();
  await api(`/users/${id}`, { method: 'DELETE' });
};

export const listLogs = async (
  filters: Record<string, string>,
  limit = 20,
  skip = 0
) => {
  const api = useApiFetch();
  const params: Record<string, string> = {};
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params[key] = value;
  });
  return await api<LogListResponse>('/logs', { params: { ...params, limit, skip } });
};

export const getSettings = async () => {
  const api = useApiFetch();
  return await api<SettingsPayload>('/settings');
};

export const updateSettings = async (payload: SettingsPayload) => {
  const api = useApiFetch();
  return await api<SettingsPayload>('/settings', { method: 'PUT', body: payload });
};

export const previewData = async (
  file: File,
  sheet = 'Student',
  limit = 5,
  skip = 0,
  search = ''
) => {
  const api = useApiFetch();
  const form = new FormData();
  form.append('file', file);
  return await api('/data/preview', {
    method: 'POST',
    params: { sheet, limit, skip, search: search || undefined },
    body: form
  });
};

export const validateData = async (file: File) => {
  const api = useApiFetch();
  const form = new FormData();
  form.append('file', file);
  return await api('/data/validate', { method: 'POST', body: form });
};

export const importData = async (file: File) => {
  const api = useApiFetch();
  const form = new FormData();
  form.append('file', file);
  return await api('/data/import', { method: 'POST', body: form });
};

export const importAdmissionPdf = async (file: File) => {
  const api = useApiFetch();
  const form = new FormData();
  form.append('file', file);
  return await api('/data/import-pdf', { method: 'POST', body: form });
};

export const getImportProgress = async (jobId: string) => {
  const api = useApiFetch();
  return await api('/data/import/progress', { params: { job_id: jobId } });
};

export const listDataItems = async (
  sheet = 'Student',
  search = '',
  limit = 50,
  skip = 0
) => {
  const api = useApiFetch();
  return await api<DataItemsResponse>('/data/items', {
    params: { sheet, search: search || undefined, limit, skip }
  });
};

export const updateDataItem = async (
  sheet: string,
  itemId: number,
  payload: Record<string, any>
) => {
  const api = useApiFetch();
  return await api(`/data/items/${sheet}/${itemId}`, { method: 'PUT', body: payload });
};

export const createDataItem = async (sheet: string, payload: Record<string, any>) => {
  const api = useApiFetch();
  return await api(`/data/items/${sheet}`, { method: 'POST', body: payload });
};

export const deleteDataItem = async (sheet: string, itemId: number) => {
  const api = useApiFetch();
  return await api(`/data/items/${sheet}/${itemId}`, { method: 'DELETE' });
};

export const exportDataSheet = async (
  sheet: string,
  search = '',
  fileName?: string
) => {
  const config = useRuntimeConfig();
  const params = new URLSearchParams();
  params.set('sheet', sheet);
  if (search) params.set('search', search);
  const response = await fetch(`${config.public.apiBase}/data/export?${params.toString()}`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.detail || 'Export failed');
  }
  const blob = await response.blob();
  const name = fileName || `neu_${sheet.toLowerCase()}_export.xlsx`;

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const exportAllData = async (fileName?: string) => {
  const config = useRuntimeConfig();
  const response = await fetch(`${config.public.apiBase}/data/export-all`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.detail || 'Export failed');
  }
  const blob = await response.blob();
  const name = fileName || 'neu_all_data_export.xlsx';
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const clearData = async () => {
  const api = useApiFetch();
  return await api('/data/clear', { method: 'POST' });
};
