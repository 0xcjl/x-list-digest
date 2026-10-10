import argparse
from analyze import aggregate
from common import read
from pathlib import Path
import re
from collections import Counter
from zoneinfo import ZoneInfo
from common import iso
def literal(value):
    return re.sub(r'([\\`*_\[\]$~<>#!+|{}()])',r'\\\1',str(value)).replace('\n',' ')
def cell(s):return literal(s)
def link(row):
    ident=str(row['tweet_id']);handle=row['author_handle']
    if not ident.isdigit() or not re.fullmatch(r'[A-Za-z0-9_]{1,50}',handle):raise ValueError('invalid post identity')
    return f'https://x.com/{handle}/status/{ident}'
def stamp(value,meta):return iso(value).astimezone(ZoneInfo(meta.get('timezone','Asia/Bangkok'))).strftime('%Y-%m-%d %H:%M:%S %Z')
def render(rows, meta):
    stats=aggregate(rows);lines=[f"# X List「{literal(meta['list_name'])}」摘要",'',
      f"总帖数：{len(rows)}；作者数：{len(stats['authors'])}；窗口：{stamp(meta['window_start'],meta)} — {stamp(meta['window_end'],meta)}",
      f"覆盖状态：{meta.get('coverage','partial')}；停止原因：{meta.get('stop_reason','unknown')}",'',
      '## 顶部摘要']
    for r in sorted(rows,key=lambda r:sum(r.get('engagement',{}).values()),reverse=True)[:3]:
        lines.append(f"- 热门：@{literal(r['author_handle'])} — {literal(r['key_thesis'])} [原帖]({link(r)})")
    for r in [r for r in rows if r['category'] not in ('off_topic','other')][:6]:lines.append(f"- @{literal(r['author_handle'])}：{literal(r['key_thesis'])}")
    lines+=['','## 大类分布','| 类别 | 数量 |','|---|---:|']
    lines += [f'| {k} | {v} |' for k,v in stats['categories'].items()]
    lines+=['','## 分类详情']
    for cat in stats['categories']:
        lines+=['',f'### {cat}']
        for r in rows:
            if r['category']==cat:lines.append(f"- @{literal(r['author_handle'])} / {stamp(r['timestamp_iso'],meta)} / {r['sentiment']}：{literal(r['key_thesis'])} [原帖]({link(r)})")
    lines+=['','## 跨作者对比（按标的）']
    for t,data in sorted(stats['tickers'].items()):
        lines+=['',f'### {literal(t)}']
        for a,s in sorted(data['author_votes'].items()):lines.append(f'- @{literal(a)}：{s}')
        lines.append('作者票数：'+str(dict(Counter(data['author_votes'].values()))))
        lines.append('论据：')
        for r in data['posts']:lines.append(f"- @{literal(r['author_handle'])}：{literal(r['key_thesis'])} [证据]({link(r)})")
        comparison=meta.get('comparisons',{}).get(t,{})
        evidence={r['tweet_id']:r for r in data['posts']}
        for field,label in (('consensus','共识'),('disagreements','分歧')):
            for point in comparison.get(field,[]):
                ids=point.get('tweet_ids',[])
                if not ids or not all(ident in evidence for ident in ids):raise ValueError('comparison must cite observed posts for that ticker')
                if field=='consensus' and len({evidence[ident]['author_handle'] for ident in ids})<2:raise ValueError('consensus must cite at least two independent authors')
                lines.append(f"- {label}：{literal(point['text'])} "+' '.join(f'[证据]({link(evidence[ident])})' for ident in ids))
        lines.append('以上为作者观点分布；共识和分歧需结合论据，票数不代表事实。')
    lines+=['','## 跑题统计','| 作者 | 总帖数 | 跑题 | 跑题率 | 建议 |','|---|---:|---:|---:|---|']
    for a,d in sorted(stats['authors'].items(),key=lambda kv:kv[1]['rate'],reverse=True):
        suggestion='考虑移除（仅建议）' if d['total']>=3 and d['rate']>=.5 else '观察'
        lines.append(f"| {cell(a)} | {d['total']} | {d['off_topic']} | {d['rate']:.0%} | {suggestion} |")
    lines+=['','## 单帖详情']
    for r in rows:
        lines+=['',f"### @{literal(r['author_handle'])} — {r['tweet_id']}",'\n'.join('> '+literal(line) for line in r['text'].splitlines()),f"[原帖]({link(r)})",f"媒体：{cell(r.get('media',[]))}；互动：{cell(r.get('engagement',{}))}"]
    lines+=['','## 元数据']+[f'- {literal(k)}：{literal(v)}' for k,v in meta.items() if k != 'comparisons']
    return '\n'.join(lines)+'\n'
if __name__=='__main__':
    import json
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--metadata',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(render(read(a.input),json.loads(Path(a.metadata).read_text())))
