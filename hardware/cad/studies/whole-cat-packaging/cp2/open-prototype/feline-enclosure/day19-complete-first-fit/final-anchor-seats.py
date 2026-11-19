from common import *
s=(O/'day19-common-floor-and-bundle-assembly/anchor-seats.py').read_text().replace('whole-cat19B.FCStd','whole-cat19I.FCStd').replace('B19_FrontFloor','H19_FrontFrame').replace('B19_RearFloor','E19_RearBase').replace('"anchor-seats.json"','"final-anchor-seats.json"')
exec(s)
