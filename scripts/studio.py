#!/usr/bin/env python3
"""VideoGuard 4: offline storyboard, continuity, QA and spend ledger."""
import argparse, hashlib, json, sys
from decimal import Decimal
from pathlib import Path
from budget import number
from guard import lint, handoff, debug


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def index(rows):
    out = {}
    for row in rows:
        key = row['id']
        if not isinstance(key, str) or not key.strip() or key in out:
            raise ValueError('IDs must be unique nonempty strings')
        out[key] = row
    return out


def storyboard(project):
    shots = index(project['shots']); identities = index(project.get('identities', [])); findings = []; cards = []; offset = Decimal(0)
    def note(code, level, shot, detail):
        findings.append(dict(code=code, level=level, shot=shot, detail=detail))
    if not shots: note('NO_SHOTS','BLOCK',None,'No shots specified')
    for sid, shot in shots.items():
        duration = number(shot['duration']); start = offset; offset += duration
        if not duration: note('DURATION','BLOCK',sid,'Duration must be positive')
        for field in ('purpose','subject','action','camera','lighting','opening','ending'):
            if not shot.get(field): note('MISSING_FIELD','REVIEW',sid,field)
        if shot.get('narrative') and not all(shot['narrative'].get(k) for k in ('desire','obstacle','geometry','gaze','rhythm')):
            note('NARRATIVE','REVIEW',sid,'Complete the narrative beat or omit for non-narrative shots')
        cast = shot.get('cast', {}); refs = []
        for cid, binding in cast.items():
            identity = identities.get(cid)
            if not identity: note('UNKNOWN_IDENTITY','BLOCK',sid,cid); continue
            locked = identity.get('locked', {}); observed = binding.get('attributes', {})
            if not locked: note('EMPTY_IDENTITY','REVIEW',sid,cid)
            for key, value in locked.items():
                if key not in observed: note('IDENTITY_UNCHECKED','REVIEW',sid,f'{cid}.{key}')
                elif observed[key] != value: note('IDENTITY_DRIFT','BLOCK',sid,f'{cid}.{key}')
            if not identity.get('approved') or not identity.get('reference_id') or not identity.get('version'):
                note('IDENTITY_APPROVAL','REVIEW',sid,cid)
            elif binding.get('version') != identity['version']:
                note('STALE_IDENTITY','BLOCK',sid,cid)
            else: refs.append(identity['reference_id'])
        handoff_brief = {**shot,'kind':'video'}
        for item in lint(handoff_brief)+handoff(handoff_brief):
            note(item['code'],'BLOCK' if item['level']=='BLOCK' else 'REVIEW',sid,item['message'])
        cards.append(dict(id=sid,start=str(start),end=str(offset),duration=str(duration),reference_ids=refs,prompt=shot.get('prompt',''),purpose=shot.get('purpose'),opening=shot.get('opening'),ending=shot.get('ending')))
    if project.get('duration') is not None and number(project['duration']) != offset:
        note('TIMELINE','BLOCK',None,'Shot durations do not equal target duration')
    ordered=list(shots.values())
    for left,right in zip(ordered,ordered[1:]):
        if right.get('continuous_from_previous') and left.get('ending') != right.get('opening'):
            note('CONTINUITY','REVIEW',right['id'],'Previous ending and current opening mismatch; verify transition')
    return {'verdict':'BLOCK' if any(x['level']=='BLOCK' for x in findings) else 'REVIEW' if findings else 'READY_FOR_REVIEW','duration':str(offset),'cards':cards,'findings':findings,'authorization':False}


QA = {'brief': ('intent','constraints','composition','model_capability','price'), 'reference': ('identity','protected_elements','framing','reference_approval'), 'output': ('identity','protected_elements','motion','artifacts','text','delivery')}


def quality(report):
    phase=report['phase']; required=QA[phase]; observations=report.get('observations',{}); results=[]
    for key in required:
        item=observations.get(key,{}); state=item.get('status','UNKNOWN'); evidence=item.get('evidence','')
        if state not in ('PASS','FAIL','UNKNOWN','NA'): raise ValueError('invalid QA status')
        if state != 'UNKNOWN' and (not isinstance(evidence,str) or not evidence.strip()): state='UNKNOWN'
        if state=='NA' and key in ('intent','constraints','model_capability','price','reference_approval','delivery'): state='UNKNOWN'
        results.append({'criterion':key,'status':state,'evidence':evidence})
    states={r['status'] for r in results}
    return {'phase':phase,'verdict':'BLOCK' if 'FAIL' in states else 'REVIEW' if 'UNKNOWN' in states else 'READY_FOR_REVIEW','checks':results,'note':'Evidence supplied by reviewer; no pixel or motion analysis performed.','authorization':False}


