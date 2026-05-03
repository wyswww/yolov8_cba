import torch
import numpy as np

# 从Python整数创建一个零维张量（标量）
tensor0d = torch.tensor(1)

# 从Python列表创建一个一维张量（向量）
tensor1d = torch.tensor([1, 2, 3])

# 从嵌套的Python列表创建一个二维张量
tensor2d = torch.tensor([[1, 2],
                         [3, 4]])

# 从嵌套的Python列表创建一个三维张量
tensor3d_1 = torch.tensor([[[1, 2], [3, 4]],
                           [[5, 6], [7, 8]]])

# 从NumPy数组创建一个张量
ary3d = np.array([[[1, 2], [3, 4]],
                  [[5, 6], [7, 8]]])
tensor3d_2 = torch.tensor(ary3d)  # 复制 NumPy 数组
tensor3d_3 = torch.from_numpy(ary3d)  # 与 NumPy 数组共享内存