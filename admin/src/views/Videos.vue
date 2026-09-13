<template>
  <div>
    <div class="toolbar">
      <h2 class="title">短剧管理</h2>
      <el-button type="warning" @click="openCreate">新建短剧</el-button>
    </div>

    <el-table :data="videos" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" />
      <el-table-column label="分类" width="120">
        <template #default="{ row }">{{ categoryName(row.category_id) }}</template>
      </el-table-column>
      <el-table-column prop="episode_count" label="集数" width="80" />
      <el-table-column label="上下线" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_online ? 'success' : 'info'">{{ row.is_online ? "上线" : "下线" }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/videos/${row.id}`)">编辑/分集</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新建短剧" width="420">
      <el-form :model="form" label-width="90">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="免费集数">
          <el-input-number v-model="form.free_episodes" :min="0" />
        </el-form-item>
        <el-form-item label="解锁全剧价">
          <el-input-number v-model="form.unlock_price_coins" :min="0" />
          <span class="unit">币</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="warning" @click="save">创建后去添加分集</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { categoryApi, videoApi } from "../api";

const videos = ref([]);
const categories = ref([]);
const dialogVisible = ref(false);
const router = useRouter();
const form = reactive({ title: "", category_id: null, free_episodes: 3, unlock_price_coins: 0 });

function categoryName(id) {
  return categories.value.find((c) => c.id === id)?.name || "-";
}

async function load() {
  const [v, c] = await Promise.all([videoApi.list(), categoryApi.list()]);
  videos.value = v;
  categories.value = c;
}

function openCreate() {
  form.title = "";
  form.category_id = null;
  form.free_episodes = 3;
  form.unlock_price_coins = 0;
  dialogVisible.value = true;
}

async function save() {
  const created = await videoApi.create({ ...form });
  ElMessage.success("创建成功，请继续添加分集");
  dialogVisible.value = false;
  router.push(`/videos/${created.id}`);
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除短剧「${row.title}」及其所有分集？`, "提示", { type: "warning" });
  await videoApi.remove(row.id);
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
.unit {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}
</style>
