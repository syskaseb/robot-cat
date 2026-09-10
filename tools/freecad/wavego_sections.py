"""Non-destructive presentation snapshots; cuts are made with FreeCAD MCP tools.

Run in FreeCAD with __file__ set. This does not edit the mechanical source.
Snapshot geometry is frozen, not a second editable construction model.
"""
import json
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Draft

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/wavego/mechanics'
NAME = 'WAVEGO_electronics_sections'
SHELLS = {
    'Base': 'CAT_Base_Chassis_Tray', 'Lid': 'CAT_Back_Lid',
    'Head': 'CAT_Head_Shell', 'Neck': 'CAT_Neck_Load_Frame',
    'Face': 'CAT_Face_Mask', 'TailMount': 'CAT_Tail_Mount',
    'Tail': 'CAT_Tail', 'CameraCarrier': 'CAT_Camera_Carrier',
}
COLORS = {'lower': (0.94, 0.61, 0.18), 'upper': (0.15, 0.69, 0.67),
          'head': (0.40, 0.72, 0.31), 'neck': (0.63, 0.43, 0.78),
          'tail': (0.63, 0.43, 0.78)}


def prepare():
    source = App.getDocument('WAVEGO_cat_mechanical')
    assert NAME not in App.listDocuments(), 'Presentation already exists; reuse it'
    data = json.loads((OUT / 'components.json').read_text(encoding='utf-8'))
    mapping = json.loads((OUT.parent / 'layout/object-map.json').read_text(encoding='utf-8'))
    doc = App.newDocument(NAME)
    groups = {key: doc.addObject('App::DocumentObjectGroup', key)
              for key in ('ShellSnapshots', 'ComponentEnvelopes', 'ChassisContext', 'ViewLabels')}

    def snapshot(original, name, group, color):
        obj = doc.addObject('Part::Feature', name)
        shape = original.Shape.copy()
        shape.Placement = original.getGlobalPlacement()
        obj.Shape = shape
        obj.Label = original.Label
        obj.addProperty('App::PropertyString', 'SourceObject', 'Snapshot')
        obj.SourceObject = original.Name
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = (0.14, 0.17, 0.20)
        obj.ViewObject.DisplayMode = 'Flat Lines'
        group.addObject(obj)
        return obj

    for key, name in SHELLS.items():
        snapshot(source.getObject(name), 'Shell_' + key, groups['ShellSnapshots'], (0.64, 0.67, 0.70))
    for c in data['components']:
        obj = snapshot(source.getObject(mapping[c['id']]), 'Comp_' + c['id'],
                       groups['ComponentEnvelopes'], COLORS[c['zone']])
        for prop, value in [('ComponentId', c['id']), ('EnvelopeStatus', c['status']), ('MountingNote', c.get('note', 'Mounting design pending'))]:
            obj.addProperty('App::PropertyString', prop, 'Component envelope')
            setattr(obj, prop, value)
    for o in source.Objects:
        if o.TypeId != 'Part::Feature' or not o.Name.startswith('Part__Feature') or o.Shape.isNull():
            continue
        if o.Label in ('TopCover', 'Part9', 'Part001'):
            continue
        snapshot(o, 'Context_' + o.Name, groups['ChassisContext'], (0.72, 0.74, 0.77))
    doc.Label = 'WAVEGO - przekroje elektroniki / rezerwy montazowe'
    doc.recompute()
    return doc


