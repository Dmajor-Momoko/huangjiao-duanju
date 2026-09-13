"""开发用演示数据：管理员账号、分类、几部短剧及分集、VIP 套餐。仅在对应数据为空时写入一次。"""

import logging
import secrets

from sqlalchemy import select

from app.core.config import settings
from app.core.invite import generate_invite_code
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.banned_word import BannedWord
from app.models.banner import Banner
from app.models.content import StaticPage
from app.models.distribution import DistributionConfig
from app.models.order import AdFreePlan, VipPlan
from app.models.signin import SignInRule
from app.models.task import TaskDefinition
from app.models.user import User
from app.models.video import Category, Video, VideoEpisode, VideoImage, VideoPerformer

logger = logging.getLogger("seed")


async def seed_data() -> None:
    async with AsyncSessionLocal() as db:
        has_admin = await db.scalar(select(User.id).where(User.is_admin.is_(True)).limit(1))
        if not has_admin:
            # ADMIN_PASSWORD 留空时随机生成，避免仓库里出现一个人人都知道的默认密码。
            admin_password = settings.admin_password or secrets.token_urlsafe(9)
            invite_code = await generate_invite_code(db)
            db.add(
                User(
                    phone=settings.admin_phone,
                    nickname="管理员",
                    password_hash=hash_password(admin_password),
                    is_admin=True,
                    invite_code=invite_code,
                )
            )
            await db.commit()
            if not settings.admin_password:
                logger.warning(
                    "\n%s\n已自动创建初始管理员账号（未在 .env 设置 ADMIN_PASSWORD，随机生成）：\n"
                    "  手机号：%s\n  密码：%s\n"
                    "请立即登录管理后台修改密码，这个随机密码只会打印这一次。\n%s",
                    "=" * 60,
                    settings.admin_phone,
                    admin_password,
                    "=" * 60,
                )

        has_distribution_config = await db.scalar(select(DistributionConfig.id).limit(1))
        if not has_distribution_config:
            db.add(DistributionConfig())
            await db.commit()

        has_static_page = await db.scalar(select(StaticPage.id).limit(1))
        if not has_static_page:
            db.add_all(
                [
                    StaticPage(
                        slug="user_agreement",
                        title="用户协议",
                        content="欢迎使用黄蕉短剧。请遵守相关法律法规，文明使用本平台。（示例内容，请在管理后台替换为正式协议文本）",
                    ),
                    StaticPage(
                        slug="privacy_policy",
                        title="隐私政策",
                        content="我们重视你的隐私，仅收集运营本服务所必需的信息。（示例内容，请在管理后台替换为正式隐私政策文本）",
                    ),
                    StaticPage(
                        slug="about_us",
                        title="关于我们",
                        content="黄蕉短剧是一个短剧付费观看平台。（示例内容，请在管理后台替换为正式介绍文本）",
                    ),
                    StaticPage(
                        slug="vip_intro",
                        title="VIP会员说明",
                        content="开通 VIP 后可免费观看全部短剧的所有已上线剧集。（示例内容，请在管理后台替换为正式说明文本）",
                    ),
                ]
            )
            await db.commit()

        has_banned_word = await db.scalar(select(BannedWord.id).limit(1))
        if not has_banned_word:
            db.add_all([BannedWord(word="测试违禁词"), BannedWord(word="法轮功"), BannedWord(word="六合彩")])
            await db.commit()

        has_signin_rule = await db.scalar(select(SignInRule.id).limit(1))
        if not has_signin_rule:
            db.add_all(
                [
                    SignInRule(day=1, coins=10),
                    SignInRule(day=2, coins=10),
                    SignInRule(day=3, coins=20),
                    SignInRule(day=4, coins=20),
                    SignInRule(day=5, coins=30),
                    SignInRule(day=6, coins=30),
                    SignInRule(day=7, coins=50),
                ]
            )
            await db.commit()

        has_task = await db.scalar(select(TaskDefinition.id).limit(1))
        if not has_task:
            db.add_all(
                [
                    TaskDefinition(
                        code="daily_login",
                        title="每日登录",
                        description="每天打开 App 即可领取",
                        reward_coins=5,
                        task_type="daily",
                        daily_limit=1,
                        sort=1,
                    ),
                    TaskDefinition(
                        code="watch_ad",
                        title="观看广告",
                        description="观看一次广告获得奖励，每日最多 3 次",
                        reward_coins=5,
                        task_type="daily",
                        daily_limit=3,
                        sort=2,
                    ),
                    TaskDefinition(
                        code="share_app",
                        title="分享给好友",
                        description="把短剧分享给好友",
                        reward_coins=10,
                        task_type="daily",
                        daily_limit=1,
                        sort=3,
                    ),
                    TaskDefinition(
                        code="complete_profile",
                        title="完善资料",
                        description="设置昵称和头像，仅需完成一次",
                        reward_coins=20,
                        task_type="once",
                        daily_limit=1,
                        sort=4,
                    ),
                ]
            )
            await db.commit()

        has_category = await db.scalar(select(Category.id).limit(1))
        if has_category:
            return

        categories = [Category(name=name, sort=i) for i, name in enumerate(["都市", "古装", "甜宠", "悬疑"])]
        db.add_all(categories)
        await db.flush()

        demo_videos = [
            {
                "title": "重生之都市逆袭",
                "category": categories[0],
                "description": "被辜负的豪门千金重生归来，一路逆袭。",
                "free_episodes": 3,
                "unlock_price_coins": 300,
                "episode_count": 12,
                "performers": [
                    {"type": "performer", "name": "林晚", "role": "饰 沈知夏"},
                    {"type": "performer", "name": "陈屿", "role": "饰 顾深"},
                    {"type": "director", "name": "周明", "role": ""},
                ],
                "image_names": ["定妆照", "片场剧照", "海报"],
            },
            {
                "title": "王爷的替嫁新娘",
                "category": categories[1],
                "description": "替嫁王府的农家女，意外卷入宫廷阴谋。",
                "free_episodes": 3,
                "unlock_price_coins": 300,
                "episode_count": 20,
                "performers": [
                    {"type": "performer", "name": "苏晴", "role": "饰 阿禾"},
                    {"type": "performer", "name": "赵珩", "role": "饰 王爷"},
                    {"type": "director", "name": "李然", "role": ""},
                ],
                "image_names": ["王府剧照", "婚服造型"],
            },
            {
                "title": "闪婚总裁契约爱",
                "category": categories[2],
                "description": "一纸契约婚约，甜蜜与心动同时降临。",
                "free_episodes": 2,
                "unlock_price_coins": 200,
                "episode_count": 15,
                "performers": [
                    {"type": "performer", "name": "夏栀", "role": "饰 温栀"},
                    {"type": "performer", "name": "封屿", "role": "饰 总裁"},
                ],
                "image_names": ["婚礼剧照", "办公室剧照", "海报", "花絮"],
            },
        ]

        created_videos = []
        for item in demo_videos:
            video = Video(
                title=item["title"],
                category_id=item["category"].id,
                cover="",
                description=item["description"],
                free_episodes=item["free_episodes"],
                unlock_price_coins=item["unlock_price_coins"],
            )
            db.add(video)
            await db.flush()
            created_videos.append(video)
            for no in range(1, item["episode_count"] + 1):
                db.add(
                    VideoEpisode(
                        video_id=video.id,
                        episode_no=no,
                        title=f"第{no}集",
                        video_url=f"https://example.com/videos/{video.id}/{no}.m3u8",
                        duration=90,
                    )
                )
            for i, p in enumerate(item["performers"]):
                db.add(VideoPerformer(video_id=video.id, sort=i, **p))
            for i, name in enumerate(item["image_names"]):
                db.add(VideoImage(video_id=video.id, name=name, image_url="", sort=i))

        db.add_all(
            [
                Banner(title=v.title, image_url="", link_url=f"/video/{v.id}", sort=i)
                for i, v in enumerate(created_videos)
            ]
        )

        db.add_all(
            [
                VipPlan(name="周卡", price_cents=1900, duration_days=7, sort=1),
                VipPlan(name="月卡", price_cents=3900, duration_days=30, sort=2),
                VipPlan(name="年卡", price_cents=19800, duration_days=365, sort=3),
            ]
        )

        db.add_all(
            [
                AdFreePlan(name="免广告月卡", price_cents=990, duration_days=30, sort=1),
                AdFreePlan(name="免广告年卡", price_cents=6800, duration_days=365, sort=2),
            ]
        )

        await db.commit()
