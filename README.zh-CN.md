# X List Digest

[English](README.md) | [简体中文](README.zh-CN.md)

采集已授权的 X 列表，跳过已归档帖子，将实际观察到的市场观点整理成每天一份创作参考日报。宿主 Agent 负责使用已登录浏览器及逐帖分析；固定脚本负责时间窗口、保护上限、去重、Markdown 和 SQLite 归档。

2.x 版本采用宿主原生浏览器及飞书 CLI，替代旧版独立 HTTP 发布和 CLI 包装器。2.0.1 增加标签页激活与按所有权清理。公开包不包含私密列表、凭据、飞书目标或已启用的定时任务。

## 功能

- 跨日期、跨列表增量采集，冻结历史帖子 ID，保留可审计证据。
- 固定过去 24 小时窗口，默认保护上限为 500 条、45 分钟、300 步。
- 列表页和详情页分开遍历；排序、全文或线程证据不足时保留 `partial`。
- 日报顶部呈现热门前五的主题及拓展写作方向，分类统计和跨作者标的对比采用表格。
- 多列表、同日多次运行合并为一份去重日报；周日汇总跑题统计并说明样本限制。
- 可选使用用户已授权的飞书原生 CLI，按月归档，支持版本核对、检查点恢复和完整回读。
- 原生浏览器操作前激活目标页；只清理明确属于本技能运行的标签页，保留预算续跑所需列表页。

## 安装

使用可信的 Agent Skills 安装器，或将目录放入宿主的技能发现路径。启用执行能力前检查发布内容，宿主差异见[适配说明](references/agent-adapters.md)。

需要 Python 3.11 或以上版本。用户授权安装依赖后，在技能目录创建虚拟环境：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/doctor.py
```

在 `config.yaml` 配置自己的列表别名，参考[配置示例](assets/config.example.yaml)。可选的 macOS Hermes 预检使用既有 Hermes Python、psutil、Chrome 和已经授权的 `~/.hermes/chrome-debug` 浏览器配置，默认端口为 9234。预检不会安装这些依赖，也不会替用户登录 X。

## 使用

向 Agent 发出请求：

> 运行 x-list-digest，列表 primary，窗口 24 小时，输出 both。

`both` 表示聊天摘要和本地文件；`feishu` 还需要已配置的原生 CLI 用户身份及明确授权的根文件夹。完整流程见[中文技能说明](SKILL.zh-CN.md)，宿主发现与执行入口仍为 [SKILL.md](SKILL.md)。

用户数据默认保存在 `~/.local/share/x-list-digest`，位于安装包外。失败运行和源证据保留。定时任务必须单独授权，`cron_runner.py` 仅预览调度参数，不安装调度器。模型、时间、工具和登录态必须在实际宿主中核验。

Hermes 的 `agent.max_turns` 是模型迭代额度，与采集的条数、时间、步数上限分别管理。此工作流可考虑 400 轮，为分析和飞书回读预留空间；修改全局设置需要用户授权，不能延长已经启动的任务。若本地日报已生成而飞书未完成，只恢复归档，不重新采集。

## 验证与限制

```sh
.venv/bin/python -m unittest discover -s tests
```

本机 macOS Codex/Hermes 适配已有真实增量采集和原生飞书回读证据。通用包测试覆盖固定脚本，不代表所有宿主的浏览器兼容性均已验证；当前修复之后的自然定时运行仍需单独验收。

保护上限停止或 `window_boundary_unverified` 不证明完整覆盖 24 小时。X 页面结构变化、全文或媒体与线程证据不完整、机器睡眠、认证过期，都可能阻断采集或降低覆盖度。未知互动数保留为 `null`，不能补零。

## 许可与来源

MIT-0。维护仓库：[0xcjl/x-list-digest](https://github.com/0xcjl/x-list-digest)。本版延续同一仓库的原始技能及本地验证的适配，不分发第三方技能。

GitHub 提供中英文说明；ClawHub 发布包保持英文。中文说明是通用版本，不包含本机私密配置。
