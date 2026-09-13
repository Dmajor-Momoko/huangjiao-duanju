<template>
  <div v-if="video">
    <div class="toolbar">
      <el-button link @click="$router.push('/videos')">‹ 返回列表</el-button>
      <h2 class="title">{{ video.title }}</h2>
    </div>

    <el-card class="section">
      <template #header>
        <div class="ep-header">
          <span>基本信息</span>
          <el-button size="small" @click="checkContent">内容检测</el-button>
        </div>
      </template>
      <el-form :model="video" label-width="100">
        <el-form-item label="标题">
          <el-input v-model="video.title" @change="saveBasic" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="video.description" type="textarea" :rows="3" @change="saveBasic" />
        </el-form-item>
        <el-form-item label="封面图">
          <div class="upload-row">
            <el-input v-model="video.cover" placeholder="图片 URL，或点右侧按钮上传" @change="saveBasic" />
            <el-upload :show-file-list="false" :http-request="handleCoverUpload" accept="image/*">
              <el-button :loading="coverUploading">上传图片</el-button>
            </el-upload>
          </div>
          <img v-if="video.cover" :src="video.cover" class="cover-preview" />
        </el-form-item>
        <el-form-item label="免费集数">
          <el-input-number v-model="video.free_episodes" :min="0" @change="saveBasic" />
        </el-form-item>
        <el-form-item label="解锁全剧价">
          <el-input-number v-model="video.unlock_price_coins" :min="0" @change="saveBasic" />
          <span class="unit">币</span>
        </el-form-item>
        <el-form-item label="是否上线">
          <el-switch v-model="video.is_online" @change="saveBasic" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="section">
      <template #header>
        <div class="ep-header">
          <span>分集管理（共 {{ video.episodes.length }} 集）</span>
          <el-button type="warning" size="small" @click="openAddEpisode">添加分集</el-button>
        </div>
      </template>
      <el-table :data="video.episodes" border size="small">
        <el-table-column prop="episode_no" label="集数" width="80" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="video_url" label="播放地址" show-overflow-tooltip />
        <el-table-column prop="duration" label="时长(秒)" width="90" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditEpisode(row)">编辑</el-button>
            <el-button link type="danger" @click="removeEpisode(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="epDialogVisible" :title="epEditing ? '编辑分集' : '添加分集'" width="420">
      <el-form :model="epForm" label-width="90">
        <el-form-item label="集数">
          <el-input-number v-model="epForm.episode_no" :min="1" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="epForm.title" />
        </el-form-item>
        <el-form-item label="播放地址">
          <div class="upload-row">
            <el-input v-model="epForm.video_url" placeholder="https://.../xx.mp4，或点右侧按钮上传" />
            <el-upload :show-file-list="false" :http-request="handleEpisodeVideoUpload" accept="video/*">
              <el-button :loading="epVideoUploading">{{ epUploadProgress ? `${epUploadProgress}%` : "上传视频" }}</el-button>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="时长(秒)">
          <el-input-number v-model="epForm.duration" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="epDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="saveEpisode">保存</el-button>
      </template>
    </el-dialog>

    <el-card class="section">
      <template #header>
        <div class="ep-header">
          <span>演职员管理（共 {{ video.performers.length }} 人）</span>
          <el-button type="warning" size="small" @click="openAddPerformer">添加演职员</el-button>
        </div>
      </template>
      <el-table :data="video.performers" border size="small">
        <el-table-column label="类型" width="80">
          <template #default="{ row }">{{ row.type === "director" ? "导演" : "演员" }}</template>
        </el-table-column>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="role" label="饰演角色" />
        <el-table-column prop="sort" label="排序" width="70" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditPerformer(row)">编辑</el-button>
            <el-button link type="danger" @click="removePerformer(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="perfDialogVisible" :title="perfEditing ? '编辑演职员' : '添加演职员'" width="420">
      <el-form :model="perfForm" label-width="90">
        <el-form-item label="类型">
          <el-radio-group v-model="perfForm.type">
            <el-radio value="performer">演员</el-radio>
            <el-radio value="director">导演</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="perfForm.name" />
        </el-form-item>
        <el-form-item label="饰演角色" v-if="perfForm.type === 'performer'">
          <el-input v-model="perfForm.role" />
        </el-form-item>
        <el-form-item label="头像">
          <div class="upload-row">
            <el-input v-model="perfForm.avatar" placeholder="图片 URL，或点右侧按钮上传" />
            <el-upload :show-file-list="false" :http-request="handlePerformerAvatarUpload" accept="image/*">
              <el-button :loading="perfAvatarUploading">上传</el-button>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="perfForm.bio" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="perfForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="perfDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="savePerformer">保存</el-button>
      </template>
    </el-dialog>

    <el-card class="section">
      <template #header>
        <div class="ep-header">
          <span>壁纸图集（共 {{ video.images.length }} 张）</span>
          <el-button type="warning" size="small" @click="openAddImage">添加图片</el-button>
        </div>
      </template>
      <el-table :data="video.images" border size="small">
        <el-table-column prop="name" label="名称" width="140" />
        <el-table-column label="预览" width="80">
          <template #default="{ row }">
            <el-image v-if="row.image_url" :src="row.image_url" style="width: 40px; height: 40px" preview-teleported :preview-src-list="[row.image_url]" />
          </template>
        </el-table-column>
        <el-table-column prop="downloads" label="下载次数" width="90" />
        <el-table-column prop="sort" label="排序" width="70" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditImage(row)">编辑</el-button>
            <el-button link type="danger" @click="removeImage(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="imgDialogVisible" :title="imgEditing ? '编辑图片' : '添加图片'" width="420">
      <el-form :model="imgForm" label-width="90">
        <el-form-item label="名称">
          <el-input v-model="imgForm.name" />
        </el-form-item>
        <el-form-item label="图片">
          <div class="upload-row">
            <el-input v-model="imgForm.image_url" placeholder="图片 URL，或点右侧按钮上传" />
            <el-upload :show-file-list="false" :http-request="handleGalleryImageUpload" accept="image/*">
              <el-button :loading="imgUploading">上传</el-button>
            </el-upload>
          </div>
          <img v-if="imgForm.image_url" :src="imgForm.image_url" class="cover-preview" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="imgForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="imgDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="saveImage">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { contentCheckApi, uploadApi, videoApi } from "../api";

