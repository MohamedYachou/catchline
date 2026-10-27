from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path(__file__).resolve().parent;m=json.loads((O/'build-metrics.json').read_text());v=json.loads((O/'validation.json').read_text());f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
c=Image.new('RGB',(1600,1260),'#14232c');d=ImageDraw.Draw(c);d.text((24,16),'STAGE 4 / SEAFOOD HOUSE — booths, fish display, expanded kitchen and bar',font=f,fill='white')
for path,box,label in [(O/'renders/seafood-room-1440x900.png',(0,95,1120,700),'Stage 4 • 1440 × 900'),(O.parent/'Stage3Restaurant/renders/restaurant-room-1440x900.png',(1120,95,480,300),'Accepted Stage 3 reference'),(O/'renders/seafood-room-844x390.png',(0,850,844,390),'Stage 4 • 844 × 390')]:
 im=Image.open(path).convert('RGB');im.thumbnail((box[2],box[3]));c.paste(im,(box[0]+(box[2]-im.width)//2,box[1]));d.text((box[0]+14,box[1]-30),label,font=f,fill='white')
for i,line in enumerate(['14 × 5 m room / kitchen 5 × 5','2 six-seat upholstered booths','2 indoor / 6 terrace linen tables','Separate bar / 5 stools','Ice fish counter + display tank','V4 atlas + EXPORT_ nodes','Blender camera proof','Native integration: Claude']):d.text((900,850+i*41),line,font=f,fill='#e5d7b9')
c.save(O/'seafood-review.jpg',quality=95)
(O/'REPORT.md').write_text(f'''# Stage 4 Seafood house

Stage4Seafood.fbx and packed Stage4Seafood.blend provide the 14 × 5 metre room and 5 × 5 kitchen. The kitchen grows two tiles into the old guest area and gains an open iced-fish counter, grill, steamer and large fridge. Two upholstered six-seat booths, a separate five-stool bar, an open-front fish display tank and six terrace linen tables distinguish the Seafood house from the accepted Restaurant. There are 44 table seats (20 indoor, 24 terrace), plus five bar stools. No crew or guests are baked in.

## Layout and import

One tile = one metre. V4 origin retained: room X[-4,10], Y[-2.5,2.5]; kitchen X[-4,1], same Y. Floor top Z0.04; terrace top Z-0.03; review water Z-0.55. The wider room is explicitly built, without stretching furniture. `layout.json` records bounds, furniture positions, seat sockets and the entry jetty. Convert Blender to Unity with [x,z,-y]. Table seat sockets are local to the table assembly and must be translated by its position; booth sockets are explicitly marked absolute. Tabletop heights are absolute. Geometry is a visual layout kit, not a navigation bake.

Every FBX mesh is EXPORT_<component>, with exact inventory and world bounds in build-metrics.json and validation.json. Hide a complete furniture assembly before replacing it, including its included chairs. Important new nodes: EXPORT_SeafoodBooth_1/2, EXPORT_SeafoodDiningTable_1/2, EXPORT_SeafoodTerraceTable_1..6, EXPORT_SeafoodBarCounter, EXPORT_SeafoodBarStools, EXPORT_SeafoodIceCounter, EXPORT_SeafoodDisplayTank, EXPORT_SeafoodGrill, EXPORT_SeafoodSteamer, EXPORT_SeafoodBigFridge, EXPORT_SeafoodTerraceDeck, EXPORT_SeafoodTerraceRail, EXPORT_SeafoodStringLights and EXPORT_SeafoodEntryJetty. The display tank uses opaque blue rear/sides and an open front/top so fish remain readable without a transparency shader. Its body stays below the rear windows.

## Materials and lighting

textures/* are byte-identical to Stage1V4. BaseColor sRGB; Surface linear R roughness, G metallic, B emission. Bind Surface explicitly; Blender emission is base colour × mask × 2.5. Source images packed; production FBX embeds BaseColor. Every mesh has UV0, a positive-area UV1 and atlas material. New/UV0-only appended props receive separated per-triangle lightmap charts.

lighting.json inherits the accepted Stage3/V4 world and grading and records relocated practicals, eight table lamps, two booth lamps, terrace bulbs and ice-counter light. Production FBX excludes lights, cameras and presentation sea. Seafood-V4-check.blend contains the review setup and accepted painted water.

## Verified checks

Independent fresh FBX import PASS: {v['mesh_count']} meshes, {v['triangles']:,} triangles (author budget220,000), complete expected EXPORT_ inventory, finite world bounds, <0.00001m export/source bound difference, valid material indices, two UV channels and positive UV1 triangle areas. The imported KitchenKit/Upgrades props originally lacked UV1; this was corrected before final validation. Accepted V4 and Stage3 source blends are unchanged; hashes recorded. Actual final desktop1440×900 and mobile844×390 images opened: kitchen, fish counter, booths, tank, bar and terrace read clearly. V4 camera rotation and respective lenses/resolutions retained, camera distance widened to include the room. final-cameras.json records exact transforms. seafood-review.jpg compares the accepted Stage3 proof.

No Assets, runtime code, metas or git edits; no commit. Claude owns Unity import, Surface/light binding, layout replacement, seat/navigation/camera checks and native acceptance. Blender proof is not native runtime acceptance.
''')
print('STAGE4 PACKAGE PASS')
