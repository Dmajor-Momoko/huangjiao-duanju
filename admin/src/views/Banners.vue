<template>
  <div>
    <div class="toolbar">
      <h2 class="title">首页焦点图</h2>
      <el-button type="warning" @click="openCreate">新建焦点图</el-button>
    </div>

    <el-table :data="banners" border>
      <el-table-column label="预览" width="100">
        <template #default="{ row }">
          <el-image
            v-if="row.image_url"
            :src="row.image_url"
            style="width: 60px; height: 26px; object-fit: cover"
            preview-teleported
            :preview-src-list="[row.image_url]"
          />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" width="160" />
      <el-table-column prop="link_url" label="跳转链接" show-overflow-tooltip />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="启用" width="90">
        <template #default="{ row }">
          <el-switch v-model="row.is_active" @change="toggleActive(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑焦点图' : '新建焦点图'" width="440">
      <el-form :model="form" label-width="90">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="图片">
          <div class="upload-row">
            <el-input v-model="form.image_url" placeholder="图片 URL，或点右侧按钮上传" />
            <el-upload :show-file-list="false" :http-request="handleImageUpload" accept="image/*">
              <el-button :loading="uploading">上传</el-button>
            </el-upload>
          </div>
          <img v-if="form.image_url" :src="form.image_url" class="preview" />
        </el-form-item>
        <el-form-item label="跳转链接">
          <el-input v-model="form.link_url" placeholder="站内路径如 /video/1，或外部 https:// 链接，留空则不跳转" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="warning" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { bannerApi, uploadApi } from "../api";

const banners = ref([]);
const dialogVisible = ref(false);
const editing = ref(null);
const uploading = ref(false);
const form = reactive({ title: "", image_url: "", link_url: "", sort: 0, is_active: true });

async function load() {
  banners.value = await bannerApi.list();
}

function openCreate() {
  editing.value = null;
  Object.assign(form, { title: "", image_url: "", link_url: "", sort: 0, is_active: true });
  dialogVisible.value = true;
}

function openEdit(row) {
  editing.value = row;
  Object.assign(form, { ...row });
  dialogVisible.value = true;
}

async function handleImageUpload({ file }) {
  uploading.value = true;
  try {
    const res = await uploadApi.upload(file);
    form.image_url = res.url;
  } catch (e) {
    ElMessage.error(e.message || "上传失败");
  } finally {
    uploading.value = false;
  }
}

async function save() {
  if (editing.value) {
    await bannerApi.update(editing.value.id, { ...form });
  } else {
    await bannerApi.create({ ...form });
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  await load();
}

async function toggleActive(row) {
  await bannerApi.update(row.id, { is_active: row.is_active });
  ElMessage.success("已更新");
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除焦点图「${row.title}」？`, "提示", { type: "warning" });
  await bannerApi.remove(row.id);
  ElMessage.success("已删除");
  await load();
}

onMounted(load);
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.upload-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.upload-row .el-input {
  flex: 1;
}
.preview {
  margin-top: 8px;
  max-width: 200px;
  border-radius: 6px;
  display: block;
}
</style>
