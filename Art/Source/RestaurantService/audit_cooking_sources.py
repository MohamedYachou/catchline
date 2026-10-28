"""Read-only production .blend inspection, separate from exported FBX audit."""
import bpy, json, hashlib
from pathlib import Path

O = Path(__file__).resolve().parent
records = json.loads((O / 'cooking-manifest.json').read_text())
results = []
for rec in records:
    path = O / 'blends' / (rec['name'] + '.blend')
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    objects = list(bpy.context.scene.objects)
    assert len(objects) == 1 and objects[0].type == 'MESH', rec['name']
    ob = objects[0]
    assert ob.get('service_props_task') == 'SERVICE-PROPS-2'
    assert ob.location.length < 1e-7 and max(abs(v - 1) for v in ob.scale) < 1e-7
    assert ob.rotation_euler.to_matrix().is_identity
    ob.data.calc_loop_triangles()
    assert len(ob.data.loop_triangles) == rec['tris']
    assert len(ob.data.materials) == 1 and ob.data.materials[0].name == 'RestaurantAtlas'
    zs = [v.co.z for v in ob.data.vertices]
    assert abs(min(zs) - (-.62 if rec['name'] == 'Restaurant_Ferry' else 0)) < 2e-5
    images = [n.image for n in ob.data.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE']
    assert len(images) == 2 and all(i.packed_file for i in images)
    if rec['name'] in ['Restaurant_Ferry', 'Restaurant_CatchBoard']:
        mat = ob.data.materials[0]
        assert mat.get('ReviewMatchesCanonicalEmission')
        bs = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        emission = bs.inputs['Emission Strength'].links[0].from_node
        assert emission.operation == 'MULTIPLY' and abs(emission.inputs[1].default_value - 2.8) < 1e-6
        assert emission.inputs[0].links[0].from_socket.name == 'Blue'
    results.append(dict(name=rec['name'], source=str(path.relative_to(O)),
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        tris=rec['tris'], production_mesh_only=True, packed_atlas_images=len(images)))
    print('SOURCE_PASS', rec['name'], flush=True)
(O / 'cooking-source-audit.json').write_text(json.dumps(dict(status='PASS', items=results), indent=2) + '\n')
print('SOURCE_ALL_PASS', len(results), flush=True)
