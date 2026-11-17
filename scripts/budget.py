#!/usr/bin/env python3
"""Offline budget checker; input uses a single explicitly declared unit."""
import json, sys
from decimal import Decimal, InvalidOperation

def number(v):
    if isinstance(v, bool): raise ValueError('boolean is not a number')
    d=Decimal(str(v))
    if not d.is_finite() or d<0: raise ValueError('expected finite nonnegative amount')
    return d

def evaluate(plan):
    unit=plan['unit']; cap=number(plan['cap']); base=Decimal(0); retry=Decimal(0); unknown=[]; ids=set()
    if not isinstance(unit,str) or not unit.strip(): raise ValueError('unit required')
    for step in plan['steps']:
        sid=step['id']
        if sid in ids: raise ValueError('duplicate step ID')
        ids.add(sid)
        if step.get('unit',unit)!=unit: raise ValueError('mixed units')
        n=number(step['quantity']); r=number(step.get('retry_quantity',0))
        if n!=n.to_integral_value() or r!=r.to_integral_value(): raise ValueError('quantity must be integer')
        if step.get('price') is None:
            if n+r: unknown.append(sid)
            continue
        price=number(step['price']); base+=n*price; retry+=r*price
    total=base+retry
    return {'unit':unit,'base_known':str(base),'retry_known':str(retry),'total_known':str(total),'cap':str(cap),'unpriced_steps':unknown,'status':'BLOCK' if total>cap else 'UNKNOWN' if unknown else 'WITHIN_CAP'}

if __name__=='__main__':
    try:
        if len(sys.argv)!=2: raise ValueError('usage: budget.py plan.json')
        with open(sys.argv[1],encoding='utf-8') as f: result=evaluate(json.load(f))
        print(json.dumps(result,indent=2))
    except (ValueError,KeyError,TypeError,InvalidOperation,OSError) as e:
        print(json.dumps({'status':'INVALID','error':str(e)})); sys.exit(2)
