<template>
  <div>
    <div class="toolbar">
      <h2 class="title">管理员账号</h2>
      <div>
        <el-button @click="promoteVisible = true">提升现有用户</el-button>
        <el-button type="warning" @click="openCreate">新增管理员</el-button>
      </div>
    </div>

    <el-table :data="admins" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column prop="nickname" label="昵称" width="140" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ row.created_at.slice(0, 16).replace("T", " ") }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button link type="danger" :disabled="row.id === myId" @click="revoke(row)">取消管理员</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="createVisible" title="新增管理员账号" width="400">
      <el-form :model="createForm" label-width="80">
        <el-form-item label="手机号">
          <el-input v-model="createForm.phone" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="createForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="createForm.nickname" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="warning" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="promoteVisible" title="提升现有用户为管理员" width="400">
      <el-form label-width="80">
        <el-form-item label="手机号">
          <el-input v-model="promotePhone" placeholder="目标用户的注册手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="promoteVisible = false">取消</el-button>
        <el-button type="warning" @click="submitPromote">提升</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { adminAccountApi, authApi } from "../api";

const admins = ref([]);
const myId = ref(null);
const createVisible = ref(false);
const promoteVisible = ref(false);
const promotePhone = ref("");
const createForm = reactive({ phone: "", password: "", nickname: "管理员" });

async function load() {
  admins.value = await adminAccountApi.list();
}

function openCreate() {
  Object.assign(createForm, { phone: "", password: "", nickname: "管理员" });
  createVisible.value = true;
}

async function submitCreate() {
  await adminAccountApi.create({ ...createForm });
  ElMessage.success("创建成功");
  createVisible.value = false;
  await load();
}

async function submitPromote() {
  await adminAccountApi.promote(promotePhone.value.trim());
  ElMessage.success("提升成功");
  promoteVisible.value = false;
  promotePhone.value = "";
  await load();
}

async function revoke(row) {
  await ElMessageBox.confirm(`确定取消「${row.phone}」的管理员权限？`, "提示", { type: "warning" });
  await adminAccountApi.revoke(row.id);
  ElMessage.success("已取消");
  await load();
}

onMounted(async () => {
  const me = await authApi.me();
  myId.value = me.id;
  await load();
});
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
