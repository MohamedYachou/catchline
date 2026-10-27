"""Independent saved-source/actual-FBX and RGBA audit. Run inside Blender."""
import argparse, bpy, hashlib, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--name',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);OUT=ROOT/'Art/Models/PropsV2'/a.name
m=json.loads((OUT/'build-manifest.json').read_text());checks=[]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def check(condition,description):
    assert condition,description
    checks.append(description)
for file,digest in m['delivery_sha256'].items():check(sha(OUT/file)==digest,'current delivery SHA256 '+file)
for row in m['provenance']:check(sha(ROOT/row['file'])==row['sha256'],'protected reference unchanged '+row['file'])
runtime=ROOT/m['runtime_file'];local=OUT/(a.name+('.png' if m['kind']=='RGBA effect' else '.fbx'))
check(sha(runtime)==sha(local),'runtime bytes equal reviewed delivery')
result={'name':a.name,'revision':m['revision'],'delivery_sha256':m['delivery_sha256'],'runtime_sha256':sha(runtime),'checks':checks,'native_acceptance':'Not tested; art only, no Unity/code writes.'}
if m['kind']=='RGBA effect':
    image=bpy.data.images.load(str(local),check_existing=False);w,h=image.size
    check([w,h]==m['logical_size'],'declared pixel dimensions')
    px=list(image.pixels);alpha=px[3::4]
    check(all(math.isfinite(x) and 0<=x<=1 for x in px),'finite bounded RGBA')
    check(all(alpha[y*w+x]==0 for x,y in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]),'all four corners transparent')
    check(0<max(alpha)<.7,'restrained nonopaque effect alpha')
    fraction=sum(v>0 for v in alpha)/len(alpha)
    if a.name=='DeckLightPool':
        centre=alpha[(h//2)*w+w//2]
        check(centre>.6,'warm pool centre visible')
        samples=[alpha[(h//2)*w+w//2+x] for x in (0,30,65,100,124)]
        check(all(x>=y for x,y in zip(samples,samples[1:])),'pool fades monotonically to transparent rim')
        check(.6<fraction<.8,'single circular pool footprint')
    else:check(.001<fraction<.03,'sparse transparent rain streaks')
    result.update(dimensions=[w,h],alpha_min=min(alpha),alpha_max=max(alpha),painted_pixel_fraction=fraction)
else:
    def snapshot():
        data={}
        for o in bpy.context.scene.objects:
            if o.type!='MESH':continue
            pts=[o.matrix_world@v.co for v in o.data.vertices]
            check(bool(pts) and bool(o.data.polygons),'nonempty geometry '+o.name)
            check(all(math.isfinite(c) for v in pts for c in v),'finite vertices '+o.name)
            mats={}
            for poly in o.data.polygons:
                slot=o.material_slots[poly.material_index].material if o.material_slots else None
                key=slot.name if slot else '__NONE__';mats[key]=mats.get(key,0)+len(poly.vertices)-2
            colours={}
            for slot in o.material_slots:
                mat=slot.material
                if not mat:continue
                node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if mat.use_nodes else None
                colours[mat.name]=list(node.inputs['Base Color'].default_value) if node else list(mat.diffuse_color)
                if mat.use_nodes:
                    for n in mat.node_tree.nodes:
                        if n.type=='TEX_IMAGE' and n.image:
                            check(n.image.packed_file is not None or Path(bpy.path.abspath(n.image.filepath)).is_file(),'resolved material image '+n.image.name)
            data[o.name]={'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'material_triangles':mats,'material_colours':colours}
        return data
    bpy.ops.wm.open_mainfile(filepath=str(OUT/(a.name+'.blend')))
    check(all(o.type in ('MESH','EMPTY') for o in bpy.context.scene.objects),'saved source excludes review lights/cameras/surfaces')
    roots=[o for o in bpy.context.scene.objects if not o.parent]
    check(len(roots)==1 and roots[0].name=='PropsV2_'+a.name,'one named export root')
    check(max(abs(roots[0].matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-7,'identity root pivot')
    check(bpy.context.scene.unit_settings.scale_length==1,'source metres')
    src=snapshot();count=sum(d['triangles'] for d in src.values())
    check(count==m['triangles'],'source triangle manifest current')
    check({n:d['triangles'] for n,d in src.items()}==m['mesh_parts'],'source parts manifest current')
    check(0<count<50000,'bounded small-prop geometry budget')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(runtime))
    imported=snapshot()
    check(set(src)==set(imported),'actual FBX preserves every named mesh')
    error=0;colour_error=0
    for name,d in src.items():
        other=imported[name]
        check(d['triangles']==other['triangles'],'actual FBX triangle count '+name)
        check(d['material_triangles']==other['material_triangles'],'actual FBX face materials '+name)
        error=max(error,max(abs(x-y) for p,q in zip(d['bounds'],other['bounds']) for x,y in zip(p,q)))
        check(set(d['material_colours'])==set(other['material_colours']),'actual FBX material slots '+name)
        for mat,colour in d['material_colours'].items():colour_error=max(colour_error,max(abs(x-y) for x,y in zip(colour,other['material_colours'][mat])))
    check(error<.0001,'actual FBX world bounds within 0.1mm; metres/axes preserved')
    check(colour_error<.0001,'actual FBX base colours preserved')
    result.update(triangles=count,mesh_count=len(src),source_parts=src,actual_fbx_parts=imported,max_bounds_error_m=error,max_material_colour_error=colour_error,pivot_use=m['pivot_use'])
result['render_sha256']={f:sha(ROOT/f) for f in m.get('render_files',[])}
result['pass']=True
(OUT/'validation.json').write_text(json.dumps(result,indent=2))
print('PROPSV2 AUDIT PASS',a.name,m['revision'],len(checks),'checks',flush=True)
