from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_current_user
from app.models.user import User
from app.services.storage import get_storage_provider

router = APIRouter(prefix="/uploads", tags=["上传"])


@router.post("")
async def upload_file(file: UploadFile, current_user: User = Depends(get_current_user)):
    provider = get_storage_provider()
    url = await provider.save(file)
    return {"url": url}
