"""Recover every current candidate from pinned receipt ancestry.

Material-only receipts may contain only their two attempted routes. Missing
proposal geometry is inherited, never silently omitted from neighbor checks.
Only qualified_changed_routes are positive route evidence.
"""
import hashlib,json,subprocess

def resolve(macro,root):
    base=json.loads((root/macro['inherited_receipt']).read_text())
    routes={n:base['routes'][n] for n in macro['retained_route_ids']}
    ancestry=[];chain=[macro];seen=set();node=macro
    while node.get('inherited_qualified_receipt'):
        ref=node['inherited_qualified_receipt'];commit=ref['git_commit'];path=ref['receipt']
        assert (commit,path) not in seen,'Cyclic receipt ancestry'
        seen.add((commit,path));assert len(seen)<=20,'Unbounded receipt ancestry'
        raw=subprocess.check_output(['git','show',commit+':'+path],cwd=root)
        digest=hashlib.sha256(raw).hexdigest();assert digest==ref['sha256'],'Changed inherited receipt'
        node=json.loads(raw);chain.append(node);ancestry.append(dict(commit=commit,path=path,sha256=digest))
    for node in reversed(chain):
        routes.update(node.get('proposed_routes',{}));routes.update(node.get('qualified_changed_routes',{}))
    assert len(routes)==36,('Incomplete current36 candidate scene',sorted(routes))
    return routes,ancestry
