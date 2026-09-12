# -*- coding: utf-8 -*-
"""线稿图像预处理：RGBA→RGB、统一命名、可选裁剪缩放。

用法:
    python preprocess.py <输入目录> <输出目录> [选项]

功能:
    1. RGBA→RGB（透明背景替换为白色）
    2. 自动裁剪白边（可选，--crop）
    3. 缩放到统一尺寸（可选，--size 640）
    4. 统一重命名为 prefix_001.jpg, prefix_002.jpg, ...
    5. 保存文件名映射表 mapping.csv
"""

import sys
import os
import argparse
import csv
from pathlib import Path
from PIL import Image, ImageOps


VALID_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def rgba_to_rgb(img):
    """将 RGBA 图像合成到白色背景上转为 RGB。"""
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    if img.mode in ("L", "P"):
        return img.convert("RGB")
    if img.mode == "RGB":
        return img
    return img.convert("RGB")


def auto_crop(img, margin=5):
    """自动裁剪白边，留少量边距。"""
    gray = img.convert("L")
    # 二值化：非纯白像素视为内容
    inv = gray.point(lambda p: 0 if p > 250 else 255)
    bbox = inv.getbbox()
    if bbox is None:
        return img
    left = max(0, bbox[0] - margin)
    top = max(0, bbox[1] - margin)
    right = min(img.width, bbox[2] + margin)
    bottom = min(img.height, bbox[3] + margin)
    return img.crop((left, top, right, bottom))


def preprocess(source_dir, output_dir, prefix="taotie", size=None, do_crop=False):
    source = Path(source_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    images = sorted(
        f for f in source.iterdir()
        if f.suffix.lower() in VALID_EXT
    )
    if not images:
        print(f"[错误] 在 {source} 中未找到图片文件")
        return 1

    mapping = []
    count = 0

    for img_path in images:
        try:
            img = Image.open(img_path)
        except Exception as e:
            print(f"[跳过] {img_path.name} — 无法打开: {e}")
            continue

        # RGBA → RGB
        img = rgba_to_rgb(img)

        # 自动裁剪
        if do_crop:
            img = auto_crop(img)

        # 缩放到统一尺寸（保持宽高比）
        if size:
            img = ImageOps.contain(img, (size, size))

        count += 1
        new_name = f"{prefix}_{count:03d}.jpg"
        save_path = out / new_name
        img.save(save_path, "JPEG", quality=95)

        mapping.append({
            "original": img_path.name,
            "new": new_name,
            "orig_size": f"{img_path.stat().st_size}",
            "new_size": f"{img.width}x{img.height}",
        })
        print(f"[{count:03d}] {img_path.name} → {new_name} ({img.width}x{img.height})")

    # 保存映射表
    csv_path = out / "mapping.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["original", "new", "orig_size", "new_size"])
        w.writeheader()
        w.writerows(mapping)

    print(f"\n{'='*50}")
    print(f"预处理完成: {count} 张图片 → {out}/")
    print(f"映射表: {csv_path}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="线稿图像预处理")
    parser.add_argument("source", help="原始图片目录")
    parser.add_argument("output", help="输出目录")
    parser.add_argument("--prefix", default="taotie", help="输出文件名前缀 (默认 taotie)")
    parser.add_argument("--size", type=int, default=None, help="统一缩放到的最大边长 (默认不缩放)")
    parser.add_argument("--crop", action="store_true", help="自动裁剪白边")
    args = parser.parse_args()

    sys.exit(preprocess(
        args.source, args.output,
        prefix=args.prefix, size=args.size, do_crop=args.crop,
    ))
