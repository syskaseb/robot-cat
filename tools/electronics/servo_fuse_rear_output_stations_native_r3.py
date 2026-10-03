"""Finish the coupled R2 layout from its five exact remaining witnesses.

Two RL anchors on the actual solid roof with a connecting wing. One full RR
landing on existing bank stock. Match the two existing input paths and both
bank/cover openings; no moved wires, bodies or speculative fasteners.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rear_output_stations_native_r2.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r2_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-rear-output-stations-native-r2','servo-fuse-rear-output-stations-native-r3')
code=code.replace("    pins={};V=A.Vector", "    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rear_output_stations_native_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_rear_output_stations_native_r2.py')\n    pins['hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r2/preflight.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r2/preflight.json')")
code=code.replace("[[-68,85,117.85,-64,89,118.05],[-53,85,117.85,-49,89,118.05]]", "[[-68,85,117.85,-64,89,118],[-76,85,117.85,-72,89,118]]")
code=code.replace("[[-64,-93,109.35,-60,-90,111.75],[-53,-93,109.35,-49,-90,111.75]]", "[[-53,-93,109.35,-49,-90,109.55]]")
code=code.replace("        owner='CandidateDeck' if leg=='RL' else 'Bank/RightClipAccessFinished_WORLD'", "        if leg=='RL':stock('RLAnchorWing',[-76,85,117.85,-64,89,120.25])\n        owner='CandidateDeck' if leg=='RL' else 'Bank/RightClipAccessFinished_WORLD'")
code=code.replace("    toolshapes=[Part.makeCylinder", '''    # Preserve the actual R4 input centreline/OD; carve matching space, not
    # accept the two measured wire conflicts. No new cable bend or extra lead.
    for ident in ('W038','W039'):
        fp=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4'/('release_0.0_'+ident+'_CENTERLINE.brep')
        path=Part.Wire(load(fp).Edges);edge=path.Edges[0];normal=edge.tangentAt(edge.FirstParameter);od=3.1
        profile=Part.Wire([Part.makeCircle(od/2+.2,path.Vertexes[0].Point,normal)])
        wiretools.append(path.makePipeShell([profile],True,False));full_paths.append((ident+'_existing_input',od,path,normal))
    toolshapes=[Part.makeCylinder''')
code=code.replace("    candidate['Cover']=owners['ModifiableCover'].cut", '''    for name,b in strap_slots:
        if name.startswith('RLFactory'):
            q=list(b);q[4]=max(q[4],111);cover_tools.append((name+'OpenSide',q))
    # R2's53.456mm3 RR rail/cover collision: one open-sided relief for the
    # entire station, not discrete cutouts that can trap it during assembly.
    rr=[b for name,b in stocks if name.startswith('RR')]
    cover_tools.append(('RRStationOpenSide',[min(b[0] for b in rr)-.3,-111,min(b[2] for b in rr)-.3,
        max(b[3] for b in rr)+.3,max(b[4] for b in rr)+.3,max(b[5] for b in rr)+.3]))
    left_tools=[(name,b) for name,b in strap_slots if name.startswith('RLHousingTieHead')]
    assert len(left_tools)==1
    candidate['BankLeft']=owners['Bank/LeftClipAccessFinished_WORLD'].cut(box(left_tools[0][1]))
    owners['Bank/LeftClipAccessFinished_WORLD']=candidate['BankLeft']
    candidate['Cover']=owners['ModifiableCover'].cut''')
code=code.replace("slots=slots,strap_slots=strap_slots,cover_tools=cover_tools,", "slots=slots,strap_slots=strap_slots,cover_tools=cover_tools,left_tools=left_tools,")
code=code.replace("('Cover','CoverRearOutputPassages.FCStd',None)]", "('Cover','CoverRearOutputPassages.FCStd',None),('BankLeft','ServoFuseBank.FCStd',None)]")
code=code.replace("        gp=native/source;pin(gp);d=A.openDocument(str(gp));", "        gp=ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1/ServoFuseBank.FCStd' if tag=='BankLeft' else native/source;pin(gp);d=A.openDocument(str(gp));")
code=code.replace("(slots+strap_slots if leg else cover_tools)", "(slots+strap_slots if leg else left_tools if tag=='BankLeft' else cover_tools)")
code=code.replace("            parent=d.RearOutputPassagesFinished", "            parent=d.LeftClipAccessFinished if tag=='BankLeft' else d.RearOutputPassagesFinished")
code=code.replace("replacements=['Deck','BankRight','Cover']", "replacements=['Deck','BankRight','Cover','BankLeft']")
code=code.replace("    for name,s in changed.items():\n        s.exportBrep", "    print('REAR_OUTPUT_STATIONS_SHARED_FIT',flush=True)\n    for name,s in changed.items():\n        s.exportBrep")
code=code.replace("    for tag,s in candidate.items():", "    print('REAR_OUTPUT_STATIONS_BOP_CHECK',flush=True)\n    for tag,s in candidate.items():")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
