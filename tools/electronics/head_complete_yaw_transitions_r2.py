"""Continue full interface after demonstrated radius/cover conflicts, not repeat.

The expanded span permits31.5mm minimum at the sampled poses. Segmenting the
Bezier preserves its actual centerline, rather than replacing a failed solid
operation by a zero-collision claim. Old partial result remains diagnostic.
"""
import head_complete_yaw_transitions_r1 as B
B.OUT=B.ROOT/'hardware/electronics/full-cat/head-complete-yaw-transitions-r2'
B.END_X=-20
B.FLEX_LENGTH=250
if __name__=='__main__': B.main()
