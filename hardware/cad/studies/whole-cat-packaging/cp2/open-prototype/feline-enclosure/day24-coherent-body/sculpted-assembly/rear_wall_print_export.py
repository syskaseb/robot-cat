"""Refine the two undersampled loft faces of the frozen rear base for STL.

OpenCascade already supplies matching trim boundaries. Keep those samples
verbatim, refine only the interiors on their exact UV surfaces, then check
the serialized mesh against the independent BRep volume.
"""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
import trimesh
from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS, TopoDS_Shape

HERE = Path(__file__).resolve().parent
WORK = Path(tempfile.gettempdir()) / "day24-coherent-body" / "sculpted-assembly"
FACES = (64, 124)
TOLERANCE_MM = .06
NATIVE_PIN = "ab43ac577077ccfb38e6dbffff537d0356680bbfaf9c3454694bed9dd9b14f58"


def pin(path):
    return sha256(path.read_bytes()).hexdigest()


def values(surface, uv):
    return np.array([surface.Value(u, v).Coord() for u, v in uv], dtype=float)


def edges_of(tri):
    return np.sort(np.stack((tri, np.roll(tri, -1, axis=1)), axis=2), axis=2)


def probe(vertices, uv, tri, surface):
    edges, index, counts = np.unique(edges_of(tri).reshape(-1, 2), axis=0,
                                     return_inverse=True, return_counts=True)
    edge_uv = uv[edges].mean(axis=1)
    center_uv = uv[tri].mean(axis=1)
    edge_xyz, center_xyz = values(surface, edge_uv), values(surface, center_uv)
    edge_error = np.linalg.norm(edge_xyz - vertices[edges].mean(axis=1), axis=1)
    center_error = np.linalg.norm(center_xyz - vertices[tri].mean(axis=1), axis=1)
    return edges, index.reshape(-1, 3), counts, edge_uv, edge_xyz, edge_error, center_uv, center_xyz, center_error


def refine(vertices, uv, tri, surface):
    source_count = len(tri)
    initial_boundary = None
    for _ in range(8):
        edges, index, counts, edge_uv, edge_xyz, edge_error, center_uv, center_xyz, center_error = probe(vertices, uv, tri, surface)
        assert np.all(counts <= 2)
        boundary = edges[counts == 1]
        if initial_boundary is None:
            initial_boundary = boundary
            original_max = float(max(edge_error.max(), center_error.max()))
        else:
            assert np.array_equal(initial_boundary, boundary)
        split = (counts == 2) & (edge_error > TOLERANCE_MM)
        extra = (center_error > TOLERANCE_MM) & ~np.any(split[index], axis=1)
        if not (split.any() or extra.any()):
            break
        mid = np.full(len(edges), -1, dtype=int)
        mid[split] = np.arange(len(vertices), len(vertices) + np.count_nonzero(split))
        centers = np.full(len(tri), -1, dtype=int)
        first = len(vertices) + np.count_nonzero(split)
        centers[extra] = np.arange(first, first + np.count_nonzero(extra))
        result = []
        for face, mids, center in zip(tri, mid[index], centers):
            a, b, c = face
            n = np.count_nonzero(mids >= 0)
            if n == 0:
                result.extend(((a,b,center),(b,c,center),(c,a,center)) if center >= 0 else (face,))
            elif n == 1:
                p = int(np.argmax(mids >= 0))
                a, b, c = np.roll(face, -p)
                e = mids[p]
                result.extend(((a,e,c),(e,b,c)))
            elif n == 2:
                p = (int(np.argmax(mids < 0)) + 1) % 3
                a, b, c = np.roll(face, -p)
                e, f, _ = np.roll(mids, -p)
                result.extend(((a,e,c),(e,b,f),(e,f,c)))
            else:
                e, f, g = mids
                result.extend(((a,e,g),(e,b,f),(f,c,g),(e,f,g)))
        vertices = np.vstack((vertices, edge_xyz[split], center_xyz[extra]))
        uv = np.vstack((uv, edge_uv[split], center_uv[extra]))
        tri = np.asarray(result, dtype=int)
    else:
        edges, _, counts, _, _, edge_error, _, _, center_error = probe(vertices, uv, tri, surface)
        assert np.array_equal(initial_boundary, edges[counts == 1])
    return vertices[tri], {
        "original_triangles":source_count,"refined_triangles":len(tri),"boundary_edges":len(initial_boundary),
        "original_sampled_deviation_mm":round(original_max,6),
        "refined_interior_edge_deviation_mm":round(float(edge_error[counts == 2].max()),6),
        "unchanged_boundary_sampled_deviation_mm":round(float(edge_error[counts == 1].max()),6),
        "refined_centroid_deviation_mm":round(float(center_error.max()),6),
    }


def raw_shape():
    receipt = json.loads((HERE / "native-readback.json").read_text(encoding="utf-8"))
    assert pin(HERE / receipt["document"]) == receipt["native_sha256"] == NATIVE_PIN
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / "ab43-saved-rear-base-for-volume.brep"
    with ZipFile(HERE / receipt["document"]) as archive:
        xml = ET.fromstring(archive.read("Document.xml"))
        saved = xml.find("./ObjectData/Object[@name='E19_RearBase']/Properties/Property[@name='Shape']/Part")
        assert saved is not None
        path.write_bytes(archive.read(saved.get("file")))
    body = TopoDS_Shape()
    assert BRepTools.Read_s(body, str(path), BRep_Builder())
    return path, body