def refresh_from_mechanical():
    """Explicitly refresh existing snapshots; keep cuts, labels and controls.

    Call only after backing up the open presentation. This never edits the
    construction source and is deliberately not called on every view switch.
    """
    source = App.getDocument('WAVEGO_cat_mechanical')
    doc = App.getDocument(NAME)
    pending = []
    for obj in doc.Objects:
        if 'SourceObject' not in obj.PropertiesList:
            continue
        original = source.getObject(obj.SourceObject)
        assert original is not None, obj.SourceObject
        shape = original.Shape.copy()
        shape.Placement = original.getGlobalPlacement()
        assert not shape.isNull() and shape.isValid(), original.Name
        pending.append((obj, shape))
    assert len(pending) == 157, 'Unexpected snapshot structure; inspect first'
    doc.openTransaction('Refresh electronics presentation from mechanical model')
    try:
        for obj, shape in pending:
            obj.Shape = shape
        # OCC refinement of the domed face's half-cut creates an invalid
        # result; the unrefined native Part::Cut is valid (two sections).
        doc.getObject('Cut_Face').Refine = False
        doc.recompute()
        for key in ('Base', 'Lid', 'Head', 'Neck', 'Face', 'CameraCarrier'):
            cut = doc.getObject('Cut_' + key)
            # A virtual half-cut may split a one-solid face into disconnected
            # sections (e.g. the cheek bridge is on the removed side).
            # Require valid solid geometry, not physical connectivity after cutting.
            assert cut and cut.Shape.isValid() and len(cut.Shape.Solids) >= 1, key
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    return len(pending)


def label(doc, name, lines, point, top=False, height=4.0):
    obj = next((o for o in doc.getObject('ViewLabels').Group
                if getattr(o, 'SectionLabelKey', '') == name), None)
    rotation = App.Rotation() if top else App.Rotation(App.Vector(1, 0, 0), 90)
    placement = App.Placement(App.Vector(*point), rotation)
    if obj is None:
        obj = Draft.make_text(lines, placement=placement, height=height)
        obj.Label = name
        obj.addProperty('App::PropertyString', 'SectionLabelKey', 'Presentation')
        obj.SectionLabelKey = name
        doc.getObject('ViewLabels').addObject(obj)
    else:
        obj.Placement = placement
    obj.Text = [lines] if isinstance(lines, str) else lines
    obj.ViewObject.FontSize = height
    obj.ViewObject.TextColor = (0.10, 0.14, 0.19)
    obj.Visibility = True
    return obj


