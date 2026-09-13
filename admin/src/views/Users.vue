<template>
  <div>
    <div class="toolbar">
      <h2 class="title">用户管理</h2>
      <el-input
        v-model="keyword"
        placeholder="按手机号搜索"
        style="width: 220px"
        clearable
        @keyup.enter="load"
        @clear="load"
      />
    </div>

    <el-table :data="users" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="coins" label="币余额" width="90" />
      <el-table-column prop="invite_code" label="邀请码" width="100" />
      <el-table-column label="佣金余额/累计" width="140">
        <template #default="{ row }">
          ¥{{ (row.commission_balance_cents / 100).toFixed(2) }} / ¥{{ (row.commission_total_cents / 100).toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column label="VIP" width="180">
        <template #default="{ row }">
          <el-tag v-if="row.is_vip" type="warning">至 {{ formatDate(row.vip_expire_at) }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.is_admin" type="danger">管理员</el-tag>
          <span v-else>普通用户</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="110">
        <template #default="{ row }">
          <el-button link type="primary" @click="openAdjust(row)">调整</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="调整用户余额/会员" width="420">
      <p class="target">目标用户：{{ target?.phone }}</p>
      <el-form :model="form" label-width="110">
        <el-form-item label="币变动">
          <el-input-number v-model="form.coins_delta" :min="-100000" :max="100000" />
          <div class="tip">正数增加，负数扣减</div>
        </el-form-item>
        <el-form-item label="延长会员天数">
          <el-input-number v-model="form.extend_vip_days" :min="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="warning" @click="save">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { userApi } from "../api";

const users = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const target = ref(null);
const form = reactive({ coins_delta: 0, extend_vip_days: 0, remark: "管理员调整" });

async function load() {
  users.value = await userApi.list(keyword.value);
}

function openAdjust(row) {
  target.value = row;
  form.coins_delta = 0;
  form.extend_vip_days = 0;
  form.remark = "管理员调整";
  dialogVisible.value = true;
}

async function save() {
  await userApi.adjust(target.value.id, { ...form });
  ElMessage.success("调整成功");
  dialogVisible.value = false;
  await load();
}

function formatDate(str) {
  if (!str) return "-";
  return str.slice(0, 16).replace("T", " ");
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
.target {
  margin-bottom: 12px;
  color: #666;
}
.tip {
  font-size: 12px;
  color: #999;
}
</style>
