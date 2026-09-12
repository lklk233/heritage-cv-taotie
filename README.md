# Heritage CV Taotie

基于 Ultralytics YOLOv8 的青铜器兽面纹（饕餮纹）识别研究项目。本仓库保存可复现的源码、配置和实验结果；数据集、模型权重、原始文献与本地缓存不上传 GitHub。

## 项目结构

```text
heritage-cv-taotie/
├── README.md
├── .gitignore
├── environment.yml
├── requirements.txt
├── src/                    # 数据处理、训练、验证和推理代码
├── configs/                # YOLO 数据集配置
├── docs/                   # 项目说明文档
├── results/                # 可公开的指标、曲线和预测示例
├── assets/                 # README 等文档使用的静态资源
└── irrelevant_files/       # 本地数据、权重、原始文献和缓存（Git 忽略）
```

## 环境安装

```bash
conda env create -f environment.yml
conda activate heritage-cv-taotie
```

也可以使用 pip：

```bash
pip install -r requirements.txt
```

## 本地数据布局

数据与权重默认放在不会提交到 Git 的 `irrelevant_files/`：

```text
irrelevant_files/
├── datasets/
│   ├── taotie/
│   │   ├── images/{train,val}/
│   │   ├── labels/{train,val}/
│   │   └── real/
│   └── panlong/
│       ├── images/{train,val}/
│       └── labels/{train,val}/
└── models/
    ├── pretrained/yolov8n.pt
    └── checkpoints/taotie_train4/best.pt
```

## 使用方法

所有命令均从项目根目录运行。

```bash
# 检查运行环境
python src/check_environment.py

# 校验兽面纹数据集
python src/taotie/verify_dataset.py

# 训练
python src/taotie/train.py

# 批量预测本地真实图片
python src/taotie/predict.py
```

推理脚本也支持自定义路径：

```bash
python src/taotie/predict.py --model path/to/best.pt --source path/to/images --output results/predictions
```

## 当前结果

现有实验使用 76 张兽面纹线稿正样本和 19 张蟠龙纹负样本。训练集经过离线增强后包含 300 张图片，验证集包含 20 张图片。最终实验文件见 `results/taotie_train4/`。

需要注意：当前正样本采用覆盖整张图片的边界框，因此结果主要反映整图级纹饰识别能力，不能等同于真实文物照片中的精确区域定位能力。

## 数据与模型

由于文件体积、数据来源授权和 GitHub 仓库大小限制，本仓库不提供：

- 原始或处理后的训练数据；
- 真实文物测试图片；
- YOLO 预训练权重和训练权重；
- PDF、Word、训练日志与本地缓存。

这些文件在本地统一保存在 `irrelevant_files/`，并由 `.gitignore` 排除。
