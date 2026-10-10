# 停止信号
Verify you are human / suspicious activity / CAPTCHA：立即停，不绕过验证。
/login、login.x.com：立即停，提示在本机手动登录。
Too many requests / rate limit / 请求过多：一次等待降速，再出现停止。
5xx、出错了、重试：临时错误，不能直接归因为限流。
