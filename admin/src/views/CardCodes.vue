<template>
  <div>
    <div class="toolbar">
      <h2 class="title">卡密管理</h2>
      <el-button type="warning" @click="openCreate">生成卡密</el-button>
    </div>

    <el-radio-group v-model="statusFilter" class="filter" @change="load">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="unused">未使用</el-radio-button>
      <el-radio-button value="used">已使用</el-radio-button>
    </el-radio-group>

    <el-table :data="cards" border>
      <el-table-column prop="code" label="卡密" width="180" />
      <el-table-column label="类型" width="80">
        <template #default="{ row }">{{ row.card_type === "vip" ? "VIP" : "币" }}</template>
      </el-table-column>
      <el-table-column label="面值" width="100">
        <template #default="{ row }">{{ row.card_type === "vip" ? `${row.vip_days} 天` : `${row.coins} 币` }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'unused' ? 'success' : 'info'">
            {{ row.status === "unused" ? "未使用" : "已使用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="used_by_phone" label="使用人" width="120" />
      <el-table-column prop="expire_at" label="有效期至" width="160">
        <template #default="{ row }">{{ row.expire_at ? row.expire_at.slice(0, 16) : "永久有效" }}</template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" show-overflow-tooltip />
      <el-table-column prop="created_at" label="生成时间" width="160">
        <template #default="{ row }">{{ row.created_at.slice(0, 16) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="90">
        <template #default="{ row }">
          <el-button link type="danger" :disabled="row.status !== 'unused'" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="生成卡密" width="440">
      <el-form :model="form" label-width="90">
        <el-form-item label="类型">
          <el-radio-group v-model="form.card_type">
            <el-radio value="vip">VIP 天数</el-radio>
            <el-radio value="coins">币</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="VIP 天数" v-if="form.card_type === 'vip'">
          <el-input-number v-model="form.vip_days" :min="1" />
        </el-form-item>
        <el-form-item label="币数" v-else>
          <el-input-number v-model="form.coins" :min="1" />
        </el-form-item>
        <el-form-item label="生成数量">
          <el-input-number v-model="form.count" :min="1" :max="500" />
        </el-form-item>
        <el-form-item label="有效期至">
          <el-date-picker v-model="form.expire_at" type="date" value-format="YYYY-MM-DD" placeholder="不选则永久有效" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="warning" @click="save">生成</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resultVisible" title="生成成功" width="440">
      <el-input v-model="resultText" type="textarea" :rows="10" readonly />
      <template #footer>
        <el-button type="warning" @click="copyResult">复制全部</el-button>
        <el-button @click="resultVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { cardApi } from "../api";

const cards = ref([]);
const statusFilter = ref("");
const dialogVisible = ref(false);
const resultVisible = ref(false);
const resultText = ref("");
const form = reactive({ card_type: "vip", vip_days: 7, coins: 100, count: 10, expire_at: null, remark: "" });

async function load() {
  cards.value = await cardApi.list(statusFilter.value ? { status: statusFilter.value } : {});
}

function openCreate() {
  Object.assign(form, { card_type: "vip", vip_days: 7, coins: 100, count: 10, expire_at: null, remark: "" });
  dialogVisible.value = true;
}

async function save() {
  const created = await cardApi.createBatch({ ...form });
  ElMessage.success(`已生成 ${created.length} 张卡密`);
  dialogVisible.value = false;
  resultText.value = created.map((c) => c.code).join("\n");
  resultVisible.value = true;
  await load();
}

async function copyResult() {
  await navigator.clipboard.writeText(resultText.value);
  ElMessage.success("已复制到剪贴板");
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除卡密「${row.code}」？`, "提示", { type: "warning" });
  await cardApi.remove(row.id);
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
.filter {
  margin-bottom: 16px;
}
</style>