def show(mode='side'):
    doc = App.getDocument(NAME)
    App.setActiveDocument(NAME)
    Gui.updateGui()
    Gui.Selection.clearSelection()
    data = json.loads((OUT / 'components.json').read_text(encoding='utf-8'))
    groups = ('ShellSnapshots', 'ComponentEnvelopes', 'ChassisContext', 'ViewLabels')
    for name in groups:
        doc.getObject(name).Visibility = True
    for o in doc.Objects:
        if hasattr(o, 'Shape') or 'SectionLabelKey' in o.PropertiesList or o.Name.startswith(('Origin', 'X_Axis', 'Y_Axis', 'Z_Axis', 'XY_Plane', 'XZ_Plane', 'YZ_Plane')):
            o.Visibility = False
    if hasattr(Gui, 'Snapper') and getattr(Gui.Snapper, 'grid', None):
        Gui.Snapper.grid.off()

    middle = {'Pi', 'Speaker', 'TerminalStrip', 'FrontDisconnects', 'RearDisconnects', 'TailServo'}
    upper = {'Grove', 'ReSpeaker', 'BusAdapter', 'MainPower', 'Amplifier', 'Touch', 'BulkCap'}
    power = {'TerminalStrip', 'FuseRR', 'FuseRL', 'FuseFR', 'FuseFL', 'MainPower', 'FrontDisconnects', 'RearDisconnects'}
    head = {'PanServo', 'TiltServo', 'Camera', 'IR', 'ToF'}
    ids = ({c['id'] for c in data['components']} if mode == 'side' else
           {'Battery', 'Pololu', 'AuxBuck', 'IMU'} if mode == 'lower' else
           middle if mode == 'middle' else upper if mode == 'upper' else power if mode == 'power' else head)
    for cid in ids:
        doc.getObject('Comp_' + cid).Visibility = True
        if cid in ('PanServo', 'TiltServo', 'TailServo'):
            doc.getObject('Comp_' + cid).ViewObject.ShapeColor = COLORS['tail']

    if mode in ('side', 'head'):
        for key in ('Base', 'Lid', 'Head', 'Neck', 'Face', 'CameraCarrier'):
            o = doc.getObject('Cut_' + key)
            if o and (mode == 'side' or key in ('Head', 'Neck', 'Face', 'CameraCarrier')):
                o.Visibility = True
                o.ViewObject.DisplayMode = 'Flat Lines'
                o.ViewObject.ShapeColor = (0.64, 0.67, 0.70)
                o.ViewObject.LineColor = (0.22, 0.25, 0.29)
        if mode == 'side':
            for key in ('Tail', 'TailMount'):
                doc.getObject('Shell_' + key).Visibility = True
    elif mode in ('middle', 'upper', 'power'):
        obj = doc.getObject('Shell_Base')
        obj.Visibility = True
        obj.ViewObject.DisplayMode = 'Wireframe'

    for o in doc.getObject('ChassisContext').Group:
        b = o.Shape.BoundBox
        if mode == 'side':
            o.Visibility = b.YMin >= 0 or 'MainFrame' in o.Label or 'BottomCover' in o.Label
        elif mode in ('lower', 'middle', 'upper', 'power'):
            o.Visibility = any(t in o.Label for t in ('MainFrame', 'SidePanel', 'BottomCover'))

    if mode == 'side':
        title = ['WAVEGO / wnetrze robota', 'Przekroj obudowy Y=0; elektronika pokazana w calosci']
        label(doc, 'SideTitle', title, (-210, -160, 274), height=10)
        label(doc, 'SideFooter', ['01 LiPo   03 druga przetwornica   04 IMU   05 Pi + HAT + chlodzenie',
                                 '06 glosnik   08 PCA9685   09 ReSpeaker   21/22 serwa glowy   26 serwo ogona',
                                 'Kolory = rezerwy miejsca. Mocowania modulow i naped ogona NIE sa ukonczone.'],
              (-210, -160, -175), height=7)
        numbered = {'Battery', 'AuxBuck', 'IMU', 'Pi', 'Speaker', 'Grove', 'ReSpeaker', 'PanServo', 'TiltServo', 'TailServo'}
        for c in data['components']:
            if c['id'] in numbered:
                x, y, z = c['min']; dx, dy, dz = c['size']
                label(doc, 'SideNum_' + c['id'], c['label'][:2], (x + dx/2 - 3, -100, z + dz/2), height=9)
    elif mode in ('lower', 'middle', 'upper', 'power'):
        title = {'lower': 'DOL / pakiet i przetwornice', 'middle': 'SRODEK / komputer, glosnik, dystrybucja', 'upper': 'GORA / sterowanie i audio', 'power':'ZASILANIE / listwa, bezpieczniki, zlacza'}[mode]
        label(doc, mode + '_title', [title, 'Widok z gory; pozostale warstwy ukryte; przod = -X (lewo)'], (-115, 95, 280), top=True, height=7)
        descriptions = {'Battery':'01 LiPo', 'Pololu':'02 Pololu', 'AuxBuck':'03 5 V', 'IMU':'04 IMU',
                        'Pi':'05 Pi + HAT', 'Speaker':'06 Glosnik', 'TerminalStrip':'07 Listwa',
                        'Grove':'08 PCA9685', 'ReSpeaker':'09 ReSpeaker', 'BusAdapter':'10 Bus Adapter',
                        'MainPower':'11 Zasilanie', 'Amplifier':'12', 'Touch':'19', 'BulkCap':'20',
                        'TailServo':'26 Serwo', 'FrontDisconnects':'18', 'RearDisconnects':'17'}
        for c in data['components']:
            if c['id'] in ids:
                x, y, z = c['min']; dx, dy, dz = c['size']
                text = descriptions.get(c['id'], c['label'][:2])
                point = (x + 2, y + dy/2, 250)
                if mode == 'lower' and c['id'] == 'AuxBuck':
                    text, point = '03', (x+4, y+dy-3, 250)
                if mode == 'lower' and c['id'] == 'IMU':
                    text, point = '04 IMU', (x+2, y+dy/2, 250)
                if mode == 'power' and c['id'] == 'TerminalStrip':
                    point = (x+3, y+3, 250)
                label(doc, mode + '_' + c['id'], text, point, top=True, height=6)
        if mode == 'upper':
            label(doc, 'UpperLegend', ['12 wzmacniacz MAX98357A   19 dotyk TTP223   20 opcjonalny kondensator',
                                      'Bezpieczniki pod tymi modulami: osobny widok ZASILANIE'], (-115,-90,280), top=True, height=5)
        if mode == 'lower':
            label(doc, 'LowerLegend', '03 druga przetwornica 5 V; 04 IMU znajduje sie NAD nia', (-115,-73,280), top=True, height=5)
        if mode == 'power':
            label(doc, 'PowerLegend', ['13-16 cztery oprawki bezpiecznikow nad listwa',
                                      '17/18 odlaczanie tylnych/przednich nog; wyzsze moduly ukryte'], (-115,-90,280), top=True, height=5)
    else:
        for key in ('Head', 'Neck', 'Face', 'CameraCarrier'):
            o = doc.getObject('Cut_' + key)
            if o:
                o.Visibility = False
        doc.getObject('Shell_Head').Visibility = True
        doc.getObject('Shell_Head').ViewObject.DisplayMode = 'Wireframe'
        doc.getObject('Shell_CameraCarrier').Visibility = True
        label(doc, 'HeadTitleTop', ['GLOWA / wnetrze od gory', 'Przod = -X (lewo)'], (-193,65,280), top=True, height=5)
        label(doc, 'HeadLegendTop', ['23 Kamera   24 IR   25 ToF', '21/22 - rezerwy serw, nie gotowe napedy'], (-193,-66,280), top=True, height=4)
        for c in data['components']:
            if c['id'] in ids:
                x, y, z = c['min']; dx, dy, dz = c['size']
                point = (x+2, y+dy/2, 270)
                if c['id'] == 'PanServo':
                    point = (-110,-14,270)
                label(doc, 'HeadTop_' + c['id'], c['label'][:2], point, top=True, height=5)
    doc.recompute()
    return doc


