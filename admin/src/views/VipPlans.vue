<template>
  <div>
    <div class="toolbar">
      <h2 class="title">会员套餐</h2>
      <el-button type="warning" @click="openCreate">新建套餐</el-button>
    </div>

    <el-table :data="plans" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="名称" />
      <el-table-column label="价格" width="120">
        <template #default="{ row }">¥{{ (row.price_cents / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="duration_days" label="有效天数" width="100" />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑套餐' : '新建套餐'" width="400">
      <el-form :model="form" label-width="90">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="价格(元)">
          <el-input-number v-model="form.price_yuan" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="有效天数">
          <el-input-number v-model="form.duration_days" :min="1" />
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
import { vipPlanApi } from "../api";

const plans = ref([]);
const dialogVisible = ref(false);
const editing = ref(null);
const form = reactive({ name: "", price_yuan: 0, duration_days: 30, sort: 0 });

async function load() {
  plans.value = await vipPlanApi.list();
}

function openCreate() {
  editing.value = null;
  form.name = "";
  form.price_yuan = 0;
  form.duration_days = 30;
  form.sort = 0;
  dialogVisible.value = true;
}

function openEdit(row) {
  editing.value = row;
  form.name = row.name;
  form.price_yuan = row.price_cents / 100;
  form.duration_days = row.duration_days;
  form.sort = row.sort;
  dialogVisible.value = true;
}

async function save() {
  const payload = {
    name: form.name,
    price_cents: Math.round(form.price_yuan * 100),
    duration_days: form.duration_days,
    sort: form.sort,
  };
  if (editing.value) {
    await vipPlanApi.update(editing.value.id, payload);
  } else {
    await vipPlanApi.create(payload);
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除套餐「${row.name}」？`, "提示", { type: "warning" });
  await vipPlanApi.remove(row.id);
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
