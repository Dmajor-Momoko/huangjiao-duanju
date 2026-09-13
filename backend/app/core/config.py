import logging
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("config")

# 开源仓库里不能带任何"看起来像默认密码"的值——任何人读到源码就等于拿到了它。
# 所以这里不给 secret_key 设默认值，而是在下面显式处理：
# - 生产模式（debug=False）必须在 .env 里显式配置 SECRET_KEY，否则拒绝启动
# - 开发模式下允许省略，但每次启动随机生成一个临时密钥（重启后所有旧 token 失效，仅用于本地开发）
_INSECURE_PLACEHOLDER = "change-me-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "duanju-v3"
    debug: bool = True
    secret_key: str = ""
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    database_url: str = "sqlite+aiosqlite:///./duanju.db"

    # 初始管理员账号；ADMIN_PASSWORD 留空时 seed.py 会随机生成一个并打印到启动日志，
    # 不会把一个所有人都知道的默认密码写进公开仓库。
    admin_phone: str = "13800000000"
    admin_password: str = ""

    payment_provider: str = "mock"
    wechat_pay_mch_id: str = ""
    wechat_pay_api_key: str = ""
    alipay_app_id: str = ""
    alipay_private_key: str = ""

    sms_provider: str = "mock"
    sms_access_key_id: str = ""
    sms_access_key_secret: str = ""
    sms_sign_name: str = ""

    storage_provider: str = "local"
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_bucket: str = ""
    oss_endpoint: str = ""


def _resolve_secret_key(raw: Settings) -> str:
    if raw.secret_key and raw.secret_key != _INSECURE_PLACEHOLDER:
        return raw.secret_key

    if not raw.debug:
        raise RuntimeError(
            "生产模式（DEBUG=false）必须在 .env 里设置一个真实的 SECRET_KEY，"
            "不能留空或用示例值，否则任何人拿到源码都能伪造登录 token。\n"
            f"可以用这个随机生成的值：SECRET_KEY={secrets.token_hex(32)}"
        )

    generated = secrets.token_hex(32)
    logger.warning(
        "未在 .env 设置 SECRET_KEY，已生成临时密钥用于本次开发运行；"
        "重启进程后此前签发的所有登录 token 都会失效。正式部署前请在 .env 里固定一个 SECRET_KEY。"
    )
    return generated


settings = Settings()
settings.secret_key = _resolve_secret_key(settings)
