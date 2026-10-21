# 飞书个人助手增量交付说明

日期：2026-10-21（Asia/Shanghai）。本次只处理用户上传的 `feishu-personal-assistant-main.zip`，未克隆替代版本，未修改、提交或推送任何 GitHub 远程仓库。

## 原项目检查结果

- 这是 Python 项目，没有独立网页前端、构建工具或现成 CI 工作流；交互入口是飞书长连接机器人。界面改进因此落实为文字回复、帮助和指令反馈。
- `main.py` 装配机器人、SQLite、模型客户端、路由和定时任务。`bot.py` 负责消息/附件/流式卡片、入站事件持久化和重放。
- `router.py` 结合确定性菜单指令、模型意图分类、模拟面试/考试会话；业务模块覆盖文献、面试、题库、岗位、画像、待办、GitHub release。
- 原 README 已是中文。本次补齐 Windows 安装、历史功能、配置优先级、隐私边界和实际测试说明，保留原有业务功能介绍。
- 原数据库已有 `conversations`、`conv_messages`、`kv_store` 活跃会话指针，以及独立的 `interview_sessions` 和 `inbox_events`。历史本来就会持久化；原实现每条仅保存前 500 字，没有用户直接查询/搜索入口。
- 原会话删除先删消息、再按用户过滤会话，数据库方法被错误传入他人 ID 时会删除他人消息。本次在同一事务内先验证归属再删除。
- 原配置使用 `yaml.safe_load`，本机 `config.yaml` 和 `data/` 已忽略，但结构错误可能产生不清晰异常；路由日志和异常回显可能暴露输入。本次强化相关入口，不声称做过完整安全审计。
- 原测试脚本实际列出 35 项，其中联网测试会吞异常并计作通过；旧 README 标注的 33 项不准确。

## 精确文件变更

| 文件 | 改动 |
|---|---|
| `README.md` | 中文安装与功能说明、Windows 命令、环境变量、隐私边界、测试及上游归属 |
| `config.example.yaml` | 清空凭证示例，模型 ID 明确待填，说明环境变量覆盖，不自动读取 `.env` |
| `.gitignore` | 补充环境文件、本机配置、密钥文件、数据库旁路文件、日志、备份、测试和编辑器缓存 |
| `feishu_assistant/history.py`（新增） | 历史命令解析、分页、跨自己会话搜索、时间/角色/摘要、空结果与参数提示、帮助 |
| `feishu_assistant/db.py` | 用户限定查询、LIKE 字面转义、索引、原子保存完整一轮对话、所有权校验与事务删除 |
| `feishu_assistant/router.py` | 在模型和练习路由之前处理历史命令；只允许私聊回显、不重复存档；完整存储与模型截断分离；恢复失效活跃指针；删除当前会话时清理练习状态；改进新建提示、移除敏感路由日志和原始异常回显 |
| `feishu_assistant/bot.py` | 将真实事件聊天类型写入入站元数据，覆盖正文伪造值；后台异常回复不含原始异常 |
| `feishu_assistant/config.py` | 白名单环境变量覆盖、映射/字符串/正整数/有限温度/时间校验；安全 YAML 错误提示；支持无 YAML 的环境变量配置 |
| `feishu_assistant/llm.py` | 调用失败及 JSON 解析失败不回显供应商原始错误或模型正文 |
| `tests/smoke_test.py` | 显式统计 PASS/FAIL/SKIP；联网测试须 `--network` 开启，无结果不再假通过 |
| `tests/test_history_config.py`（新增） | 22 项离线回归：分页、搜索、隔离、来源防伪造、上下文、存储、事务、错误与配置 |
| `docs/TECH_DESIGN.md` | 添加本次增量说明入口，纠正“凭证不出本机”的过度表述 |
| `docs/DELIVERY.md`（新增） | 本交付说明与 rainy200 后续步骤 |
| `docs/TEST_RESULTS.md`（新增） | 实际测试输出、环境版本和验证边界 |

保留 `LICENSE` 原文及原作者版权。未修改依赖清单、定时任务或各业务模块实现；没有新增前端、外部存储、ORM 或数据库重建。现有库启动时仅创建两个不存在的索引，不重写旧消息。

## 使用和验收

在机器人私聊中：

1. 正常聊几句，发「对话历史」：每页 10 **条消息**，不是 10 轮；第一页最新，页内按时间正序。发「对话历史 2」查看更早记录。
2. 发「搜索历史 简历」：跨自己的所有会话，按最新优先返回最多 10 条匹配消息；超过时提示缩小关键词。`%`、`_` 和反斜线按字面匹配，不当通配符。
3. 发「帮助」：即使没配置模型也可使用帮助、历史查看和搜索。面试或考试期间查询不会作为答案提交，不中断练习。
4. 新建、切换会话后检查历史；重启后确认记录仍在。旧版截断数据无法恢复；新增记录完整保存，界面摘要约 180 字，模型上下文仍最多最近 20 条、每条 500 字。
5. 在群聊使用历史命令，只得到私聊提示；不回显历史。此限制针对本次新增历史查询，不代表其他原有功能已完成全面群聊隐私加固。

