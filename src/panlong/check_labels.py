# -*- coding: utf-8 -*-
"""验证 LabelImg 标注输出的正确性。

用法:
    python check_labels.py <标注图片目录>

检查项:
    1. 图片与标签文件一一配对
    2. 标签文件非空
    3. class_id 全为 0（仅 "long" 类）
    4. 坐标在 [0, 1] 归一化范围内
    5. 每行恰好 5 个数值
"""

import sys
import os
from pathlib import Path

VALID_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def check_labels(source_dir):
    source = Path(source_dir)
    if not source.is_dir():
        print(f"[错误] 目录不存在: {source}")
        return 1

    images = sorted(
        f for f in source.iterdir()
        if f.suffix.lower() in VALID_IMAGE_EXT
    )
    label_files = sorted(source.glob("*.txt"))

    errors = 0
    warnings = 0

    # 1) 配对检查
    img_stems = {f.stem for f in images}
    lbl_stems = {f.stem for f in label_files}

    orphan_images = img_stems - lbl_stems
    orphan_labels = lbl_stems - img_stems

    if orphan_images:
        errors += len(orphan_images)
        print(f"\n[错误] {len(orphan_images)} 张图片缺少标签:")
        for name in sorted(orphan_images)[:10]:
            print(f"  - {name}")
        if len(orphan_images) > 10:
            print(f"  ... 及另外 {len(orphan_images) - 10} 项")

    if orphan_labels:
        errors += len(orphan_labels)
        print(f"\n[错误] {len(orphan_labels)} 个标签缺少图片:")
        for name in sorted(orphan_labels)[:10]:
            print(f"  - {name}")
        if len(orphan_labels) > 10:
            print(f"  ... 及另外 {len(orphan_labels) - 10} 项")

    # 2) 逐标签文件检查
    paired_images = sorted(
        f for f in images if f.stem in lbl_stems
    )

    for img_path in paired_images:
        label_path = source / f"{img_path.stem}.txt"
        lines = label_path.read_text(encoding="utf-8").strip().splitlines()

        if not lines or (len(lines) == 1 and lines[0] == ""):
            warnings += 1
            print(f"[警告] 标签为空: {label_path.name}  (图片有内容但未标注)")
            continue

        for line_no, line in enumerate(lines, 1):
            parts = line.strip().split()
            if len(parts) != 5:
                errors += 1
                print(f"[错误] {label_path.name}:{line_no} 需要 5 个值，实际 {len(parts)} → {line}")
                continue

            try:
                cls_id = int(parts[0])
                x, y, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            except ValueError:
                errors += 1
                print(f"[错误] {label_path.name}:{line_no} 数值解析失败 → {line}")
                continue

            if cls_id != 0:
                errors += 1
                print(f"[错误] {label_path.name}:{line_no} class_id={cls_id}，预期 0（当前项目仅 'long' 类）")

            for name, val in [("x_center", x), ("y_center", y), ("width", w), ("height", h)]:
                if val < 0 or val > 1:
                    errors += 1
                    print(f"[错误] {label_path.name}:{line_no} {name}={val:.4f} 超出 [0,1] 范围")

    # 总结
    print(f"\n{'='*50}")
    print(f"图片总数: {len(images)}")
    print(f"标签总数: {len(label_files)}")
    print(f"有效配对: {len(paired_images)}")
    if warnings:
        print(f"警告: {warnings}")
    if errors:
        print(f"错误: {errors}")
        print("\n[结果] 发现 {errors} 个错误，请修正后重新运行。")
    else:
        print("\n[结果] 全部通过，标注数据可用于划分数据集。")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_labels.py <标注图片目录>")
        print("示例: python check_labels.py images/raw")
        sys.exit(1)

    sys.exit(check_labels(sys.argv[1]))
