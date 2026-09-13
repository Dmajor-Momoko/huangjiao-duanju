<template>
  <div>
    <div class="toolbar">
      <h2 class="title">积分任务</h2>
      <el-button type="warning" @click="openCreate">新建任务</el-button>
    </div>

    <el-table :data="tasks" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="code" label="代码" width="140" />
      <el-table-column prop="title" label="标题" width="140" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column label="类型" width="90">
        <template #default="{ row }">{{ row.task_type === "once" ? "一次性" : "每日" }}</template>
      </el-table-column>
      <el-table-column prop="daily_limit" label="每日上限" width="90" />
      <el-table-column prop="reward_coins" label="奖励币数" width="90" />
      <el-table-column label="启用" width="90">
        <template #default="{ row }">
          <el-switch v-model="row.is_active" @change="toggleActive(row)" />
        </template>
      </el-table-column>
      <el-table-column prop="sort" label="排序" width="70" />
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑任务' : '新建任务'" width="440">
      <el-form :model="form" label-width="90">
        <el-form-item label="代码">
          <el-input v-model="form.code" :disabled="!!editing" placeholder="英文标识，如 watch_ad" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.task_type">
            <el-radio value="daily">每日</el-radio>
            <el-radio value="once">一次性</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="每日上限" v-if="form.task_type === 'daily'">
          <el-input-number v-model="form.daily_limit" :min="1" />
        </el-form-item>
        <el-form-item label="奖励币数">
          <el-input-number v-model="form.reward_coins" :min="0" />
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
import { taskApi } from "../api";

const tasks = ref([]);
const dialogVisible = ref(false);
const editing = ref(null);
const form = reactive({
  code: "",
  title: "",
  description: "",
  task_type: "daily",
  daily_limit: 1,
  reward_coins: 0,
  sort: 0,
  is_active: true,
});

async function load() {
  tasks.value = await taskApi.list();
}

function openCreate() {
  editing.value = null;
  Object.assign(form, {
    code: "",
    title: "",
    description: "",
    task_type: "daily",
    daily_limit: 1,
    reward_coins: 0,
    sort: 0,
    is_active: true,
  });
  dialogVisible.value = true;
}

function openEdit(row) {
  editing.value = row;
  Object.assign(form, { ...row });
  dialogVisible.value = true;
}

async function save() {
  if (editing.value) {
    const { code, ...payload } = form;
    await taskApi.update(editing.value.id, payload);
  } else {
    await taskApi.create({ ...form });
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  await load();
}

async function toggleActive(row) {
  await taskApi.update(row.id, { is_active: row.is_active });
  ElMessage.success("已更新");
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除任务「${row.title}」？`, "提示", { type: "warning" });
  await taskApi.remove(row.id);
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
