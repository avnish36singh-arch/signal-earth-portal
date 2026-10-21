#!/usr/bin/env python3
"""
Signal Earth - Equirectangular Texture Boundary Seam Fixer
Smooths the antimeridian seam (left col 0 and right col 4095) of assets/earth-blue-marble.jpg
using a raised-cosine 16-pixel blending window so wrap-around has 0 discontinuity.
Zero em dashes or en dashes.
"""

import os
from PIL import Image
import numpy as np

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG_PATH = os.path.join(WORKSPACE_ROOT, "assets", "earth-blue-marble.jpg")

def fix_seam():
    im = Image.open(IMG_PATH)
    arr = np.array(im, dtype=float)
    h, w, c = arr.shape

    # Blend window width = 16 pixels on each side
    K = 16
    left_strip = arr[:, :K].copy()
    right_strip = arr[:, -K:].copy()

    # Smooth raised cosine blend weights from 0 to 1
    # At col 0, weight = 0.5 (perfect average of col 0 and col -1)
    weights = 0.5 * (1 + np.cos(np.linspace(0, np.pi, K))) # from 1 down to 0

    for i in range(K):
        w_i = weights[i] # 1.0 at outer, 0.0 at inner
        # Interpolate between col i and col (w - K + i)
        avg = 0.5 * (arr[:, i] + arr[:, w - K + i])
        arr[:, i] = (1.0 - w_i * 0.5) * arr[:, i] + (w_i * 0.5) * arr[:, w - K + i]
        arr[:, w - K + i] = (1.0 - w_i * 0.5) * arr[:, w - K + i] + (w_i * 0.5) * left_strip[:, i]

    # Ensure col 0 matches col -1 exactly
    arr[:, 0] = arr[:, -1] = 0.5 * (arr[:, 0] + arr[:, -1])

    # Clamp and save
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    fixed_im = Image.fromarray(arr)
    fixed_im.save(IMG_PATH, quality=92)
    print(f"[+] Fixed equirectangular texture antimeridian seam on {IMG_PATH}")

if __name__ == "__main__":
    fix_seam()
