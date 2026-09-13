<template>
  <div>
    <div class="toolbar">
      <h2 class="title">违禁词管理</h2>
    </div>
    <p class="hint">
      用户提交昵称/意见反馈时会自动校验，命中则拒绝提交。发布短剧标题/简介时可在编辑页用"内容检测"按钮人工核查（不强制拦截）。
    </p>

    <div class="add-row">
      <el-input v-model="newWord" placeholder="输入违禁词" style="width: 240px" @keyup.enter="add" />
      <el-button type="warning" @click="add">添加</el-button>
    </div>

    <el-table :data="words" border style="margin-top: 16px">
      <el-table-column prop="word" label="违禁词" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { bannedWordApi } from "../api";

const words = ref([]);
const newWord = ref("");

async function load() {
  words.value = await bannedWordApi.list();
}

async function add() {
  const word = newWord.value.trim();
  if (!word) return;
  await bannedWordApi.create(word);
  newWord.value = "";
  ElMessage.success("已添加");
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除违禁词「${row.word}」？`, "提示", { type: "warning" });
  await bannedWordApi.remove(row.id);
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
  margin-bottom: 8px;
}
.hint {
  font-size: 12px;
  color: #999;
  margin-bottom: 16px;
}
.add-row {
  display: flex;
  gap: 8px;
}
</style>
