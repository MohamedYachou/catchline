"""Paint-only variants of the exact current released production boat meshes.

FBXs are the canonical handoffs built from historical boat sources; importing
them avoids accidentally reintroducing unreleased source-blend components.
No transforms, vertices, faces, UVs, normals or source files are edited.
"""
import bpy,sys,json,importlib.util,argparse,re
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GullHarbour/HarbourV2'
spec=importlib.util.spec_from_file_location('harbour_build',Path(__file__).with_name('build.py'))
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
spec=importlib.util.spec_from_file_location('harbour_audit',Path(__file__).with_name('audit.py'))
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
VARIANTS={'CompactFisherV1_VariantRed':('CompactFisherV1','M_Crimson','#A9433C'),
 'PrepFisherV1_VariantGreen':('PrepFisherV1','M_KelpGreen','#477A56'),
 'Tier5DeepLines103_VariantBlue':('Tier5DeepLines103','M_HullBlue','#2A6685'),
 'Skiff_VariantYellow':('Skiff','M_OilskinYellow','#E6AD38')}
def build(name,render=True):
    base,paint,hexcode=VARIANTS[name]
    source=R/'Assets/Art/Models/Boats'/(base+'.fbx');before=B.sha(source)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.import_scene.fbx(filepath=str(source));bpy.context.view_layer.update()
    original=A.geometry();objects=list(bpy.context.scene.objects)
    meshes=[o for o in objects if o.type=='MESH']
    col=bpy.data.collections.new('ASSET_EXPORT');bpy.context.scene.collection.children.link(col)
    root=bpy.data.objects.new(name,None);col.objects.link(root)
    for o in objects:
        if o.parent is None:
            world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o)
    root['task']='HARBOUR-ART-1';root['paint_only']=True;root['canonical_fbx_sha256']=before
    mat=bpy.data.materials.get(paint) or B.H.material(paint,hexcode)
    # Imported material values are retained everywhere except broad hull/cabin
    # painted panels. Glass, timber, machinery and safety markings stay distinct.
    changes=[]
    for o in meshes:
        key=re.sub(r'\.\d+$','',o.name)
        slots=set()
        if key in ('Hull','HullPaintBand'):slots={'M_HullNavy','M_HullBlue'}
        elif key in ('HelmConsole','Console'):slots={'M_RailIvory'}
        elif key in ('HelmRoof','squared helm canopy'):slots={'M_HullNavy','M_RailIvory'}
        elif key=='teal canopy brow':slots={'M_SeaTeal'}
        for i,old in enumerate(list(o.data.materials)):
            if old and re.sub(r'\.\d+$','',old.name) in slots:
                changes.append({'mesh':o.name,'slot':i,'from':old.name,'to':paint})
                o.data.materials[i]=mat
    assert changes,name
    identity=A.same_geometry(original,A.geometry())
    # Preview helper uses its shared material cache, independent of imported
    # slot references. Reuse canonical imports where present.
    B.H.MATERIALS.clear()
    B.H.MATERIALS.update({k:bpy.data.materials.get(k) or B.H.material(k,v) for k,v in B.PALETTE.items()})
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc,lo,hi=B.stage(meshes);B.view(sc,meshes,lo,hi,35,45)
    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    fbx=O/(name+'.fbx');blend=O/(name+'.blend')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','EMPTY'},
      global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',
      bake_space_transform=False,use_mesh_modifiers=True,use_triangles=False,mesh_smooth_type='FACE',
      bake_anim=False,add_leaf_bones=False,use_custom_props=True,path_mode='AUTO')
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),check_existing=False)
    paths=[];folder=O/'renders'/name;folder.mkdir(parents=True,exist_ok=True)
    for label,yaw,elev in [('front-right',35,45),('back-right',145,35),('back-left',215,35),('front-left',325,35),('top',0,90)]:
        B.view(sc,meshes,lo,hi,yaw,elev);sc.render.filepath=str(folder/(label+'.png'))
        if render:bpy.ops.render.render(write_still=True)
        paths.append(str(Path(sc.render.filepath).relative_to(R)))
    stats=[B.H.mesh_stats(o) for o in meshes];tris=sum(s['triangles'] for s in stats)
    row={'name':name,'group':'C','triangles':tris,'limit':1500,
      'budget_status':'INHERITED EXCEPTION: exact released hull geometry',
      'canonical_source':{'path':str(source.relative_to(R)),'sha256':before},
      'paint_changes':changes,'authoring_geometry_identity':identity,
      'bounds_blender':[list(lo),list(hi)],'dimensions_width_depth_height':list(hi-lo),
      'parts':stats,'front_unity':'original canonical hull axes preserved',
      'notes':['Paint-only exact released boat; inherited production triangle count exceeds generic prop budget. No decimation or geometry edits.'],
      'blend':str(blend.relative_to(R)),'fbx':str(fbx.relative_to(R)),
      'sha256':{'blend':B.sha(blend),'fbx':B.sha(fbx)},'renders':paths,
      'status':'exported; roundtrip/review pending'}
    (O/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2))
    assert B.sha(source)==before
    A.audit(name)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--name',required=True,choices=list(VARIANTS));ap.add_argument('--no-render',action='store_true')
    a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);build(a.name,not a.no_render)
