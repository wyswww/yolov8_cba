# -*- coding: utf-8 -*-
"""
增强注意力机制模块 - 用于YOLOv8课堂行为检测
包含: SimAM, ECA, CoordAtt, C3CBAM, C3ECA等注意力机制

注意: CBAM类已在conv.py中定义，这里不再重复定义
"""

import torch
import torch.nn as nn
import math

__all__ = ['SimAM', 'ECA', 'CoordAtt', 'C3CBAM', 'C3ECA', 'EMA']


class SimAM(nn.Module):
    """
    SimAM: A Simple, Parameter-Free Attention Module for CNNs
    来自: https://www.sciencedirect.com/science/article/abs/pii/S1364661321002061

    特点: 无需额外参数，效率高，效果好
    """
    def __init__(self, e_lambda=1e-4):
        super(SimAM, self).__init__()
        self.activation = nn.Sigmoid()
        self.e_lambda = e_lambda

    def forward(self, x):
        # 计算均值和方差
        mean = x.mean(dim=[2, 3], keepdim=True)
        var = x.var(dim=[2, 3], keepdim=True) + self.e_lambda

        # 计算注意力权重
        t = (x - mean) / torch.sqrt(var)
        t = (x - mean) / torch.sqrt(var)
        attention = self.activation(t.pow(2)).pow(0.5)

        return x * attention


class ECA(nn.Module):
    """
    高效通道注意力(Efficient Channel Attention)
    来自: https://arxiv.org/abs/1910.03151

    特点: 使用1D卷积实现局部跨通道交互，计算量小
    """
    def __init__(self, channels, gamma=2, b=1):
        super(ECA, self).__init__()
        t = int(abs((math.log(channels, 2) + b) / gamma))
        k = t if t % 2 else t + 1
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size=k, padding=k // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        y = self.avg_pool(x)
        y = self.conv(y.squeeze(-1).transpose(-1, -2)).transpose(-1, -2).unsqueeze(-1)
        y = self.sigmoid(y)
        return x * y.expand_as(x)


