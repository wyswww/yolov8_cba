# -*- coding: utf-8 -*-
"""Update the expanded thesis docx with strong_img800_tail_weakaug results.

This script avoids python-docx and edits the docx package XML directly.
It writes a new docx and updates the paper figures under ``论文图表``.
"""

from __future__ import annotations

import copy
import html
import math
import re
import shutil
import struct
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCE_DOCX = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版_插入Test结果图.docx"
OUT_DOCX = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版_最新strong实验结果.docx"
FIG_DIR = ROOT / "论文图表"

STRONG_TEST_DIR = ROOT / "runs/detect/test_strong_img800_tail_weakaug_img800"
STRONG_TRAIN_DIR = ROOT / "runs/detect/strong_img800_tail_weakaug"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

for prefix, uri in NS.items():
    if prefix != "rel":
        ET.register_namespace(prefix, uri)


TEST_ROWS = [
    ["baseline_mAP_100epochs(imgsz=640)", "0.8961", "0.7382", "0.9032", "0.8512"],
    ["optimized_attention_light_m_pretrained", "0.8353", "0.6534", "0.8090", "0.8114"],
    ["yolov8m_p2_100epochs", "0.8377", "0.6547", "0.8130", "0.8005"],
    ["baseline_finetune_img800_weakaug", "0.8898", "0.7278", "0.8975", "0.8527"],
    ["baseline_mAP_100epochs(imgsz=800)", "0.8993", "0.7297", "0.8859", "0.8616"],
    ["strong_img800_tail_weakaug", "0.9673", "0.8240", "0.9345", "0.9419"],
]

VAL_ROWS = [
    ["baseline_mAP_100epochs", "100", "0.91551", "0.75291", "YOLOv8m基线"],
    ["baseline_finetune_img800_weakaug", "25", "0.91402", "0.75852", "高分辨率弱增强微调"],
    ["baseline_finetune_img800_weakaug2", "29", "0.91402", "0.75943", "继续微调实验"],
    ["strong_img800_tail_weakaug", "39", "0.90795", "0.75936", "长尾均衡+800弱增强二阶段微调"],
]

