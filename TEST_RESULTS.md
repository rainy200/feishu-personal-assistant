# 测试记录

验证日期：2026-10-21（Asia/Shanghai）。Windows / Python 3.11.7。
最终测试使用独立虚拟环境（不继承系统包）；实际依赖版本：

```text
lark-oapi==1.7.5
openai==3.35.1
APScheduler==3.11.3
pypdf==5.9.0
arxiv==4.0.1
requests==2.34.2
PyYAML==6.0.3
python-dateutil==2.9.0.post0
```

以下版本是本次实测记录，不是对所有版本兼容性的承诺。原 requirements.txt 保持不变。

## 原始上传包基线

通过临时测试驱动加载原文件的 35 项测试列表，只排除真实网络项；未修改原始基线源码。

```text
拉取 langchain-ai/langgraph releases 失败: 限流
PASS  配置加载
PASS  JSON 解析
PASS  数据库增删改查
PASS  待办全流程
PASS  模拟面试全流程
PASS  空白PDF处理
PASS  论文PDF总结入库
PASS  需求驱动搜索
PASS  文献汇报流程
PASS  第0层硬过滤
PASS  总结缓存复用
PASS  日报跳过已入库
PASS  菜单裸指令
PASS  题库录入与考试
PASS  个人画像
PASS  面经提取入库
PASS  题库模拟面试
PASS  简历上传后引用
PASS  滚动上下文与新建对话
PASS  岗位匹配分析
PASS  面试准备三件套
PASS  图片面经识别
PASS  考试答砸入错题本
PASS  订阅时间篇数
PASS  按标题生成汇报
PASS  多对话管理
PASS  入站事件队列
PASS  批量改分类
PASS  arXiv链接汇报
PASS  日报追问链路
PASS  定时任务注册
PASS  GitHub订阅管理
PASS  GitHub release 推送
PASS  长消息拆分
SKIP original network check (offline baseline)
BASELINE passed=34 failed=0 skipped=1
```

## 修改版默认冒烟

命令：`python tests/smoke_test.py`。该次运行在环境完全隔离前执行；随后在独立环境中使用 `--network` 再次验证全部用例。

```text
拉取 langchain-ai/langgraph releases 失败: 限流
========================================
PASS  配置加载
PASS  JSON 解析
PASS  数据库增删改查
PASS  待办全流程
PASS  模拟面试全流程
PASS  空白PDF处理
PASS  论文PDF总结入库
PASS  需求驱动搜索
PASS  文献汇报流程
PASS  第0层硬过滤
PASS  总结缓存复用
PASS  日报跳过已入库
PASS  菜单裸指令
PASS  题库录入与考试
PASS  个人画像
PASS  面经提取入库
PASS  题库模拟面试
PASS  简历上传后引用
PASS  滚动上下文与新建对话
PASS  岗位匹配分析
PASS  面试准备三件套
PASS  图片面经识别
PASS  考试答砸入错题本
PASS  订阅时间篇数
PASS  按标题生成汇报
PASS  多对话管理
PASS  入站事件队列
PASS  批量改分类
PASS  arXiv链接汇报
PASS  日报追问链路
PASS  定时任务注册
PASS  GitHub订阅管理
PASS  GitHub release 推送
PASS  长消息拆分
SKIP  arXiv 联网搜索: 联网测试默认关闭；使用 --network 显式开启
========================================
通过 34 / 35；失败 0；跳过 1
已执行的冒烟测试全部通过
```

## 修改版完整冒烟（含真实网络）

命令：`python tests/smoke_test.py --network`。

```text
========================================
PASS  配置加载
PASS  JSON 解析
PASS  数据库增删改查
PASS  待办全流程
PASS  模拟面试全流程
PASS  空白PDF处理
PASS  论文PDF总结入库
PASS  需求驱动搜索
PASS  文献汇报流程
PASS  第0层硬过滤
PASS  总结缓存复用
PASS  日报跳过已入库
PASS  菜单裸指令
PASS  题库录入与考试
PASS  个人画像
PASS  面经提取入库
PASS  题库模拟面试
PASS  简历上传后引用
PASS  滚动上下文与新建对话
PASS  岗位匹配分析
PASS  面试准备三件套
PASS  图片面经识别
PASS  考试答砸入错题本
PASS  订阅时间篇数
PASS  按标题生成汇报
PASS  多对话管理
PASS  入站事件队列
PASS  批量改分类
PASS  arXiv链接汇报
PASS  日报追问链路
PASS  定时任务注册
PASS  GitHub订阅管理
拉取 langchain-ai/langgraph releases 失败: 限流
PASS  GitHub release 推送
PASS  长消息拆分
  实际检索来源：arxiv
PASS  arXiv 联网搜索
========================================
通过 35 / 35；失败 0；跳过 0
已执行的冒烟测试全部通过
```

