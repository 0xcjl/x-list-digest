# 飞书接入
环境变量 FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_FOLDER_TOKEN、FEISHU_RECEIVE_ID；可选 FEISHU_RECEIVE_ID_TYPE（默认 open_id）。不得写到 skill/config/日志。
应用需 docx:document、消息发送及目标文件夹访问权限。文件夹由用户预先创建并设置权限；本版不自动创建月度目录。
使用 tenant_access_token/internal，docx/v1/documents，docx blocks children，im/v1/messages。
报告按文本块上传，保留 Markdown 文本；本版不承诺飞书原生富文本排版。消息使用应用机器人指定收件人，不使用群 webhook。
state.json 保存文档 ID/块进度/消息 UUID。未知结果（如写入后超时）必须先核对远端，不能盲目重发块或重建文档。
云端需放行 open.feishu.cn；本机浏览器需可访问 x.com。仅安装依赖无法建立登录态或授予 API 权限。
