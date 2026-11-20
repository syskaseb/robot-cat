"""Small axial-X adapters for the existing 20C receivers, in world mm."""
import math
from pathlib import Path
import FreeCAD as App
import Part

V=App.Vector

def box(x0,y0,z0,x1,y1,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))

def join(*shapes):
    return shapes[0].multiFuse(list(shapes[1:])).removeSplitter()

def bounds(shape):
    if shape.isNull():
        return None
    b=shape.BoundBox
    return [round(v,4) for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]

def cube(row):
    return box(*row)

def volume(a,b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return abs(a.common(b).Volume)

def xt60():
    # Upper load pad and two real source lands. The primary land bears at
    # Z132.25 and has a blind key, then the existing shoulder takes X load.
    deck=box(11.6,11.1,134.78,36.8,43.45,137.35)
    pads=[box(14.23,27.86,132.25,22,41.3,135.05),
          box(15.76,30.66,129.81,18.74,33.84,132.42),
          box(35.8,28.0,135.55,37.14,39.9,136.08)]
    # The right receiver wall is stepped off the deck's nominal X end.
    # A backward corner remains below 136.05 in the captured left key.
    back=box(11.6,28.0,132.9,12.73,40.0,136.5)
    part=join(deck,*pads,back).cut(box(12.71,27.68,131.8,14.23,40.26,136.29))
    part=part.cut(box(36.24,27.7,134.7,37.3,40.25,135.55))
    # Body tie wraps the inlet boot. The other tie passes around the 20C
    # shelf and is recessed below the connector seat.
    for y in (12.65,39.1):
        part=part.cut(box(29.0,y,134.59,32.45,y+3.38,137.5))
    part=part.cut(box(19.25,11.05,135.8,22.67,43.6,137.5))
    return part.removeSplitter()

def fuse_mount():
    tray=box(-71,15.55,131.35,-20,43.85,134.15)
    web=box(-62,40.4,131.4,-52,41.64,137.7)
    top=box(-62,41.56,135.1,-52,49.85,137.7)
    # Small underside tongue uses free volume just before the source
    # shelf thickens at Y50.7. It presses upward against the flange.
    lip=box(-62,41.53,129.9,-52,46.5,132.15)
    web_low=box(-62,40.4,129.9,-52,41.64,132.3)
    part=join(tray,web,top,lip,web_low)
    part=part.cut(box(-62.04,41.67,132.22,-51.96,49.92,135.1))
    for x in (-69.,-36.):
        for y in (16.02,40.28):
            part=part.cut(box(x,y,131.2,x+6.65,y+3.34,134.35))
    # The tie passes through the real rectangular through-slot at
    # X -58.7..-55.3, Y43.1..45.3; run it before sliding on the shoe.
    passage=box(-58.62,43.17,129.75,-55.38,45.22,137.87)
    lead_in=box(-58.62,40.3,130.13,-55.38,42.25,131.86)
    return part.cut(passage).cut(lead_in).removeSplitter()

def post_mount():
    # The frame corner is an 8 mm thick upright X -117..-109. The top
    # bears at Z107.5 and two cheeks close around it. The low foot then
    # goes aft, where the raised riser stays clear of the yaw saddle.
    foot=box(-119.65,-34.4,107.5,-103.3,-26.5,110.3)
    fixed_cheek=box(-119.65,-31.88,100.5,-117.23,-26.7,108.0)
    outer_key=box(-119.65,-35,104.3,-103.3,-32.24,109.0)
    boss=box(-108.77,-36.0,100.25,-99.35,-28.2,108.4)
    low=box(-109.0,-39.2,107.5,-100.82,-34.6,120.7)
    rise=box(-104.65,-39.2,118,-100.82,-34.6,139.9)
    rail_arm=box(-106.,-40,137,-100.82,-34.5,139.9)
    rail=box(-119,-56,137,-103.75,-18,139.9)
    foot=foot.cut(box(-108.8,-28.16,107.4,-100,0,110.4))
    part=join(foot,fixed_cheek,outer_key,boss,low,rise,rail_arm,rail)
    # WAGO body tie may be threaded at any chosen Y position.
    # The 2.15 mm thickness passage runs along Y for the adjustable tie.
    for x in (-118.55,-106.5):
        part=part.cut(box(x,-53.2,136.85,x+2.15,-20.95,140.03))
    # DIN912 M3x12 clamps against the unchanged X=-109 face.
    centre=V(-100.15,-31.3,103.55)
    screw_hole=Part.makeCylinder(1.65,10.7,centre,V(-1,0,0))
    head_clear=Part.makeCylinder(2.85,2.55,V(-97.7,centre.y,centre.z),V(-1,0,0))
    nut_slot=box(-103.04,-34.6,100.73,-100.45,-28.0,106.37)
    # Nut inserts through the exposed lower face before the saddle
    # is installed. An open slot supports the flat sides against spin.
    nut_insert=box(-103.04,-34.6,100.0,-100.45,-28.0,103.9)
    part=part.cut(screw_hole).cut(head_clear).cut(nut_slot).cut(nut_insert)
    bolt=join(Part.makeCylinder(1.5,12,V(-109.0,centre.y,centre.z),V(1,0,0)),
              Part.makeCylinder(2.75,3,V(-97.01,centre.y,centre.z),V(1,0,0)))
    radius=2.75/math.cos(math.pi/6)
    pts=[V(-103.0,centre.y+radius*math.cos(i*math.pi/3),
           centre.z+radius*math.sin(i*math.pi/3)) for i in range(6)]
    nut=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(2.4,0,0))
    nut=nut.cut(Part.makeCylinder(1.5,2.6,V(-103.1,centre.y,centre.z),V(1,0,0)))
    return part.removeSplitter(),bolt,nut

def forms():
    post,bolt,nut=post_mount()
    return {"D20_XT60_Axial_Adapter":xt60(),"D20_F0_Open_Adapter":fuse_mount(),
            "D20_POST_Aft_Slotted":post,"D20_POST_Clamp_M3x12":bolt,
            "D20_POST_Clamp_Nut":nut}
