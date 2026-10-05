"""Exact line/circular-fillet length before CAD sweeping, in millimetres."""
import math
from w5_rounded_path import corner_offsets


def rounded_length(points,radius):
    cuts,units=corner_offsets(points,radius)
    angles=[math.acos(max(-1,min(1,sum(x*y for x,y in zip(a,b))))) for a,b in zip(units,units[1:])]
    return sum(math.dist(a,b) for a,b in zip(points,points[1:]))-2*sum(cuts)+radius*sum(angles)


def recipe_length(recipe):
    return (sum(e['length_mm'] for e in recipe['a']['edges'])+
            sum(e['length_mm'] for e in recipe['b']['edges'])+
            rounded_length(recipe['middle'],recipe['radius_mm']))
