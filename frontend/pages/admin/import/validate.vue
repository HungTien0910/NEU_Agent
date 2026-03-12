<template>
  <section class="admin-section">
    <h2 class="admin-title">{{ t('import.validate') }}</h2>

    <div class="admin-card admin-card--soft">
      <div class="validate-summary">
        <div>
          <span>{{ t('import.total') }}:</span>
          <strong>{{ validation?.total || 0 }}</strong>
        </div>
        <div>
          <span>{{ t('import.valid') }}:</span>
          <strong>{{ validation?.valid || 0 }}</strong>
        </div>
        <div>
          <span>{{ t('import.error') }}:</span>
          <strong class="error">{{ validation?.errors || 0 }}</strong>
        </div>
      </div>
      <div v-if="validationDone && hasErrors" class="validate-note">
        {{ t('import.note') }}: {{ noteText }}
      </div>
      <div v-else-if="validationDone && !hasErrors" class="validate-success">
        {{ t('import.clean') }}
      </div>
    </div>

    <div v-if="validationDone && hasErrors" class="admin-card">
      <div class="stat-card__label" style="font-weight: 600; color: #1b2b44">
        {{ t('import.errors') }}
      </div>
      <p v-if="errorMessage" class="import-error">{{ errorMessage }}</p>
      <table class="admin-table" style="margin-top: 10px">
        <thead>
          <tr>
            <th>{{ t('common.sheet') }}</th>
            <th>{{ t('common.row') }}</th>
            <th>{{ t('common.column') }}</th>
            <th>{{ t('common.type') }}</th>
            <th>{{ t('common.value') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in validation?.details || []" :key="row.sheet + row.row">
            <td>{{ sheetLabel(row.sheet) }}</td>
            <td>{{ row.row }}</td>
            <td>{{ columnLabel(row.column) }}</td>
            <td>{{ typeLabel(row.type) }}</td>
            <td>{{ row.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="admin-footer-actions">
      <BaseButton variant="outline" @click="goBack">
        {{ t('common.back') }}
      </BaseButton>
      <BaseButton :disabled="!canImport || isImporting" @click="doImport">
        {{ t('import.importNow') }}
      </BaseButton>
    </div>

    <div v-if="isImporting" class="admin-modal">
      <div class="admin-modal__card" style="max-width: min(520px, 90vw)">
        <div class="admin-modal__header">
          <h3 class="admin-modal__title">{{ t('import.progress') }}</h3>
        </div>
        <div class="import-progress">
          <div class="import-progress__row">
            <div class="import-progress__inline">
              <span>{{ progress.step }}</span>
              <span class="import-progress__spinner" aria-hidden="true" />
            </div>
            <strong>{{ progress.percent }}%</strong>
          </div>
          <div class="import-progress__bar">
            <span :style="{ width: `${progress.percent}%` }" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { getImportProgress, importData, validateData } from '@/services/api/admin';
import { useImportState } from '@/composables/useImportState';
import { useI18n } from '@/composables/useI18n';
import { useToast } from '@/composables/useToast';

definePageMeta({
  layout: 'admin'
});

const { t, locale } = useI18n();
const { push } = useToast();
const { file, validation, reset } = useImportState();
const errorMessage = ref('');
const isImporting = ref(false);
const hasErrors = computed(() => (validation.value?.errors || 0) > 0 || !!errorMessage.value);
const validationDone = ref(false);
const progress = reactive({
  percent: 0,
  step: '',
  status: 'idle',
  error: ''
});
const importJobId = ref<string | null>(null);
let progressTimer: ReturnType<typeof setTimeout> | null = null;
const canImport = computed(() => Boolean(validation.value && !errorMessage.value));
const sheetLabelMap = computed(() => ({
  Student: t('data.sheetStudent'),
  Course: t('data.sheetCourse'),
  Lecturer: t('data.sheetLecturer'),
  Academic: t('data.sheetAcademic')
}));
const sheetLabel = (sheet: string) => sheetLabelMap.value[sheet] || sheet;
const columnLabelMap = computed(() => ({
  MSSV: t('data.columns.mssv'),
  HoTen: t('data.columns.hoTen'),
  NgaySinh: t('data.columns.ngaySinh'),
  GioiTinh: t('data.columns.gioiTinh'),
  QueQuan: t('data.columns.queQuan'),
  Lop: t('data.columns.lop'),
  Khoa: t('data.columns.khoa'),
  NamNhapHoc: t('data.columns.namNhapHoc'),
  TrangThai: t('data.columns.trangThai'),
  GPA_Thang10: t('data.columns.gpa10'),
  MaHocPhan: t('data.columns.maHocPhan'),
  TenMonHoc: t('data.columns.tenMonHoc'),
  SoTinChi: t('data.columns.soTinChi'),
  MaGiangVien: t('data.columns.maGiangVien'),
  ChucDanh: t('data.columns.chucDanh'),
  RecordID: t('data.columns.recordId'),
  HocKy: t('data.columns.hocKy'),
  NamHoc: t('data.columns.namHoc'),
  DiemTongKet: t('data.columns.diemTongKet'),
  KetQua: t('data.columns.ketQua')
}));
const columnLabel = (column: string) =>
  columnLabelMap.value[column] || column;
const typeLabel = (type: string) => {
  if (locale.value === 'en' && type === 'NULL') {
    return 'NULL';
  }
  return type;
};
const noteText = computed(() => {
  if (!validation.value?.note) return t('common.noData');
  if (validation.value.note === 'Thiếu khóa chính (PK) ở một số dòng') {
    return t('import.noteMissingPk');
  }
  return validation.value.note;
});

const loadValidation = async () => {
  if (!file.value) {
    await navigateTo('/admin/import');
    return;
  }
  validationDone.value = false;
  errorMessage.value = '';
  try {
    validation.value = await validateData(file.value);
    validationDone.value = true;
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || t('common.noData');
    validation.value = null;
    validationDone.value = true;
  }
};

const goBack = () => navigateTo('/admin/import');

const stopPolling = () => {
  if (progressTimer) {
    clearTimeout(progressTimer);
    progressTimer = null;
  }
};

const pollProgress = async () => {
  if (!importJobId.value) return;
  try {
    const data: any = await getImportProgress(importJobId.value);
    progress.percent = data.percent || 0;
    progress.step = data.step || '';
    progress.status = data.status || 'running';
    progress.error = data.error || '';

    if (progress.status === 'done') {
      push(locale.value === 'en' ? 'Import successful.' : 'Import thành công.', 'success');
      reset();
      isImporting.value = false;
      stopPolling();
      await navigateTo('/admin/data');
      return;
    }
    if (progress.status === 'error') {
      push(progress.error || t('common.noData'), 'error');
      isImporting.value = false;
      stopPolling();
      return;
    }
  } catch {
    // keep polling, network hiccup
  }
  progressTimer = setTimeout(pollProgress, 1000);
};

const doImport = async () => {
  if (isImporting.value) return;
  if (!file.value) {
    push(locale.value === 'en' ? 'Import file not found.' : 'Không tìm thấy file import.', 'error');
    await navigateTo('/admin/import');
    return;
  }
  try {
    isImporting.value = true;
    progress.percent = 0;
    progress.step = locale.value === 'en' ? 'Starting import...' : 'Bắt đầu import...';
    progress.status = 'running';
    const response: any = await importData(file.value);
    importJobId.value = response.job_id;
    push(locale.value === 'en' ? 'Import started.' : 'Đã bắt đầu import.', 'info');
    stopPolling();
    pollProgress();
  } catch (error: any) {
    push(error?.data?.detail || t('common.noData'), 'error');
    isImporting.value = false;
  } finally {
    // handled by polling
  }
};

onMounted(loadValidation);

onBeforeUnmount(() => {
  stopPolling();
});
</script>

<style scoped>
.validate-summary {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  font-size: 14px;
  color: #6c7e99;
}

.validate-summary strong {
  margin-left: 8px;
  color: #1b2b44;
}

.validate-summary .error {
  color: #d32b2b;
}

.validate-note {
  margin-top: 10px;
  font-size: 13px;
  color: #7b8cab;
}

.validate-success {
  margin-top: 10px;
  font-size: 13px;
  color: #2a5fa7;
  font-weight: 600;
}

.import-error {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--color-danger);
}

.import-progress {
  padding: 8px 0 2px;
}

.import-progress__row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #4a5c7a;
  margin-bottom: 8px;
}

.import-progress__inline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.import-progress__spinner {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  border: 3px solid #d6e2f2;
  border-top-color: #2a5fa7;
  animation: spin 0.9s linear infinite;
  margin: 2px 0 10px;
}

.import-progress__bar {
  height: 8px;
  background: #e7eef9;
  border-radius: 999px;
  overflow: hidden;
}

.import-progress__bar span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #2a5fa7, #5a8fd6);
  border-radius: 999px;
  transition: width 0.3s ease;
}

.import-progress__step {
  margin-top: 8px;
  font-size: 12px;
  color: #7b8cab;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
