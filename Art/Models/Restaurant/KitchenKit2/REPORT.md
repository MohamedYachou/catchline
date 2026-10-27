# Restaurant kitchen kit 2

Ten placeable FBXs, metre-scale and floor/base-contact Z=0, footprint-centred origin. The original V4 atlas is byte-identical. The three upgrades follow the S8 illustrations: twin cream fridge/navy crown, six-burner range/twin ovens, navy enamel warm pendant. Each has a footprint JSON and mesh/bounds inventory. No presentation meshes, lights, cameras or crew are exported.

Dedicated semantic replacements: Grill (open grate/coals), Steamer (stacked lidded pot), DrinksFridge (bottles/shelves), Chart (coast/islands/compass), Jukebox (brass arch/speaker/controls). Net and Trophy reuse the accepted Upgrades geometry under explicit ItemId filenames. Existing models with legitimate aliases remain in use; no duplicate production files were made for those aliases.

## ItemId coverage

| ItemId | Model key | File | Delivery |
|---|---|---|---|
| PrepCounter | PrepCounter | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_PrepCounter.fbx` | existing |
| Stove | Stove | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_Stove.fbx` | existing |
| SoupKettle | SoupKettle | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_SoupKettle.fbx` | existing |
| Grill | Grill | `Art/Models/Restaurant/KitchenKit2/Restaurant_Grill.fbx` | NEW; runtime mapping needed |
| Fryer | Fryer | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_Fryer.fbx` | existing |
| Oven | Oven | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_Oven.fbx` | existing |
| Steamer | Steamer | `Art/Models/Restaurant/KitchenKit2/Restaurant_Steamer.fbx` | NEW; runtime mapping needed |
| Fridge | FridgeV2 | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_FridgeV2.fbx` | existing |
| Sink | SinkDishRack | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_SinkDishRack.fbx` | existing |
| CoffeeMachine | CoffeeBar | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_CoffeeBar.fbx` | existing |
| DrinksFridge | DrinksFridge | `Art/Models/Restaurant/KitchenKit2/Restaurant_DrinksFridge.fbx` | NEW; runtime mapping needed |
| BarCounter | PassCounter | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_PassCounter.fbx` | existing |
| Table2 | TableFor2 | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_TableFor2.fbx` | existing |
| Table4 | TableFor4 | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_TableFor4.fbx` | existing |
| Booth6 | Booth | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_Booth.fbx` | existing |
| TerraceTable | TerraceTable | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_TerraceTable.fbx` | existing |
| Reception | ReceptionDesk | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_ReceptionDesk.fbx` | existing |
| Trophy | Trophy | `Art/Models/Restaurant/KitchenKit2/Restaurant_Trophy.fbx` | NEW; runtime mapping needed |
| Net | Net | `Art/Models/Restaurant/KitchenKit2/Restaurant_Net.fbx` | NEW; runtime mapping needed |
| Lamp | LampPost | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_LampPost.fbx` | existing |
| Plant | PlantPot1 | `Assets/Art/Models/Restaurant/Stage1V2/Restaurant_PlantPot1.fbx` | existing |
| Chart | Chart | `Art/Models/Restaurant/KitchenKit2/Restaurant_Chart.fbx` | NEW; runtime mapping needed |
| Jukebox | Jukebox | `Art/Models/Restaurant/KitchenKit2/Restaurant_Jukebox.fbx` | NEW; runtime mapping needed |

## Integration

New filenames already include `Restaurant_`; do not add that prefix a second time. Update the seven stand-in ItemId mappings to the keys above. BigFridge/ReliableStove/CosyPendantLamp are upgrade variants, not new ItemIds; the lead chooses how to toggle them. Wall props use local base0 and suggested mounting height in footprint JSON; the pendant base is the underside of its shade, suggested Z=1.65m. No invisible floor support is included. Give the pendant a warm point light at its bulb (local0,0,.04), ~8 Blender W / 2m recipe range; preserve Surface.B emission. Lamps/coal are opaque atlas colours, not alpha materials.

Use the shared Restaurant atlas material with BaseColor plus Surface R=roughness,G=metallic,B=emission, suggested emission multiplier2.5. FBX embeds BaseColor; packed source retains Surface too. Axes Blender X,Y,Z -> Unity X,Z,-Y. Footprints reserve occupancy, operator access is adjacent.

## Verification

`validation.json`: ten fresh independent FBX imports; exact mesh inventories, identity transforms, finite bounds/roundtrip<1e-5m, floor-contact0 and footprint containment, all UV face corners inside a single inset atlas cell, correct triangle totals, embedded base loaded and identical V4 texture hashes. `kitchen-kit-review.jpg` shows all ten closeups; exact saved V4 camera lineups at1440x900 and844x390 use neutral review lighting/floor. Native Unity import, mapping, arrange mode, shading and final gameplay visibility remain for Claude. No Assets/code/git edits; no commit.
