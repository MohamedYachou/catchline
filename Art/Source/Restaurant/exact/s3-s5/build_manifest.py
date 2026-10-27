"""Reference measurement and mechanical packaging; artwork is built-in imagegen only."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[4]
CONCEPT=PROJECT/'Art/Source/Restaurant/concepts'
entries=[]
def add(name,screen,rect,description,size=None,slice=None,opaque=False):
    x,y,w,h=rect
    entries.append(dict(name=name,screen=screen,rect=rect,description=description,
        size=size or [w*3,h*3],borders=slice,opaque=opaque))
# Rectangles are measured in reference logical pixels, top-left origin, 844x390.
add('v2-sign-plank',3,[234,0,398,72],'wood title sign with two golden hanging ropes, brass left rivet and lit brass lantern on the right; remove title text', [1592,288])
add('v2-plan-paper',3,[258,69,408,295],'large ivory paper plan card with navy outer contour, warm cream rim, two golden rope loops at its upper corners, thin horizontal divider below calendar area; remove ALL text, calendar, food pictures, fish pictures and inner cards',[1224,885],[72,90,72,66])
add('v2-plan-dish-card',3,[275,162,122,123],'empty ivory inset dish card with very fine tan border and small rounded corners; remove fish, guests and ALL text',None,[27,27,27,27])
add('v2-ticket',3,[670,66,165,224],'cream paper special request note, slightly clockwise tilted, layered paper edge, brass round pin at top center, thin beige dividers; remove ALL text, balloons and buttons',None)
add('v2-btn-accept',3,[681,184,139,51],'green glossy Accept button blank, thick navy outline, white top highlight, darker green bottom lip; no text or tick',None,[42,36,42,42])
add('v2-btn-secondary',3,[679,230,140,51],'cream glossy Not tonight button blank, thick navy outline, ivory top highlight, darker tan bottom lip; no text or cross',None,[42,36,42,42])
add('v2-btn-primary',3,[668,297,165,70],'orange glossy Got it button blank, thick dark navy outline, white narrow top highlight, darker orange-red thick bottom lip; no lettering/checkmark',None,[60,48,60,60])
add('v2-btn-back',3,[12,8,130,51],'cream rounded Back button with thick navy outline and soft shadow, NO arrow or text',None,[39,36,39,39])
add('v2-icon-back',3,[26,18,31,30],'filled navy left arrow with subtle lighter edge, exact chunky reference shape')
add('v2-icon-calendar',3,[292,91,47,49],'calendar icon with two black binding rings, orange header, white paper, 3x3 blue squares, thick dark ink outline; no text')
add('v2-icon-special',3,[685,79,44,45],'red and pink birthday balloons with golden confetti, dark navy outlines, small curling strings')
add('v2-icon-tick',3,[693,311,39,36],'bold cream white checkmark with thick dark navy outline, exact slanted reference shape')
add('v2-icon-cross',3,[698,241,22,22],'bold orange-red cross with dark navy outline, rounded beveled tips')
add('v2-icon-guests',3,[301,257,21,20],'two small solid navy human head-and-shoulder silhouettes, one slightly taller')
add('v2-catch-pile',3,[281,298,112,51],'two silver blue mackerel lying on small blue ice chips, black wavy dorsal stripes, navy outlines; no labels',[672,306])
add('v2-mira-plan',3,[0,44,281,346],'Mira exact full-body planning pose: warm tan young adult woman, big brown eyes, wavy shoulder-length brown hair, navy captain cap with cream band and gold compass badge, navy gold-button coat, ivory cable-knit sweater, binoculars, clipboard with anchor in her right arm at image left, her left hand palm-up presenting toward image right. Extend lower body naturally to navy trousers and brown boots; preserve reference face and pose. Full body head to boots isolated, do not crop',[1600,2000])
add('v2-bg-plan',3,[0,0,844,390],'EXACT blue horizontal painted wooden plank wall background from reference. Remove all UI, characters, lettering and objects, reconstruct continuous wall behind them. Navy blue horizontal wood grain and narrow dark seams, same lighting',[2532,1170],opaque=True)
add('v2-prep-catch-panel',4,[66,60,272,254],'empty catch panel: glossy navy-blue rounded header band above ivory paper body, thick dark navy outer contour with cyan rim highlight; NO text fish icons rows or food',None,[66,147,66,57])
add('v2-prep-portions-panel',4,[343,60,466,262],'empty portions panel: glossy navy-blue rounded header band above ivory paper body, thick dark navy outer contour cyan rim highlight; NO text icons rows buttons or controls',None,[66,147,66,57])
add('v2-paper-row',4,[81,118,244,85],'empty ivory inset row with subtle rounded cream/tan border and very light warm paper shading; remove fish and ALL text',None,[30,30,30,30])
add('v2-number-field',4,[629,112,99,38],'empty ivory quantity field with rounded tan hairline outline and warm shadow, remove number',None,[24,24,24,24])
add('v2-btn-minus',4,[569,111,53,50],'blue glossy square minus control, navy thick outline, pale blue top-edge shine, darker blue bottom lip, bold white minus sign with dark outline',None,[36,36,36,36])
add('v2-btn-plus',4,[734,110,57,52],'orange glossy square plus control, navy thick outline, pale orange top-edge shine, darker red-orange bottom lip, bold white plus sign with dark outline',None,[36,36,36,36])
add('v2-bar-track',4,[628,150,102,14],'horizontal grey warm stone pill-shaped slider track, inset shading, no yellow knob',None,[21,18,21,18])
add('v2-bar-knob',4,[672,148,12,18],'tiny vertical golden rounded slider thumb with bright pale yellow left highlight and amber right shadow',[72,108])
add('v2-toggle-selected',4,[611,285,81,30],'small orange glossy selected forecast pill, dark outline cream top shine and darker lip, NO text',None,[30,27,30,27])
add('v2-toggle-unselected',4,[529,285,80,30],'small ivory glossy unselected forecast pill with dark outline, NO text',None,[30,27,30,27])
add('v2-summary-strip',4,[198,322,434,58],'empty ivory summary strip with navy thick outer contour, rounded corners and warm rim; remove all icons text checkbox and separators',None,[51,42,51,42])
add('v2-checkbox-on',4,[490,333,38,37],'square ivory inset checkbox with navy thick rounded outline, bold navy checkmark and small cream shine')
add('v2-checkbox-off',4,[490,333,38,37],'same square ivory inset checkbox with navy thick rounded outline, EMPTY center no checkmark')
add('v2-divider',4,[353,331,5,41],'thin vertical tan paper divider, soft irregular tapered ends',[30,246])
add('v2-icon-forecast',4,[418,287,25,24],'three solid navy ascending bar-chart columns, rounded tops')
add('v2-icon-cutlery-white',4,[366,69,30,35],'white fork and knife silhouette with thin navy outline, broad bold reference shape')
add('v2-icon-cutlery',4,[216,331,29,35],'navy fork and knife solid silhouettes, broad bold reference shape')
add('v2-icon-fish-white',4,[90,73,36,26],'solid white fish side silhouette facing left, navy outline')
add('v2-icon-fish-market',4,[366,335,44,29],'small bright blue painted fish facing left with dark navy outline, exact summary-strip fish')
add('v2-icon-cooler',4,[642,9,43,39],'blue portable cooler with white lid, navy thick outline, carrying handle and blue shaded sides')
add('v2-icon-cloche',4,[650,332,43,31],'white domed serving cloche with navy outline, blue-grey shading, small round top knob')
add('v2-sign-fish',4,[229,0,53,50],'tiny warm wood hanging sign with two short ropes and navy fish silhouette, no text')
add('v2-dish-grilled-fish',4,[362,111,91,51],'orange golden grilled whole fish on oval white blue-rim plate, dark grill marks, parsley and lemon wedge, exact reference serving angle',[546,306])
add('v2-dish-fish-soup',3,[408,166,110,75],'blue-and-cream bowl of orange fish soup with white fish chunks, green herb and carrot, white plate under bowl, exact reference',[660,450])
add('v2-dish-coffee',3,[541,169,99,73],'white blue-rim coffee cup and saucer, dark coffee surface, two golden biscuits, exact reference angle',[594,438])
add('v2-dish-fillets',4,[364,228,90,49],'two golden fish fillets with diagonal grill marks on oval white blue-rim plate, herbs and lemon, exact reference',[540,294])
add('v2-bg-prep',4,[0,0,844,390],'reconstruct EXACT prep backdrop: warm restaurant interior on left, big brass lantern bottom left on timber counter with paper chart and pen, plants, hanging fish sign at upper left, twilight harbour through open right side with distant lights and deep blue water. Remove ALL UI/panels/text/icons/characters. Keep foreground lantern left and right harbour framing',[2532,1170],opaque=True)
add('v2-closing-board',5,[119,11,607,358],'large ivory closing-summary board, navy thick outline and cream bevel, rounded corners; NO header, text, subcards or illustrations',None,[63,63,63,63])
add('v2-closing-header',5,[119,11,607,53],'long navy-blue painted plank header with thick dark navy outline, thin cyan top shine and four small gold rivets two on either end; no text or moon',None,[75,48,75,48])
add('v2-metric-row',5,[129,96,191,45],'empty ivory inset closing metric row with thin tan edge and softly rounded corners, NO icons/text',None,[30,30,30,30])
add('v2-tonight-row',5,[129,227,191,57],'empty pale golden closing earnings row with gold edge and tiny gold spark rays on left, no coin or text',None,[63,30,30,30])
add('v2-review-card',5,[327,64,219,64],'empty ivory guest review card, thin tan rounded border, faint warm paper texture; remove portrait/stars/text',None,[27,27,27,27])
add('v2-popularity-card',5,[552,64,168,152],'empty ivory popularity panel with softly rounded tan border, no text/star/bar/numbers',None,[30,30,30,30])
add('v2-star-full',5,[563,107,44,42],'gold five-point star with orange inner bevel, dark navy outline and pale-yellow top-left shine',[264,252])
add('v2-star-empty',5,[471,141,21,21],'pale ivory-grey five-point empty review star, thin warm grey outline',[126,126])
add('v2-progress-track',5,[558,154,147,21],'horizontal rounded ivory-grey popularity bar track with dark navy outline, no fill/star',None,[30,27,30,27])
add('v2-progress-fill',5,[560,156,107,17],'glossy emerald green progress bar horizontal fill, pale green top shine, flat right end and rounded left end, no outline decoration',None,[24,18,9,18])
add('v2-bubble-mira',5,[486,259,108,52],'ivory speech bubble with navy thick outline, rounded corners, short pointed tail at right toward Mira, NO text')
add('v2-illus-cats',5,[130,292,104,69],'two adorable harbour cats ginger-white and black-white sitting beside a blue bowl with fish scraps, dark navy outlines, exact reference',[624,414])
add('v2-dish-lemonade',5,[143,141,42,39],'glass orange lemonade with ice cubes, blue bent straw, yellow lemon slice on rim, navy outline',[252,234])
add('v2-icon-coins',5,[143,185,44,39],'three small shiny gold coin stacks, orange edges, dark navy outlines',[264,234])
add('v2-icon-coin-service',5,[153,231,53,49],'big glossy gold coin with embossed euro-like currency mark in reference, orange edge navy contour and pale rim shine',[318,294])
add('v2-icon-bed',5,[562,332,43,31],'cream pillow and mattress in simple navy outlined bed with brown headboard, exact bold reference silhouette')
add('v2-icon-moon',5,[592,18,34,34],'gold crescent moon with orange bevel and navy outline')
add('v2-mira-wave',5,[580,209,148,167],'Mira closing wave exact reference face/pose: warm tan young adult, big brown eyes, wavy dark brown hair, navy gold compass cap, ivory sweater and navy coat with brass buttons; one white-gloved hand waving at image left. Full body head to boots isolated with navy trousers/brown boots, extend naturally below crop. Preserve beautiful warm smiling reference face',[1600,2000])
add('v2-portrait-crew-jo',5,[329,290,65,68],'exact young adult crew Jo in orange knit beanie, short dark hair, warm tan skin, navy coat with yellow braces, facing slightly right, friendly smile, bust only',[512,512])
add('v2-bg-closing',5,[0,0,844,390],'reconstruct EXACT closing harbour backdrop: twilight blue fishing village restaurant quay, warm golden lanterns/windows, umbrella table and blue chairs on left, timber planked quay and barrels/right restaurant, navy water in foreground with orange window reflections, rope rail and mooring posts left/right. Remove ALL UI/board/people/text/icons, fill hidden background naturally. Same framing',[2532,1170],opaque=True)
for i,(rect,desc) in enumerate([
([335,68,59,56],'friendly tan adult male guest with short dark beard, navy knit cap, yellow shirt'),
([335,132,59,60],'friendly adult woman guest, warm tan skin, auburn long hair, yellow rain hat, blue coat'),
([335,201,59,60],'elderly male guest with grey moustache and eyebrows, navy sailor cap with gold anchor, blue coat and red scarf'),
([335,68,59,56],'adult woman guest with dark brown skin, short curly black hair, teal cardigan, friendly smile, civilian'),
([335,132,59,60],'older adult woman guest with fair skin and grey bun, coral scarf and navy blouse, friendly smile, civilian'),
([335,201,59,60],'adult male guest with olive skin, brown hair and small beard, rust jacket, friendly smile, civilian')],1):
    add(f'v2-review-portrait-{i:02}',5,rect,'individual guest portrait bust, reference review art style: '+desc+'; no circle frame/text/stars',[512,512])
fish=[('mackerel','slender silver-blue Atlantic mackerel with two dorsal fins, dark blue wavy tiger stripes on its upper back, forked tail'),('pollock','olive-bronze pollock with pale belly, three dorsal fins, curved pale lateral line and protruding lower jaw, NO chin barbel'),('cod','Atlantic cod, olive tan mottled back, cream belly, THREE dorsal fins, rounded broad tail, clear short chin barbel'),('herring','Atlantic herring slender silver blue body, SINGLE central triangular dorsal fin, deeply forked tail, big eye, silver scales'),('whiting','whiting slim pale silver-beige body, three dorsal fins, small mouth, black spot at pectoral fin base, pale grey tail'),('plaice','European plaice flat oval brown fish with distinct vivid orange spots, both eyes on upper surface at head, continuous frilled fins, seen from above'),('seabass','European seabass silver elongated body, strong spiny first dorsal and soft second dorsal, dark grey back, large mouth, forked tail'),('redmullet','red mullet coral-pink red back and silver-pink belly, two long chin barbels, two dorsal fins and yellow-striped fins'),('turbot','turbot broad near-circular diamond flatfish, sandy mottled brown upper surface, both eyes together on upper head, bumpy skin and frilled edge, seen above'),('conger','European conger eel long dark slate grey serpentine body with pale belly, broad head and large jaws, continuous dorsal/anal fin, no scales, gently curved horizontal pose'),('crab','brown edible crab Cancer pagurus seen above, broad reddish brown pie-crust edged shell, two large black-tipped claws and eight walking legs, species-correct'),('squid','European squid with elongated tapered pale ivory-pink mantle, paired triangular rear fins, two large eyes, eight arms plus two longer feeding tentacles, horizontal side view')]
for name,desc in fish:
    add('v2-fishart-'+name,4,[89,132,123,61] if name=='mackerel' else [88,216,126,67], 'painted species-correct '+desc+'. Single uncooked whole specimen facing RIGHT, crisp dark navy outline, rich natural painted shading like reference prep mackerel/pollock, NO plate ice water props or labels',[1024,512])
# Final reference pass: foreground variants must retain their own source artwork.
add('v2-prep-topbar',4,[0,0,844,57],'the exact full-width blue horizontal wood plank top strip, thin dark lower seam; remove Back control, fish sign, title and cooler pill; opaque continuous blue planks only',[2532,171],opaque=True)
add('v2-accent-rays',5,[584,217,32,36],'exact THREE short golden yellow excitement rays beside Mira, diagonally arranged fan, softly rounded tips, flat warm gold, NO navy contour or glow', [210,204])
add('v2-bar-fill',4,[629,150,52,12],'only the dark grey left filled part of slider: horizontal rounded grey capsule, flat #626765 grey fill, tiny light upper edge, no thumb, navy contour, cream frame or letters',[312,72],[18,12,18,12])
add('v2-icon-fish-bringback',3,[397,319,36,24],'exact tiny cyan blue simple fish glyph facing LEFT with black eye, dark blue thin contour, no realistic scales or extra fins; remove surrounding paper and lettering',[216,144])
add('v2-icon-pollock-bringback',3,[529,319,39,24],'exact tiny grey blue pollock glyph facing LEFT with simple tiny dark spots on upper body, thin navy contour and small black eye; remove surrounding paper and lettering',[234,144])
add('v2-dish-grilled-plan',3,[277,165,118,68],'exact pale golden grilled fish steak on white navy-rim oval plate, diagonal dark grill marks, leafy parsley behind and lemon wedge right, matching source composition, no letters',[708,408])
add('v2-dish-soup-prep',4,[362,169,91,52],'exact small solid dark BLUE bowl of orange fish soup with cream fish chunks, green leaves and carrot, NO saucer or plate beneath, source angle and proportions',[546,312])
add('v2-dish-closing-fish',5,[140,101,56,34],'exact small orange cooked whole fish with visible head/tail on BLUE oval plate, lemon wedge and green herbs, matching source silhouette; no text',[336,204])
ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'references').mkdir(exist_ok=True)
for e in entries:
    src=next(CONCEPT.glob(f"ui-{e['screen']}-*.png"))
    im=Image.open(src).convert('RGBA'); x,y,w,h=e['rect']
    im.crop((x,y,x+w,y+h)).save(ROOT/'references'/(e['name']+'.png'))
    e['reference']=str(src)
    e['crop']=str(ROOT/'references'/(e['name']+'.png'))
    e['prompt']=('Production Catchline restaurant game sprite. Reference image 1 is the ONLY style and exact shape/colour/lighting authority. Recreate ONLY this individual piece: '+e['description']+'. Match reference silhouette, proportions, colour, thick hand-inked navy contours, bevel and shadow faithfully, do not redesign or simplify into flat vector art. '+('Opaque full-bleed background, no transparency. ' if e['opaque'] else 'One isolated sprite, genuinely transparent background, no backdrop or grid. ')+'NO letters, words, numbers or watermarks baked in (functional plus/minus symbols and described currency emboss are allowed). Leave room for live UI text where appropriate. Crisp high-resolution painted edges. Requested production canvas '+str(e['size'][0])+'x'+str(e['size'][1])+'. Reference image 2 is the complete screen for context; do not generate any other piece or whole screen.')
(ROOT/'manifest.json').write_text(json.dumps(entries,indent=2),encoding='utf8')
print(f'{len(entries)} measured assets; reference crops ready')
