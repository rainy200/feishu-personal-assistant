"""配置加载与校验。"""
import os
import sys
import math
import re
from copy import deepcopy

import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
DB_PATH = os.path.join(DATA_DIR, "assistant.db")

SETUP_GUIDE = """\
【飞书个人助手】尚未完成配置，请按以下步骤操作：

1. 在飞书开放平台 (open.feishu.cn) 创建企业自建应用，开启机器人能力
2. 权限管理中添加：im:message、im:message:send_as_bot、im:resource
3. 事件订阅选择「长连接」模式，添加事件：接收消息 im.message.receive_v1
4. 创建版本并发布应用
5. 复制 config.example.yaml 为 config.yaml，填入 app_id / app_secret
6. 在 llm 一节填入 api_key、base_url 和可用的 model，或设置对应环境变量

详细图文步骤见 README.md。配置好后重新运行即可。"""

LLM_GUIDE = (
    "我的大模型还没配置好，暂时无法工作。\n"
    "请在项目目录的 config.yaml 里填入 llm.api_key（Kimi/DeepSeek/OpenAI 兼容接口均可），"
    "然后重启服务。详见 README.md。"
)


class Config:
    def __init__(self, data):
        if data is not None and not isinstance(data, dict):
            raise ValueError("配置顶层必须是 YAML 映射")
        self._data = deepcopy(data or {})
        for section in ("feishu", "llm", "schedule", "paper", "bitable", "wiki", "github"):
            value = self._data.get(section)
            if value is not None and not isinstance(value, dict):
                raise ValueError("%s 配置必须是 YAML 映射" % section)
            self._data[section] = value or {}
        # 明确列出支持的环境变量；不展开任意字符串，不依赖 .env 文件。
        for env, section, key in (
            ("FEISHU_APP_ID", "feishu", "app_id"),
            ("FEISHU_APP_SECRET", "feishu", "app_secret"),
            ("LLM_API_KEY", "llm", "api_key"),
            ("LLM_BASE_URL", "llm", "base_url"),
            ("LLM_MODEL", "llm", "model"),
            ("GITHUB_TOKEN", "github", "token"),
        ):
            if env in os.environ:
                self._data[section][key] = os.environ[env]
        text_fields = {
            "feishu": ("app_id", "app_secret"),
            "llm": ("base_url", "api_key", "model"),
            "schedule": ("morning_brief", "paper_digest"),
            "bitable": ("app_token", "paper_app_token"),
            "wiki": ("space_id", "parent_node"),
            "github": ("token",),
        }
        for section, fields in text_fields.items():
            for key in fields:
                value = self._data[section].get(key)
                if value is not None and not isinstance(value, str):
                    raise ValueError("%s.%s 必须是字符串（请加引号）" % (section, key))
        for section, key, default in (
            ("paper", "digest_top_n", 3), ("paper", "search_top_n", 5),
            ("github", "poll_minutes", 60),
        ):
            value = self._data[section].get(key, default)
            if isinstance(value, bool) or not re.fullmatch(r"[0-9]{1,9}", str(value)) or int(value) < 1:
                raise ValueError("%s.%s 必须是正整数" % (section, key))
        try:
            temperature = self._data["llm"].get("temperature", 0.3)
            if isinstance(temperature, bool) or not math.isfinite(float(temperature)):
                raise ValueError
        except (TypeError, ValueError, OverflowError):
            raise ValueError("llm.temperature 必须是有限数值") from None
        for key in ("morning_brief", "paper_digest"):
            value = self._data["schedule"].get(key)
            if value and not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value.strip()):
                raise ValueError("schedule.%s 必须是 HH:MM 格式" % key)
        feishu = self._data.get("feishu") or {}
        llm = self._data.get("llm") or {}
        schedule = self._data.get("schedule") or {}
        paper = self._data.get("paper") or {}
        bitable = self._data.get("bitable") or {}

        self.feishu_app_id = (feishu.get("app_id") or "").strip()
        self.feishu_app_secret = (feishu.get("app_secret") or "").strip()

        self.llm_base_url = (llm.get("base_url") or "https://api.moonshot.cn/v1").strip()
        self.llm_api_key = (llm.get("api_key") or "").strip()
        self.llm_model = (llm.get("model") or "kimi-k2-0905-preview").strip()
        self.llm_temperature = float(llm.get("temperature", 0.3))

        self.morning_brief = (schedule.get("morning_brief") or "08:00").strip()
        self.paper_digest = (schedule.get("paper_digest") or "08:30").strip()

        self.paper_digest_top_n = int(paper.get("digest_top_n", 3))
        self.paper_search_top_n = int(paper.get("search_top_n", 5))

        # 多维表格归档（可选）：题库/错题本同步到用户的飞书多维表格
        self.bitable_app_token = (bitable.get("app_token") or "").strip()
        # 文献库专用多维表格（bitable 节下可选的第二张表）
        self.paper_bitable_token = (bitable.get("paper_app_token") or "").strip()

        # 知识库归档（可选）：面经真题按分类分文档写入知识库空间
        wiki = self._data.get("wiki") or {}
        self.wiki_space_id = (wiki.get("space_id") or "").strip()
        self.wiki_parent_node = (wiki.get("parent_node") or "").strip()

        # GitHub 仓库订阅（可选）：token 提高 API 限额（60→5000 次/小时），不配也能用
        github = self._data.get("github") or {}
        self.github_token = (github.get("token") or "").strip()
        self.github_poll_minutes = int(github.get("poll_minutes", 60))

    @property
    def feishu_configured(self):
        return bool(self.feishu_app_id and self.feishu_app_secret) and not self.feishu_app_id.startswith("cli_xxx")

    @property
    def llm_configured(self):
        return bool(self.llm_api_key) and not self.llm_api_key.startswith("sk-xxx")


def load_config(exit_on_missing=False):
    """加载本机 YAML 与环境变量；启动时缺少飞书凭证或格式错误则显示安全提示。"""
    try:
        data = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError:
                    # YAML 异常可能附带含密钥的原始行，不能直接打印。
                    raise ValueError("config.yaml 格式错误，请检查缩进、冒号与引号") from None
        cfg = Config(data)
    except (ValueError, OSError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else "无法读取 config.yaml，请检查文件权限"
        if exit_on_missing:
            print("配置错误：" + message)
            sys.exit(1)
        raise ValueError(message) from None
    if exit_on_missing and not cfg.feishu_configured:
        print(SETUP_GUIDE)
        sys.exit(1)
    return cfg
