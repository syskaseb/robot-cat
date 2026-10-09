"""Run only changed PI/SYS interfaces, reusing pinned unchanged partials."""
import open_prototype_source_receiving_space as S
import open_prototype_pi_family_plan as G

if __name__=='__main__':
    S.G=G
    S.run()
