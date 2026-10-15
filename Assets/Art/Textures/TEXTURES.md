# Catchline water and effects

Seven original RGBA PNGs, each 1024 x 1024, authored by Art/Source/build_water_textures.py using deterministic periodic mathematical shapes, NumPy and Pillow. Colours derive from the existing STYLE.md palette. No external bitmap or third-party texture. Each has sRGB/source metadata. No Unity settings or materials are created.

| File | Alpha | Wrap | Use |
| --- | --- | --- | --- |
| water-tile.png | opaque | Repeat | Sea teal, soft caustic contours and sparse streaks |
| water-tile-shallow.png | opaque | Repeat | Lighter Sandbar water, muted sandy patches |
| water-tile-deep.png | opaque | Repeat | Navy Deep channel, dim blue contours |
| foam-ring.png | transparent | Clamp | Soft irregular contact/impact ring |
| wake-trail.png | transparent | Clamp | V wake; narrow apex at image top, expanding tail below |
| splash-sheet.png | transparent | Clamp | 4 x 4 flipbook, 16 cells of 256 x 256 |
| deck-planks-detail.png | transparent, max alpha 13/255 | Repeat | Optional subtle long grain overlay, no plank seams |

Water tiles and deck overlay have exactly matching first/last pixel rows and columns. validation.json records seam, size and alpha checks. The water has no baked lighting, reflection, normal map, displacement or animation. Deck grain runs vertically in image space; align this axis with fore-aft planks.

Effects use straight alpha, with transparent gutters. Splash cells run left-to-right then top-to-bottom: index 0 at top-left, index 15 at bottom-right. Last cell is intentionally transparent. For bottom-left UVs, scale is (0.25, 0.25); offset is (column/4, 1-(row+1)/4). Play once with consumer timing. Clamp sampling within each cell to avoid neighbouring-frame bleed.

Art/Models/DayBoatKit/water-textures-contact-sheet.png shows each water repeated 2 x 2 and effects composited over teal. Rebuild with Python 3.12+ and NumPy/Pillow; the script also regenerates validation and review sheet.
