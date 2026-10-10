// Evaluate this function through browser_exec(local=true) on the current X page.
() => {
  const text = document.body.innerText;
  const status = /verify you are human|suspicious activity|验证码/i.test(text) ? 'captcha'
    : /\/login|login\.x\.com/.test(location.href) ? 'login_required'
    : /rate limit|too many requests|请求过多/i.test(text) ? 'rate_limited' : 'ok';
  const tweets = [...document.querySelectorAll('article[data-testid="tweet"]')].flatMap(a => {
    const time = a.querySelector('time[datetime]');
    const link = time?.closest('a');
    const match = link?.getAttribute('href')?.match(/^\/([^/]+)\/status\/(\d+)/);
    if (!match || !time) return [];
    const count = key => {
      const label = a.querySelector(`[data-testid="${key}"]`)?.getAttribute('aria-label') || '';
      const n = label.match(/[\d,.]+\s*[KM]?/i)?.[0] || '0';
      return Math.round(parseFloat(n.replace(/,/g,'')) * (/M/i.test(n)?1e6:/K/i.test(n)?1e3:1));
    };
    return [{tweet_id:match[2],author_handle:match[1],timestamp_iso:time.dateTime,
      url:'https://x.com'+link.getAttribute('href'),text:a.querySelector('[data-testid="tweetText"]')?.innerText || '',
      media:[...a.querySelectorAll('[data-testid="tweetPhoto"] img')].map(i=>({alt:i.alt,url:i.src})),
      engagement:{likes:count('like'),replies:count('reply'),reposts:count('retweet')},
      expandable:/Show more|显示更多|Show this thread|显示此帖文串/i.test(a.innerText)}];
  });
  return {status,logged_in:!!document.querySelector('[data-testid="AppTabBar_Profile_Link"]'),tweets};
}
