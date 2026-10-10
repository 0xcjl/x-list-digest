"""Feishu docx publishing with resumable local checkpoints. Explicit invocation only."""
import argparse,json,os,sqlite3
from pathlib import Path
from urllib.request import Request,urlopen
BASE='https://open.feishu.cn/open-apis'
def api(path,data,token=None):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    with urlopen(Request(BASE+path,json.dumps(data).encode(),headers),timeout=30) as response:r=json.load(response)
    if r.get('code',0)!=0:raise RuntimeError(f"Feishu API error code {r.get('code')}")
    return r
def publish(report,title,state_path,folder_token):
    from common import write
    state=json.loads(Path(state_path).read_text()) if Path(state_path).exists() else {}
    token=api('/auth/v3/tenant_access_token/internal',{'app_id':os.environ['FEISHU_APP_ID'],'app_secret':os.environ['FEISHU_APP_SECRET']})['tenant_access_token']
    if not state.get('document_id'):
        doc=api('/docx/v1/documents',{'title':title,'folder_token':folder_token},token)['data']['document']
        state.update(document_id=doc['document_id'],chunks_written=0);write(state_path,state)
    # Store Markdown faithfully as plain-text blocks. Feishu rich Markdown rendering is not assumed.
    chunks=[report[i:i+1500] for i in range(0,len(report),1500)]
    for i in range(state['chunks_written'],len(chunks),40):
        children=[{'block_type':2,'text':{'elements':[{'text_run':{'content':s}}]}} for s in chunks[i:i+40]]
        api(f"/docx/v1/documents/{state['document_id']}/blocks/{state['document_id']}/children",{'children':children,'index':-1},token)
        state['chunks_written']=min(i+40,len(chunks));write(state_path,state)
    state['doc_url']=f"https://feishu.cn/docx/{state['document_id']}";write(state_path,state)
    if not state.get('message_id'):
        receiver=os.environ['FEISHU_RECEIVE_ID'];receive_type=os.environ.get('FEISHU_RECEIVE_ID_TYPE','open_id')
        if receive_type not in ('open_id','user_id','union_id','email','chat_id'):raise ValueError('invalid receive ID type')
        import uuid
        state.setdefault('message_uuid',str(uuid.uuid4()));write(state_path,state)
        msg=api('/im/v1/messages?receive_id_type='+receive_type,{'receive_id':receiver,'msg_type':'text','uuid':state['message_uuid'],
          'content':json.dumps({'text':title+'\n'+report[:1200]+'\n完整报告：'+state['doc_url']},ensure_ascii=False)},token)
        state['message_id']=msg['data']['message_id'];write(state_path,state)
    return state
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--title',required=True);p.add_argument('--state',required=True);p.add_argument('--db');p.add_argument('--digest-id',type=int);a=p.parse_args()
    state=publish(Path(a.report).read_text(),a.title,a.state,os.environ['FEISHU_FOLDER_TOKEN'])
    if a.db and a.digest_id:
        with sqlite3.connect(a.db) as c:c.execute('UPDATE digests SET feishu_doc_url=?,feishu_msg_id=? WHERE id=?',(state['doc_url'],state['message_id'],a.digest_id))
    print(state['doc_url'])
