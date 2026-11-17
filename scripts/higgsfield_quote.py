#!/usr/bin/env python3
"""Build a cost-only CLI invocation. Explicit --execute required; never generate."""
import argparse,json,shutil,subprocess,sys,re
from pathlib import Path
ALLOWED={'mode','start-image','end-image','prompt','duration','resolution','aspect-ratio'}
def command(request):
    model=request['model']; params=request['params']
    if not isinstance(model,str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*',model):raise ValueError('invalid model id')
    args=['higgsfield','generate','cost',model]
    for key,value in params.items():
        if key not in ALLOWED or isinstance(value,(dict,list,bool)) or value is None:raise ValueError('unsupported parameter: '+key)
        value=str(value)
        if value.startswith('-') or '\x00' in value:raise ValueError('unsafe parameter value')
        args.extend(['--'+key,value])
    return args

def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--execute',action='store_true');a=p.parse_args()
    try:
        cmd=command(json.loads(a.input.read_text(encoding='utf-8')))
        if not a.execute: print(json.dumps({'status':'PREVIEW_ONLY','argv':cmd}));return 0
        if not shutil.which('higgsfield'):raise ValueError('Official CLI not installed')
        r=subprocess.run(cmd,shell=False,capture_output=True,text=True,timeout=45)
        print(json.dumps({'status':'QUOTE_RETURNED' if r.returncode==0 else 'UNKNOWN','stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode}));return 0 if r.returncode==0 else 2
    except (ValueError,KeyError,TypeError,OSError,subprocess.TimeoutExpired) as e: print(json.dumps({'status':'UNKNOWN','error':str(e)}));return 2
if __name__=='__main__':sys.exit(main())