def triangulate(body):
    BRepTools.Clean_s(body)
    operation = BRepMesh_IncrementalMesh(body, .045, False, .13, True)
    assert operation.IsDone()
    walker = TopExp_Explorer(body, TopAbs_FACE)
    batches, proof = [], {}
    rank = 0
    while walker.More():
        face = TopoDS.Face(walker.Current())
        loc = TopLoc_Location()
        pol = BRep_Tool.Triangulation_s(face, loc)
        assert pol is not None
        vertices = np.array([pol.Node(i).Transformed(loc.Transformation()).Coord()
                             for i in range(1, pol.NbNodes() + 1)])
        tri = np.array([pol.Triangle(i).Get() for i in range(1, pol.NbTriangles() + 1)]) - 1
        if face.Orientation() == TopAbs_REVERSED:
            tri = tri[:, ::-1]
        if rank in FACES:
            assert pol.HasUVNodes()
            uv = np.array([pol.UVNode(i).Coord() for i in range(1, pol.NbNodes() + 1)])
            surface = BRepAdaptor_Surface(face, True)
            assert np.linalg.norm(values(surface, uv) - vertices, axis=1).max() < .001
            tris, changes = refine(vertices, uv, tri, surface)
            proof[str(rank)] = changes
            print(rank, changes, flush=True)
        else:
            tris = vertices[tri]
        batches.append(tris)
        rank += 1
        walker.Next()
    assert len(proof) == len(FACES)
    return np.concatenate(batches), proof


def validate(tris, dst):
    points = tris.reshape(-1, 3)
    # Use the existing world-coordinate STL precision at the trim boundaries,
    # so two independently emitted copies of the same vertex stay connected.
    world32 = points.astype(np.float32)
    world, idx = np.unique(world32, axis=0, return_inverse=True)
    shift = -world.min(axis=0).astype(float)
    bed = (world.astype(float) + shift).astype(np.float32)
    unique, second = np.unique(bed, axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(vertices=unique, faces=second[idx].reshape(-1,3), process=False)
    print("mesh audit", mesh.is_watertight, mesh.is_winding_consistent, mesh.volume,
          "triangles", len(mesh.faces), "exact merge at bed",len(world)-len(unique), flush=True)
    assert mesh.is_volume
    assert np.all(mesh.area_faces > 0)
    mesh.export(dst, file_type="stl")
    saved = trimesh.load_mesh(dst, process=False)
    raw, inv = np.unique(np.asarray(saved.triangles,dtype=np.float32).reshape(-1,3), axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(vertices=raw,faces=inv.reshape(-1,3),process=False)
    counts = np.unique(edges_of(mesh.faces).reshape(-1,2), axis=0, return_counts=True)[1]
    assert len(counts) and np.all(counts == 2) and mesh.is_volume
    shells = sorted(mesh.split(only_watertight=False), key=lambda part: part.volume, reverse=True)
    # One outer shell plus the native, enclosed 0.294 mm³ negative shell.
    assert len(shells) == 2 and all(part.is_watertight for part in shells)
    outer, void = shells
    assert outer.volume > 0 and -.31 < void.volume < -.28
    assert np.all(void.bounds[0] > outer.bounds[0]) and np.all(void.bounds[1] < outer.bounds[1])
    return mesh, shift, [float(part.volume) for part in shells]


def run():
    path, body = raw_shape()
    gk = GProp_GProps()
    err = BRepGProp.VolumePropertiesGK_s(body, gk, 1e-6, False, True, False, False, False)
    reference_volume = gk.Mass()
    assert 0 <= err < 1.e-4 and 225000 < reference_volume < 226000
    tris, proof = triangulate(body)
    dst = WORK / "flat24S-E19_RearBase-PrintBed.stl"
    mesh, shift, shells = validate(tris, dst)
    error = abs(mesh.volume / reference_volume - 1)
    print("checked", reference_volume, mesh.volume, error, mesh.bounds, flush=True)
    assert error < .0075
    assert all(row["refined_centroid_deviation_mm"] < .10 for row in proof.values())
    record = {
        "native_sha256":NATIVE_PIN,"source":"E19_RearBase","exported_saved_brep_sha256":pin(path),
        "base_triangulation_mm":.045,"base_triangulation_angle_rad":.13,"faces":proof,
        "reference_volume_mm3":reference_volume,"reference_adaptive_error":err,"stl_volume_mm3":mesh.volume,
        "fractional_volume_error":error,"surface_file":dst.name,"sha256":pin(dst),"watertight":True,
        "triangles":len(mesh.faces),"signed_shell_volumes_mm3":shells,"assembly_translation_mm":shift.tolist(),"bounds_mm":mesh.bounds.tolist()
    }
    (HERE/"rear-refined-proof.json").write_text(json.dumps(record,indent=2)+chr(10),encoding="utf-8")


if __name__ == "__main__":
    run()
