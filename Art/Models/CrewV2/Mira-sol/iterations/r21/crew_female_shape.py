"""Reusable CrewV2 clothed female silhouette, in the CrewRig metre bind pose.

Apply AFTER authoring a male garment and BEFORE skinning/export (or to an
already skinned garment's bind vertices). Weights, indices, bones and Z never
change. Apply the SAME field to torso tailoring/buttons/straps; skip head,
arms/hands and boots. female=False is exactly the original male shape.
No bpy dependency: future Lise/Tess/etc builders can import this module.
"""
import math

VERSION = 'CrewV2-female-1'


def smooth_window(value, low, high, feather):
    def ease(t):
        t = min(1.0, max(0.0, t))
        return t*t*(3.0-2.0*t)
    return ease((value-low)/feather)*ease((high-value)/feather)


def female_shape(co, female=True, region='torso'):
    """Return bind (x,y,z). region='hips' is for proximal trouser geometry.

    Torso: waist up to10% narrower; coat hip hem8% wider/7% deeper;
    small broad chest volume at upper front, maximum12mm under clothing.
    Hips: blend to zero by the knee, keeping feet and rig stance identical.
    """
    x,y,z = co
    if not female:
        return (x,y,z)
    if region == 'hips':
        t = smooth_window(z,.185,.355,.065)
        return (x*(1.0+.06*t), y*(1.0+.08*t), z)
    hip = math.exp(-((z-.302)/.047)**2)
    waist = math.exp(-((z-.397)/.041)**2)
    upper = smooth_window(z,.425,.535,.035)
    nx = x*(1.0+.08*hip-.10*waist)
    ny = y*(1.0+.07*hip-.035*waist)
    # Gentle single garment volume, with a subtle paired form underneath.
    # No skin detail or exposed anatomy; all role clothes use this envelope.
    front = min(1.0,max(0.0,(-y-.010)/.065))
    chest = math.exp(-((abs(x)-.052)/.063)**2)
    ny -= .012*upper*front*chest
    return (nx,ny,z)


def region_for_weights(weights):
    """Return deformation region for an existing CrewRig skinned vertex.

    Excludes arms even at shoulder intersections; head/neck/boots stay exact.
    Apply to every clothing/torso accessory mesh, not the head mesh.
    """
    if any(w>1e-7 and ('UpLeg' in n or n.endswith('Leg')) for n,w in weights.items()):
        return 'hips'
    if any(w>1e-7 and n in {'Hips','Spine','Spine1'} for n,w in weights.items()):
        return 'torso'
    return None
