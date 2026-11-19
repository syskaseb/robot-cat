"""Place intact reference and saved opaque CAD views on the same sheet."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
P=Path(__file__).parent;h=next(p for p in P.parents if p.name=="hardware")
out=Image.new("RGB",(1560,1072),"#f4f3f0");draw=ImageDraw.Draw(out)
font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",23)
files=[(h/"reference/appearance/ola-cat-reference.jpg","Robot Oli"),(P/"three-quarter.png","19D · widok ¾"),(P/"front.png","19D · przód"),(P/"side.png","19D · bok")]
for i,(path,label) in enumerate(files):
    left=(i%2)*780;top=(i//2)*536
    with Image.open(path) as src:
        im=ImageOps.contain(src.convert("RGB"),(768,484));out.paste(im,(left+(780-im.width)//2,top+44+(484-im.height)//2))
    draw.text((left+18,top+8),label,fill="#292928",font=font)
out.save(P/"ola-and-19D.png")

