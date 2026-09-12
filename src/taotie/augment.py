# -*- coding: utf-8 -*-
"""离线数据增强：对训练集图片做几何/色彩变换，自动裁黑边，标签保持全图框。

用法:
    python augment.py --multiplier 3

功能:
    每张训练图片生成 N 个增强变体（multiplier=3 则 60→180 张）
    增强策略（随机组合）:
        - 水平翻转 (50% 概率)
        - 旋转 ±8°
        - 缩放 0.85~1.15
        - 亮度/对比度调整
    几何变换后自动裁剪黑边 → 标签仍为全图框
    负样本图片同样增强（无需标签）

输出:
    增强后的图片+标签直接写入 images/train/ 和 labels/train/
    文件名加 _aug1, _aug2 后缀
"""

import sys
import random
import argparse
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np

VALID_EXT = {".jpg", ".jpeg", ".png", ".bmp"}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "irrelevant_files" / "datasets" / "taotie"


def auto_crop_black(img, threshold=20):
    """自动裁剪黑色/近黑色边框（保留内容区域）。"""
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img)
    # 找到非黑色像素（任何通道 > threshold）
    mask = np.any(arr > threshold, axis=2).astype(np.uint8)
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any() or not cols.any():
        return img
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    return img.crop((x_min, y_min, x_max + 1, y_max + 1))


def augment_one(img, rng):
    """对单张图片施加随机增强组合，返回增强后的图片。"""
    aug = img.copy()

    # 水平翻转
    if rng.random() < 0.5:
        aug = ImageOps.mirror(aug)

    # 旋转 ±8°
    angle = rng.uniform(-8, 8)
    if abs(angle) > 0.5:
        aug = aug.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0))
        aug = auto_crop_black(aug)

    # 缩放 0.85~1.15
    scale = rng.uniform(0.85, 1.15)
    if abs(scale - 1.0) > 0.02:
        w, h = aug.size
        new_w, new_h = int(w * scale), int(h * scale)
        aug = aug.resize((new_w, new_h), Image.BICUBIC)
        if scale < 1.0:
            # 缩小后用黑边填充到原尺寸
            canvas = Image.new("RGB", (w, h), (0, 0, 0))
            ox, oy = (w - new_w) // 2, (h - new_h) // 2
            canvas.paste(aug, (ox, oy))
            aug = canvas
        else:
            # 放大后取中心裁剪
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            aug = aug.crop((left, top, left + w, top + h))
        aug = auto_crop_black(aug)

    # 亮度 0.8~1.2
    brightness = rng.uniform(0.8, 1.2)
    aug = ImageEnhance.Brightness(aug).enhance(brightness)

    # 对比度 0.8~1.2
    contrast = rng.uniform(0.8, 1.2)
    aug = ImageEnhance.Contrast(aug).enhance(contrast)

    return aug


def augment_dataset(multiplier=3, seed=42):
    rng = random.Random(seed)
    base = DATASET_ROOT

    img_train = base / "images" / "train"
    lbl_train = base / "labels" / "train"

    if not img_train.is_dir():
        print("[错误] images/train/ 为空，请先运行 split_dataset.py")
        return 1

    images = sorted(f for f in img_train.iterdir() if f.suffix.lower() in VALID_EXT)
    if not images:
        print("[错误] 训练集无图片")
        return 1

    # 统计原始数量
    pos_count = sum(1 for f in images if not f.stem.startswith("neg"))
    neg_count = sum(1 for f in images if f.stem.startswith("neg"))
    aug_pos, aug_neg = 0, 0

    print(f"原始训练集: {pos_count} 正样本 + {neg_count} 负样本")
    print(f"每个样本生成 {multiplier} 个增强变体\n")

    for img_path in images:
        img = Image.open(img_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

        stem = img_path.stem
        is_positive = not stem.startswith("neg")
        has_label = (lbl_train / f"{stem}.txt").exists()

        for i in range(1, multiplier + 1):
            aug_img = augment_one(img, rng)

            # 生成随机文件名（避免与原文件按前缀聚类）
            rand_id = rng.randint(1000, 9999)
            aug_stem = f"{stem}_aug{i}_{rand_id}"
            aug_img_path = img_train / f"{aug_stem}.jpg"
            aug_img.save(aug_img_path, "JPEG", quality=95)

            # 正样本：复制标签（全图框不变）
            if is_positive and has_label:
                label_content = f"0 0.5 0.5 1.0 1.0\n"
                (lbl_train / f"{aug_stem}.txt").write_text(label_content, encoding="utf-8")
                aug_pos += 1
            else:
                aug_neg += 1

        if len(images) <= 20 or images.index(img_path) % 10 == 0:
            print(f"  [{images.index(img_path)+1}/{len(images)}] {stem} → ×{multiplier}")

    # 报告
    new_pos = pos_count + aug_pos
    new_neg = neg_count + aug_neg
    print(f"\n{'='*50}")
    print(f"数据增强完成 (multiplier={multiplier})")
    print(f"  正样本: {pos_count} → {new_pos} ({aug_pos} 增强)")
    print(f"  负样本: {neg_count} → {new_neg} ({aug_neg} 增强)")
    print(f"  训练集总计: {new_pos + new_neg} 张图片")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="训练集离线数据增强")
    parser.add_argument("--multiplier", type=int, default=3, help="每个样本生成的增强变体数 (默认 3)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    sys.exit(augment_dataset(args.multiplier, args.seed))
