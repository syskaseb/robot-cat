"""Conservative saved-surface keepouts for CHEAP planning, not collision proof.

Boxes enclose individual actual CAD faces, not entire empty carrier volumes.
A rejected reservation may be a false positive and must NEVER be reported as
an actual material contact. Final qualification still uses valid real BReps.
"""
import itertools,math
from open_prototype_path_preflight import samples
from route_current_leg_fanouts import sampling_parts


class FaceKeepouts:
    def __init__(self,rows):
        self.grid={};self.cell=12
        for row in rows:
            b=row['bounds_mm'];owner=row['owner']
            ranges=[range(math.floor((b[j]-4)/self.cell),math.floor((b[j+3]+4)/self.cell)+1) for j in range(3)]
            for key in itertools.product(*ranges):self.grid.setdefault(key,[]).append((owner,b))

    def hit(self,parts,radius,terminal_owners=(),terminal_land_mm=0):
        assert 0<radius<=4
        walked=0;previous=None
        for _,p in samples(sampling_parts(parts),step=1):
            if previous is not None:walked+=math.dist(previous,p)
            previous=p
            key=tuple(math.floor(v/self.cell) for v in p)
            for owner,b in self.grid.get(key,()):
                # Only the explicitly owned mating entry, never a whole
                #component or another object beside the terminal mouth.
                if owner in terminal_owners and walked<=terminal_land_mm:continue
                d2=sum(max(b[j]-p[j],0,p[j]-b[j+3])**2 for j in range(3))
                if d2<radius*radius:
                    return dict(other='PlanningKeepout/'+owner,point_mm=p,
                        conservative_reservation_only=True,actual_material_collision_proved=False)
        return None


def terminal_owners(role):
    """Logical leg fuse names map to the actual OUT contact, not its casing."""
    leg_fuses={'FL':'L1','FR':'R1','RL':'L4','RR':'R4'}
    if role.startswith('F_'):
        leg=role[2:4];index=role[4:]
        if leg in leg_fuses and index in ('1','2','3'):
            side=leg_fuses[leg][0];base=int(leg_fuses[leg][1])
            return (f'F_{side}{base+int(index)-1}_CP2_OUT',)
    return (role,role+'_CP2','W1Ref_'+role+'_CP2')
