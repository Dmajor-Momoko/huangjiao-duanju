<template>
  <div>
    <div class="toolbar">
      <h2 class="title">静态页面</h2>
    </div>

    <el-table :data="pages" border>
      <el-table-column prop="slug" label="标识" width="140" />
      <el-table-column prop="title" label="标题" width="160" />
      <el-table-column prop="content" label="内容预览" show-overflow-tooltip />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="编辑页面" width="560">
      <el-form :model="form" label-width="70">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="12" />
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
import { ElMessage } from "element-plus";
import { staticPageApi } from "../api";

const pages = ref([]);
const dialogVisible = ref(false);
const editing = ref(null);
const form = reactive({ title: "", content: "" });

async function load() {
  pages.value = await staticPageApi.list();
}

function openEdit(row) {
  editing.value = row;
  form.title = row.title;
  form.content = row.content;
  dialogVisible.value = true;
}

async function save() {
  await staticPageApi.update(editing.value.slug, { ...form });
  ElMessage.success("保存成功");
  dialogVisible.value = false;
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
</style>
