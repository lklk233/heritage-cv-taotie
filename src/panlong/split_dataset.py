# -*- coding: utf-8 -*-
"""将原始标注数据按比例划分到 YOLO 训练集/验证集，支持负样本。

用法:
    python split_dataset.py <正样本目录> [--negatives <负样本目录>] [--ratio 0.8] [--seed 42]

正样本（有标签，如蟠龙纹线稿）:
    <正样本目录>/
        panlong_001.jpg
        panlong_001.txt   ← 自动生成的 YOLO 标签

负样本（无标签，如非龙纹线稿）:
    <负样本目录>/
        other_001.jpg
        other_002.jpg
        ...               ← 无对应 .txt 文件

划分后的结构:
    images/train/   ← 正样本图片 + 负样本图片
    images/val/     ← 正样本图片 + 负样本图片
    labels/train/   ← 仅正样本标签
    labels/val/     ← 仅正样本标签
"""

import sys
import os
import random
import argparse
import shutil
from pathlib import Path

VALID_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "irrelevant_files" / "datasets" / "panlong"


def split_dataset(source_dir, ratio=0.8, seed=42, negatives_dir=None):
    source = Path(source_dir)
    if not source.is_dir():
        print(f"[错误] 目录不存在: {source}")
        return 1

    # 收集正样本（图片-标签配对）
    images = sorted(
        f for f in source.iterdir()
        if f.suffix.lower() in VALID_IMAGE_EXT
    )
    pairs = []
    for img in images:
        label = source / f"{img.stem}.txt"
        if label.exists():
            pairs.append((img, label))
        else:
            print(f"[警告] 跳过无标签文件: {img.name}")

    if not pairs:
        print("[错误] 未找到任何图片-标签配对。请先运行 auto_label.py 生成标签。")
        return 1

    # 收集负样本（仅图片，无标签）
    negative_images = []
    if negatives_dir:
        neg_dir = Path(negatives_dir)
        if neg_dir.is_dir():
            negative_images = sorted(
                f for f in neg_dir.iterdir()
                if f.suffix.lower() in VALID_IMAGE_EXT
            )
            if negative_images:
                print(f"负样本: {len(negative_images)} 张 (来自 {negatives_dir})")
        else:
            print(f"[警告] 负样本目录不存在: {negatives_dir}")

    # 随机划分
    random.seed(seed)

    # 正样本划分
    random.shuffle(pairs)
    split_idx = int(len(pairs) * ratio)
    train_pairs = pairs[:split_idx]
    val_pairs = pairs[split_idx:]

    # 负样本划分（随机混入训练/验证集）
    if negative_images:
        random.shuffle(negative_images)
        neg_split = int(len(negative_images) * ratio)
        train_negatives = negative_images[:neg_split]
        val_negatives = negative_images[neg_split:]
    else:
        train_negatives = []
        val_negatives = []

    # 目标目录
    base = DATASET_ROOT
    dirs = {
        "images/train": base / "images" / "train",
        "images/val":   base / "images" / "val",
        "labels/train": base / "labels" / "train",
        "labels/val":   base / "labels" / "val",
    }

    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    # 清理旧数据
    for d in dirs.values():
        for old in d.iterdir():
            old.unlink()

    # 复制正样本
    def copy_positive_pairs(pair_list, split_name):
        img_dst = dirs[f"images/{split_name}"]
        lbl_dst = dirs[f"labels/{split_name}"]
        for img, lbl in pair_list:
            shutil.copy2(img, img_dst / img.name)
            shutil.copy2(lbl, lbl_dst / lbl.name)

    copy_positive_pairs(train_pairs, "train")
    copy_positive_pairs(val_pairs, "val")

    # 复制负样本（仅图片，无标签）
    def copy_negative_images(neg_list, split_name):
        if not neg_list:
            return
        img_dst = dirs[f"images/{split_name}"]
        for img in neg_list:
            shutil.copy2(img, img_dst / img.name)

    copy_negative_images(train_negatives, "train")
    copy_negative_images(val_negatives, "val")

    # 统计
    def count_boxes(pairs_list):
        total_boxes = 0
        for _, lbl in pairs_list:
            lines = lbl.read_text("utf-8").strip().splitlines()
            total_boxes += sum(1 for line in lines if line.strip())
        return total_boxes

    train_boxes = count_boxes(train_pairs)
    val_boxes = count_boxes(val_pairs)

    print(f"\n{'='*50}")
    print(f"数据集划分完成 (seed={seed})")
    print(f"  正样本: {len(pairs)} 张")
    print(f"    训练集: {len(train_pairs)} 张图片, {train_boxes} 个标注框 ({100*len(train_pairs)/len(pairs):.1f}%)")
    print(f"    验证集: {len(val_pairs)} 张图片, {val_boxes} 个标注框 ({100*len(val_pairs)/len(pairs):.1f}%)")
    if negative_images:
        print(f"  负样本: {len(negative_images)} 张")
        print(f"    训练集: {len(train_negatives)} 张 (无标签)")
        print(f"    验证集: {len(val_negatives)} 张 (无标签)")
    print(f"\n文件已分配到 images/train, images/val, labels/train, labels/val")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="划分 YOLO 数据集（支持负样本）")
    parser.add_argument("source", help="正样本目录（含图片+标签配对）")
    parser.add_argument("--negatives", default=None, help="负样本目录（仅图片，无标签）")
    parser.add_argument("--ratio", type=float, default=0.8, help="训练集比例 (默认 0.8)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子 (默认 42)")
    args = parser.parse_args()

    sys.exit(split_dataset(args.source, args.ratio, args.seed, args.negatives))
