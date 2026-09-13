<template>
  <div>
    <div class="toolbar">
      <h2 class="title">分销配置</h2>
    </div>

    <el-form :model="form" label-width="140" style="max-width: 480px">
      <el-form-item label="一级（直推）返佣">
        <el-input-number v-model="form.direct_rate_percent" :min="0" :max="100" />
        <span class="unit">%</span>
      </el-form-item>
      <el-form-item label="二级（间推）返佣">
        <el-input-number v-model="form.indirect_rate_percent" :min="0" :max="100" />
        <span class="unit">%</span>
      </el-form-item>
      <el-form-item label="最低提现金额">
        <el-input-number v-model="minYuan" :min="0" :precision="2" />
        <span class="unit">元</span>
      </el-form-item>
      <el-form-item label="单笔最高提现金额">
        <el-input-number v-model="maxYuan" :min="0" :precision="2" />
        <span class="unit">元</span>
      </el-form-item>
      <el-form-item label="提现手续费">
        <el-input-number v-model="form.service_fee_percent" :min="0" :max="100" />
        <span class="unit">%</span>
      </el-form-item>
      <el-form-item>
        <el-button type="warning" @click="save">保存</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from "vue";
import { ElMessage } from "element-plus";
import { distributionApi } from "../api";

const form = reactive({
  direct_rate_percent: 20,
  indirect_rate_percent: 5,
  min_withdraw_cents: 1000,
  max_withdraw_cents: 500000,
  service_fee_percent: 0,
});

const minYuan = computed({
  get: () => form.min_withdraw_cents / 100,
  set: (v) => (form.min_withdraw_cents = Math.round(v * 100)),
});
const maxYuan = computed({
  get: () => form.max_withdraw_cents / 100,
  set: (v) => (form.max_withdraw_cents = Math.round(v * 100)),
});

async function load() {
  Object.assign(form, await distributionApi.getConfig());
}

async function save() {
  Object.assign(form, await distributionApi.updateConfig({ ...form }));
  ElMessage.success("保存成功");
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
.unit {
  margin-left: 8px;
  color: #999;
  font-size: 13px;
}
</style>