TEXT_REPLACEMENTS_BY_PREFIX = {
    "本文围绕学生课堂行为检测任务，构建了包含举手": (
        "本文围绕学生课堂行为检测任务，构建了包含举手、阅读、书写、使用手机、低头、趴桌六类行为的数据集配置与训练流程。"
        "系统以YOLOv8m为核心检测模型，完成了基线训练、轻量注意力机制实验、P2小目标检测头实验、高分辨率弱增强微调实验、"
        "长尾均衡高分辨率二阶段微调实验以及高分辨率推理实验。最新实验结果表明，strong_img800_tail_weakaug模型在测试集上取得"
        "mAP@0.5为0.9673、mAP@0.5:0.95为0.8240、Precision为0.9345、Recall为0.9419的结果，"
        "相比同等imgsz=800测试口径下的baseline模型分别提升0.0679、0.0942、0.0486和0.0803，综合性能最优。"
    ),
    "YOLOv8m is adopted as the core detection model. Six classroom behavior categories": (
        "YOLOv8m is adopted as the core detection model. Six classroom behavior categories are considered, including hand-raising, reading, writing, using phone, bowing the head and leaning over the table. "
        "This thesis completes baseline training, lightweight attention experiments, P2 detection-head experiments, high-resolution weak-augmentation fine-tuning, tail-balanced high-resolution two-stage fine-tuning and unified test evaluation. "
        "The latest strong_img800_tail_weakaug model achieves 0.9673 mAP@0.5, 0.8240 mAP@0.5:0.95, 0.9345 precision and 0.9419 recall on the test set, outperforming the baseline under the same 800-pixel evaluation setting."
    ),
    "本文没有简单地对少数类进行过度复制": (
        "针对低头和趴桌等少数类样本偏少的问题，本文在前期实验中主要通过调整输入分辨率、减弱不真实增强和提高分类损失权重进行优化；"
        "在最新实验中进一步引入长尾重采样训练集，并与高分辨率弱增强二阶段微调结合，从而缓解类别不均衡对模型学习的影响。"
    ),
    "4.6 改进实验三：高分辨率弱增强微调": "4.6 改进实验三：长尾均衡高分辨率弱增强微调",
    "在注意力和P2结构实验均未超过基线后": (
        "在注意力和P2结构实验均未超过基线后，本文将改进重点转向训练策略优化。前期实验保持模型结构不变，从baseline_mAP_100epochs的best.pt出发进行微调，将输入尺寸从640提高到800，并显著减弱数据增强强度。"
        "最新strong_img800_tail_weakaug实验在此基础上进一步使用classroom_tail_oversampled长尾均衡训练集，使低头、趴桌等少数类在训练阶段获得更多有效学习机会。"
    ),
    "微调实验使用较低初始学习率0.0001": (
        "strong_img800_tail_weakaug实验使用较低初始学习率0.0001，训练轮数设置为60，batch size设置为4。"
        "为了避免后期训练受到不真实增强样本干扰，mosaic、mixup和copy-paste均设置为0，颜色扰动、旋转、平移和尺度缩放也相应降低。"
        "同时将分类损失权重cls从0.5提高到0.65，使模型更关注课堂行为类别区分，特别是低头和趴桌等少数类。"
    ),
    "验证集结果显示，baseline_finetune_img800_weakaug实验": (
        "验证集结果显示，baseline_finetune_img800_weakaug实验的最佳mAP@0.5:0.95达到0.75852，继续微调实验baseline_finetune_img800_weakaug2达到0.75943。"
        "最新strong_img800_tail_weakaug实验最佳mAP@0.5:0.95为0.75936，验证集定位指标与前期最优微调结果基本持平。"
        "在独立测试集上，该模型取得mAP@0.5为0.9673、mAP@0.5:0.95为0.8240、Precision为0.9345、Recall为0.9419，"
        "相较于同等imgsz=800测试口径下的baseline模型提升明显，说明长尾均衡训练集与高分辨率弱增强二阶段微调组合具有更好的泛化效果。"
    ),
    "为了保证实验可复现，本文为不同实验分别编写独立训练脚本": (
        "为了保证实验可复现，本文为不同实验分别编写独立训练脚本，包括train_baseline_100epochs.py、train_optimized_attention.py、train_p2.py、"
        "train_finetune_img800.py、train_img800_weakaug.py和train_strong_img800_tail_weakaug.py。每个脚本中明确记录模型路径、数据集路径、训练轮数、"
        "batch size、输入尺寸、优化器、学习率和数据增强参数。"
    ),
    "表6-1展示了主要模型在测试集上的检测结果": (
        "表6-1展示了主要模型在测试集上的检测结果。YOLOv8m基线模型在原始imgsz=640测试口径下取得mAP@0.5为0.8961、mAP@0.5:0.95为0.7382、"
        "Precision为0.9032、Recall为0.8512的结果；在统一imgsz=800测试口径下取得mAP@0.5为0.8993、mAP@0.5:0.95为0.7297、"
        "Precision为0.8859、Recall为0.8616。最新strong_img800_tail_weakaug模型在同一测试集和imgsz=800设置下取得最优结果。"
    ),
    "高分辨率弱增强微调模型在测试集上的mAP@0.5为0.8898": (
        "最新strong_img800_tail_weakaug模型在测试集上的mAP@0.5为0.9673，mAP@0.5:0.95为0.8240，Precision为0.9345，Recall为0.9419。"
        "与同等imgsz=800测试口径下的baseline模型相比，mAP@0.5提升0.0679，mAP@0.5:0.95提升0.0942，Precision提升0.0486，Recall提升0.0803。"
        "该结果表明，单纯结构改进效果有限，而长尾均衡训练、高分辨率输入和弱增强二阶段微调的组合更适合本课堂行为检测数据集。"
    ),
    "在不重新训练模型的情况下，本文进一步测试了基线权重": (
        "在不重新训练模型的情况下，本文进一步测试了基线权重在imgsz=800下的推理效果。结果显示，该策略取得mAP@0.5为0.8993、mAP@0.5:0.95为0.7297、"
        "Precision为0.8859、Recall为0.8616。虽然mAP@0.5和Recall较原始640测试口径有所改善，但mAP@0.5:0.95和Precision仍低于最新strong_img800_tail_weakaug模型，"
        "说明仅提高推理分辨率不足以充分解决类别不均衡和细粒度行为识别问题。"
    ),
    "在训练策略优化实验中，baseline_finetune_img800_weakaug": (
        "在训练策略优化实验中，baseline_finetune_img800_weakaug从基线best.pt出发，以imgsz=800进行弱增强微调；strong_img800_tail_weakaug进一步引入长尾均衡训练集。"
        "验证集结果显示，baseline_finetune_img800_weakaug2的最佳mAP@0.5:0.95为0.75943，strong_img800_tail_weakaug为0.75936，二者非常接近。"
        "但从测试集结果看，strong模型明显超过baseline，说明长尾均衡处理对测试集泛化更有帮助。"
    ),
    "需要注意的是，该验证集收益没有在最新测试集结果中同步体现": (
        "需要注意的是，前期仅采用高分辨率弱增强微调时，验证集收益没有稳定转化为测试集收益；最新实验加入长尾均衡训练集后，测试集mAP@0.5:0.95提升到0.8240。"
        "这说明课堂行为检测的主要瓶颈不仅是输入分辨率，还包括类别长尾、少数类学习不足和强增强破坏行为语义等问题。"
    ),
    "综合实验结果，本文得到以下结论": (
        "综合实验结果，本文得到以下结论：第一，YOLOv8m基线模型具有较强稳定性，是后续实验的重要起点；第二，简单增加注意力模块或P2检测头并未提升性能，"
        "说明结构改进需要结合数据规模和预训练权重迁移充分设计；第三，strong_img800_tail_weakaug采用长尾均衡训练集、高分辨率输入、弱增强和二阶段微调，"
        "在测试集上取得mAP@0.5为0.9673、mAP@0.5:0.95为0.8240的最优结果；第四，最终系统可优先采用该模型作为高精度检测方案，若更重视实时性，可继续保留baseline作为轻量备选。"
    ),
    "课堂图片中存在大量多人目标": (
        "课堂图片中存在大量多人目标，同一张图中可能出现几十个学生行为框。对于这类密集目标，如果标注框过小或边界不准确，会直接影响定位指标mAP@0.5:0.95。"
        "最新实验表明，高分辨率输入与长尾均衡训练结合后能够显著提升测试集定位质量，说明更清晰的输入和更均衡的类别学习对密集课堂行为检测均有积极作用。"
        "后续数据预处理仍可继续关注图片质量统一、减少过度压缩以及小目标类别标注复核。"
    ),
    "输入尺寸是影响小目标检测的重要参数": (
        "输入尺寸是影响小目标检测的重要参数。imgsz=640是YOLO常用默认设置，训练速度较快；imgsz=800能够保留更多局部细节，有助于手机、手部和低头区域检测，但显存开销和推理时间也会增加。"
        "本文最新实验显示，单独提高baseline推理分辨率只能带来有限收益，而在imgsz=800基础上结合长尾均衡训练与弱增强二阶段微调后，测试集mAP@0.5:0.95提升到0.8240，说明输入尺寸需要与训练数据分布优化共同发挥作用。"
    ),
    "小目标问题主要体现在使用手机和举手行为中": (
        "小目标问题主要体现在使用手机和举手行为中。手机在课堂图像中面积较小，且可能被手部遮挡或与桌面颜色接近；举手行为虽然动作明显，但手部区域较细，远距离拍摄时可能只占很少像素。"
        "P2检测头理论上有助于小目标检测，但本文实验未提升，说明仅增加检测尺度不足以解决问题。最新strong模型通过高分辨率输入保留更多局部细节，同时通过长尾均衡训练改善少数类学习，取得了更稳定的测试集提升。"
    ),
    "输入分辨率提高会增加推理时间。最新测试结果显示": (
        "输入分辨率提高会增加推理时间。最新测试结果显示，strong_img800_tail_weakaug模型在imgsz=800测试口径下取得mAP@0.5为0.9673、mAP@0.5:0.95为0.8240、"
        "Precision为0.9345、Recall为0.9419，明显超过baseline。考虑到该模型仍采用YOLOv8m结构，额外开销主要来自800输入尺寸，系统可将其作为高精度默认方案；"
        "在显存或实时性要求更严格的场景中，可切换到640输入的baseline模型。"
    ),
    "根据本文实验结果，后续模型优化应优先从数据和训练策略入手": (
        "根据本文实验结果，后续模型优化应继续优先从数据和训练策略入手。首先，可在当前长尾均衡训练的基础上补充少数类真实样本，尤其是bowing the head和leaning over the table类别。"
        "补充样本时应覆盖不同座位、不同拍摄角度、不同光照和不同遮挡情况，使模型学习到更稳定的类别特征。"
    ),
    "本章对模型实验结果和系统测试情况进行了综合分析": (
        "本章对模型实验结果和系统测试情况进行了综合分析。首先说明了实验环境和评价指标，然后对YOLOv8m基线模型、轻量注意力模型、P2检测头模型、高分辨率弱增强微调模型、"
        "高分辨率推理结果以及strong_img800_tail_weakaug模型进行了对比。实验表明，长尾均衡训练集、高分辨率输入、弱增强和二阶段微调组合能够显著提升测试集综合性能，"
        "strong_img800_tail_weakaug可作为本文最终推荐模型。"
    ),
    "在算法实验方面，本文首先训练YOLOv8m基线模型": (
        "在算法实验方面，本文首先训练YOLOv8m基线模型，并取得较稳定的测试集综合结果。随后尝试轻量ECA注意力、P2小目标检测头和高分辨率弱增强微调，发现单纯结构改进或单独微调并不能稳定超过基线。"
        "在此基础上，本文进一步提出strong_img800_tail_weakaug训练策略，将长尾均衡训练集、高分辨率输入、弱增强和二阶段微调结合，最终在测试集上取得mAP@0.5为0.9673、mAP@0.5:0.95为0.8240的最优结果。"
    ),
    "在训练脚本中，train_baseline_100epochs.py是最重要的基线训练文件": (
        "在训练脚本中，train_baseline_100epochs.py是重要的基线训练文件。该脚本从yolov8m.pt加载预训练权重，设置数据集路径、训练轮数、batch size、输入尺寸、优化器和数据增强参数，"
        "并将训练结果保存到runs/detect/baseline_mAP_100epochs目录下。在最新实验中，train_strong_img800_tail_weakaug.py进一步从该基线best.pt出发，"
        "结合classroom_tail_oversampled数据集、imgsz=800和弱增强策略进行二阶段微调，成为最终推荐的高精度模型训练脚本。"
    ),
    "在论文实验分析中，不能只依赖终端输出": (
        "在论文实验分析中，不能只依赖终端输出，还应结合results.csv查看每轮指标变化。例如baseline_mAP_100epochs在第90轮取得最佳mAP@0.5:0.95，"
        "baseline_finetune_img800_weakaug2在第29轮附近取得较优验证指标，strong_img800_tail_weakaug在第39轮取得最佳mAP@0.5:0.95。"
        "通过这些信息可以更准确地描述模型训练过程。"
    ),
    "结果管理还涉及命名规范": (
        "结果管理还涉及命名规范。本文为不同实验设置独立run name，例如baseline_mAP_100epochs、optimized_attention_light_m_pretrained、yolov8m_p2_100epochs、"
        "baseline_finetune_img800_weakaug和strong_img800_tail_weakaug。清晰的命名能够减少实验混淆，方便后续复现实验和撰写论文表格。"
    ),
    "本章对全文研究工作进行了总结": (
        "本章对全文研究工作进行了总结，并从不足、部署、创新、代码组织、应用价值和维护扩展等角度进行了展望。总体来看，本文完成了基于YOLOv8的课堂行为检测模型训练与桌面端系统实现，"
        "形成了从数据输入、模型推理、专注度计算到结果保存的完整流程。最新实验结果表明，strong_img800_tail_weakaug模型在当前数据集上取得最优综合表现，适合作为系统高精度默认模型。"
    ),
    "图6-1 主要模型测试指标对比图": "图6-1 最新主要模型测试指标对比图",
    "图6-2 test.py测试集样本预测结果图": "图6-2 strong_img800_tail_weakaug测试集样本预测结果图",
    "图6-3 test.py测试集PR曲线": "图6-3 strong_img800_tail_weakaug测试集PR曲线",
    "图6-4 test.py测试集归一化混淆矩阵": "图6-4 strong_img800_tail_weakaug测试集归一化混淆矩阵",
    "图6-5 weakaug2模型测试集样本预测结果图": "图6-5 strong_img800_tail_weakaug训练结果曲线图",
}


