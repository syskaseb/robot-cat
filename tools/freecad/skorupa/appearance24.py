"""Retain per-face materials, not merely the feature's default ShapeColor."""

def copy_appearance(source, target):
    a=source.ViewObject; b=target.ViewObject
    for prop in ['ShapeColor','LineColor','Transparency','DisplayMode',
                 'Deviation','AngularDeflection','DiffuseColor','ShapeAppearance']:
        if prop in a.PropertiesList and prop in b.PropertiesList:
            setattr(b,prop,getattr(a,prop))
    for prop in ['MaterialNote','Mounting','SourceRecipe']:
        if prop in source.PropertiesList and source.getTypeIdOfProperty(prop)=='App::PropertyString':
            if prop not in target.PropertiesList:
                target.addProperty('App::PropertyString',prop,'Manufacturing')
            setattr(target,prop,getattr(source,prop))
    assert list(a.DiffuseColor)==list(b.DiffuseColor),source.Name
