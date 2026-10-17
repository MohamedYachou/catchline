# PTS water, bounded Catchline adapter

Source: the local Plunder The Seas `com.unity.urp-water-system` package,
2.0.0-preview.5, Unity Boat Attack water. Original checkout remains unchanged.
Copyright and Unity Companion License are in LICENSE.md. Original shader hashes
are recorded in source-sha256.json; docs/tools/port_pts_water.py reproduces this.

Keeps PTS Gerstner waves, packed moving surface normals, absorption/scattering,
refraction, Fresnel and water lighting. Adapter changes: orthographic eye depth
and view direction; bounded mesh instead of perspective tile LOD; camera-depth
wave mask instead of its absent authored depth buffer; voyage clock; map detail
scale/optical calibration; capped wave steepness and sun glint strength; probe
keyword typo; safe nonnegative SSS power; foam forced off. Unused reflection,
structured-buffer, volumetric-shadow and debug variants are omitted. The
runtime supplies small wave arrays, neutral interaction buffers and coastal sky.
WATER-006 uses blue ripple lighting, original moving packed normals and tiny
crossing displacement. Large swells/height-based colour bands are removed;
sun glints stay blue-capped and foam is disabled, following Mo's supplied game refs.

Does not install the original package managers, physics, legacy camera passes or
change the render pipeline. Uses ordinary URP opaque and depth textures. The old
coastal shader remains available as a fallback until native review is complete.
