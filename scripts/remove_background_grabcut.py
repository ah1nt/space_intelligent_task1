from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a rough foreground PNG with GrabCut.")
    parser.add_argument("input_image", help="Input image path")
    parser.add_argument("output_image", help="Output RGBA PNG path")
    args = parser.parse_args()

    input_path = Path(args.input_image)
    output_path = Path(args.output_image)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_bgr = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise FileNotFoundError(f"cannot read image: {input_path}")

    height, width = image_bgr.shape[:2]
    rect = (
        int(width * 0.18),
        int(height * 0.12),
        int(width * 0.64),
        int(height * 0.72),
    )

    mask = np.zeros((height, width), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(image_bgr, mask, rect, bgd_model, fgd_model, 8, cv2.GC_INIT_WITH_RECT)

    alpha = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0,
    ).astype(np.uint8)

    kernel = np.ones((5, 5), np.uint8)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)

    image_rgba = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2BGRA)
    image_rgba[:, :, 3] = alpha
    cv2.imwrite(str(output_path), image_rgba)

    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