历史查询不调用大模型，但结果仍通过飞书发送。数据库、入站事件和附件属于本机明文私人数据。删除某个对话不会删除独立业务记录、原始入站事件或飞书云端消息；项目也没有自动保留期或数据库加密。本次不扩大到多租户部署、并发调度和入站重放机制重构。

## 验证结果

| 验证 | 结果 |
|---|---|
| 原始包基线 | 34 项本地测试通过，0 失败；联网项未纳入基线 |
| 修改版默认冒烟 | 34 通过，0 失败，1 项联网测试明确跳过 |
| 修改版 `--network` | **35 通过，0 失败，0 跳过**；真实返回来源为 arXiv |
| 新增回归 | **22 通过，0 失败**；不访问真实飞书/模型 |
| Python 编译检查 | 通过 |
| 独立虚拟环境 `pip check` | 通过，未发现依赖冲突 |
| 真实飞书收发、真实 LLM、飞书表格/知识库同步 | 未测试：需要用户自己的凭证与已发布应用 |

最初在系统 Python 运行时因缺 `openai` 无法导入测试，首次安装依赖又被网络权限拦截。获得联网权限并配置工作目录内的独立虚拟环境后已解决。安装早期复用了系统包，随后已关闭系统包继承、补齐独立依赖，最终 `pip check` 和回归/联网测试均在独立环境运行。没有修改系统 Python 的包。

日志中的“拉取 releases 失败：限流”是原测试主动模拟的失败场景，测试验证游标不推进、下次可重试，不是本次真实 GitHub 调用失败。完整命令、版本、逐项输出见 [测试记录](TEST_RESULTS.md)。

## rainy200 的 GitHub 后续步骤（尚未执行）

建议保留 Fork 关系与上游署名，流程依据 [GitHub 官方 Fork 文档](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo)。

1. 用 **rainy200** 登录 GitHub，打开 [原仓库](https://github.com/wangziyingly/feishu-personal-assistant)，选择 **Fork**，Owner 选 **rainy200**，名称保留 `feishu-personal-assistant`。如果该账号已存在同名 Fork，直接使用已有副本。
2. 将自己的 Fork 克隆到一个新的本地文件夹，然后开一个增量分支：

   ```powershell
   git clone https://github.com/rainy200/feishu-personal-assistant.git
   cd feishu-personal-assistant
   git switch -c feat/conversation-history
   ```

3. 解压交付 ZIP，打开里面的 `feishu-personal-assistant` 文件夹。按上表将 **14 个变更文件**复制到刚克隆的仓库相同位置（含隐藏文件 `.gitignore`）；保留克隆目录的 `.git`。若最新上游或自己的 Fork 已改过同一文件，先合并差异，不要直接覆盖其他工作。本补丁只针对本次上传快照，不宣称兼容未来提交。
4. 按 README 在本机创建虚拟环境并运行两条离线测试命令。确认 `git remote -v` 的 `origin` 为自己的 rainy200 仓库，查看 `git diff --stat` 和 `git diff`。
5. 只暂存本次改动，查看暂存差异，确认没有真实配置、密钥、数据库、附件或日志：

   ```powershell
   git add .gitignore README.md config.example.yaml docs/TECH_DESIGN.md docs/DELIVERY.md docs/TEST_RESULTS.md feishu_assistant/history.py feishu_assistant/db.py feishu_assistant/router.py feishu_assistant/config.py feishu_assistant/bot.py feishu_assistant/llm.py tests/smoke_test.py tests/test_history_config.py
   git diff --cached --stat
   git diff --cached
   git commit -m "feat: add private conversation history commands and safer configuration"
   ```

6. **你确认内容后再执行**以下推送命令，目标仅为自己的 Fork 分支：

   ```powershell
   git push -u origin feat/conversation-history
   ```

   在 GitHub 创建 PR 时，确认 base repository 是 **rainy200/feishu-personal-assistant**，base 为自己仓库的默认分支，compare 为 `feat/conversation-history`。不要误选上游仓库作为 base。审阅后再合并到自己的默认分支。

若不使用 Git，也可在自己的 Fork 中通过 **Add file → Upload files** 上传上述改动并提交到新分支；要上传解压后的源码文件和文件夹，不能只上传 ZIP。注意 `.gitignore` 可能被文件管理器隐藏。不要把个人运行目录一起上传。

## 简历表述建议

可写：“基于开源飞书个人助手扩展对话历史查看与跨会话关键词搜索；复用 SQLite 会话模型，实现用户隔离、原子存储与模型上下文截断分离，完善配置校验和回归测试。”

讲清上游已有能力与自己的增量；本次验证为 35 项冒烟测试及 22 项新增回归测试。没有测量生产吞吐、线上用户数或成本下降比例，不宜编造这些指标。
