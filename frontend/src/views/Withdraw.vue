<template>
  <div class="page">
    <div class="nav-bar">提现</div>

    <div class="balance-card" v-if="overview">
      <div class="num">¥{{ (overview.commission_balance_cents / 100).toFixed(2) }}</div>
      <div class="label">可提现佣金余额</div>
    </div>

    <div class="section-title">收款账户</div>
    <div class="form">
      <select class="field" v-model="accountForm.account_type">
        <option value="alipay">支付宝</option>
        <option value="wechat">微信</option>
        <option value="bank">银行卡</option>
      </select>
      <input class="field" v-model="accountForm.real_name" placeholder="真实姓名" />
      <input
        class="field"
        v-model="accountForm.account_no"
        :placeholder="accountForm.account_type === 'bank' ? '银行卡号' : '账号（可选，微信可只传收款码）'"
        v-if="accountForm.account_type !== 'wechat'"
      />
      <input
        class="field"
        v-model="accountForm.bank_name"
        placeholder="开户行"
        v-if="accountForm.account_type === 'bank'"
      />
      <div class="upload-row" v-if="accountForm.account_type !== 'bank'">
        <input type="file" accept="image/*" @change="onUploadQr" />
        <img v-if="accountForm.qr_image" :src="accountForm.qr_image" class="qr-preview" />
      </div>
      <button class="btn-primary" :disabled="savingAccount" @click="saveAccount">
        {{ savingAccount ? "保存中..." : "保存收款账户" }}
      </button>
    </div>

    <div class="section-title">申请提现</div>
    <div class="form" v-if="rules">
      <p class="hint">
        单笔 ¥{{ (rules.min_withdraw_cents / 100).toFixed(2) }} ~ ¥{{ (rules.max_withdraw_cents / 100).toFixed(2) }}，
        手续费 {{ rules.service_fee_percent }}%
      </p>
      <input class="field" v-model.number="amountYuan" type="number" placeholder="提现金额（元）" />
      <button class="btn-primary" :disabled="!amountYuan || withdrawing" @click="doWithdraw">
        {{ withdrawing ? "提交中..." : "申请提现" }}
      </button>
    </div>

    <div class="section-title">提现记录</div>
    <div v-if="!applies.length" class="empty-tip">还没有提现记录</div>
    <div v-else class="list">
      <div class="row" v-for="a in applies" :key="a.order_no">
        <div>
          <div>¥{{ (a.amount_cents / 100).toFixed(2) }}</div>
          <div class="sub">{{ a.created_at.slice(0, 16).replace("T", " ") }}</div>
          <div class="sub" v-if="a.status === 'rejected'">驳回原因：{{ a.reject_reason }}</div>
        </div>
        <span class="tag" :class="a.status">{{ statusText(a.status) }}</span>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { distributionApi, uploadApi } from "../api";
import TabBar from "../components/TabBar.vue";

const overview = ref(null);
const rules = ref(null);
const applies = ref([]);
const accountForm = reactive({ account_type: "alipay", real_name: "", account_no: "", bank_name: "", qr_image: "" });
const amountYuan = ref(null);
const savingAccount = ref(false);
const withdrawing = ref(false);

async function load() {
  const [ov, rl, list, account] = await Promise.all([
    distributionApi.overview(),
    distributionApi.withdrawRules(),
    distributionApi.withdrawList(),
    distributionApi.getAccount(),
  ]);
  overview.value = ov;
  rules.value = rl;
  applies.value = list;
  if (account) Object.assign(accountForm, account);
}

async function onUploadQr(e) {
  const file = e.target.files[0];
  if (!file) return;
  const res = await uploadApi.upload(file);
  accountForm.qr_image = res.url;
}

async function saveAccount() {
  savingAccount.value = true;
  try {
    await distributionApi.updateAccount({ ...accountForm });
    alert("保存成功");
  } catch (e) {
    alert(e.message);
  } finally {
    savingAccount.value = false;
  }
}

async function doWithdraw() {
  withdrawing.value = true;
  try {
    await distributionApi.withdraw(Math.round(amountYuan.value * 100));
    alert("提现申请已提交，等待审核");
    amountYuan.value = null;
    await load();
  } catch (e) {
    alert(e.message);
  } finally {
    withdrawing.value = false;
  }
}

function statusText(status) {
  return { pending: "审核中", paid: "已到账", rejected: "已驳回" }[status] || status;
}

onMounted(load);
</script>

<style scoped>
.balance-card {
  margin: 16px;
  background: var(--brand-soft);
  border-radius: var(--radius-lg);
  padding: 20px;
  text-align: center;
}
.num {
  font-size: 26px;
  font-weight: 700;
  color: var(--brand-dark);
}
.label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.section-title {
  padding: 16px 16px 8px;
  font-size: 14px;
  font-weight: 700;
  border-top: 8px solid var(--bg);
}
.form {
  padding: 0 16px;
}
.hint {
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
}
.upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.qr-preview {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}
.list {
  padding: 0 16px;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
}
.sub {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}
.tag {
  font-size: 11px;
  border-radius: 10px;
  padding: 2px 10px;
  background: var(--bg);
  color: var(--text-muted);
}
.tag.paid {
  background: var(--brand-soft);
  color: var(--brand-dark);
}
.tag.rejected {
  background: #fdeaea;
  color: #e64340;
}
</style>
