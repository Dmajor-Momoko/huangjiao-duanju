"""
文件存储抽象层。LocalStorageProvider 把文件存到本地 uploads/ 目录，通过静态路由 /uploads 访问，
适合开发环境。接入阿里云 OSS / 七牛云时实现对应 Provider 的 save()，并把 STORAGE_PROVIDER 改掉。
"""

import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

UPLOAD_DIR = Path("uploads")


class StorageProvider(ABC):
    @abstractmethod
    async def save(self, file: UploadFile) -> str:
        raise NotImplementedError


class LocalStorageProvider(StorageProvider):
    async def save(self, file: UploadFile) -> str:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename or "").suffix
        name = f"{uuid.uuid4().hex}{ext}"
        dest = UPLOAD_DIR / name
        content = await file.read()
        dest.write_bytes(content)
        return f"/uploads/{name}"


class AliyunOSSProvider(StorageProvider):
    async def save(self, file: UploadFile) -> str:
        raise NotImplementedError(
            "阿里云 OSS 未接入：请在此实现上传逻辑，并配置 OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET / OSS_BUCKET / OSS_ENDPOINT"
        )


def get_storage_provider() -> StorageProvider:
    if settings.storage_provider == "aliyun_oss":
        return AliyunOSSProvider()
    return LocalStorageProvider()
