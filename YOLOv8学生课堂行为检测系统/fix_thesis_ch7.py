# -*- coding: utf-8 -*-
"""Replace sprawling Chapter 7 (7.1~7.10) with condensed 7.1 (论文总结) + 7.2 (工作展望)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('王岩松论文final_1y_v3.docx')

def set_para(para, text):
    for r in para.runs:
        r.text = ''
    if para.runs:
        para.runs[0].text = text

def clear_para(para):
    for r in para.runs:
        r.text = ''

# ===== 7.1 heading stays at [560] =====

# ===== Replace 7.1 body [561] with condensed summary =====
summary = (
    '本文设计并实现了一套基于YOLOv8的学生课堂行为检测系统，完成数据集配置、六种策略对比实验、'
    '系统开发和结果分析。系统能够识别举手、阅读、书写、使用手机、低头、趴桌六类行为，'
    '支持图片、视频、摄像头和批量检测。'
    '\n\n'
    '在算法实验方面，本文以YOLOv8m基线模型（mAP@0.5=89.61%）为起点，依次开展五组改进实验。'
    'ECA单通道注意力和P2检测头两种纯结构改进均未超过基线。CoordAtt+ECA组合注意力方案在匹配弱增强策略后'
    '取得mAP@0.5=96.25%的显著提升，验证了空间-通道互补注意力设计的有效性，同时揭示了注意力机制效果'
    '高度依赖训练策略匹配这一核心原则。Strong模型进一步融合长尾均衡训练、800高分辨率、弱增强和'
    '二阶段微调四项策略，取得mAP@0.5=96.73%、mAP@0.5:0.95=82.40%的最优结果。'
    '本文将Strong作为高精度推荐方案，将Baseline（640推理）作为轻量实时备选方案。'
    '\n\n'
    '本文创新点体现在三个方面：第一，面向课堂行为检测构建了从基线训练到六策略对比的完整实验体系，'
    '分析了不同改进方向的实际效果；第二，将目标检测与课堂专注度计算结合，设计了基于行为类别权重、'
    '置信度融合和时序跟踪的专注度评估方法；第三，基于PyQt5和OpenCV完成桌面端可视化系统开发，'
    '实现了从模型推理到专注度分析的完整交互流程。'
)
set_para(doc.paragraphs[561], summary)

# ===== Clear remaining 7.1 body [562-563] =====
for i in [562, 563]:
    clear_para(doc.paragraphs[i])

# ===== Rename 7.2 heading [564] =====
for r in doc.paragraphs[564].runs:
    if '7.2' in r.text:
        r.text = r.text.replace('7.2 不足与展望', '7.2 工作展望')
        break

# ===== Replace 7.2 body [565] with condensed outlook =====
outlook = (
    '在数据与算法层面，当前数据集类别分布不均衡，低头和趴桌样本较少，少数类识别仍有提升空间。'
    '专注度计算基于规则设计，后续可结合人工评分训练更客观的评估模型。此外可引入人体姿态估计、'
    '目标跟踪和多摄像头融合技术，提升复杂遮挡场景下的识别能力。'
    '\n\n'
    '在工程部署层面，当前系统为本地桌面端原型，后续可将模型导出为ONNX或TensorRT格式加速推理，'
    '开发Web端应用支持多用户访问，或采用边缘计算方案在教室本地完成推理、仅上传统计结果以保护隐私。'
    '系统可增加数据库模块，长期记录课堂状态数据，为教学研究提供数据支撑。'
    '\n\n'
    '在功能扩展层面，可增加结果导出（CSV或Excel）、专注度曲线绘制、类别占比可视化和检测结果筛选等功能，'
    '使统计分析更直观。视频检测可引入ByteTrack或DeepSORT等跟踪算法，关联同一学生在连续帧中的行为变化，'
    '减少单帧误检对专注度曲线的干扰。'
)
set_para(doc.paragraphs[565], outlook)

# ===== Clear ALL remaining paragraphs from [566] to [628] =====
# These are old 7.2 remaining body + 7.3~7.10 + their body text
for i in range(566, 629):
    p = doc.paragraphs[i]
    t = p.text.strip()
    if t:  # Only clear non-empty paragraphs
        clear_para(p)

print(f'Cleared paragraphs 566-628 ({629-566} total)')

# ===== Save =====
out = '王岩松论文final_1y_v3.docx'
doc.save(out)
print(f'Saved: {out}')
print('Chapter 7 condensed to 7.1 论文总结 + 7.2 工作展望')