def q(name: str) -> str:
    prefix, local = name.split(":")
    return f"{{{NS[prefix]}}}{local}"


def paragraph_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(".//w:t", NS))


def set_paragraph_text(p: ET.Element, text: str) -> None:
    first_run = p.find("w:r", NS)
    rpr = None
    if first_run is not None:
        old_rpr = first_run.find("w:rPr", NS)
        if old_rpr is not None:
            rpr = copy.deepcopy(old_rpr)

    for child in list(p):
        if child.tag == q("w:r"):
            p.remove(child)

    run = ET.SubElement(p, q("w:r"))
    if rpr is not None:
        run.append(rpr)
    t = ET.SubElement(run, q("w:t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text


def cell_text(tc: ET.Element) -> str:
    return "".join(t.text or "" for t in tc.findall(".//w:t", NS))


def set_cell_text(tc: ET.Element, text: str) -> None:
    p = tc.find("w:p", NS)
    if p is None:
        p = ET.SubElement(tc, q("w:p"))
    set_paragraph_text(p, text)


def table_text(tbl: ET.Element) -> str:
    return " | ".join(cell_text(tc) for tc in tbl.findall(".//w:tc", NS))


def set_table_rows(tbl: ET.Element, header: list[str], rows: list[list[str]]) -> None:
    trs = tbl.findall("w:tr", NS)
    needed = 1 + len(rows)
    while len(trs) < needed:
        tbl.append(copy.deepcopy(trs[-1]))
        trs = tbl.findall("w:tr", NS)

    for extra in trs[needed:]:
        tbl.remove(extra)
    trs = tbl.findall("w:tr", NS)

    all_rows = [header] + rows
    for tr, row_data in zip(trs, all_rows):
        cells = tr.findall("w:tc", NS)
        while len(cells) < len(row_data):
            tr.append(copy.deepcopy(cells[-1]))
            cells = tr.findall("w:tc", NS)
        for tc, value in zip(cells, row_data):
            set_cell_text(tc, value)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        ROOT / "Font" / "platech.ttf",
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def draw_metrics_chart(path: Path) -> None:
    models = [
        ("Baseline\n640", [0.9032, 0.8512, 0.8961, 0.7382]),
        ("Attention", [0.8090, 0.8114, 0.8353, 0.6534]),
        ("P2", [0.8130, 0.8005, 0.8377, 0.6547]),
        ("WeakAug", [0.8975, 0.8527, 0.8898, 0.7278]),
        ("Baseline\n800", [0.8859, 0.8616, 0.8993, 0.7297]),
        ("Strong\n800", [0.9345, 0.9419, 0.9673, 0.8240]),
    ]
    metric_names = ["Precision", "Recall", "mAP@0.5", "mAP@0.5:0.95"]
    colors = ["#4472C4", "#70AD47", "#ED7D31", "#A5A5A5"]

    w, h = 1400, 850
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    title_font = font(34, True)
    label_font = font(21)
    small_font = font(17)

    d.text((w // 2, 35), "主要模型测试指标对比", font=title_font, fill="#1f2937", anchor="mm")
    left, top, right, bottom = 95, 120, 1320, 690
    d.line((left, bottom, right, bottom), fill="#333333", width=2)
    d.line((left, top, left, bottom), fill="#333333", width=2)

    for i in range(6):
        y = bottom - i * (bottom - top) / 5
        val = i / 5
        d.line((left, y, right, y), fill="#e5e7eb", width=1)
        d.text((left - 12, y), f"{val:.1f}", font=small_font, fill="#555555", anchor="rm")

    group_w = (right - left) / len(models)
    bar_w = group_w * 0.16
    for mi, (name, values) in enumerate(models):
        base_x = left + mi * group_w + group_w * 0.16
        for j, value in enumerate(values):
            x1 = base_x + j * bar_w
            x2 = x1 + bar_w * 0.82
            y1 = bottom - value * (bottom - top)
            d.rectangle((x1, y1, x2, bottom), fill=colors[j])
            d.text(((x1 + x2) / 2, y1 - 8), f"{value:.3f}", font=small_font, fill="#111827", anchor="mb")
        d.multiline_text(
            (left + mi * group_w + group_w / 2, bottom + 26),
            name,
            font=label_font,
            fill="#111827",
            anchor="ma",
            align="center",
            spacing=4,
        )

    legend_x, legend_y = 330, 760
    for i, metric in enumerate(metric_names):
        x = legend_x + i * 230
        d.rectangle((x, legend_y, x + 28, legend_y + 18), fill=colors[i])
        d.text((x + 38, legend_y + 9), metric, font=label_font, fill="#111827", anchor="lm")

    path.parent.mkdir(exist_ok=True)
    img.save(path)


def next_image_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        pos = 2
        while pos < len(data):
            while pos < len(data) and data[pos] == 0xFF:
                pos += 1
            marker = data[pos]
            pos += 1
            length = struct.unpack(">H", data[pos : pos + 2])[0]
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height, width = struct.unpack(">HH", data[pos + 3 : pos + 7])
                return width, height
            pos += length
    raise ValueError(f"Unsupported image format: {path}")


def update_inline_size(p: ET.Element, image_path: Path, max_width_in: float = 5.8) -> None:
    width, height = next_image_size(image_path)
    cx = int(max_width_in * 914400)
    cy = int(cx * height / width)
    for extent in p.findall(".//wp:extent", NS):
        extent.set("cx", str(cx))
        extent.set("cy", str(cy))
    for ext in p.findall(".//a:ext", NS):
        ext.set("cx", str(cx))
        ext.set("cy", str(cy))


def rid_before_caption(root: ET.Element, caption: str) -> tuple[str, ET.Element]:
    paragraphs = root.findall(".//w:body/w:p", NS)
    for idx, p in enumerate(paragraphs):
        if caption in paragraph_text(p):
            for prev in reversed(paragraphs[:idx]):
                blip = prev.find(".//a:blip", NS)
                if blip is not None:
                    rid = blip.get(q("r:embed"))
                    if rid:
                        return rid, prev
    raise RuntimeError(f"Could not find image before caption: {caption}")


def update_rels_target(rels_root: ET.Element, rid: str, target: str) -> None:
    for rel in rels_root.findall("rel:Relationship", NS):
        if rel.get("Id") == rid:
            rel.set("Target", target)
            return
    raise RuntimeError(f"Relationship not found: {rid}")


def ensure_content_type(content_types: str, extension: str, content_type: str) -> str:
    if f'Extension="{extension}"' in content_types:
        return content_types
    return content_types.replace(
        "</Types>",
        f'<Default Extension="{extension}" ContentType="{content_type}"/></Types>',
    )


def prepare_figures() -> dict[str, Path]:
    FIG_DIR.mkdir(exist_ok=True)
    chart = FIG_DIR / "图6-1_主要模型测试指标对比图.png"
    draw_metrics_chart(chart)

    copies = {
        "图6-1 最新主要模型测试指标对比图": chart,
        "图6-2 strong_img800_tail_weakaug测试集样本预测结果图": FIG_DIR / "图6-2_strong模型测试集样本预测结果图.jpg",
        "图6-3 strong_img800_tail_weakaug测试集PR曲线": FIG_DIR / "图6-3_strong模型测试集PR曲线.png",
        "图6-4 strong_img800_tail_weakaug测试集归一化混淆矩阵": FIG_DIR / "图6-4_strong模型测试集归一化混淆矩阵.png",
        "图6-5 strong_img800_tail_weakaug训练结果曲线图": FIG_DIR / "图6-5_strong模型训练结果曲线图.png",
    }
    src_map = {
        copies["图6-2 strong_img800_tail_weakaug测试集样本预测结果图"]: STRONG_TEST_DIR / "val_batch0_pred.jpg",
        copies["图6-3 strong_img800_tail_weakaug测试集PR曲线"]: STRONG_TEST_DIR / "PR_curve.png",
        copies["图6-4 strong_img800_tail_weakaug测试集归一化混淆矩阵"]: STRONG_TEST_DIR / "confusion_matrix_normalized.png",
        copies["图6-5 strong_img800_tail_weakaug训练结果曲线图"]: STRONG_TRAIN_DIR / "results.png",
    }
    for dst, src in src_map.items():
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copyfile(src, dst)
    return copies


def main() -> None:
    if not SOURCE_DOCX.exists():
        raise FileNotFoundError(SOURCE_DOCX)

    figures = prepare_figures()

    with zipfile.ZipFile(SOURCE_DOCX, "r") as zin:
        doc_tree = ET.ElementTree(ET.fromstring(zin.read("word/document.xml")))
        doc_root = doc_tree.getroot()
        rels_tree = ET.ElementTree(ET.fromstring(zin.read("word/_rels/document.xml.rels")))
        rels_root = rels_tree.getroot()
        content_types = zin.read("[Content_Types].xml").decode("utf-8")

        for p in doc_root.findall(".//w:p", NS):
            text = paragraph_text(p).strip()
            for prefix, new_text in TEXT_REPLACEMENTS_BY_PREFIX.items():
                if text.startswith(prefix):
                    set_paragraph_text(p, new_text)
                    break

        tables = doc_root.findall(".//w:tbl", NS)
        for tbl in tables:
            txt = table_text(tbl)
            if "baseline_mAP_100epochs" in txt and "Precision" in txt:
                set_table_rows(
                    tbl,
                    ["模型", "mAP@0.5", "mAP@0.5:0.95", "Precision", "Recall"],
                    TEST_ROWS,
                )
            elif "训练轮数" in txt and "最佳mAP@0.5:0.95" in txt:
                set_table_rows(
                    tbl,
                    ["实验名称", "训练轮数", "最佳mAP@0.5", "最佳mAP@0.5:0.95", "说明"],
                    VAL_ROWS,
                )

        media_entries: list[tuple[Path, str]] = []
        for idx, (caption, image_path) in enumerate(figures.items(), start=1):
            rid, image_para = rid_before_caption(doc_root, caption)
            suffix = image_path.suffix.lower()
            media_name = f"updated_strong_fig_{idx}{suffix}"
            update_rels_target(rels_root, rid, f"media/{media_name}")
            update_inline_size(image_para, image_path)
            media_entries.append((image_path, f"word/media/{media_name}"))
            if suffix == ".png":
                content_types = ensure_content_type(content_types, "png", "image/png")
            elif suffix in {".jpg", ".jpeg"}:
                content_types = ensure_content_type(content_types, suffix[1:], "image/jpeg")

        doc_xml = ET.tostring(doc_root, encoding="utf-8", xml_declaration=True)
        rels_xml = ET.tostring(rels_root, encoding="utf-8", xml_declaration=True)

        tmp_docx = OUT_DOCX.with_suffix(".tmp.docx")
        with zipfile.ZipFile(tmp_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc_xml)
                elif item.filename == "word/_rels/document.xml.rels":
                    zout.writestr(item, rels_xml)
                elif item.filename == "[Content_Types].xml":
                    zout.writestr(item, content_types.encode("utf-8"))
                else:
                    zout.writestr(item, zin.read(item.filename))
            for src, target in media_entries:
                zout.write(src, target)

    tmp_docx.replace(OUT_DOCX)
    print(OUT_DOCX)
    for path in figures.values():
        print(path)


if __name__ == "__main__":
    main()
