<template>
  <section class="admin-section">
    <h2 class="admin-title">{{ t('import.title') }}</h2>

    <div class="admin-grid admin-grid--2">
      <div v-if="!file" class="admin-card">
        <div class="stat-card__label" style="font-weight: 600; color: #1b2b44">
          {{ t('import.upload') }}
        </div>
        <div class="upload-box" @click="triggerFile">
          {{ t('import.uploadHint') }}
        </div>
      </div>
      <div v-else class="admin-card">
        <div class="admin-toolbar" style="align-items: center">
          <div class="stat-card__label" style="font-weight: 600; color: #1b2b44">
            {{ t('import.fileInfo') }}
          </div>
          <BaseButton variant="outline" @click="triggerFile">
            {{ t('import.changeFile') }}
          </BaseButton>
        </div>
        <ul class="file-info">
          <li><strong>{{ t('import.fileName') }}:</strong> {{ fileInfo.name || '—' }}</li>
          <li><strong>{{ t('import.fileSize') }}:</strong> {{ fileInfo.size || '—' }}</li>
          <li><strong>{{ t('import.sheets') }}:</strong> {{ fileInfo.sheets || '—' }}</li>
        </ul>
      </div>
    </div>

    <input
      ref="fileInput"
      class="hidden-input"
      type="file"
      accept=".xlsx,.xls"
      @change="onFileChange"
    />

    <div v-if="file" class="admin-card">
      <div class="admin-toolbar">
        <div class="stat-card__label" style="font-weight: 600; color: #1b2b44">
          {{ t('import.preview') }}
        </div>
        <BaseButton variant="outline" :disabled="!canProceed" @click="goDetail">
          {{ t('import.viewDetail') }}
        </BaseButton>
      </div>
      <p v-if="errorMessage" class="import-error">{{ errorMessage }}</p>
      <template v-else>
        <div class="admin-tabs" style="margin: 12px 0">
          <span
            v-for="sheet in previewSheets"
            :key="sheet"
            class="admin-tab"
            :class="activeSheet === sheet ? 'admin-tab--active' : ''"
            @click="loadSheet(sheet)"
          >
            {{ sheetLabel(sheet) }}
          </span>
        </div>
        <table class="admin-table">
          <thead>
            <tr>
              <th v-for="col in previewColumnDefs" :key="col.key">{{ col.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in previewRows" :key="index">
              <td v-for="col in previewColumnDefs" :key="col.key">{{ row[col.key] }}</td>
            </tr>
          </tbody>
        </table>
      </template>
    </div>

    <div v-if="file" class="admin-footer-actions">
      <BaseButton variant="outline" @click="reset">{{ t('common.cancel') }}</BaseButton>
      <BaseButton :disabled="!canProceed" @click="goValidate">
        {{ t('import.next') }}
      </BaseButton>
    </div>
  </section>
</template>

<script setup lang="ts">
import { previewData } from '@/services/api/admin';
import { useImportState } from '@/composables/useImportState';
import { useI18n } from '@/composables/useI18n';

definePageMeta({
  layout: 'admin'
});

const { t } = useI18n();
const { file, preview, reset } = useImportState();
const activeSheet = ref('Student');
const previewSheets = computed(() => preview.value?.sheets || ['Student']);
const previewRows = computed(() => preview.value?.rows || []);
const errorMessage = ref('');
const canProceed = computed(() => Boolean(file.value && !errorMessage.value));
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
const previewColumnDefs = computed(() =>
  (preview.value?.columns || []).slice(0, 6).map((col) => ({
    key: col,
    label: columnLabelMap.value[col] || col
  }))
);
const fileInput = ref<HTMLInputElement | null>(null);

const fileInfo = computed(() => {
  if (!file.value || !preview.value) {
    return { name: '', size: '', sheets: '' };
  }
  const previewFile = (preview.value as any).file || {};
  const sizeBytes = previewFile.size || file.value.size || 0;
  return {
    name: previewFile.name || file.value.name,
    size: `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`,
    sheets: preview.value.sheets.map((sheet) => sheetLabel(sheet)).join(', ')
  };
});

const triggerFile = () => {
  fileInput.value?.click();
};

const loadSheet = async (sheet: string) => {
  if (!file.value) return;
  activeSheet.value = sheet;
  errorMessage.value = '';
  try {
    const response = await previewData(file.value, sheet, 5, 0, '');
    preview.value = response as any;
    activeSheet.value = (response as any).sheet || sheet;
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || t('common.noData');
    preview.value = null;
  }
};

const onFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.files || !target.files[0]) return;
  file.value = target.files[0];
  errorMessage.value = '';
  try {
    const response = await previewData(file.value, activeSheet.value, 5, 0, '');
    preview.value = response as any;
    activeSheet.value = (response as any).sheet || activeSheet.value;
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || t('common.noData');
    preview.value = null;
  }
};

const goValidate = () => navigateTo('/admin/import/validate');
const goDetail = () => navigateTo('/admin/import/detail');
</script>

<style scoped>
.upload-box {
  margin-top: 12px;
  height: 70px;
  border-radius: 12px;
  border: 1px dashed #c9d8ef;
  background: #f8fbff;
  display: grid;
  place-items: center;
  color: #7b8cab;
  font-size: 13px;
  cursor: pointer;
}

.hidden-input {
  display: none;
}

.file-info {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #6c7e99;
  font-size: 13px;
}

.file-info strong {
  color: #1b2b44;
}

.import-error {
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--color-danger);
}
</style>
