# -*- coding: utf-8 -*-
"""使用训练好的模型预测图片中的蟠龙纹。"""

import argparse
from pathlib import Path

from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = PROJECT_ROOT / "irrelevant_files" / "models" / "checkpoints" / "panlong_train" / "best.pt"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "predictions"


def parse_args():
    parser = argparse.ArgumentParser(description="预测图片中的蟠龙纹")
    parser.add_argument("source", type=Path, help="待预测图片路径")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="模型权重路径")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="预测结果目录")
    parser.add_argument("--conf", type=float, default=0.3, help="置信度阈值")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.model.is_file():
        raise FileNotFoundError(f"模型文件不存在: {args.model}")
    if not args.source.is_file():
        raise FileNotFoundError(f"测试图片不存在: {args.source}")

    result = YOLO(str(args.model)).predict(
        source=str(args.source),
        conf=args.conf,
        iou=0.45,
        save=True,
        project=str(args.output),
        name="panlong",
        exist_ok=True,
    )[0]
    print(f"检测到 {len(result.boxes)} 个蟠龙纹候选框")
    print(f"结果目录：{args.output / 'panlong'}")


if __name__ == "__main__":
    main()
