<template>
  <div>
    <div class="toolbar">
      <h2 class="title">分类管理</h2>
      <el-button type="warning" @click="openCreate">新建分类</el-button>
    </div>

    <el-table :data="categories" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑分类' : '新建分类'" width="400">
      <el-form :model="form" label-width="60">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
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
import { categoryApi } from "../api";

const categories = ref([]);
const dialogVisible = ref(false);
const editing = ref(null);
const form = reactive({ name: "", sort: 0 });

async function load() {
  categories.value = await categoryApi.list();
}

function openCreate() {
  editing.value = null;
  form.name = "";
  form.sort = 0;
  dialogVisible.value = true;
}

function openEdit(row) {
  editing.value = row;
  form.name = row.name;
  form.sort = row.sort ?? 0;
  dialogVisible.value = true;
}

async function save() {
  if (editing.value) {
    await categoryApi.update(editing.value.id, { name: form.name, sort: form.sort });
  } else {
    await categoryApi.create({ name: form.name, sort: form.sort });
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除分类「${row.name}」？`, "提示", { type: "warning" });
  await categoryApi.remove(row.id);
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
</style>