## 新增回归

命令：`python -m unittest discover -s tests -p "test_*.py" -v`。

```text
test_env_overrides_without_mutating_input (test_history_config.ConfigTests.test_env_overrides_without_mutating_input) ... ok
test_environment_only_and_explicit_empty_override (test_history_config.ConfigTests.test_environment_only_and_explicit_empty_override) ... ok
test_example_has_no_working_credentials (test_history_config.ConfigTests.test_example_has_no_working_credentials) ... ok
test_invalid_shapes_and_values_are_safe (test_history_config.ConfigTests.test_invalid_shapes_and_values_are_safe) ... ok
test_yaml_error_does_not_echo_source_line (test_history_config.ConfigTests.test_yaml_error_does_not_echo_source_line) ... ok
test_chat_type_comes_from_event_not_message_body (test_history_config.HistoryTests.test_chat_type_comes_from_event_not_message_body) ... ok
test_command_parsing (test_history_config.HistoryTests.test_command_parsing) ... ok
test_delete_active_resets_transient_state (test_history_config.HistoryTests.test_delete_active_resets_transient_state) ... ok
test_empty_and_invalid_arguments (test_history_config.HistoryTests.test_empty_and_invalid_arguments) ... ok
test_exchange_rejects_other_owner_and_is_atomic (test_history_config.HistoryTests.test_exchange_rejects_other_owner_and_is_atomic) ... ok
test_full_text_persists_but_restored_context_is_bounded (test_history_config.HistoryTests.test_full_text_persists_but_restored_context_is_bounded) ... ok
test_history_available_without_llm_config (test_history_config.HistoryTests.test_history_available_without_llm_config) ... ok
test_history_not_disclosed_in_group_or_unknown_chat (test_history_config.HistoryTests.test_history_not_disclosed_in_group_or_unknown_chat) ... ok
test_legacy_database_and_index_creation_are_compatible (test_history_config.HistoryTests.test_legacy_database_and_index_creation_are_compatible) ... ok
test_pagination_order_and_boundaries (test_history_config.HistoryTests.test_pagination_order_and_boundaries) ... ok
test_queries_do_not_call_llm_or_pollute_history_or_session (test_history_config.HistoryTests.test_queries_do_not_call_llm_or_pollute_history_or_session) ... ok
test_router_errors_do_not_echo_exception (test_history_config.HistoryTests.test_router_errors_do_not_echo_exception) ... 消息处理失败：RuntimeError
ok
test_search_all_owned_conversations_only (test_history_config.HistoryTests.test_search_all_owned_conversations_only) ... ok
test_search_limit_and_match_excerpt (test_history_config.HistoryTests.test_search_limit_and_match_excerpt) ... ok
test_search_literal_wildcards_and_sql (test_history_config.HistoryTests.test_search_literal_wildcards_and_sql) ... ok
test_stale_foreign_and_invalid_active_ids_recover (test_history_config.HistoryTests.test_stale_foreign_and_invalid_active_ids_recover) ... ok
test_unauthorized_delete_preserves_messages (test_history_config.HistoryTests.test_unauthorized_delete_preserves_messages) ... ok

----------------------------------------------------------------------
Ran 22 tests in 27.826s

OK
```

## 其他检查及边界

- `python -m compileall -q feishu_assistant tests`：通过。
- `python -m pip check`：`No broken requirements found.`
- 新代码直接使用既有 Database/Router/FakeBot/FakeLLM 验证，不依赖真实凭证。
- 日志里的限流和 RuntimeError 是测试主动注入的异常，不是未处理的测试失败。
- 未执行真实飞书消息收发、真实模型请求、多维表格/知识库同步；需要用户在本机配置自己的应用后验收。
- ZIP 用源码白名单打包，排除所有运行数据和缓存；逐文件字节核对、CRC 检查、Python 源码解析及 LICENSE 对比在打包后执行。

原始上传 ZIP 的 SHA-256：`4fd7ea59247033a63fe24b96220a69ea758bebf36c6ecd7866981c16bb1c2a60`。
