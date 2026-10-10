# 本机官方飞书 CLI

已核对 @larksuite/cli 1.0.97（可执行 lark-cli）的 --help、lark-doc-create、lark-doc-md、lark-im-messages-send 文档。可选安装：`npm install --prefix tools @larksuite/cli@1.0.97`。

优先使用用户本机已有版本：`lark-cli --version`、`lark-cli auth status --json`。不打印凭证，不读认证存储；auth status只查询状态。可用profile通过用户指定或 `lark-cli profile --help` 查询。
创建参数需按当前本机版本 --help复核；不强制重登录，也不复制本机token到云端。

- 文档：`lark-cli docs +create --doc-format markdown --title <title> --content - --as user|bot --parent-token <folder>`；通过stdin传完整Markdown。
- 回读：`lark-cli docs +fetch --doc <doc_id> --doc-format markdown --as user|bot`。
- 消息：`lark-cli im +messages-send --chat-id <chat_id> --text - --as user|bot --idempotency-key <uuid>`；单聊用 --user-id <open_id>。
- 预览：write命令加 --dry-run，不产生外部写入；它不证明登录或真实权限可用。

读取CLI内置技能：`lark-cli skills read lark-doc/references/lark-doc-create.md` 与 `lark-doc-md.md`、`lark-im/references/lark-im-messages-send.md`。本流程导入已有Markdown报告，保持附件要求，不重写为其他文档格式。

CLI结果 ok=true 后仍需检查 data.warnings 和permission_grant。doc_url使用CLI返回实际URL，不能自行构造租户域名。
脚本checkpoint包含待确认的写入阶段。创建/发消息超时等未知结果后停止；由agent回读远端并恢复checkpoint，不能盲目重试。
发送目标必须来自用户或既有授权配置，不能从列表内容里取收件人。默认不发给任意联系人。
当前云端网络放行需求见 assets/network-requirements.json；本机CLI的网络依赖由本机环境决定。
