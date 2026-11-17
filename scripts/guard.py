#!/usr/bin/env python3
"""VideoGuard 3.0: deterministic advisory checks; never submits generation."""
import argparse, json, re, sys
from pathlib import Path
from decimal import Decimal
from budget import evaluate, number
ROOT=Path(__file__).resolve().parents[1]
MODELS=json.loads((ROOT/'data/models.json').read_text())
STYLES=json.loads((ROOT/'data/styles.json').read_text())
def finding(code, level, message): return dict(code=code,level=level,message=message)
def question(qid, prompt, options, priority): return dict(id=qid,question=prompt,options=options,recommended=options[0],priority=priority)
def interview(b):
    q=[]
    def ask(k,p,o,w):
        if b.get(k) is None or b.get(k)=='' or b.get(k)==[]: q.append(question(k,p,o,w))
    ask('kind','What output do you need?',['image','video','pipeline'],100)
    ask('goal','What must the final result communicate?',['product advertisement','creative scene','custom goal'],95)
    if b.get('kind'): ask('mode','What input workflow?',['text-to-image','image-edit'] if b.get('kind')=='image' else ['image-to-video','text-to-video','custom'],90)
    if b.get('mode') in ('image-to-video','image-edit') or b.get('kind')=='pipeline':
        ask('reference','Is the source asset available?',['provide asset','describe asset','no asset yet'],89)
        ask('preserve','What must stay unchanged?',['identity and geometry','specific elements','nothing'],88)
    if b.get('kind') in ('video','pipeline'):
        ask('duration','Target clip duration?',['5 seconds','10 seconds','custom'],80)
        ask('motion','Main action?',['one main action','multiple sequential actions','custom'],75)
    ask('aspect','What delivery aspect ratio?',['9:16','16:9','1:1','custom'],70)
    ask('budget','Maximum spend and unit?',['specify cap','planning only'],68)
    ask('model','Preferred model or let us choose?',['auto','specific model'],60)
    return {'next':max(q,key=lambda x:x['priority']) if q else None,'remaining':[x['id'] for x in sorted(q,key=lambda x:-x['priority'])]}
def lint(b):
    p=b.get('prompt',''); out=[]
    if not isinstance(p,str): raise ValueError('prompt must be text')
    if not p.strip(): out.append(finding('EMPTY','BLOCK','Prompt missing.'))
    for a,c,label in [('static camera','360','camera movement'),('no text','exact text','text'),('daylight','midnight','lighting'),('locked camera','orbit','camera movement')]:
        if a in p.lower() and c in p.lower(): out.append(finding('CONFLICT','WARN',f'Possible conflicting {label}; check intended timeline.'))
    if b.get('kind') in ('video','pipeline'):
        d=b.get('duration'); actions=b.get('actions',[]); camera=b.get('camera_moves',[])
        if d is not None and number(d)==0: out.append(finding('DURATION','BLOCK','Duration must be positive.'))
        if d is not None and number(d)<=5 and (len(actions)>=3 or len(camera)>=2): out.append(finding('OVERLOAD','WARN','Several movements in a short clip; consider simplifying.'))
    preserve=b.get('preserve',[]); change=b.get('change',[])
    if isinstance(preserve,list) and isinstance(change,list):
        overlap=set(str(x).casefold().strip() for x in preserve)&set(str(x).casefold().strip() for x in change)
        if overlap: out.append(finding('LOCK_CONFLICT','BLOCK','Same elements protected and editable: '+', '.join(sorted(overlap))))
    return out
def capabilities(b):
    model=b.get('model'); m=MODELS.get(model,{}); exact=b.get('verified_capabilities') or {}; out=[]
    if not m and not exact: out.append(finding('MODEL_UNKNOWN','UNKNOWN','Exact model not established.'))
    if exact and not (exact.get('source') and exact.get('checked_at')): out.append(finding('CAP_SOURCE','UNKNOWN','Capability override needs source and check date.')); exact={}
    for key,value in [('modes',b.get('mode')),('aspects',b.get('aspect')),('durations',b.get('duration')),('resolutions',b.get('resolution'))]:
        allowed=exact.get(key) if exact else m.get(key)
        if value is None: continue
        if allowed is None: out.append(finding('CAP_'+key.upper(),'UNKNOWN',f'Confirm {key} for exact provider model.'))
        elif value not in allowed: out.append(finding('CAP_'+key.upper(),'BLOCK',f'{value} not supported by supplied {key}.'))
    if b.get('audio') is True and exact.get('audio') is not True: out.append(finding('AUDIO','BLOCK' if exact.get('audio') is False else 'UNKNOWN','Audio not confirmed.'))
    if not exact: out.append(finding('VARIANT','UNKNOWN','Family registry is advisory; exact version must be verified.'))
    return out
