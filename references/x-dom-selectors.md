# X DOM（易变）
article[data-testid=tweet]；time[datetime]；time 最近父级 a 的 /handle/status/id；[data-testid=tweetText]。
登录指示 [data-testid=AppTabBar_Profile_Link]；媒体 [data-testid=tweetPhoto] img。
点赞/回复/转发按钮 data-testid=like/reply/retweet，aria-label 计数仅尽力提取。
Quote tweet 不应替代外层主帖 ID；遇无法识别结构记录遗漏，人工检查采集脚本。
scripts/collect.js 只读当前 DOM。导航/滚动/线程展开由宿主 browser_exec 控制。
