# 通用 Agent Skills 与能力适配

同一 SKILL.md，不依赖专有 slash command。用中文“运行 x-list-digest，列表 primary，窗口24h”即可；宿主是否支持斜杠命令由其决定。

| Agent | 用户级安装目录 | 浏览器接入 | 调度 |
|---|---|---|---|
| Codex | ~/.agents/skills/x-list-digest | 当前会话实际提供的浏览器技能/工具；遵守该工具文档 | 可用 automation 工具 |
| Hermes | ~/.hermes/skills/x-list-digest | browser_exec(local=true) 或宿主实际提供的浏览器工具 | cronjob_manage |
| Claude Code | ~/.claude/skills/x-list-digest | 已配置的浏览器 MCP 或受控本机浏览器桥接 | 宿主可用的任务调度；勿假定常驻 |
| OpenClaw | ~/.openclaw/skills/x-list-digest | browser 工具（选已有登录 profile） | 宿主 cron 工具 |

这些为包的安装/能力适配；只有在对应宿主中真实执行后才能声称该宿主联调通过。

浏览器统一动作：navigate、snapshot、scroll、expand-thread；脚本 collect.js 是 DOM 快照辅助，工具不允许任意 evaluate 时使用其受支持的 DOM/可见文本接口生成相同字段，不绕过工具限制。

宿主浏览器在本机且数据处理在云端时，只传帖子 JSON/JSONL，不导出 cookie。CLI 不可达时须在有本机终端的宿主执行发布；不能把云端新安装 CLI 当成本机已登录 CLI。

数据目录由 `--data-dir` 或 X_LIST_DIGEST_DATA_DIR 配置，默认 ~/.local/share/x-list-digest，兼容用户指定 ~/.hermes/projects/x-list-digest。支持多个别名或多次 --list；每个 list 独立窗口、目录、报告。

依赖用当前 skill 目录 .venv/bin/python；若未装，运行 install.py --agents <宿主> --install-deps，或在包根创建 venv并安装 requirements.txt。
