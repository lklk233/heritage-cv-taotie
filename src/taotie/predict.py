# -*- coding: utf-8 -*-
"""批量预测真实青铜器图片中的兽面纹（饕餮纹）。"""

import argparse
from pathlib import Path

from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = PROJECT_ROOT / "irrelevant_files" / "models" / "checkpoints" / "taotie_train4" / "best.pt"
DEFAULT_SOURCE = PROJECT_ROOT / "irrelevant_files" / "datasets" / "taotie" / "real"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "predictions"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


def parse_args():
    parser = argparse.ArgumentParser(description="批量预测真实青铜器图片中的兽面纹")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="模型权重路径")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="待预测图片目录")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="预测结果目录")
    parser.add_argument("--conf", type=float, default=0.3, help="置信度阈值")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU 阈值")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.model.is_file():
        raise FileNotFoundError(f"模型文件不存在: {args.model}")
    if not args.source.is_dir():
        raise FileNotFoundError(f"输入目录不存在: {args.source}")

    image_files = sorted(path for path in args.source.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)
    if not image_files:
        raise FileNotFoundError(f"目录中没有图片: {args.source}")

    model = YOLO(str(args.model))
    detected = 0
    for image_path in image_files:
        result = model.predict(
            source=str(image_path),
            conf=args.conf,
            iou=args.iou,
            save=True,
            project=str(args.output),
            name="taotie",
            exist_ok=True,
        )[0]
        count = len(result.boxes)
        detected += count > 0
        print(f"[{'检测' if count else '未检测'}] {image_path.name} — {count} 个框")

    print(f"完成：{len(image_files)} 张，检出 {detected} 张，未检出 {len(image_files) - detected} 张")
    print(f"结果目录：{args.output / 'taotie'}")


if __name__ == "__main__":
    main()