def handoff(b):
    if b.get('mode') not in ('image-to-video','image-edit') and b.get('kind')!='pipeline': return []
    r=b.get('reference'); out=[]
    if not isinstance(r,dict): return [finding('REFERENCE','UNKNOWN','Source image not inspected.')]
    if r.get('inspected') is not True: out.append(finding('REFERENCE','UNKNOWN','Visual inspection not confirmed.'))
    w,h=r.get('width'),r.get('height'); aspect=b.get('aspect')
    if w is not None and h is not None:
        if number(w)==0 or number(h)==0: out.append(finding('DIMENSIONS','BLOCK','Invalid reference dimensions.'))
        elif aspect and re.fullmatch(r'[1-9]\d*:[1-9]\d*',aspect):
            a,c=map(int,aspect.split(':'))
            if abs(float(number(w)/number(h))/(a/c)-1)>.1: out.append(finding('CROP','WARN','Aspect mismatch; approve crop or padding.'))
    else: out.append(finding('DIMENSIONS','UNKNOWN','Image dimensions missing.'))
    if r.get('subject_clipped') and b.get('full_body_motion'): out.append(finding('CLIP','WARN','Motion needs anatomy not visible in reference.'))
    if b.get('reveal_unseen') and b.get('preserve'): out.append(finding('UNSEEN','WARN','Unseen geometry cannot be reliably preserved from one view.'))
    if r.get('approved') is not True: out.append(finding('APPROVAL','UNKNOWN','Source frame not approved.'))
    return out
def compile_image(b):
    fields=['goal','subject','composition','lighting','style','background','exact_text','preserve','change','aspect']
    lines=[]
    for k in fields:
        v=b.get(k)
        if v is not None and v!='' and v!=[]: lines.append(k.replace('_',' ').title()+': '+(', '.join(map(str,v)) if isinstance(v,list) else str(v)))
    s=STYLES['styles'].get(b.get('style'));  
    if s: lines.append('Visual direction: '+s)
    camera=b.get('camera'); c=STYLES['camera'].get(camera)
    if c: lines.append('Camera: '+c)
    return {'prompt':'\n'.join(lines),'settings':{k:b[k] for k in ('aspect','resolution') if b.get(k)},'references':b.get('reference_ids',[]),'warnings':lint({**b,'prompt':'\n'.join(lines)})+capabilities(b),'note':'Neutral handoff JSON, not a provider API payload. Exact text and protected elements retained.'}
def token_plan(b):
    blocks=b.get('blocks',[]); cap=number(b['cap']); overhead=number(b.get('overhead',0)); output=number(b.get('output_reserve',0)); left=cap-overhead-output
    if left<0: return {'status':'BLOCK','reason':'Overhead and output reserve exceed cap'}
    seen=set(); keep=[]; skip=[]; used=Decimal(0)
    for x in sorted(blocks,key=lambda x:(not x.get('required',False),-number(x.get('priority',0)))):
        if x['id'] in seen: raise ValueError('duplicate context id')
        seen.add(x['id']); n=number(x['tokens'])
        if x.get('required') or used+n<=left: keep.append(x['id']); used+=n
        else: skip.append(x['id'])
    return {'status':'BLOCK' if used>left else 'WITHIN_ESTIMATE','keep':keep,'skip':skip,'estimated_total':str(used+overhead+output),'note':'Uses caller-supplied token estimates; never truncates required blocks.'}
def debug(b):
    stages=b.get('stages',[]); by={s['id']:s for s in stages}
    if len(by)!=len(stages): raise ValueError('duplicate stage')
    visiting=set(); done=set()
    def visit(k):
        if k in visiting: raise ValueError('cycle')
        if k in done:return
        if k not in by:raise ValueError('unknown dependency')
        visiting.add(k)
        for d in by[k].get('depends_on',[]):visit(d)
        visiting.remove(k); done.add(k)
    for k in by:visit(k)
    def ancestors(k):
        out=set()
        for d in by[k].get('depends_on',[]):out.add(d);out.update(ancestors(d))
        return out
    failed={k for k,s in by.items() if s.get('status')=='FAIL'}
    roots=sorted(k for k in failed if not ancestors(k)&failed)
    affected=sorted(k for k in by if k in roots or ancestors(k)&set(roots))
    return {'candidate_roots':roots,'revalidate':affected,'preserve':[k for k in by if k not in affected and by[k].get('status')=='PASS'],'evidence':{k:by[k].get('evidence','not supplied') for k in roots},'note':'Earliest observed failures, not proven causation. Check inputs and evidence before retry.'}
def preflight(b):
    out=lint(b)+capabilities(b)+handoff(b); budget=evaluate(b['cost_plan']) if b.get('cost_plan') else None
    if budget is None or budget['status']=='UNKNOWN':out.append(finding('COST','UNKNOWN','Quote missing or incomplete.'))
    elif budget['status']=='BLOCK':out.append(finding('COST','BLOCK','Planned cost exceeds cap.'))
    next_q=interview(b)['next']
    if next_q: out.append(finding('BRIEF','UNKNOWN','Unresolved interview field: '+next_q['id']))
    return {'verdict':'BLOCK' if any(x['level']=='BLOCK' for x in out) else 'REVIEW' if out else 'READY_FOR_REVIEW','findings':out,'budget':budget,'next_question':next_q,'authorization':False}
def quote(b):
    # Offline default: use an explicit quote, not fabricated price tables.
    return evaluate(b)
def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['interview','lint','capabilities','handoff','compile-image','tokens','debug','preflight','quote']); p.add_argument('input',type=Path); a=p.parse_args()
    funcs={'interview':interview,'lint':lint,'capabilities':capabilities,'handoff':handoff,'compile-image':compile_image,'tokens':token_plan,'debug':debug,'preflight':preflight,'quote':quote}
    try: print(json.dumps(funcs[a.command](json.loads(a.input.read_text(encoding='utf-8'))),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,TypeError,ArithmeticError,OSError,AttributeError) as e: print(json.dumps({'status':'INVALID','error':str(e)}));return 2
    return 0
if __name__=='__main__':sys.exit(main())
