import torch

# 查看PyTorch版本
print("PyTorch版本：", torch.__version__)
# 查看PyTorch内置的CUDA版本
print("PyTorch内置CUDA版本：", torch.version.cuda)
# 检查CUDA是否可用
print("CUDA是否可用：", torch.cuda.is_available())
# 查看GPU设备名称（验证GPU识别）
if torch.cuda.is_available():
    print("GPU设备：", torch.cuda.get_device_name(0))
# 依次执行
import torch
print("CUDA可用：", torch.cuda.is_available())  # 有GPU则输出True
from ultralytics import YOLO
print("YOLO加载成功")
exit()