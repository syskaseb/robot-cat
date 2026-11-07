import time,json,hashlib,zipfile,os
t89=time.monotonic();cpu89=time.process_time();footlocal89=foot88.transformGeometry(inv85);framelocal89=frame86.transformGeometry(inv85);caplocal89=cap86.transformGeometry(inv85);sections89=[]
for mode in ['transverse0_axial_normal','normal4_axial_transverse']:
    if mode.startswith('transverse'):
        pl=Part.Face(Part.makePolygon([A.Vector(x,0,n) for x,n in [(-48,-4),(46,-4),(46,16),(-48,16),(-48,-4)]]))
    else:pl=Part.Face(Part.makePolygon([A.Vector(x,y,4) for x,y in [(-49,-15),(45,-15),(45,12),(-49,12),(-49,-15)]]))
    curves=[]
    for name,s,col in [('lower_ladder',framelocal89,'#dd8619'),('removable_pressure_half',caplocal89,'#8755b5'),('current_Ankle_part123',footlocal89,'#ca293b')]+[(k,wirelocal86[k],'#1f987c') for k in ['D','V','G']]:
        se=s.section(pl);edges=[]
        for edge in se.Edges:
            edges.append([[p.x,p.z if mode.startswith('transverse') else p.y] for p in edge.discretize(Deflection=.08)])
        curves.append(dict(name=name,color=col,curves=edges))
    sections89.append(dict(mode=mode,rows=curves))
p89=OUT/'day07-SOURCE-open-ladder-C1-received-sections-and-next-interface.json';assert not p89.exists();d89=dict(id=p89.stem,status='C1_USEFUL_SUPPORTED_LADDER_RECEIVED_ANKLE_END_INTERFACE_HOLD',source_material_receipt=p86.name,source_material_sha256=hashlib.sha256(p86.read_bytes()).hexdigest(),source_completion_receipt=p87.name,source_completion_sha256=hashlib.sha256(p87.read_bytes()).hexdigest(),source_profile_facts=p88.name,source_profile_facts_sha256=hashlib.sha256(p88.read_bytes()).hexdigest(),sections=sections89,
 named_negative=dict(other=footname88,owner='Motion_RL_Ankle',gap_mm=newrows87[-1]['gap_mm'],required_mm=1.25,positive_gap_not_contact=True,actual_print_corner_local=[-43,-7,6],other_witness_local=[-43.31591014337702,-8.003760551338466,6],new_material_members=['lower:continuous_left_beam','upper:continuous_cap_plate']),
 causal_decision='Staticendfailurebelongs toEXTERIORrectangularsource-landloadinterface, notnominal3wireprofilecapacity: fullD/V/Gneutral+sourcegroundENDgaps3.590308/6.905437/9.163300. Continuousmotion/4fulltieheads/tails stillOPEN, notPASSfrom2states. NextONEstrategy is anANKLE_FACING_OPEN_FORK_SOURCE_LAND pluspurposefuljointclearancebay: separateactual9land/sleevepressure/bearingfromouterboxcorner, carrylandthroughinboardsupportedfork/actualsidebeamjoint+selectedlandtie, preservecurrentwire/jointposes iftheFULLrequiredAnklezoneandfullstockfit. FIRSTreadactualmovingfootbayagainstfullfunctional9profiles/stock/usefulloadsections; no staticmicrocornertrim/poseoffset/C2 ofthis86rectframe. Iffunctionalcapacityfails, thenwholeSOURCEspatialsplice/landpackaging mustchange withsame selectedparts/physicalunitbudgets. No newgeometrybuiltfornextstrategy.',
 unchanged_whole_SOURCE='9IDs/12portions/4MAX3physicalunits/source14/terminal11/lap4/3x8/3x20/2x9/850/900. CurrentA/U/fit/slackNULL, no oldprefixor205claim. Bodylandingroot/regions/motion/stocknotrunafterAnklenegative. Sourcecurrent1292/effective1311unchanged.',
 full_tie_source_binding='2T18I145structural +2T18R100land unchanged. Actualfeed/head/closure/tail NOTreceived becauseprintstaticfailed first; NOtrim/newstock/debitPASS. Newproperrectanglecentreline formula=2*(W+H+2t), notold2*(W+H+t), sourceunitproofmustuseactualreturnwidth andtailstack.',
 selected=False,N01_complete=False,operation_seconds=time.monotonic()-t89,process_cpu_seconds=time.process_time()-cpu89);p89.write_bytes((json.dumps(d89,ensure_ascii=False,indent=2)+'\n').encode());print('LADDER_SECTIONS89',d89['operation_seconds'],d89['process_cpu_seconds'],hashlib.sha256(p89.read_bytes()).hexdigest(),flush=True)