def zoom(factor=0.75):
    """Tighter presentation framing than the GUI's fitAll margin."""
    node = Gui.getDocument(NAME).activeView().getCameraNode()
    if hasattr(node, 'height'):
        node.height.setValue(node.height.getValue() * factor)
    Gui.Selection.clearSelection()


def open_panel():
    """Local FreeCAD controls for switching the saved presentation's layers."""
    from PySide import QtWidgets
    window = Gui.getMainWindow()
    old = window.findChild(QtWidgets.QDockWidget, 'WAVEGO_Sections_Dock')
    if old:
        old.close()
        old.deleteLater()
    dock = QtWidgets.QDockWidget('WAVEGO / przekroje elektroniki', window)
    dock.setObjectName('WAVEGO_Sections_Dock')
    body = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(body)
    whole = QtWidgets.QPushButton('Caly kot / model konstrukcyjny')
    whole.clicked.connect(lambda checked=False: show_whole_cat())
    layout.addWidget(whole)
    for mode, text in [('side','Przekroj boczny'), ('lower','Dol: pakiet i przetwornice'),
                       ('middle','Srodek: komputer i glosnik'), ('upper','Gora: sterowanie i audio'),
                       ('power','Zasilanie: bezpieczniki i zlacza'), ('head','Glowa: kamera, IR i ToF')]:
        button = QtWidgets.QPushButton(text)
        def select(checked=False, mode=mode):
            show(mode)
            view = Gui.getDocument(NAME).activeView()
            if mode == 'side':
                view.viewFront()
            else:
                view.viewTop()
            view.fitAll()
            if mode != 'side':
                zoom()
        button.clicked.connect(select)
        layout.addWidget(button)
    note = QtWidgets.QLabel('Kolory to rezerwy montazowe.\nNapedy glowy/ogona i mocowania\nmodulow nie sa jeszcze ukonczone.')
    note.setWordWrap(True)
    layout.addWidget(note)
    dock.setWidget(body)
    from PySide import QtCore
    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    dock.show()
    Gui._wavego_sections_dock = dock
    return dock


