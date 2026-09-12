# -*- coding: utf-8 -*-
"""为预处理后的正样本图片自动生成 YOLO 全图框标签。

用法:
    python auto_label.py <图片目录> [输出标签目录]

功能:
    为每张图片生成一个覆盖全图的边界框标签:
        0 0.5 0.5 1.0 1.0
    （class_id=0=panlong, 中心(0.5,0.5), 宽=1.0, 高=1.0）

    适用于"每图仅一个独立纹饰"的场景。
"""

import sys
import os
import argparse
from pathlib import Path


VALID_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


def auto_label(image_dir, label_dir=None, class_id=0):
    img_dir = Path(image_dir)
    if not img_dir.is_dir():
        print(f"[错误] 目录不存在: {img_dir}")
        return 1

    lbl_dir = Path(label_dir) if label_dir else img_dir
    lbl_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(
        f for f in img_dir.iterdir()
        if f.suffix.lower() in VALID_EXT
    )
    if not images:
        print(f"[错误] 在 {img_dir} 中未找到图片")
        return 1

    count = 0
    label_content = f"{class_id} 0.5 0.5 1.0 1.0\n"

    for img in images:
        label_path = lbl_dir / f"{img.stem}.txt"
        if label_path.exists():
            # 检查是否已有不同内容
            existing = label_path.read_text("utf-8").strip()
            if existing != label_content.strip():
                print(f"[警告] {label_path.name} 已存在且内容不同，将覆盖")
        label_path.write_text(label_content, encoding="utf-8")
        count += 1
        print(f"[{count:03d}] {img.name} → {label_path.name}  (全图框)")

    print(f"\n{'='*50}")
    print(f"标签生成完成: {count} 个标签 → {lbl_dir}/")
    print(f"标签内容: {label_content.strip()}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动生成 YOLO 全图框标签")
    parser.add_argument("image_dir", help="图片目录")
    parser.add_argument("--label_dir", default=None, help="标签输出目录 (默认与图片同目录)")
    parser.add_argument("--class_id", type=int, default=0, help="类别 ID (默认 0)")
    args = parser.parse_args()

    sys.exit(auto_label(args.image_dir, args.label_dir, args.class_id))
