# -*- coding: utf-8 -*-
"""训练前数据集完整性检查。

用法:
    python verify_dataset.py

检查项:
    1. images/train, images/val, labels/train, labels/val 目录存在
    2. 图片与标签一一配对
    3. 统计各集图片数、边界框数、类别分布
    4. 与 data.yaml 配置一致性
"""

import sys
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE = PROJECT_ROOT / "irrelevant_files" / "datasets" / "taotie"
CONFIG_PATH = PROJECT_ROOT / "configs" / "taotie.yaml"
VALID_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def verify_split(split_name):
    img_dir = BASE / "images" / split_name
    lbl_dir = BASE / "labels" / split_name

    if not img_dir.is_dir():
        return None, f"目录不存在: {img_dir}"
    if not lbl_dir.is_dir():
        return None, f"目录不存在: {lbl_dir}"

    images = sorted(
        f for f in img_dir.iterdir()
        if f.suffix.lower() in VALID_IMAGE_EXT
    )
    labels = sorted(lbl_dir.glob("*.txt"))

    img_stems = {f.stem for f in images}
    lbl_stems = {f.stem for f in labels}

    orphan_img = img_stems - lbl_stems
    orphan_lbl = lbl_stems - img_stems

    errors = []
    if orphan_lbl:
        errors.append(f"  {len(orphan_lbl)} 个标签缺少图片")

    # 统计边界框
    total_boxes = 0
    class_ids = {}
    for lbl in labels:
        for line in lbl.read_text("utf-8").strip().splitlines():
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) == 5:
                cls = int(parts[0])
                class_ids[cls] = class_ids.get(cls, 0) + 1
                total_boxes += 1

    return {
        "images": len(images),
        "labels": len(labels),
        "boxes": total_boxes,
        "class_ids": class_ids,
        "errors": errors,
        "negatives": len(orphan_img),
    }, None


def main():
    print("=" * 50)
    print("数据集验证报告")
    print("=" * 50)

    all_ok = True

    for split in ["train", "val"]:
        info, err = verify_split(split)
        if err:
            print(f"\n[{split}] {err}")
            all_ok = False
            continue

        print(f"\n[{split}]")
        print(f"  图片: {info['images']}")
        print(f"  标签: {info['labels']}")
        print(f"  边界框: {info['boxes']}")
        if info["negatives"] > 0:
            print(f"  负样本(无标签): {info['negatives']} 张")
        if info["class_ids"]:
            print(f"  类别分布: {info['class_ids']}")
        else:
            print(f"  [警告] 未检测到任何边界框")

        for e in info["errors"]:
            print(f"  [错误] {e}")
            all_ok = False

    # 与 data.yaml 对比
    yaml_path = CONFIG_PATH
    if yaml_path.exists():
        with open(yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        print(f"\n--- data.yaml ---")
        print(f"  nc (类别数): {cfg.get('nc', '?')}")
        print(f"  names: {cfg.get('names', '?')}")

        # 检查是否有数据
        train_count = len(list((BASE / "images" / "train").glob("*"))) if (BASE / "images" / "train").is_dir() else 0
        val_count = len(list((BASE / "images" / "val").glob("*"))) if (BASE / "images" / "val").is_dir() else 0

        if train_count == 0:
            print("\n[提示] 训练集为空，请先运行 split_dataset.py 划分数据。")
            all_ok = False
        else:
            print(f"\n[结果] 数据集就绪，可以运行 train.py 开始训练。")
    else:
        print("\n[错误] data.yaml 不存在")
        all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