class CoordAtt(nn.Module):
    """
    坐标注意力(Coordinate Attention)
    来自: https://arxiv.org/abs/2103.02907

    特点: 将通道注意力分解为两个1D特征编码过程，分别沿水平和垂直方向聚合特征
    """
    def __init__(self, inp, oup, reduction=32):
        super(CoordAtt, self).__init__()
        mip = max(8, inp // reduction)

        self.conv1 = nn.Conv2d(inp, mip, kernel_size=1, stride=1, padding=0)
        self.bn1 = nn.BatchNorm2d(mip)
        self.act = nn.ReLU()

        self.conv_h = nn.Conv2d(mip, oup, kernel_size=1, stride=1, padding=0)
        self.conv_w = nn.Conv2d(mip, oup, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        identity = x
        n, c, h, w = x.size()

        # 步骤1: 坐标感知池化 — 分别沿宽度和高度方向池化到1D
        x_h = x.mean(dim=3, keepdim=True)   # (b, c, h, 1) — 水平方向编码
        x_w = x.mean(dim=2, keepdim=True)   # (b, c, 1, w) — 垂直方向编码

        # 步骤2: 拼接 — 将x_w转置后拼接到x_h的高度维度上
        x_w_t = x_w.transpose(2, 3)         # (b, c, w, 1)
        x_cat = torch.cat([x_h, x_w_t], dim=2)  # (b, c, h+w, 1)

        # 步骤3: 共享卷积降维 + BN + ReLU
        x_cat = self.act(self.bn1(self.conv1(x_cat)))  # (b, mip, h+w, 1)

        # 步骤4: 拆分为水平和垂直两个分支
        x_h, x_w = x_cat.split([h, w], dim=2)  # (b, mip, h, 1), (b, mip, w, 1)
        x_w = x_w.transpose(2, 3)              # (b, mip, 1, w)

        # 步骤5: 分别卷积 + sigmoid 生成注意力权重
        a_h = self.conv_h(x_h).sigmoid()       # (b, oup, h, 1)
        a_h = self.conv_h(x_h).sigmoid()
        a_w = self.conv_w(x_w).sigmoid()

        # 步骤6: 广播乘积应用到输入特征图
        out = identity * a_h * a_w

        return out


# ============================================================
# 带注意力机制的C3模块变体
# ============================================================

class C3CBAM(nn.Module):
    """
    带CBAM注意力的C3模块
    将CBAM集成到Bottleneck中
    注意: CBAM从conv.py导入
    """
    def __init__(self, c1, c2, n=1, shortcut=True, g=1, e=0.5):
        super().__init__()
        from .conv import CBAM  # 从conv.py导入CBAM
        c_ = int(c2 * e)
        self.cv1 = nn.Conv2d(c1, c_, 1, 1)
        self.cv2 = nn.Conv2d(c1, c_, 1, 1)
        self.cv3 = nn.Conv2d(2 * c_, c2, 1)
        self.m = nn.Sequential(*(
            BottleneckWithAttention(c_, c_, shortcut, g, e=1.0)
            for _ in range(n)))

    def forward(self, x):
        return self.cv3(torch.cat((self.m(self.cv1(x)), self.cv2(x)), 1))


class BottleneckWithAttention(nn.Module):
    """带CBAM注意力的Bottleneck
    注意: CBAM从conv.py导入
    """
    def __init__(self, c1, c2, shortcut=True, g=1, e=0.5):
        from .conv import CBAM  # 从conv.py导入CBAM
        super().__init__()
        c_ = int(c2 * e)
        self.cv1 = nn.Conv2d(c1, c_, 1, 1)
        self.cv2 = nn.Conv2d(c_, c2, 3, 1, 1, groups=g)
        self.cbam = CBAM(c2)
        self.add = shortcut and c1 == c2

    def forward(self, x):
        out = self.cbam(self.cv2(self.cv1(x)))
        return out + x if self.add else out


class C3ECA(nn.Module):
    """
    带ECA注意力的C3模块
    更轻量级的通道注意力
    """
    def __init__(self, c1, c2, n=1, shortcut=True, g=1, e=0.5):
        super().__init__()
        c_ = int(c2 * e)
        self.cv1 = nn.Conv2d(c1, c_, 1, 1)
        self.cv2 = nn.Conv2d(c1, c_, 1, 1)
        self.cv3 = nn.Conv2d(2 * c_, c2, 1)
        self.eca = ECA(c2)
        # 从本地导入Bottleneck
        from .block import Bottleneck
        self.m = nn.Sequential(*(
            Bottleneck(c_, c_, shortcut, g, e=1.0)
            for _ in range(n)))

    def forward(self, x):
        out = self.eca(self.cv3(torch.cat((self.m(self.cv1(x)), self.cv2(x)), 1)))
        return out


# ============================================================
# EMA注意力 (Efficient Multi-Scale Attention)
# ============================================================

class EMA(nn.Module):
    """
    高效多尺度注意力 EMA
    来自: https://arxiv.org/abs/2309.07945

    特点: 使用分组策略和通道级平均池化实现高效注意力
    """
    def __init__(self, channels, num_groups=32):
        super(EMA, self).__init__()
        self.num_groups = num_groups
        self.group_channels = channels // num_groups
        self.conv = nn.Conv2d(channels, channels, kernel_size=1, bias=False)
        self.norm = nn.GroupNorm(num_groups, channels)
        self.act = nn.Sigmoid()

    def forward(self, x):
        b, c, h, w = x.size()
        g = self.num_groups
        x2 = x.reshape(b, g, -1, h, w)

        # 通道级平均和最大池化
        x_avg = x2.mean(dim=2, keepdim=True)
        x_avg = x2.mean(dim=2, keepdim=True)
        x_max = x2.max(dim=2, keepdim=True)[0]

        # 连接并卷积
        x_concat = torch.cat([x_avg, x_max], dim=2)
        x_concat = torch.cat([x_avg, x_max], dim=2)
        x_concat = x_concat.reshape(b, g, 2, self.group_channels, h, w)
        x_concat = x_concat.permute(0, 1, 3, 4, 5, 2).reshape(b, c, h, w)

        attention = self.act(self.norm(self.conv(x_concat)))
        return x * attention