const props = defineProps({ id: [String, Number] });
const video = ref(null);
const epDialogVisible = ref(false);
const epEditing = ref(null);
const epForm = reactive({ episode_no: 1, title: "", video_url: "", duration: 0 });
const coverUploading = ref(false);
const epVideoUploading = ref(false);
const epUploadProgress = ref(0);

const perfDialogVisible = ref(false);
const perfEditing = ref(null);
const perfForm = reactive({ type: "performer", name: "", role: "", avatar: "", bio: "", sort: 0 });
const perfAvatarUploading = ref(false);

const imgDialogVisible = ref(false);
const imgEditing = ref(null);
const imgForm = reactive({ name: "", image_url: "", sort: 0 });
const imgUploading = ref(false);

async function handleCoverUpload({ file }) {
  coverUploading.value = true;
  try {
    const res = await uploadApi.upload(file);
    video.value.cover = res.url;
    await saveBasic();
  } catch (e) {
    ElMessage.error(e.message || "上传失败");
  } finally {
    coverUploading.value = false;
  }
}

async function handleEpisodeVideoUpload({ file }) {
  epVideoUploading.value = true;
  epUploadProgress.value = 0;
  try {
    const res = await uploadApi.upload(file, (percent) => (epUploadProgress.value = percent));
    epForm.video_url = res.url;
    ElMessage.success("视频上传成功");
  } catch (e) {
    ElMessage.error(e.message || "上传失败");
  } finally {
    epVideoUploading.value = false;
    epUploadProgress.value = 0;
  }
}

async function load() {
  video.value = await videoApi.detail(props.id);
}

async function checkContent() {
  const result = await contentCheckApi.check(`${video.value.title} ${video.value.description}`);
  if (result.is_legal) {
    ElMessage.success("未发现违禁词");
  } else {
    ElMessage.error(`发现违禁词：${result.banned_words.join("、")}`);
  }
}

