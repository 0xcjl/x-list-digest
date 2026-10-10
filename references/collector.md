# 抓取节奏
|参数|default|conservative|aggressive|
|---|---:|---:|---:|
|滚动px|400|300|600|
|随机停顿秒|1.5–3.5|3–6|0.8–1.8|
|大停顿每N步|10|6|15|
|大停顿秒|4–8|6–12|2–4|
|最大步数|80|50|120|
|rate limit等待秒|60|120|30|
|总超时分钟|8|12|6|

首次 conservative。每次浏览器调用后检查 deadline；等待按不超过60秒切分。
连续5步无新帖 = exhausted_observed，仍不能证明所有帖子完整。步骤和帖子数量分开计数。
错误页“出错了/重试”只是临时错误，不必然为限流；记录 transient_error，重试一次。
停止原因包括 boundary_observed/max_tweets/max_steps/timeout/captcha/login_required/rate_limited/disconnected/exhausted_observed。
