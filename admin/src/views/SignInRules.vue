<template>
  <div>
    <div class="toolbar">
      <h2 class="title">签到奖励配置</h2>
    </div>
    <p class="hint">固定 7 天为一个周期，第 8 天起重新从第 1 天计算，这里只能调整每天的奖励币数。</p>

    <el-table :data="rules" border>
      <el-table-column prop="day" label="第几天" width="100">
        <template #default="{ row }">第{{ row.day }}天</template>
      </el-table-column>
      <el-table-column label="奖励币数">
        <template #default="{ row }">
          <el-input-number v-model="row.coins" :min="0" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button link type="primary" @click="save(row)">保存</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { signinApi } from "../api";

const rules = ref([]);

async function load() {
  rules.value = await signinApi.rules();
}

async function save(row) {
  await signinApi.updateRule(row.day, row.coins);
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
.hint {
  font-size: 12px;
  color: #999;
  margin-bottom: 16px;
}
</style>
