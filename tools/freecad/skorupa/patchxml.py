import re, os
SRC='/tmp/claude-0/v17/src'
p=os.path.join(SRC,'Document.xml'); x=open(p,encoding='utf-8').read(); orig=x

def blk(name, s):
    m=re.search(r'<Object name="%s"[ >]'%re.escape(name), s); i=m.start()
    j=s.index('</Object>', i)+len('</Object>'); return i,j,s[i:j]

IDENT = ('<PropertyPlacement Px="0.0000000000000000" Py="0.0000000000000000" Pz="0.0000000000000000" '
         'Q0="0.0000000000000000" Q1="0.0000000000000000" Q2="0.0000000000000000" Q3="1.0000000000000000" '
         'A="0.0000000000000000" Ox="0.0000000000000000" Oy="0.0000000000000000" Oz="1.0000000000000000"/>')

TOUCHED = ['PiHatCooling','PowerDistribution','PiCableAccess','PWMControllerUnplaced','MainSwitch',
           'ChargeSocketXT60','BalancerPort','Speaker','BackCover','TailBase','BatteryTray',
           'NeckBridge','NeckYawServo','TailBridge','TailYawServo','TailLiftServo',
           'BellyPod','NeckColumn']
for n in TOUCHED:
    i,j,b = blk(n,x)
    b2 = re.sub(r'<PropertyPlacement [^/]*/>', IDENT, b, count=1)
    b2 = b2.replace('<Bool value="false"/>','<Bool value="true"/>')
    x = x[:i]+b2+x[j:]

def relabel(n, lab, s):
    i,j,b = blk(n,s)
    b2 = re.sub(r'(<Property name="Label" type="App::PropertyString"[^>]*>\s*<String value=")[^"]*(")',
                lambda m: m.group(1)+lab+m.group(2), b, count=1)
    return s[:i]+b2+s[j:]

for n,lab in [
    ('PWMControllerUnplaced','PCA9685 16-ch PWM 60 x 40 x 15 - sterownik serw'),
    ('MainSwitch','Wlacznik glowny - panel serwisowy, prawy bok'),
    ('ChargeSocketXT60','Gniazdo ladowania XT60 - panel serwisowy'),
    ('BalancerPort','Port balansera 3S - panel serwisowy'),
    ('BackCover','Grzbiet v3 - kratka glosnika + otwory zlaczy'),
    ('TailBase','Nasada ogona - obudowa z kieszeniami serw'),
    ('BatteryTray','Kolyska akumulatora - gniazdo 90 x 43 x 19'),
    ('PiCableAccess','Dostep do wtykow Pi - rezerwa (skrocona)'),
    ('PiHatCooling','Pi 5 / AI HAT+ / chlodzenie - rezerwa 25 mm'),
    ('PowerDistribution','Listwa / bezpieczniki / mostki - rezerwa'),
    ('Speaker','Glosnik 5 W 100 x 45 x 21 - pod kratka w grzbiecie'),
    ('UnplacedParts','Audio i sterowanie serwami'),
    ('BellyPod','Brzusiec - obudowa akumulatora, sciana 3 mm'),
    ('NeckColumn','Kolumna szyi - obudowa serwa, sciana 3 mm'),
    ('NeckBridge','Belka szyi - skrocona do obrysu skorupy'),
    ('TailBridge','Belka ogona - skrocona do obrysu skorupy'),
]:
    x = relabel(n, lab, x)

assert x!=orig
open(p,'w',encoding='utf-8').write(x); print("Document.xml OK")

g=os.path.join(SRC,'GuiDocument.xml')
s=open(g,encoding='utf-8').read()
for nm in ('Speaker','PWMControllerUnplaced'):
    k=s.find('<ViewProvider name="%s"'%nm)
    if k>=0:
        e=s.index('</ViewProvider>',k)
        s = s[:k] + re.sub(r'(<Property name="Visibility"[\s\S]{0,300}?<Bool value=")false(")', r'\g<1>true\g<2>', s[k:e]) + s[e:]
open(g,'w',encoding='utf-8').write(s); print("GuiDocument.xml OK")
