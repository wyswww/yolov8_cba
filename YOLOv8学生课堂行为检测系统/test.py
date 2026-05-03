# ==================== 1. 导入必要库和修复环境报错 ====================
import torch  # 导入PyTorch深度学习框架
import warnings  # 导入警告模块

# 忽略程序运行中的无关警告，使界面更整洁
warnings.filterwarnings("ignore")

# 【重要修复】针对 PyTorch 2.6 版本，修复模型加载安全限制问题
# 强制设置 weights_only=False，确保能正常加载训练好的YOLOv8模型
original_load = torch.load
torch.load = lambda *args, **kwargs: original_load(*args, **kwargs, weights_only=False)

# 导入YOLO模型库
from ultralytics import YOLO

# ==================== 2. Windows 系统必须加的主函数保护 ====================
# 防止Windows系统下多进程报错，这是运行程序的入口
if __name__ == '__main__':

    # 加载模型
    model = YOLO('runs/detect/exp/weights/best.pt')

    # ==================== 关键：强制开启保存图像 + 关闭bug ====================
    metrics = model.val(
        data=r'datasets/data.yaml',    # 绝对路径更稳定
        split='test',
        imgsz=640,
        batch=1,
        workers=0,
        project='runs/test',
        name='exp',
        save_json=True,        # 强制保存结果
        save_hybrid=True,      # 保存标签
        plots=True,            #  强制生成曲线图、混淆矩阵、PR曲线
        conf=0.001,            # 低置信度也检测，保证画图完整
        iou=0.6,
    )

    # 打印核心指标
    print("=" * 50)
    print("【模型测试结果】")
    print(f"平均精确率 (mP): {metrics.box.mp:.4f}")
    print(f"平均召回率 (mR): {metrics.box.mr:.4f}")
    print(f"mAP@0.5        : {metrics.box.map50:.4f}")
    print(f"mAP@0.5:0.95   : {metrics.box.map:.4f}")
    print("=" * 50)