def route(plan):
    cap=number(plan['cap']); unit=plan['unit']; options=index(plan['options']); viable=[]; excluded=[]
    if not isinstance(unit,str) or not unit.strip(): raise ValueError('unit required')
    for oid,o in options.items():
        why=[]; price=o.get('price'); attempts=number(o.get('attempts',1)); retries=number(o.get('retries',0))
        if attempts<1 or attempts%1 or retries%1: raise ValueError('invalid attempt count')
        if o.get('unit')!=unit: why.append('UNIT_MISMATCH')
        if o.get('capability_status')!='PASS' or not o.get('capability_source'): why.append('CAPABILITY_UNVERIFIED')
        if price is None or not o.get('quote_source'): why.append('QUOTE_UNVERIFIED')
        total=None if price is None else number(price)*(attempts+retries)
        if total is not None and total>cap: why.append('OVER_CAP')
        if why: excluded.append({'id':oid,'reasons':why})
        else: viable.append({'id':oid,'worst_case':str(total)})
    viable.sort(key=lambda x:(Decimal(x['worst_case']),x['id']))
    return {'candidates':viable,'excluded':excluded,'recommended':viable[0]['id'] if viable else None,'note':'Lowest verified supplied worst-case spend, not a quality ranking.','authorization':False}


def approval_payload(stage, entry):
    return {'stage':stage['id'],'inputs':stage.get('inputs'), 'dependency_versions':stage.get('dependency_versions',{}),'attempt':entry['id'],'quote':entry.get('quote'),'quote_source':entry.get('quote_source'),'unit':entry.get('unit')}


def ledger(project):
    cap=number(project['cap']); unit=project['unit']; stages=index(project['stages']); entries=index(project.get('attempts',[])); errors=[]; spent=Decimal(0); reserved=Decimal(0); unknown=[]; accepted=set(); active=set()
    if not isinstance(unit,str) or not unit.strip(): raise ValueError('unit required')
    debug({'stages':list(stages.values())})  # validate dependency graph
    for key,e in entries.items():
        sid=e['stage']; status=e['status']
        if sid not in stages or e.get('unit')!=unit or status not in ('RESERVED','BILLED','RELEASED'): raise ValueError('invalid ledger entry '+key)
        if status=='BILLED':
            if e.get('actual') is None: unknown.append(key)
            else: spent+=number(e['actual'])
            if e.get('accepted') is True: accepted.add(sid)
        if status=='RESERVED':
            active.add(sid)
            approval=e.get('approval',{}); payload=approval_payload(stages[sid],e)
            if not isinstance(payload['inputs'],dict) or not payload['inputs'] or approval.get('confirmed') is not True or approval.get('fingerprint')!=fingerprint(payload): errors.append('APPROVAL_MISSING_OR_STALE:'+key)
            if e.get('quote') is None or not e.get('quote_source'): unknown.append(key)
            else: reserved+=number(e['quote'])
    for sid in active:
        stage=stages[sid]
        for dep in stage.get('depends_on',[]):
            if stages[dep].get('status')!='PASS': errors.append('DEPENDENCY_NOT_ACCEPTED:'+sid+':'+dep)
    for sid,s in stages.items():
        bound=s.get('dependency_versions',{})
        for dep in s.get('depends_on',[]):
            version=stages[dep].get('version')
            if not version or bound.get(dep)!=version: errors.append('STALE_DEPENDENCY:'+sid+':'+dep)
    return {'verdict':'BLOCK' if spent+reserved>cap or errors else 'REVIEW' if unknown else 'WITHIN_RECORDED_CAP','spent':str(spent),'reserved':str(reserved),'remaining_known':str(cap-spent-reserved),'unit':unit,'unknown':unknown,'errors':errors,'accepted_stages':sorted(accepted),'cost_per_accepted_stage':str(spent/len(accepted)) if accepted and not unknown else None,'authorization':False}


def compare(dataset):
    unit=dataset['unit']; rows=index(dataset['pairs']); totals={k:{'cost':Decimal(0),'accepted':0,'first':0,'attempts':0} for k in ('baseline','guard')}
    if not rows: raise ValueError('no paired trials')
    for row in rows.values():
        if not row.get('settings_fingerprint'): raise ValueError('matched settings fingerprint required')
        for k,t in totals.items():
            item=row[k]; n=number(item['attempts']); cost=number(item['cost']); accept=item['accepted']; first=item['first_attempt_accepted']
            if item['unit']!=unit or not isinstance(accept,bool) or not isinstance(first,bool) or n%1 or n<1 or (first and not accept): raise ValueError('invalid trial')
            t['cost']+=cost;t['attempts']+=int(n);t['accepted']+=int(accept);t['first']+=int(first)
    result={}
    for k,t in totals.items(): result[k]={**t,'cost':str(t['cost']),'first_attempt_rate':str(Decimal(t['first'])/len(rows)),'cost_per_accepted':str(t['cost']/t['accepted']) if t['accepted'] else None}
    return {'pairs':len(rows),'unit':unit,'results':result,'note':'Descriptive results only; no causal attribution or significance claim. Include planner and failed attempts in costs.'}


def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['storyboard','qa','route','ledger','fingerprint','compare']); p.add_argument('input',type=Path); a=p.parse_args()
    try:
        data=json.loads(a.input.read_text(encoding='utf-8')); out={'storyboard':storyboard,'qa':quality,'route':route,'ledger':ledger,'fingerprint':fingerprint,'compare':compare}[a.command](data); print(json.dumps(out,ensure_ascii=False,indent=2)); return 0
    except (ValueError,KeyError,TypeError,ArithmeticError,AttributeError,OSError) as e: print(json.dumps({'status':'INVALID','error':str(e)})); return 2
if __name__=='__main__': sys.exit(main())
