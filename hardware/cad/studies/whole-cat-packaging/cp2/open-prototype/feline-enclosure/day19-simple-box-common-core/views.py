from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
v=G.activeDocument().activeView()
skins=['E19_FrontShroud','E19_ForeLid','E19_RearLid','D19D_Face','D19D_PitchBack','E19_UpperYawCover']+group('D19D_Iris','D19D_Pupil','D19D_Ear')+['D19D_Nose']
air=['BUS25514_installed','Pi_components_and_cooling','D19D_ToF','C19_FFC190','D19_DATA_STORAGE_LAYER','B19_TailJRUnderBank','B19_TailLaps','D18C_DATA_BUS_FULL26_PROJECT_BOOT','D19D_HeadServoWires','Pi_USB_DATA_Delock_mating','D19_MIC_FULL_HEIGHT_RESERVE','D19_AUX_POPULATED_9P5_RESERVE']+group('E19_Field')
skins+=['E19_BatteryDoor']
for n in ['D19D_HeadServoWires','D19_DATA216_OPEN_RESERVE','ReSpeakerLite_on_REMOVABLE_back','E19_MTA_sample_land']:hide(n)
for name,pos,inside in [('interior',(.28,-.65,1.45),True),('side',(0,-1,.06),False),('front',(-1,0,.06),False),('three-quarter',(-.62,-1,.39),False)]:
    for n in air:
        o=D.getObject(n)
        if o:o.ViewObject.Visibility=inside and n not in ('D19D_HeadServoWires','BUS25514_installed')
    for n in skins:D.getObject(n).ViewObject.Visibility=not inside
    z=V(*pos);z.normalize();x=V(0,0,1).cross(z);x.normalize()
    v.setCameraOrientation(A.Rotation(x,z.cross(x),z,'ZXY').Q);v.fitAll();v.redraw();G.updateGui();v.saveImage(str(P/(name+'.png')),1440,960,'White')
D.recompute();D.save()
