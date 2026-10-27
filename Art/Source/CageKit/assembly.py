"""Isolated editable cage-view fit, transparent teal water and phone recognition.
Uses delivered sources as linked copies; never reads/writes a Unity scene/save.
"""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as B
import render as V
O=B.O
def append(name):
    with bpy.data.libraries.load(str(O/(name+'.blend')),link=False) as (a,b):b.objects=a.objects
    for o in b.objects:bpy.context.scene.collection.objects.link(o)
    return next(o for o in b.objects if o.parent is None)
def find(root,name):return next(o for o in root.children_recursive if o.name.split('.')[0]==name)
def prop(g,name):return g.object(name,None,bpy.context.scene.collection)
def fixture():
    B.H.PALETTE=B.P;B.H.MATERIALS={k:B.H.material(k,v) for k,v in B.P.items()}
    g=B.G();g.beam((-1,-.16,0),(1.1,-.16,0),.05,.05,'M_RailIvory',.008)
    # Hull coaming/deck are deliberately below the work and camera.
    for x in (-.8,.9):g.beam((x,-.16,-.42),(x,-.16,0),.035,.035,'M_Steel')
    g.box((0,.35,-.45),(2.2,1.05,.08),'M_HullNavy')
    for i in range(8):g.box((-.96+i*.275,.35,-.402),(.27,1.05,.012),'M_DeckWood' if i%2 else 'M_WoodHighlight')
    prop(g,'ReviewRailAndDeck')
def run():
    bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC'
    cage=append('CrabCage');hauler=append('PotHauler');board=append('SortingBoard');crab=append('CrabBerried')
    # Rail at z0; clamp's channel centre z.065, so mount base -.065.
    cage.location=(.82,-.85,-.445);hauler.location=(.37,-.16,-.065);board.location=(-.23,-.025,.026)
    crab.location=(-.27,-.025,.067);crab.rotation_euler.z=math.radians(-8)
    bpy.context.view_layer.update();fixture()
    B.H.MATERIALS['M_Rope'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
    # Rope follows the actual 0.3m groove, then leads down to the rear bridle.
    c=hauler.location+Vector((0,0,.247));tie=find(cage,'Bridle').matrix_world.translation
    g=B.G();pts=[tie]
    pts += [(c.x,c.y+.128*math.sin(a),c.z+.128*math.cos(a)) for a in [-math.pi/2+i*math.pi/12 for i in range(13)]]
    pts += [(c.x,c.y+.30,c.z-.17),(c.x+.1,c.y+.37,-.37)]
    B.tube(g,pts,.006,'M_Rope',6);prop(g,'ReviewHaulRope')
    # Transparent surface shows the lower cage without pretending this is a native shader.
    V.plane(-.85,200,'#168F9F').name='ReviewSeabedColour'
    water=V.plane(-.27,200,'#168F9F');water.name='ReviewWater'
    m=water.data.materials[0];nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.32
    tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.32;nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(bs.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('Material Output').inputs[0])
    sc,cam=V.stage();cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24;cam.data.lens=24/(2*math.tan(math.radians(26)))
    cam.location=(0,1.0,1.0);cam.rotation_euler=(Vector((0,1-math.sqrt(3),0))-cam.location).to_track_quat('-Z','Y').to_euler()
    rows=[]
    for label,size in [('cage-view-1440',(1440,900)),('cage-view-844',(844,390))]:
        sc.render.resolution_x,sc.render.resolution_y=size;p=O/'renders/assembly'/(label+'.png');V.render(sc,p);rows.append({'file':p.relative_to(O).as_posix(),'view':'isolated 30degree rail camera; half-submerged cage, berried crab on board','size':size})
    # Editable review scene includes stage; source exports remain four clean assets.
    bpy.ops.wm.save_as_mainfile(filepath=str(O/'CageKit-assembly.blend'))
    contract={'camera':{'source_location':list(cam.location),'down_pitch_degrees':30,'vertical_fov_degrees':52,'height_above_rail_metres':1},'water_source_z':-.27,'cage_source_base_z':-.445,'cage_body_height_metres':.35,'submerged_body_fraction':.175/.35,'hauler_rail_channel_centre_source_z':0,'placements':{o.name:list(o.location) for o in (cage,hauler,board,crab)},'evidence':'isolated Blender fit matching runtime30degree pitch/52degree verticalFOV; artist rail layout, not exact native placement','images':rows}
    (O/'assembly.json').write_text(json.dumps(contract,indent=2)+'\n');print('CAGE ASSEMBLY COMPLETE',len(rows),flush=True)
def recognition():
    rows=[]
    # Each crab gets the same camera/light and fixed frame, not a resized crop.
    for label in ('berried','plain'):
        bpy.ops.wm.open_mainfile(filepath=str(O/'CrabBerried.blend'))
        if label=='plain':bpy.data.objects.remove(bpy.data.objects['EggMass'],do_unlink=True)
        sc,cam=V.stage();V.plane(-.001);sc.render.resolution_x=390;sc.render.resolution_y=390
        V.look(cam,(0,0,.04),(.28,1,.95),.34);p=O/'renders/recognition'/(label+'-390.png');V.render(sc,p);rows.append({'file':p.relative_to(O).as_posix(),'view':label+' / same fixed390px rear operator-camera view','size':[390,390]})
    (O/'recognition.json').write_text(json.dumps(rows,indent=2)+'\n');print('CAGE RECOGNITION COMPLETE',len(rows),flush=True)
if __name__=='__main__':
    if '--recognition' in sys.argv:recognition()
    else:run()
