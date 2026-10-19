"""Locate the first malformed sweep prefix, no world or native edits."""
import math
import feline_integrated_head_neck as neck
from receive_feline_positive_service_deck import pipe


def diagnostic(edges,r):
    for i,e in enumerate(edges):
        a=e.tangentAt(e.FirstParameter);b=edges[i-1].tangentAt(edges[i-1].LastParameter) if i else a
        try:s,p=pipe(edges[:i+1],r);status='OK'
        except AssertionError as exc:status=repr(exc)
        print('SWEEP_PREFIX',i+1,'tangent_dot',a.dot(b),'status',status,flush=True)
    return pipe(edges,r)


if __name__=='__main__':neck.pipe=diagnostic;neck.positive_channel_candidates()
