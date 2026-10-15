"""Finite binary-domain solver with actual compatibility supplied by caller.

Arc consistency propagates impossible future choices before branching. An
exhausted budget is different from a contradiction in the received domains.
"""
import collections,time


def solve(domains,compatible,seconds=60,max_nodes=50000):
    tick=time.monotonic();stats=dict(nodes=0,revisions=0,removed=0,empty_domains=[],budget_exhausted=False)
    def propagate(current):
        queue=collections.deque((a,b) for a in current for b in current if a!=b)
        while queue:
            if time.monotonic()-tick>seconds:stats['budget_exhausted']=True;return False
            a,b=queue.popleft();stats['revisions']+=1
            keep=[x for x in current[a] if any(compatible(a,x,b,y) for y in current[b])]
            if len(keep)==len(current[a]):continue
            stats['removed']+=len(current[a])-len(keep);current[a]=keep
            if not keep:
                stats['empty_domains'].append(dict(variable=a,against=b));return False
            queue.extend((c,a) for c in current if c not in (a,b))
        return True
    def visit(current):
        stats['nodes']+=1
        if stats['nodes']>max_nodes or time.monotonic()-tick>seconds:
            stats['budget_exhausted']=True;return None
        if not propagate(current):return None
        unresolved=[n for n,d in current.items() if len(d)>1]
        if not unresolved:return {n:d[0] for n,d in current.items()}
        name=min(unresolved,key=lambda n:len(current[n]))
        for value in current[name]:
            child={n:list(d) for n,d in current.items()};child[name]=[value]
            result=visit(child)
            if result is not None:return result
            if stats['budget_exhausted']:break
        return None
    result=visit({n:list(d) for n,d in domains.items()})
    stats['seconds']=round(time.monotonic()-tick,3)
    stats['status']='solution' if result is not None else ('budget_exhausted' if stats['budget_exhausted'] else 'contradiction_in_received_domains')
    return result,stats
