<template>
  <div>
    <div class="toolbar">
      <h2 class="title">操作日志</h2>
    </div>
    <p class="hint">仅记录敏感操作：管理员账号变更、用户余额/会员调整、卡密批量生成、提现审核。常规内容管理（短剧/分集等）不在此列。</p>

    <el-table :data="logs" border>
      <el-table-column prop="admin_phone" label="操作人" width="140" />
      <el-table-column prop="action" label="操作类型" width="160" />
      <el-table-column prop="detail" label="详情" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">{{ row.created_at.slice(0, 16).replace("T", " ") }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { actionLogApi } from "../api";

const logs = ref([]);

onMounted(async () => {
  logs.value = await actionLogApi.list();
});
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
