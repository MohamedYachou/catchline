# Day-boat stations

One tile is 1 m. Roots sit at the footprint centre on deck height zero. Unity axes X right, Y up, Z toward bow. Access is Unity -Z (source +Y). Keep one clear tile beyond that side.

| Asset | Footprint across x fore-aft | Access | Parts | Moving pivot in Unity metres | Drive |
| --- | --- | --- | --- | --- | --- |
| NetDrum | 2 x 1 | -Z | Frame, Drum | Drum (0, 0.69, 0) | Local X rotation |
| PowerHauler | 1 x 1 | -Z; rail on +Z | Frame, Sheave | Sheave (0, 1.16, 0.25) | Local X rotation |
| Conveyor_Straight | 1 x 1 | -Z maintenance | Frame, Belt | Belt (0, 0.50, 0) | Translate/recycle ridges along Z |
| Conveyor_Corner | 1 x 1 | -Z maintenance | Frame, Belt | Belt (-0.40, 0.50, 0.40) | Rotate/recycle around curvature centre, local Y |
| SortingChute | 2 x 1 | -Z | SortingChute | root | Static, external bin at outlet |
| FishHold | 2 x 2 | -Z | HoldWell, HatchLid | HatchLid (0, 0.075, -0.91) | Negative local X lifts lid |
| IceMachine | 1 x 1 | -Z controls | IceMachine | root | Static |
| GuttingTable | 2 x 1 | -Z worktop | GuttingTable | root | Static |
| Crane | 1 x 1 stored | -Z | Pedestal, Boom | Boom (0, 0.92, 0) | Local X hinge |

All parts are siblings under Catchline_<asset>. Source and FBX names/pivots are recorded in ../build-metrics.json and checked by ../validation.json. Operator-side previews show control faces. No baked animation, colliders, interaction sockets or occupancy logic.

Belts have separate geometry ridges for UV-less travel. Continuous travel requires consumer wrapping/recycling; the corner curvature pivot is supplied. FishHold extends 0.66 m below deck and requires a corresponding deck opening. The stored crane fits its footprint; operational sweep can extend beyond it. Rope payout, hook constraints, equipment contacts and collisions remain gameplay integration.
