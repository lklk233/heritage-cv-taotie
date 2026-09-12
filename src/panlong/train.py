# -*- coding: utf-8 -*-
"""训练蟠龙纹 YOLOv8 模型。"""

from pathlib import Path

import torch
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_CONFIG = PROJECT_ROOT / "configs" / "panlong.yaml"
PRETRAINED_WEIGHT = PROJECT_ROOT / "irrelevant_files" / "models" / "pretrained" / "yolov8n.pt"
RESULTS_DIR = PROJECT_ROOT / "results"


def main():
    cuda_available = torch.cuda.is_available()
    print("CUDA 可用:", cuda_available)
    if cuda_available:
        print("GPU 型号:", torch.cuda.get_device_name(0))

    model_source = str(PRETRAINED_WEIGHT) if PRETRAINED_WEIGHT.exists() else "yolov8n.pt"
    model = YOLO(model_source)
    model.train(
        data=str(DATA_CONFIG),
        epochs=100,
        imgsz=640,
        batch=8,
        device=0 if cuda_available else "cpu",
        patience=20,
        save=True,
        project=str(RESULTS_DIR),
        name="panlong_train",
    )


if __name__ == "__main__":
    main()
