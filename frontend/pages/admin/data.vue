<template>
  <section class="admin-section">
    <h2 class="admin-title">{{ t('data.title') }}</h2>

    <div v-if="rows.length" class="admin-toolbar">
      <div class="admin-tabs">
        <span
          v-for="sheet in sheetOptions"
          :key="sheet.value"
          class="admin-tab"
          :class="activeSheet === sheet.value ? 'admin-tab--active' : ''"
          @click="switchSheet(sheet.value)"
        >
          {{ sheet.label }}
        </span>
      </div>
      <BaseInput v-model="keyword" :placeholder="t('data.search')" class="admin-search" />
    </div>

    <div class="admin-card">
      <div v-if="rows.length === 0" class="admin-empty">
        {{ t('common.noData') }}
    </div>
      <div v-else>
        <table class="admin-table">
          <thead>
            <tr>
              <th v-for="col in columns" :key="col.key">{{ col.label }}</th>
              <th>{{ t('users.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in rows" :key="index">
              <td v-for="col in columns" :key="col.key">{{ row[col.key] }}</td>
              <td>
                <div class="admin-actions">
                  <button class="icon-btn" :title="t('common.edit')" @click="openEdit(row)">
                    ✎
                  </button>
                  <button
                    class="icon-btn icon-btn--danger"
                    :title="t('common.delete')"
                    @click="openDelete(row)"
                  >
                    🗑
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="data-table-footer">
          <button
            class="icon-btn icon-btn--primary"
            :title="t('data.create')"
            @click="openCreate"
          >
            +
          </button>
          <div class="pager">
            <span>{{ t('common.page') }} {{ page }} / {{ totalPages }}</span>
            <div class="pager-actions">
              <select v-model.number="pageSize" class="pager-select" @change="changePageSize">
                <option v-for="size in pageSizes" :key="size" :value="size">
                  {{ size }}
                </option>
              </select>
              <button class="icon-btn" :disabled="page === 1" @click="prevPage">‹</button>
              <button class="icon-btn" :disabled="page === totalPages" @click="nextPage">
                ›
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="rows.length" class="admin-footer-actions">
      <BaseButton variant="outline" @click="openExport">
        {{ t('data.export') }}
      </BaseButton>
      <BaseButton variant="danger" @click="clearAll">
        {{ t('data.clearAll') }}
      </BaseButton>
    </div>

    <div v-if="showEditModal" class="admin-modal">
      <div class="admin-modal__card">
        <div class="admin-modal__header">
          <h3 class="admin-modal__title">
            {{ isCreateMode ? t('data.create') : t('data.edit') }}
          </h3>
          <button class="admin-modal__close" @click="closeEdit">×</button>
        </div>
        <div class="admin-form-grid">
          <BaseInput
            v-for="field in formFields"
            :key="field.key"
            v-model="editForm[field.key]"
            :label="field.label"
            :readonly="field.readonly"
          />
        </div>
        <div class="admin-footer-actions">
          <BaseButton variant="outline" @click="closeEdit">
            {{ t('common.cancel') }}
          </BaseButton>
          <BaseButton :disabled="isSaving" @click="saveEdit">
            {{ t('common.save') }}
          </BaseButton>
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="admin-modal">
      <div class="admin-modal__card" style="max-width: min(520px, 90vw)">
        <div class="admin-modal__header">
          <h3 class="admin-modal__title">{{ t('common.delete') }}</h3>
          <button class="admin-modal__close" @click="closeDelete">×</button>
        </div>
        <p class="admin-modal__subtitle">{{ t('data.deleteConfirm') }}</p>
        <div class="admin-footer-actions">
          <BaseButton variant="outline" @click="closeDelete">
            {{ t('common.cancel') }}
          </BaseButton>
          <BaseButton variant="danger" :disabled="isDeleting" @click="confirmDelete">
            {{ t('common.delete') }}
          </BaseButton>
        </div>
      </div>
    </div>

    <div v-if="showExportModal" class="admin-modal">
      <div class="admin-modal__card" style="max-width: min(520px, 90vw)">
        <div class="admin-modal__header">
          <h3 class="admin-modal__title">{{ t('data.export') }}</h3>
          <button class="admin-modal__close" @click="closeExport">×</button>
        </div>
        <div class="admin-form-grid admin-form-grid--single">
          <BaseInput v-model="exportName" :label="t('data.exportName')" />
          <label class="admin-checkbox">
            <input v-model="exportAll" type="checkbox" />
            <span>{{ t('data.exportAll') }}</span>
          </label>
        </div>
        <div class="admin-footer-actions">
          <BaseButton variant="outline" @click="closeExport">
            {{ t('common.cancel') }}
          </BaseButton>
          <BaseButton :disabled="isExporting" @click="exportSheet">
            {{ t('data.export') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import {
  clearData,
  createDataItem,
  deleteDataItem,
  exportAllData,
  exportDataSheet,
  listDataItems,
  updateDataItem
} from '@/services/api/admin';
import { useI18n } from '@/composables/useI18n';
import { useToast } from '@/composables/useToast';

definePageMeta({
  layout: 'admin'
});

const { t, locale } = useI18n();
const { push } = useToast();

const keyword = ref('');
const activeSheet = ref('Student');
const rows = ref<any[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const pageSizes = [10, 20, 50, 100, 200];
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const showExportModal = ref(false);
const isSaving = ref(false);
const isDeleting = ref(false);
const isExporting = ref(false);
const isCreateMode = ref(false);
const exportAll = ref(false);
const exportName = ref('');
const editForm = reactive<Record<string, any>>({});
const editId = ref<number | null>(null);
const deleteId = ref<number | null>(null);
const sheetOptions = computed(() => [
  { value: 'Student', label: t('data.sheetStudent') },
  { value: 'Course', label: t('data.sheetCourse') },
  { value: 'Lecturer', label: t('data.sheetLecturer') },
  { value: 'Academic', label: t('data.sheetAcademic') }
]);

const columns = computed(() => {
  const map: Record<string, { key: string; label: string }[]> = {
    Student: [
      { key: 'mssv', label: t('data.columns.mssv') },
      { key: 'hoTen', label: t('data.columns.hoTen') },
      { key: 'ngaySinh', label: t('data.columns.ngaySinh') },
      { key: 'gioiTinh', label: t('data.columns.gioiTinh') },
      { key: 'khoa', label: t('data.columns.khoa') },
      { key: 'namNhapHoc', label: t('data.columns.namNhapHoc') },
      { key: 'trangThai', label: t('data.columns.trangThai') },
      { key: 'gpa10', label: t('data.columns.gpa10') },
      { key: 'gpa4', label: t('data.columns.gpa4') }
    ],
    Course: [
      { key: 'maHocPhan', label: t('data.columns.maHocPhan') },
      { key: 'tenMonHoc', label: t('data.columns.tenMonHoc') },
      { key: 'soTinChi', label: t('data.columns.soTinChi') }
    ],
    Lecturer: [
      { key: 'maGiangVien', label: t('data.columns.maGiangVien') },
      { key: 'hoTen', label: t('data.columns.hoTen') },
      { key: 'chucDanh', label: t('data.columns.chucDanh') },
      { key: 'khoa', label: t('data.columns.khoa') }
    ],
    Academic: [
      { key: 'recordId', label: t('data.columns.recordId') },
      { key: 'maHocPhan', label: t('data.columns.maHocPhan') },
      { key: 'hocKy', label: t('data.columns.hocKy') },
      { key: 'namHoc', label: t('data.columns.namHoc') },
      { key: 'diemTongKet', label: t('data.columns.diemTongKet') },
      { key: 'ketQua', label: t('data.columns.ketQua') }
    ]
  };
  return map[activeSheet.value] || map.Student;
});

const editFields = computed(() => {
  const map: Record<string, { key: string; label: string; readonly?: boolean }[]> = {
    Student: [
      { key: 'mssv', label: t('data.columns.mssv'), readonly: true },
      { key: 'hoTen', label: t('data.columns.hoTen') },
      { key: 'ngaySinh', label: t('data.columns.ngaySinh') },
      { key: 'gioiTinh', label: t('data.columns.gioiTinh') },
      { key: 'queQuan', label: t('data.columns.queQuan') },
      { key: 'lop', label: t('data.columns.lop') },
      { key: 'khoa', label: t('data.columns.khoa') },
      { key: 'namNhapHoc', label: t('data.columns.namNhapHoc') },
      { key: 'trangThai', label: t('data.columns.trangThai') },
      { key: 'gpa10', label: t('data.columns.gpa10') },
      { key: 'gpa4', label: t('data.columns.gpa4') }
    ],
    Course: [
      { key: 'maHocPhan', label: t('data.columns.maHocPhan'), readonly: true },
      { key: 'tenMonHoc', label: t('data.columns.tenMonHoc') },
      { key: 'soTinChi', label: t('data.columns.soTinChi') }
    ],
    Lecturer: [
      { key: 'maGiangVien', label: t('data.columns.maGiangVien'), readonly: true },
      { key: 'hoTen', label: t('data.columns.hoTen') },
      { key: 'chucDanh', label: t('data.columns.chucDanh') },
      { key: 'khoa', label: t('data.columns.khoa') }
    ],
    Academic: [
      { key: 'recordId', label: t('data.columns.recordId'), readonly: true },
      { key: 'mssv', label: t('data.columns.mssv') },
      { key: 'maHocPhan', label: t('data.columns.maHocPhan') },
      { key: 'tenMonHoc', label: t('data.columns.tenMonHoc') },
      { key: 'soTinChi', label: t('data.columns.soTinChi') },
      { key: 'hocKy', label: t('data.columns.hocKy') },
      { key: 'namHoc', label: t('data.columns.namHoc') },
      { key: 'lopHocPhan', label: t('data.columns.lopHocPhan') },
      { key: 'giangVienPhuTrach', label: t('data.columns.giangVienPhuTrach') },
      { key: 'diemThanhPhan', label: t('data.columns.diemThanhPhan') },
      { key: 'diemTongKet', label: t('data.columns.diemTongKet') },
      { key: 'ketQua', label: t('data.columns.ketQua') }
    ]
  };
  return map[activeSheet.value] || map.Student;
});

const formFields = computed(() => {
  if (!isCreateMode.value) return editFields.value;
  return editFields.value.map((field) => ({ ...field, readonly: false }));
});

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

const loadRows = async () => {
  const skip = (page.value - 1) * pageSize.value;
  const data = await listDataItems(activeSheet.value, keyword.value, pageSize.value, skip);
  rows.value = data.items || [];
  total.value = data.total || 0;
  if (page.value > totalPages.value) {
    page.value = totalPages.value;
  }
};

const switchSheet = async (sheet: string) => {
  activeSheet.value = sheet;
  page.value = 1;
  await loadRows();
};

const nextPage = async () => {
  if (page.value < totalPages.value) {
    page.value += 1;
    await loadRows();
  }
};

const prevPage = async () => {
  if (page.value > 1) {
    page.value -= 1;
    await loadRows();
  }
};

const changePageSize = async () => {
  page.value = 1;
  await loadRows();
};

const clearAll = async () => {
  const text = window.prompt(t('data.clearConfirmPrompt'));
  if (text === null) return;
  if (text.trim().toLowerCase() !== 'delete') {
    push(t('data.clearConfirmInvalid'), 'error');
    return;
  }
  try {
    await clearData();
    push(locale.value === 'en' ? 'Data cleared.' : 'Đã xóa toàn bộ dữ liệu.', 'success');
    page.value = 1;
    await loadRows();
  } catch (error: any) {
    push(error?.data?.detail || t('common.noData'), 'error');
  }
};

const openEdit = (row: any) => {
  isCreateMode.value = false;
  editId.value = row.id;
  Object.keys(editForm).forEach((key) => delete editForm[key]);
  editFields.value.forEach((field) => {
    editForm[field.key] = row[field.key] ?? '';
  });
  showEditModal.value = true;
};

const openCreate = () => {
  isCreateMode.value = true;
  editId.value = null;
  Object.keys(editForm).forEach((key) => delete editForm[key]);
  editFields.value.forEach((field) => {
    editForm[field.key] = '';
  });
  showEditModal.value = true;
};

const closeEdit = () => {
  showEditModal.value = false;
  editId.value = null;
};

const saveEdit = async () => {
  if (isSaving.value) return;
  try {
    isSaving.value = true;
    const payload: Record<string, any> = {};
    editFields.value.forEach((field) => {
      if (isCreateMode.value || !field.readonly) {
        payload[field.key] = editForm[field.key];
      }
    });
    if (isCreateMode.value) {
      await createDataItem(activeSheet.value, payload);
      push(locale.value === 'en' ? 'Data created.' : 'Thêm dữ liệu thành công.', 'success');
    } else if (editId.value) {
      await updateDataItem(activeSheet.value, editId.value, payload);
      push(locale.value === 'en' ? 'Data updated.' : 'Cập nhật dữ liệu thành công.', 'success');
    }
    closeEdit();
    await loadRows();
  } catch (error: any) {
    push(error?.data?.detail || t('common.noData'), 'error');
  } finally {
    isSaving.value = false;
    isCreateMode.value = false;
  }
};

const openDelete = (row: any) => {
  deleteId.value = row.id;
  showDeleteModal.value = true;
};

const closeDelete = () => {
  showDeleteModal.value = false;
  deleteId.value = null;
};

const confirmDelete = async () => {
  if (!deleteId.value) return;
  if (isDeleting.value) return;
  try {
    isDeleting.value = true;
    await deleteDataItem(activeSheet.value, deleteId.value);
    push(locale.value === 'en' ? 'Deleted.' : 'Đã xóa dữ liệu.', 'success');
    closeDelete();
    await loadRows();
  } catch (error: any) {
    push(error?.data?.detail || t('common.noData'), 'error');
  } finally {
    isDeleting.value = false;
  }
};

const exportSheet = async () => {
  try {
    isExporting.value = true;
    const name = exportName.value.trim() || `neu_${activeSheet.value.toLowerCase()}_export.xlsx`;
    if (exportAll.value) {
      await exportAllData(name || 'neu_all_data_export.xlsx');
    } else {
      const search = keyword.value.trim();
      await exportDataSheet(activeSheet.value, search, name);
    }
    closeExport();
  } catch (error: any) {
    push(error?.message || t('common.noData'), 'error');
  } finally {
    isExporting.value = false;
  }
};

const openExport = () => {
  exportAll.value = false;
  exportName.value = `neu_${activeSheet.value.toLowerCase()}_export.xlsx`;
  showExportModal.value = true;
};

watch(exportAll, (value) => {
  exportName.value = value
    ? 'neu_all_data_export.xlsx'
    : `neu_${activeSheet.value.toLowerCase()}_export.xlsx`;
});

const closeExport = () => {
  showExportModal.value = false;
};

watch(keyword, async () => {
  page.value = 1;
  await loadRows();
});
onMounted(loadRows);
</script>

<style scoped>
.admin-empty {
  padding: 18px;
  border-radius: 12px;
  background: #f8fbff;
  border: 1px dashed #d6e2f2;
  color: #7b8cab;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.admin-empty__actions {
  display: flex;
  gap: 8px;
}

.data-table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  color: #7b8cab;
  font-size: 12px;
}

.pager-actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

.pager-select {
  border: 1px solid #d7e3f7;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  color: #1b2b44;
  background: #ffffff;
}
</style>