async function saveBasic() {
  await videoApi.update(video.value.id, {
    title: video.value.title,
    description: video.value.description,
    cover: video.value.cover,
    free_episodes: video.value.free_episodes,
    unlock_price_coins: video.value.unlock_price_coins,
    is_online: video.value.is_online,
  });
  ElMessage.success("已保存");
}

function openAddEpisode() {
  epEditing.value = null;
  epForm.episode_no = video.value.episodes.length + 1;
  epForm.title = `第${epForm.episode_no}集`;
  epForm.video_url = "";
  epForm.duration = 90;
  epDialogVisible.value = true;
}

function openEditEpisode(row) {
  epEditing.value = row;
  epForm.episode_no = row.episode_no;
  epForm.title = row.title;
  epForm.video_url = row.video_url;
  epForm.duration = row.duration;
  epDialogVisible.value = true;
}

async function saveEpisode() {
  if (epEditing.value) {
    await videoApi.updateEpisode(epEditing.value.id, { ...epForm });
  } else {
    await videoApi.addEpisode(video.value.id, { ...epForm });
  }
  ElMessage.success("保存成功");
  epDialogVisible.value = false;
  await load();
}

async function removeEpisode(row) {
  await ElMessageBox.confirm(`确定删除第 ${row.episode_no} 集？`, "提示", { type: "warning" });
  await videoApi.removeEpisode(row.id);
  ElMessage.success("已删除");
  await load();
}

async function handlePerformerAvatarUpload({ file }) {
  perfAvatarUploading.value = true;
  try {
    const res = await uploadApi.upload(file);
    perfForm.avatar = res.url;
  } catch (e) {
    ElMessage.error(e.message || "上传失败");
  } finally {
    perfAvatarUploading.value = false;
  }
}

function openAddPerformer() {
  perfEditing.value = null;
  Object.assign(perfForm, { type: "performer", name: "", role: "", avatar: "", bio: "", sort: 0 });
  perfDialogVisible.value = true;
}

function openEditPerformer(row) {
  perfEditing.value = row;
  Object.assign(perfForm, { ...row });
  perfDialogVisible.value = true;
}

async function savePerformer() {
  if (perfEditing.value) {
    await videoApi.updatePerformer(perfEditing.value.id, { ...perfForm });
  } else {
    await videoApi.addPerformer(video.value.id, { ...perfForm });
  }
  ElMessage.success("保存成功");
  perfDialogVisible.value = false;
  await load();
}

async function removePerformer(row) {
  await ElMessageBox.confirm(`确定删除「${row.name}」？`, "提示", { type: "warning" });
  await videoApi.removePerformer(row.id);
  ElMessage.success("已删除");
  await load();
}

async function handleGalleryImageUpload({ file }) {
  imgUploading.value = true;
  try {
    const res = await uploadApi.upload(file);
    imgForm.image_url = res.url;
  } catch (e) {
    ElMessage.error(e.message || "上传失败");
  } finally {
    imgUploading.value = false;
  }
}

function openAddImage() {
  imgEditing.value = null;
  Object.assign(imgForm, { name: "", image_url: "", sort: 0 });
  imgDialogVisible.value = true;
}

function openEditImage(row) {
  imgEditing.value = row;
  Object.assign(imgForm, { name: row.name, image_url: row.image_url, sort: row.sort });
  imgDialogVisible.value = true;
}

async function saveImage() {
  if (imgEditing.value) {
    await videoApi.updateImage(imgEditing.value.id, { ...imgForm });
  } else {
    await videoApi.addImage(video.value.id, { ...imgForm });
  }
  ElMessage.success("保存成功");
  imgDialogVisible.value = false;
  await load();
}

async function removeImage(row) {
  await ElMessageBox.confirm(`确定删除「${row.name}」？`, "提示", { type: "warning" });
  await videoApi.removeImage(row.id);
  ElMessage.success("已删除");
  await load();
}

onMounted(load);
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.title {
  margin: 0;
}
.section {
  margin-bottom: 16px;
}
.ep-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.unit {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}
.upload-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.upload-row .el-input {
  flex: 1;
}
.cover-preview {
  margin-top: 8px;
  max-width: 160px;
  max-height: 220px;
  border-radius: 6px;
  display: block;
}
</style>
