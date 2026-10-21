"""不依赖大模型的历史查询指令及展示；持久化仍由 Database 负责。"""
import re

PAGE_SIZE = 10
PREVIEW_CHARS = 180
HELP = """使用帮助
· 对话历史 / 对话历史 2：按页查看当前对话，每页 10 条消息
· 搜索历史 关键词：搜索你所有对话，显示最新 10 条匹配消息
· 对话列表 / 新建对话 名字 / 切换到第2个：管理对话
· 搜文献 / 模拟面试 / 考考我 / 个人画像：使用原有功能
· 明天下午3点提醒我交周报：创建待办

历史查询仅在机器人私聊可用，不调用大模型，不计入聊天历史，也不会中断考试或面试。
历史展示为摘要；新消息完整保存到本机，旧版已截断的内容无法恢复。"""


def parse_history_command(text):
    """返回 (action, argument)，未命中返回 None；参数错误由模块解释。"""
    text = (text or "").strip()
    if text in ("帮助", "使用帮助", "/help"):
        return "help", ""
    match = re.fullmatch(r"(对话历史|搜索历史)(?:\s+(.*))?", text, re.S)
    if match:
        return ("history" if match[1] == "对话历史" else "search", (match[2] or "").strip())
    return None


def _preview(text, keyword=""):
    text = " ".join(text.split())
    pos = text.lower().find(keyword.lower()) if keyword else 0
    start = max(0, pos - 40)
    snippet = text[start:start + PREVIEW_CHARS]
    return ("…" if start else "") + snippet + ("…" if start + PREVIEW_CHARS < len(text) else "")


class HistoryCommands:
    def __init__(self, db):
        self.db = db

    def handle(self, user_id, conv_id, command):
        action, argument = command
        if action == "help":
            return HELP
        if action == "history":
            if argument and (not re.fullmatch(r"[0-9]{1,6}", argument) or int(argument) < 1):
                return "页码需为 1–999999 的整数，例如「对话历史 2」。"
            page = int(argument or "1")
            conv = self.db.get_conversation(conv_id, user_id)
            if not conv:
                return "当前对话不存在，回复「对话列表」查看。"
            rows = self.db.history_page(user_id, conv_id, PAGE_SIZE + 1, (page - 1) * PAGE_SIZE)
            if not rows:
                return "这一页还没有历史消息。回复「对话历史」返回最新一页，或先聊点什么。"
            more = len(rows) > PAGE_SIZE
            lines = ["对话「%s」· 第 %d 页（最新页优先，页内按时间正序）" % (_preview(conv["name"]), page)]
            for row in reversed(rows[:PAGE_SIZE]):
                role = "你" if row["role"] == "user" else "助手"
                lines.append("[%s] %s：%s" % (row["created_at"], role, _preview(row["content"])))
            lines.append("下一页：对话历史 %d" % (page + 1) if more else "已到最早的记录。")
            lines.append("内容仅展示摘要；可用「搜索历史 关键词」查找。")
            return "\n\n".join(lines)
        if not argument or len(argument) > 100:
            return "请输入 1–100 字的关键词，例如「搜索历史 简历」。"
        rows = self.db.search_conversation_messages(user_id, argument, PAGE_SIZE + 1)
        if not rows:
            return "没有找到匹配记录，试试更短的关键词。"
        lines = ["历史搜索 · 最新 %d 条匹配消息" % min(len(rows), PAGE_SIZE)]
        for row in rows[:PAGE_SIZE]:
            role = "你" if row["role"] == "user" else "助手"
            lines.append("「%s」[%s] %s：%s" % (
                _preview(row["name"]), row["created_at"], role, _preview(row["content"], argument)))
        if len(rows) > PAGE_SIZE:
            lines.append("还有更多匹配，请用更具体的关键词缩小范围。")
        lines.append("仅搜索你自己的全部对话；内容展示为摘要。")
        return "\n\n".join(lines)
