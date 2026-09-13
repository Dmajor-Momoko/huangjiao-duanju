<template>
  <div>
    <div class="toolbar">
      <h2 class="title">提现审核</h2>
    </div>

    <el-radio-group v-model="statusFilter" class="filter" @change="load">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="pending">待审核</el-radio-button>
      <el-radio-button value="paid">已打款</el-radio-button>
      <el-radio-button value="rejected">已驳回</el-radio-button>
    </el-radio-group>

    <el-table :data="applies" border>
      <el-table-column prop="order_no" label="申请单号" width="200" />
      <el-table-column prop="user_phone" label="用户手机号" width="130" />
      <el-table-column label="申请金额" width="100">
        <template #default="{ row }">¥{{ (row.amount_cents / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="手续费" width="90">
        <template #default="{ row }">¥{{ (row.fee_cents / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="实际到账" width="100">
        <template #default="{ row }">¥{{ (row.actual_cents / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="收款方式" width="90">
        <template #default="{ row }">{{ { alipay: "支付宝", wechat: "微信", bank: "银行卡" }[row.account_type] }}</template>
      </el-table-column>
      <el-table-column label="收款信息" min-width="200">
        <template #default="{ row }">
          <div>{{ accountInfo(row).real_name }}</div>
          <div v-if="accountInfo(row).account_no">{{ accountInfo(row).account_no }}</div>
          <div v-if="accountInfo(row).bank_name">{{ accountInfo(row).bank_name }}</div>
          <el-image v-if="accountInfo(row).qr_image" :src="accountInfo(row).qr_image" style="width: 40px; height: 40px" preview-teleported :preview-src-list="[accountInfo(row).qr_image]" />
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reject_reason" label="驳回原因" show-overflow-tooltip />
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button link type="primary" @click="approve(row)">通过</el-button>
            <el-button link type="danger" @click="openReject(row)">驳回</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="rejectVisible" title="驳回提现申请" width="400">
      <el-input v-model="rejectReason" placeholder="请输入驳回原因" />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { distributionApi } from "../api";

const applies = ref([]);
const statusFilter = ref("");
const rejectVisible = ref(false);
const rejectReason = ref("");
const rejectTarget = ref(null);

async function load() {
  applies.value = await distributionApi.listWithdrawApplies(statusFilter.value);
}

function accountInfo(row) {
  try {
    return JSON.parse(row.account_snapshot);
  } catch {
    return {};
  }
}

function statusText(status) {
  return { pending: "待审核", paid: "已打款", rejected: "已驳回" }[status] || status;
}

function statusType(status) {
  return { pending: "warning", paid: "success", rejected: "info" }[status] || "info";
}

async function approve(row) {
  await ElMessageBox.confirm(`确认已向 ${row.user_phone} 打款 ¥${(row.actual_cents / 100).toFixed(2)}？`, "提示", {
    type: "warning",
  });
  await distributionApi.approveWithdraw(row.id);
  ElMessage.success("已通过");
  await load();
}

function openReject(row) {
  rejectTarget.value = row;
  rejectReason.value = "";
  rejectVisible.value = true;
}

async function confirmReject() {
  await distributionApi.rejectWithdraw(rejectTarget.value.id, rejectReason.value || "管理员驳回");
  ElMessage.success("已驳回，佣金已退回用户余额");
  rejectVisible.value = false;
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
.filter {
  margin-bottom: 16px;
}
</style>
