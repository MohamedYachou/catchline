"""Read-only source appends into isolated exact-lens net-view evidence scene.
No Unity/runtime/saves. Camera fit is a contract fixture, not a native capture.
"""
import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as B
import render as V
O=B.O
DEPENDENCIES={}
def append_file(rel,root_name=None):
    path=B.R/rel;DEPENDENCIES[rel]=B.sha(path)
    with bpy.data.libraries.load(str(path),link=False) as (a,b):b.objects=a.objects
    for o in b.objects:bpy.context.scene.collection.objects.link(o)
    roots=[o for o in b.objects if o.parent is None]
    return next(o for o in roots if root_name is None or o.name.split('.')[0]==root_name),b.objects

def boat_fixture():
    # Existing real compact-fisher roller, not a newly invented replacement asset.
    _,objs=append_file('Art/Models/GullHarbour/HarbourV2/CompactFisherV1_VariantRed.blend')
    keep=[o for o in objs if o.name.split('.')[0] in ('SternNetRoller','NetDrum','NetCrank','NetMountFittings')]
    bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in keep for v in o.data.vertices]
    centre=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))*.5 for i in range(3)))
    target=Vector((-.58,-1.25,.60))
    for o in keep:
        m=o.matrix_world.copy();o.parent=None;o.matrix_world=m;o.location+=target-centre
        o.name='ReviewExisting_'+o.name
    for o in objs:
        if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
    P=dict(B.P,M_HullNavy='#173F57',M_DeckWood='#C08B50',M_WoodHighlight='#D1A169')
    B.H.PALETTE=P;B.H.MATERIALS={k:B.H.material(k,v,.8) for k,v in P.items()}
    g=B.G();g.box((0,-.40,.25),(3.5,1.7,.28),'M_HullNavy')
    for i in range(14):g.box((-1.625+i*.25,-.40,.399),(.243,1.65,.02),'M_DeckWood' if i%2 else 'M_WoodHighlight')
    g.box((0,-1.25,.51),(3.5,.12,.18),'M_RailIvory')
    g.box((0,-1.315,.46),(3.5,.016,.045),'M_HullNavy')
    g.object('ReviewRailDeckFixture',None,bpy.context.scene.collection)

def fish_six(fill):
    # Canonical mackerel centred across X; six separate fish roots and six bodies.
    # Distinct staggered rows in depth, leaving readable silhouettes through holes.
    placements=[(-.30,-.09,-.13),(0,-.08,-.13),(.30,-.075,-.10),
                (-.30,.065,.025),(0,.075,.035),(.30,.065,.02)]
    rows=[]
    for i,p in enumerate(placements):
        root,objs=append_file('Art/Models/Fish043/Mackerel/Mackerel.blend','Catchline_Mackerel')
        root.name=f'ReviewFish_{i+1:02d}';root.parent=fill;root.location=B.to_b(p)
        root.rotation_euler=(0,0,math.radians(90+(-1)**i*8))
        root.scale=(.82,.82,.82)
        rows.append({'root':root.name,'fill_local_unity':p,'scale':.82,'source':'Fish043/Mackerel'})
    return rows

def run(_=None):
    bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
    sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    root,_=append_file('Art/Models/NetKit/NetBunt.blend','NetBunt')
    root.location=B.to_b((.65,.35,2.5));fill=bpy.data.objects['Fill'];fish=fish_six(fill)
    boat_fixture();sc,cam=V.stage()
    water=V.plane(0,'#168F9F');water.name='ReviewWater'
    bs=water.data.materials[0].node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.44
    # Exactly 54deg vertical FOV independent of frame aspect ratio.
    cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24
    cam.data.lens=24/(2*math.tan(math.radians(54/2)))
    cam.location=(0,0,2)
    direction=Vector((0,-math.cos(math.radians(34)),-math.sin(math.radians(34))))
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    rows=[]
    for state in (0,1):
        bpy.data.objects['Bunt'].data.shape_keys.key_blocks['Taut'].value=state
        fill.location=B.to_b(B.stretch((0,-.09,.31)) if state else (0,-.09,.31))
        for item in fish:
            f=bpy.data.objects[item['root']];p=item['fill_local_unity']
            f.location=B.to_b((p[0]*(.72 if state else 1),p[1]*(.78 if state else 1),p[2]))
            k=.82*(.8 if state else 1);f.scale=(k,k,k)
        for label,size in [('1440',(1440,900)),('844',(844,390))]:
            sc.render.resolution_x,sc.render.resolution_y=size
            name=f'net-view-{"taut" if state else "slack"}-{label}'
            p=O/'renders/assembly'/(name+'.png');V.render(sc,p)
            rows.append({'file':p.relative_to(O).as_posix(),'state':'Taut' if state else 'Slack','size':list(size),'fish_count':6})
    bpy.data.objects['Bunt'].data.shape_keys.key_blocks['Taut'].value=0;fill.location=B.to_b((0,-.09,.31))
    for item in fish:
        f=bpy.data.objects[item['root']];f.location=B.to_b(item['fill_local_unity']);f.scale=(.82,.82,.82)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(O/'NetKit-camera-fixture.blend'))
    for rel,sha in DEPENDENCIES.items():assert B.sha(B.R/rel)==sha,(rel,'source changed during fixture')
    row={'evidence':'Isolated artist fixture, not Unity/native capture. Existing compact-fisher roller, simple rail/deck stage; exact required lens/pitch/height, six canonical fish.',
      'camera':{'location_unity':[0,2,0],'height_above_water_m':2,'pitch_down_degrees':34,'vertical_fov_degrees':54,'sensor_fit':'VERTICAL','lens_mm':cam.data.lens,'sensor_height_mm':24},
      'water_y_unity':0,'bunt_mouth_unity':list(B.to_u(root.location)),'bunt_distance_outward_m':2.5,
      'fish':fish,'images':rows,'readonly_dependencies_sha256':DEPENDENCIES}
    (O/'assembly.json').write_text(json.dumps(row,indent=2)+'\n')
    print('NET ASSEMBLY',len(rows),flush=True)
if __name__=='__main__':run()
