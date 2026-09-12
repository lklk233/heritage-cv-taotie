# Project structure

- `src/taotie/`：兽面纹数据处理、训练、验证、推理和报告生成脚本。
- `src/panlong/`：蟠龙纹实验脚本，目前数据集尚未完成。
- `configs/`：Ultralytics YOLO 数据集配置。
- `results/taotie_train4/`：最终训练参数、CSV 指标和评估图表，不包含权重。
- `results/real_predictions/`：真实文物图片的历史预测输出。
- `assets/`：项目文档引用的静态资源。
- `irrelevant_files/`：数据集、模型、论文资料、日志、缓存和旧目录；该目录不会提交到 Git。

源码通过 `Path(__file__)` 定位项目根目录，训练和推理命令应从仓库根目录执行。