def show_whole_cat():
    """Return to the uncut mechanical source without saving or editing shapes."""
    name = 'WAVEGO_cat_mechanical'
    if name not in App.listDocuments():
        App.openDocument(str(OUT.parent / (name + '.FCStd')))
    App.setActiveDocument(name)
    Gui.updateGui()
    doc = App.getDocument(name)
    path = ROOT / 'tools/freecad/wavego_mechanics_check.py'
    ns = {'__file__': str(path), '__name__': 'mechanical_view_only'}
    exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), ns)
    ns['presentation'](doc, mode='closed')
    view = Gui.getDocument(name).activeView()
    # Explicit world basis: the actual front is -X, not FreeCAD's default
    # isometric (+X) side. Avoid orientation inherited from another document.
    view.setCameraOrientation(App.Rotation(App.Vector(0, -1, 0),
        App.Vector(0, 0, 1), App.Vector(-1, -0.65, 0.45), 'ZXY').Q)
    view.fitAll()
    node = view.getCameraNode()
    if hasattr(node, 'height'):
        node.height.setValue(node.height.getValue() * 0.8)
    Gui.Selection.clearSelection()


def export_views():
    """Capture each explicit document view; MCP's active-view capture can be stale.

    Geometry must already be refreshed. Leave the whole construction model
    visible, with the actual -X front facing the viewer.
    """
    for mode in ('side', 'lower', 'middle', 'upper', 'power', 'head'):
        show(mode)
        view = Gui.getDocument(NAME).activeView()
        if mode == 'side':
            view.viewFront()
        else:
            view.viewTop()
        view.fitAll()
        if mode != 'side':
            zoom()
        Gui.updateGui()
        Gui.getDocument(NAME).activeView().saveImage(
            str(OUT / ('section-' + mode + '.png')), 1600, 1200, 'White')
    show_whole_cat()
    Gui.updateGui()
    Gui.getDocument('WAVEGO_cat_mechanical').activeView().saveImage(
        str(OUT / 'cat-full.png'), 1600, 1200, 'White')
    return 7


def export_face_details():
    """CAD close-ups, without representing envelope boxes as real lenses."""
    doc = App.getDocument('WAVEGO_cat_mechanical')
    visibility = {o.Name: o.Visibility for o in doc.Objects if hasattr(o, 'Visibility')}
    try:
        for obj in doc.Objects:
            if hasattr(obj, 'Shape') and hasattr(obj, 'Visibility'):
                obj.Visibility = False
        for name in ('CAT_Head_Shell', 'CAT_Face_Mask'):
            obj = doc.getObject(name)
            obj.Visibility = True
            obj.Tip.Visibility = True
        view = Gui.getDocument(doc.Name).activeView()
        for name, direction in [('front', (-1, 0, 0)), ('detail', (-1, -0.65, 0.35))]:
            view.setCameraOrientation(App.Rotation(App.Vector(0, -1, 0),
                App.Vector(0, 0, 1), App.Vector(*direction), 'ZXY').Q)
            view.fitAll()
            Gui.updateGui()
            view.saveImage(str(OUT / ('cute-face-' + name + '.png')), 1200, 1000, 'White')
    finally:
        for name, visible in visibility.items():
            doc.getObject(name).Visibility = visible
