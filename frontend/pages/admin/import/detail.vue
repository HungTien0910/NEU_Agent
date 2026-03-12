<template>
  <section class="admin-section">
    <h2 class="admin-title">{{ t('import.viewDetail') }}</h2>

    <div class="admin-toolbar">
      <div class="admin-tabs">
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
      <BaseInput v-model="keyword" :placeholder="t('common.search')" class="admin-search" />
    </div>

    <div class="admin-card">
      <table class="admin-table" style="margin-top: 10px">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody v-if="(preview?.rows || []).length">
          <tr v-for="(row, index) in preview?.rows || []" :key="index">
            <td v-for="col in columns" :key="col.key">{{ row[col.key] }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="showEmpty" class="admin-empty">
        {{ emptyMessage }}
      </div>
      <div class="pager">
        <span>{{ t('common.page') }} {{ page }} / {{ totalPages }}</span>
        <div class="pager-actions">
          <select v-model.number="pageSize" class="pager-select" @change="changePageSize">
            <option v-for="size in pageSizes" :key="size" :value="size">
              {{ size }}
            </option>
          </select>
          <button class="icon-btn" :disabled="page === 1" @click="prevPage">‹</button>
          <button class="icon-btn" :disabled="page === totalPages" @click="nextPage">›</button>
        </div>
      </div>
    </div>

    <div class="admin-footer-actions">
      <BaseButton variant="outline" @click="goBack">
        {{ t('common.back') }}
      </BaseButton>
      <BaseButton @click="goNext">{{ t('import.next') }}</BaseButton>
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
const keyword = ref('');
const { file, preview } = useImportState();
const activeSheet = ref('Student');
const page = ref(1);
const pageSize = ref(10);
const pageSizes = [10, 20, 50, 100, 200];
let searchTimer: ReturnType<typeof setTimeout> | null = null;
const previewSheets = computed(() => preview.value?.sheets || ['Student']);
const sheetLabelMap = computed(() => ({
  Student: t('data.sheetStudent'),
  Course: t('data.sheetCourse'),
  Lecturer: t('data.sheetLecturer'),
  Academic: t('data.sheetAcademic')
}));
const sheetLabel = (sheet: string) => sheetLabelMap.value[sheet] || sheet;
const totalPages = computed(() => preview.value?.total_pages || 1);
const columns = computed(() => {
  const map: Record<string, { key: string; label: string }[]> = {
    Student: [
      { key: 'MSSV', label: t('data.columns.mssv') },
      { key: 'HoTen', label: t('data.columns.hoTen') },
      { key: 'NgaySinh', label: t('data.columns.ngaySinh') },
      { key: 'GioiTinh', label: t('data.columns.gioiTinh') },
      { key: 'QueQuan', label: t('data.columns.queQuan') },
      { key: 'Lop', label: t('data.columns.lop') },
      { key: 'Khoa', label: t('data.columns.khoa') },
      { key: 'NamNhapHoc', label: t('data.columns.namNhapHoc') },
      { key: 'TrangThai', label: t('data.columns.trangThai') },
      { key: 'GPA_Thang10', label: t('data.columns.gpa10') }
    ],
    Course: [
      { key: 'MaHocPhan', label: t('data.columns.maHocPhan') },
      { key: 'TenMonHoc', label: t('data.columns.tenMonHoc') },
      { key: 'SoTinChi', label: t('data.columns.soTinChi') }
    ],
    Lecturer: [
      { key: 'MaGiangVien', label: t('data.columns.maGiangVien') },
      { key: 'HoTen', label: t('data.columns.hoTen') },
      { key: 'ChucDanh', label: t('data.columns.chucDanh') },
      { key: 'Khoa', label: t('data.columns.khoa') }
    ],
    Academic: [
      { key: 'RecordID', label: t('data.columns.recordId') },
      { key: 'MSSV', label: t('data.columns.mssv') },
      { key: 'MaHocPhan', label: t('data.columns.maHocPhan') },
      { key: 'HocKy', label: t('data.columns.hocKy') },
      { key: 'NamHoc', label: t('data.columns.namHoc') },
      { key: 'DiemTongKet', label: t('data.columns.diemTongKet') },
      { key: 'KetQua', label: t('data.columns.ketQua') }
    ]
  };
  return map[activeSheet.value] || map.Student;
});
const showEmpty = computed(() => (preview.value?.rows || []).length === 0);
const emptyMessage = computed(() => {
  if (keyword.value.trim()) {
    return t('common.noSearchData');
  }
  return t('common.noData');
});

const loadSheet = async (sheet: string) => {
  if (!file.value) {
    await navigateTo('/admin/import');
    return;
  }
  activeSheet.value = sheet;
  page.value = 1;
  preview.value = await previewData(file.value, sheet, pageSize.value, 0, keyword.value.trim());
};

const loadPage = async (nextPage: number) => {
  if (!file.value) return;
  const safePage = Math.max(1, Math.min(nextPage, totalPages.value || 1));
  page.value = safePage;
  const skip = (page.value - 1) * pageSize.value;
  preview.value = await previewData(
    file.value,
    activeSheet.value,
    pageSize.value,
    skip,
    keyword.value.trim()
  );
};

const changePageSize = () => {
  page.value = 1;
  return loadPage(1);
};

const prevPage = () => loadPage(page.value - 1);
const nextPage = () => loadPage(page.value + 1);

const goBack = () => navigateTo('/admin/import');
const goNext = () => navigateTo('/admin/import/validate');

onMounted(() => loadSheet(activeSheet.value));

watch(keyword, () => {
  if (searchTimer) {
    clearTimeout(searchTimer);
  }
  searchTimer = setTimeout(() => {
    loadPage(1);
  }, 300);
});
</script>

<style scoped>
.admin-empty {
  padding: 18px;
  color: #8a9bb5;
  font-size: 13px;
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
