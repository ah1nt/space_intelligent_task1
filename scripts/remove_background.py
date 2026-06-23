from __future__ import annotations

import argparse
from pathlib import Path

from rembg import remove


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove image background and export RGBA PNG.")
    parser.add_argument("input_image", help="Input image path")
    parser.add_argument("output_image", help="Output RGBA PNG path")
    args = parser.parse_args()

    input_path = Path(args.input_image)
    output_path = Path(args.output_image)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, "rb") as f:
        input_bytes = f.read()

    output_bytes = remove(input_bytes)

    with open(output_path, "wb") as f:
        f.write(output_bytes)

    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
