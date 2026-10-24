# Catchline - /gemini UI & Fish Catch Notification Asset Pack

Drop this entire `gemini/` folder into your Unity project under `Assets/gemini/`.

## Folder Structure
- `HUD/`: 9-sliceable warm cream (`#FDF6E5`) and deep nautical navy (`#0B3E61` / `#003150`) HUD panels, active tab squircles, buttons, and progress bars matching your target renders.
- `CatchNotification_Tiers/`:
  - `Tier1_Common` (White/Silver Glow) through `Tier6_Leviathan` (Abyssal Red Glow)
  - Includes `*_EmptyCardTemplate.png` (for dynamic UI text/sprite binding in Unity), `*_GlowBurst.png` (standalone radial sunburst to rotate behind the fish), and `*_PopulatedPreview.png`.
- `FishRenders/`: 3D normal-shaded fish sprites with glossy specular highlights, subsurface belly gradients, and dark nautical outlines (`#0B253A`).
- `Icons/`: 3D-shaded Gold Coin and Wooden Hold Crate icons.
- `Scripts/`: `FishSpeciesData.cs` ScriptableObject definition for configuring Tiers 1-6.
