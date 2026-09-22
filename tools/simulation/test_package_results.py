import zipfile
import package_results as packaging


def test_archive_is_repeatable(tmp_path,monkeypatch):
    monkeypatch.setattr(packaging,'ROOT',tmp_path)
    source=tmp_path/'geometry.json';source.write_text('{"example": 1}',encoding='utf8')
    target=tmp_path/'inputs.zip'
    packaging.archive(target,[source],tmp_path)
    first=target.read_bytes();digest=target.with_suffix('.sha256').read_bytes()
    packaging.archive(target,[source],tmp_path)
    assert target.read_bytes()==first and target.with_suffix('.sha256').read_bytes()==digest
    with zipfile.ZipFile(target) as z:
        assert z.read('geometry.json')==source.read_bytes()
        assert z.getinfo('geometry.json').create_system==3


def test_packaging_does_not_rewrite_other_revisions(tmp_path,monkeypatch):
    out=tmp_path/'v29';out.mkdir()
    history=tmp_path/'v28';history.mkdir()
    old=history/'inputs.zip';old.write_bytes(b'untouched historical checkpoint')
    (out/'geometry.json').write_text('{}',encoding='utf8')
    (out/'meshes').mkdir();(out/'meshes/base_link.stl').write_text('solid example\nendsolid',encoding='ascii')
    (out/'trials').mkdir();(out/'trials/one.json').write_text('{}',encoding='utf8')
    monkeypatch.setattr(packaging,'ROOT',tmp_path);monkeypatch.setattr(packaging,'OUT',out)
    packaging.main()
    assert old.read_bytes()==b'untouched historical checkpoint'
    assert {p.name for p in out.glob('*.zip')}=={'inputs.zip','meshes.zip','telemetry.zip'}
