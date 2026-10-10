# x-list-digest — Codex / Hermes / Claude Code / OpenClaw

同一份 Agent Skills 包，通用 SKILL.md + 宿主能力适配 + Python数据处理 + 本机飞书CLI发布。已配置首个列表：https://x.com/i/lists/1894277899064414325 。

## 安装到实际运行 Agent 的机器

```bash
python3 scripts/install.py --agents all --install-deps
# 只装某个宿主
python3 scripts/install.py --agents claude-code --install-deps
# 更新由本安装器管理的版本
python3 scripts/install.py --agents all --update --install-deps
```

| Agent | 用户级目录 |
|---|---|
| Codex | ~/.agents/skills/x-list-digest |
| Hermes | ~/.hermes/skills/x-list-digest |
| Claude Code | ~/.claude/skills/x-list-digest |
| OpenClaw | ~/.openclaw/skills/x-list-digest |

重载宿主后自然语言调用“使用 x-list-digest，总结 primary 过去24h”。斜杠命令支持取决于宿主。安装器不安装这些Agent本身，也不宣称四个宿主都完成真实运行验证。云端安装不能自动安装到用户Mac。

## 多列表与手动入口

config.yaml 的 lists 按alias管理。添加别名即可，无需改代码。

```yaml
lists:
  primary:
    name: 'X List 1894277899064414325'
    url: 'https://x.com/i/lists/1894277899064414325'
  research:
    name: '填真实名称'
    url: 'https://x.com/i/lists/填真实数字ID'
```

```bash
.venv/bin/python scripts/run.py init --list primary --window 24h --output both
# 多列表（须已配置research）
.venv/bin/python scripts/run.py init --list primary --list research --window 168h
```

每个list独立返回run_dir和固定窗口；宿主Agent按SKILL.md采集 raw.jsonl、填写 metadata.json、生成 analysis.json/comparisons.json，然后：

```bash
.venv/bin/python scripts/run.py finish --run-dir /实际/run_dir
```

数据默认 ~/.local/share/x-list-digest，可用 X_LIST_DIGEST_DATA_DIR 或 --data-dir 指定。输出报告+JSON检查点+SQLite；同一run重复finish不重复落库。聊天摘要由Agent读取报告生成。both=摘要+文件；feishu模式才发布。

## 本机浏览器与飞书 CLI

沿用已登录X的宿主浏览器，不导出cookies。本机与云端是不同环境；右侧打开页面不等于当前聊天有浏览器控制工具。

优先用户已有官方 lark-cli；可选安装官方固定版本：

```bash
npm install --prefix tools @larksuite/cli@1.0.97
.venv/bin/python scripts/doctor.py --cli ./tools/node_modules/.bin/lark-cli
```

本机已认证的CLI直接使用其profile，不读取密钥、不要求将token传到云端。

```bash
.venv/bin/python scripts/feishu_cli.py \
  --cli lark-cli --profile 用户实际profile \
  --report /实际/报告.md --title 'X List 摘要' \
  --state /实际/run_dir/publish-state.json \
  --folder-token 实际folder_token --chat-id 实际chat_id --as user \
  --dry-run
```

先核对输出，用户授权后去掉 --dry-run 完成发布。已授权目标无需重复批准。--as 必须与用户意图和CLI现有身份一致；可用 --user-id 代替 --chat-id。有 --db 和 --digest-id 时写回SQLite发布记录。

创建后回读报告章节，再发送摘要；checkpoint防重复，未知写入结果暂停待核对。CLI还需检查warnings/permission_grant。具体命令见 references/feishu-cli.md。

## 依赖、验证与边界

Python≥3.10，SQLite使用标准库；PyYAML/croniter依赖已锁定到requirements.txt。无需额外模型API key，LLM分析由调用Agent完成。

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/demo.py demo-output
```

演示与自动测试均使用合成数据；飞书发布测试使用mock。真实联调状态见 INTEGRATION.md。

网络所需域名见 assets/network-requirements.json。用户授权放行仍需宿主支持的配置入口实际应用；不能编辑策略文件或绕过代理。实际网络策略和工具检查结果才证明可达。

浏览器采集、线程展开、限流节奏由宿主Agent执行；Python不是独立抓取器。CLI必须在具有用户登录态的机器上运行。定时仅在明确要求时按宿主注册；本版不自动创建定时任务。

SQLite tweets保留最新分析，历史run JSON保留当时快照；关联表支持帖子归属多个日报。飞书HTTP API旧脚本保留为可选备用，默认使用CLI，不要求环境变量密钥。
