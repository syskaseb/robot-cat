"""Complete the current lateral installation after the source file identified the audio boot as a textual allowance."""
from pathlib import Path
import json,math
P=Path(__file__).parent
s=(P/'fit-assembly.py').read_text();exec(s[:s.index("m=json.loads")])
m=json.loads((P/'mic-port.json').read_bytes())
add('G19_PiAudioBoot',box(-20,-26.39,104.6,26,14,13),(.53,.41,.67),'project USB-A boot on upper opposite stack; physical delivered plug unknown')
hide('G19_PiAudioBoot')
wr('mounted-mic.json',dict(board=bounds(sh('E19_ReSpeakerSource')),bodies=len(sh('E19_ReSpeakerSource').Solids),steel={n:bounds(sh(n)) for n in group('HB_MIC_')},Pi_audio_field=bounds(sh('G19_PiAudioBoot')),mouth=m['mouth'],positive_X=True))
exec(s[s.index("changed=['E19_RearBase"):])
