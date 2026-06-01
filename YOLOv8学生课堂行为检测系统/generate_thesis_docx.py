# -*- coding: utf-8 -*-
"""Generate thesis draft DOCX/Markdown without external dependencies."""

from __future__ import annotations

import html
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "12.王岩松山东科技大学本科毕业设计（论文）规范格式.docx"
OUT_DOCX = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_初稿.docx"
OUT_MD = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_初稿.md"


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def run(text: str, bold: bool = False, size: int = 21) -> str:
    b = "<w:b/>" if bold else ""
    return (
        "<w:r><w:rPr>"
        '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>'
        f"{b}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"
    )


def para(text: str = "", align: str = "both", bold: bool = False, size: int = 21, first_line: bool = True) -> str:
    ind = '<w:ind w:firstLine="420"/>' if first_line else ""
    return (
        "<w:p><w:pPr>"
        f"<w:jc w:val=\"{align}\"/>"
        '<w:spacing w:line="360" w:lineRule="auto"/>'
        f"{ind}</w:pPr>{run(text, bold=bold, size=size)}</w:p>"
    )


def heading(text: str, level: int = 1) -> str:
    if level == 1:
        return para(text, align="center", bold=True, size=28, first_line=False)
    if level == 2:
        return para(text, align="left", bold=True, size=24, first_line=False)
    return para(text, align="left", bold=True, size=21, first_line=False)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table(rows: list[list[str]]) -> str:
    xml = ["<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/>"
           "<w:tblBorders><w:top w:val=\"single\" w:sz=\"4\"/><w:left w:val=\"single\" w:sz=\"4\"/>"
           "<w:bottom w:val=\"single\" w:sz=\"4\"/><w:right w:val=\"single\" w:sz=\"4\"/>"
           "<w:insideH w:val=\"single\" w:sz=\"4\"/><w:insideV w:val=\"single\" w:sz=\"4\"/>"
           "</w:tblBorders></w:tblPr>"]
    for i, row in enumerate(rows):
        xml.append("<w:tr>")
        for cell in row:
            xml.append("<w:tc><w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>")
            xml.append(para(cell, align="center", bold=(i == 0), size=20, first_line=False))
            xml.append("</w:tc>")
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def bullet(text: str) -> str:
    return para("（1）" + text, first_line=True)


def body_xml(parts: list[str]) -> str:
    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="851" w:footer="992" w:gutter="0"/>'
        '<w:cols w:space="425"/>'
        '<w:docGrid w:type="lines" w:linePitch="312"/>'
        "</w:sectPr>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:v="urn:schemas-microsoft-com:vml" '
        'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:w10="urn:schemas-microsoft-com:office:word" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
        'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
        'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
        'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
        'mc:Ignorable="w14 wp14"><w:body>'
        + "".join(parts)
        + sect
        + "</w:body></w:document>"
    )


TITLE = "基于YOLOv8的学生课堂行为检测系统设计与实现"
EN_TITLE = "Design and Implementation of a Student Classroom Behavior Detection System Based on YOLOv8"


content: list[str] = []

# Cover
content += [
    para("本科毕业设计（论文）", align="center", bold=True, size=36, first_line=False),
    para("", first_line=False),
    para(TITLE, align="center", bold=True, size=32, first_line=False),
    para(EN_TITLE, align="center", size=24, first_line=False),
    para("", first_line=False),
    para("学    院：  计算机科学与工程学院", align="left", size=28, first_line=False),
    para("专业班级：  计算机科学与技术（请填写班级）", align="left", size=28, first_line=False),
    para("姓    名：  （请填写姓名）", align="left", size=28, first_line=False),
    para("学    号：  （请填写学号）", align="left", size=28, first_line=False),
    para("指导教师：  （请填写指导教师）", align="left", size=28, first_line=False),
    para("完成日期：  2026年5月", align="left", size=28, first_line=False),
    para("", first_line=False),
    para("教务处制", align="center", size=24, first_line=False),
    page_break(),
]

# Declarations
content += [
    heading("学位论文原创性声明", 1),
    para("本人呈交给山东科技大学的学位论文，除所列参考文献和世所公认的文献外，全部是本人攻读学位期间在导师指导下的研究成果。除文中已经标明引用的内容外，本论文不包含任何其他个人或集体已经发表或撰写过的研究成果。对本文的研究做出贡献的个人和集体，均已在文中以明确方式标明。本人完全意识到本声明的法律结果由本人承担。"),
    para("若有不实之处，本人愿意承担相关法律责任。"),
    para("本人签名：                         日 期：     年   月   日", first_line=False),
    para("", first_line=False),
    heading("学位论文使用授权声明", 1),
    para("本人完全了解山东科技大学有关保留、使用学位论文的规定，同意本人所撰写的学位论文的使用授权按照学校的管理规定处理。"),
    para("作为申请学位的条件之一，学校有权保留学位论文并向国家有关部门或其指定机构送交论文的电子版和纸质版；有权将学位论文的全部或部分内容编入有关数据库发表，并可以以电子、网络及其他数字媒体形式公开出版；允许学校档案馆和图书馆保留学位论文的纸质版和电子版，可以使用影印、缩印或扫描等复制手段保存和汇编学位论文；为教学和科研目的，学校档案馆和图书馆可以将公开的学位论文作为资料在档案馆、图书馆等场所或在校园网上供校内师生阅读、浏览。"),
    para("（保密的学位论文在解密后适用本授权）"),
    para("作者签名：                          导师签名：", first_line=False),
    para("日   期：    年   月   日           日   期：    年   月   日", first_line=False),
    page_break(),
]

# Abstracts
content += [
    heading("摘    要", 1),
    para("随着智慧教育和计算机视觉技术的发展，课堂教学状态的自动感知逐渐成为教育信息化建设中的重要内容。传统课堂行为观察主要依赖教师人工记录或课后抽样分析，存在主观性强、实时性差、工作量大等问题，难以满足课堂教学质量持续化、数据化分析的需求。针对上述问题，本文设计并实现了一套基于YOLOv8的学生课堂行为检测系统，通过深度学习目标检测模型对课堂图像、视频和摄像头画面中的学生行为进行识别，并在此基础上完成课堂专注度的辅助分析与可视化展示。"),
    para("系统以YOLOv8m为核心检测模型，围绕举手、阅读、书写、使用手机、低头、趴桌六类课堂行为建立数据集配置和训练流程。本文完成了数据集划分、模型训练、注意力机制实验、P2小目标检测头实验以及高分辨率弱增强微调实验。实验结果表明，YOLOv8m基线模型在测试集上达到mAP@0.5为0.8961、mAP@0.5:0.95为0.7382、Precision为0.9032、Recall为0.8512，能够较好满足课堂行为检测任务需求。进一步实验发现，简单叠加ECA注意力和P2检测头并未提升整体精度，而基于强基线模型进行高分辨率弱增强微调能够在验证集上提升mAP@0.5:0.95，说明训练策略优化比盲目增加网络结构更加适合本项目数据特征。"),
    para("在系统实现方面，本文基于Python、PyTorch、OpenCV和PyQt5完成了桌面端检测系统开发。系统支持图片检测、视频检测、实时摄像头检测、批量图片处理、检测结果保存、行为类别展示、置信度显示和班级专注度计算等功能。针对视频流场景，系统设计了融合类别权重、检测置信度、时序稳定性和班级趋势的专注度计算方法，使检测结果能够进一步转化为课堂状态分析指标。测试结果表明，该系统具有较好的检测准确性、交互性和实用性，可为智慧课堂、教学质量分析和学生行为研究提供参考。"),
    para("关键词：YOLOv8；课堂行为检测；目标检测；深度学习；PyQt5；专注度分析", first_line=False),
    page_break(),
    heading("ABSTRACT", 1),
    para("With the development of smart education and computer vision, automatic perception of classroom teaching status has become an important topic in educational informatization. Traditional classroom behavior observation mainly relies on manual recording or post-class sampling, which is subjective, inefficient and difficult to quantify in real time. To address these problems, this thesis designs and implements a student classroom behavior detection system based on YOLOv8. The system detects student behaviors in classroom images, videos and camera streams, and further provides auxiliary analysis and visual display of classroom concentration."),
    para("YOLOv8m is adopted as the core detection model. Six classroom behavior categories are considered, including hand-raising, reading, writing, using phone, bowing the head and leaning over the table. This thesis completes dataset configuration, model training, attention mechanism experiments, P2 detection-head experiments, and high-resolution weak-augmentation fine-tuning. Experimental results show that the YOLOv8m baseline achieves 0.8961 mAP@0.5, 0.7382 mAP@0.5:0.95, 0.9032 precision and 0.8512 recall on the test set. Additional experiments indicate that simply adding ECA attention or a P2 detection head does not improve the overall accuracy, while fine-tuning the strong baseline with higher image resolution and weaker augmentation improves mAP@0.5:0.95 on the validation set. This demonstrates that training strategy optimization is more suitable for this dataset than blindly increasing model complexity."),
    para("The system is implemented with Python, PyTorch, OpenCV and PyQt5. It supports image detection, video detection, real-time camera detection, batch image processing, result saving, behavior category display, confidence display and class concentration calculation. For video streams, a concentration evaluation method integrating behavior category weights, detection confidence, temporal stability and class-level trend is designed. The system test shows that the proposed system has good accuracy, interactivity and practical value, and can provide useful support for smart classrooms and teaching quality analysis."),
    para("KEY WORDS: YOLOv8; Classroom Behavior Detection; Object Detection; Deep Learning; PyQt5; Concentration Analysis", first_line=False),
    page_break(),
]

# TOC
toc_lines = [
    "摘    要",
    "ABSTRACT",
    "第1章 绪论",
    "1.1 研究背景与意义",
    "1.2 国内外研究现状",
    "1.3 本文主要研究内容",
    "第2章 相关技术基础",
    "2.1 深度学习与目标检测",
    "2.2 YOLOv8检测算法",
    "2.3 系统开发相关技术",
    "第3章 系统需求分析与总体设计",
    "第4章 数据集构建与模型训练",
    "第5章 系统功能实现",
    "第6章 实验结果与分析",
    "第7章 总结与展望",
    "参考文献",
    "致谢",
]
content += [heading("目    录", 1)]
content += [para(line, first_line=False) for line in toc_lines]
content.append(page_break())

# Chapter 1
content += [
    heading("第1章 绪论", 1),
    heading("1.1 研究背景与意义", 2),
    para("课堂是学校教学活动的核心场景，学生在课堂中的行为状态能够直观反映学习参与度和课堂教学效果。传统教学管理主要依靠教师经验判断学生是否专注，例如观察学生是否阅读、书写、举手、低头或使用手机等。这种方式虽然直观，但容易受到教师主观感受、课堂规模和观察角度的影响。当班级人数较多或课堂时间较长时，教师难以持续、全面地记录每名学生的行为状态。"),
    para("近年来，深度学习在目标检测、图像分类、姿态估计等计算机视觉任务中取得显著进展。以YOLO系列为代表的一阶段目标检测算法兼具较高检测精度和较快推理速度，适合部署在实时性要求较高的课堂场景中。将目标检测技术应用于课堂行为分析，可以自动识别学生的典型课堂行为，为教师提供客观、连续、可追溯的数据支撑，有助于改进课堂管理方式和教学评价手段。"),
    para("本文以学生课堂行为检测为研究对象，结合YOLOv8目标检测模型和桌面端可视化技术，设计并实现一套学生课堂行为检测系统。该系统不仅能够检测学生行为类别和位置，还进一步计算班级专注度指标，使检测结果从单纯的目标框输出扩展到课堂状态分析，具有一定的工程应用价值。"),
    heading("1.2 国内外研究现状", 2),
    para("目标检测技术经历了从传统人工特征到深度学习端到端检测的发展过程。早期方法依赖Haar、HOG、SIFT等人工设计特征，泛化能力有限。深度学习方法出现后，R-CNN、Fast R-CNN、Faster R-CNN等两阶段检测算法通过候选区域生成与分类回归取得了较高精度，但推理速度相对较慢。一阶段检测算法以YOLO、SSD等为代表，直接在特征图上预测目标类别和边界框，显著提升了检测速度。"),
    para("在教育场景中，课堂行为识别研究主要包括学生姿态分析、表情识别、专注度评估、异常行为检测等方向。部分研究使用传统机器学习方法提取人体姿态或面部特征，部分研究使用卷积神经网络完成动作分类。由于真实课堂环境存在遮挡、目标尺度变化、光照差异和多人密集等问题，单纯分类模型难以处理多目标定位与行为识别的联合需求。因此，基于目标检测的课堂行为识别方案具有更好的适应性。"),
    para("YOLOv8作为较新的YOLO系列实现，在模型结构、训练策略和工程易用性方面均较成熟，支持检测、分割、分类、姿态估计等多种任务。本文选择YOLOv8作为基础模型，并围绕课堂行为数据集进行训练、对比和系统集成。"),
    heading("1.3 本文主要研究内容", 2),
    bullet("构建学生课堂行为检测任务的数据配置，确定举手、阅读、书写、使用手机、低头、趴桌六类行为类别，并统计数据集划分和类别分布。"),
    bullet("基于YOLOv8m完成课堂行为检测模型训练，设计统一的训练参数和评价指标，获得稳定的基线模型。"),
    bullet("围绕注意力机制、P2小目标检测头和高分辨率弱增强微调开展改进实验，分析不同策略对检测性能的影响。"),
    bullet("基于PyQt5开发可视化检测系统，实现图片、视频、摄像头和批量检测等功能，并设计课堂专注度计算方法。"),
    bullet("通过实验结果和系统测试验证模型与系统的有效性，总结系统不足并提出后续优化方向。"),
]

# Chapter 2
content += [
    heading("第2章 相关技术基础", 1),
    heading("2.1 深度学习与目标检测", 2),
    para("深度学习通过多层神经网络自动学习数据中的高层语义特征，避免了传统视觉方法对人工特征设计的依赖。在图像任务中，卷积神经网络能够利用卷积核提取局部空间特征，并通过层级堆叠逐渐形成从边缘纹理到目标语义的表达能力。目标检测任务不仅需要判断图像中是否存在某一类别目标，还需要给出目标的位置坐标，因此通常同时包含分类和边界框回归两个子任务。"),
    para("常见目标检测评价指标包括Precision、Recall、mAP@0.5和mAP@0.5:0.95。Precision反映预测结果中正确检测所占比例，Recall反映真实目标被检出的比例；mAP@0.5表示IoU阈值为0.5时各类别平均精度的均值，mAP@0.5:0.95则在多个IoU阈值下计算平均结果，更能反映模型定位质量。"),
    heading("2.2 YOLOv8检测算法", 2),
    para("YOLO系列算法将目标检测视为单阶段回归问题，直接从输入图像预测目标类别、边界框和置信度。YOLOv8延续了单阶段检测思想，整体结构可分为Backbone、Neck和Head三部分。Backbone负责提取多尺度图像特征，Neck完成不同尺度特征融合，Head输出最终检测结果。YOLOv8使用C2f模块增强梯度流动和特征表达能力，并采用解耦检测头分别处理分类和回归任务。"),
    para("本文选用YOLOv8m作为主要模型。与YOLOv8n、YOLOv8s相比，YOLOv8m具有更强的特征表达能力；与YOLOv8l、YOLOv8x相比，其参数量和显存开销更适中，适合本科项目中的训练、验证和桌面系统集成。"),
    heading("2.3 系统开发相关技术", 2),
    para("系统使用Python作为主要开发语言。模型训练和推理基于PyTorch与Ultralytics YOLO框架完成，图像读写和视频帧处理使用OpenCV实现，中文文字绘制使用PIL辅助完成。桌面端交互界面基于PyQt5开发，能够提供按钮、表格、图像显示、文件选择、实时刷新等功能。"),
    para("在工程实现上，系统采用模块化设计。Config.py保存模型路径和类别名称等配置；detect_tools.py封装图像格式转换、中文绘制、结果保存等工具函数；main.py实现界面逻辑、模型加载、图片检测、视频检测、摄像头检测和专注度计算；train与test脚本负责模型训练和性能评估。"),
]

# Chapter 3
content += [
    heading("第3章 系统需求分析与总体设计", 1),
    heading("3.1 功能需求分析", 2),
    para("根据课堂行为检测任务特点，系统需要满足以下功能需求：第一，支持单张图片输入，完成行为检测并显示检测框、类别、置信度和坐标信息；第二，支持视频文件输入，按帧进行检测并实时显示检测结果；第三，支持摄像头输入，实现近实时课堂行为监测；第四，支持批量图片处理，将检测后的结果保存到指定目录；第五，能够根据检测结果计算班级专注度，为课堂状态分析提供直观指标。"),
    para("除功能需求外，系统还需要具备一定的可用性和稳定性。模型加载后应能在普通GPU环境下完成推理；界面操作应尽量简单，用户能够通过按钮完成图片选择、视频选择、摄像头打开、结果保存等操作；检测异常或输入为空时系统应给出提示，避免程序崩溃。"),
    heading("3.2 非功能需求分析", 2),
    para("在性能方面，系统应在保证检测精度的基础上尽量提高推理速度，使其能够处理课堂视频流。在准确性方面，系统需要对多学生、多类别和局部小目标具有较好的识别能力。在扩展性方面，系统应保留模型路径、类别名称和训练配置的可修改性，便于后续替换更优模型或扩展新的行为类别。"),
    heading("3.3 系统总体架构", 2),
    para("系统总体上分为数据层、模型层、业务逻辑层和界面层。数据层包括课堂行为图片、标签文件、数据集配置文件和训练结果文件；模型层以YOLOv8m检测模型为核心，负责完成目标检测推理；业务逻辑层负责图像预处理、结果解析、专注度计算、视频帧处理和结果保存；界面层基于PyQt5实现用户交互和结果展示。"),
    para("系统运行流程如下：用户选择图片、视频或摄像头输入；程序调用YOLO模型进行推理；模型输出边界框、类别编号和置信度；系统将类别编号转换为中英文行为名称，并在图像上绘制检测结果；随后根据行为类别和置信度计算专注度，最终在界面中显示人数、行为类别、坐标、置信度和班级专注度等信息。"),
]

# Chapter 4
content += [
    heading("第4章 数据集构建与模型训练", 1),
    heading("4.1 数据集说明", 2),
    para("本文使用的课堂行为数据集位于datasets/学生课堂行为检测数据集目录下，采用YOLO格式标注。数据集包含images和labels两个主要目录，并划分为train、val和test三个子集。经统计，训练集标签文件4202个，验证集标签文件1207个，测试集标签文件209个。检测类别共六类，分别为hand-raising、reading、writing、using phone、bowing the head和leaning over the table。"),
    para("训练集类别标注数量存在一定不均衡，其中reading类别数量最多，为13553个；bowing the head和leaning over the table分别为1017个和1099个，属于相对少样本类别。类别分布不均衡会影响模型对少数类的学习效果，因此在训练策略优化中需要适当关注分类损失权重、数据增强强度和输入分辨率。"),
    para("表4-1 训练集类别分布", align="center", first_line=False),
    table([
        ["类别编号", "类别名称", "训练集标注数量"],
        ["0", "hand-raising", "8083"],
        ["1", "reading", "13553"],
        ["2", "writing", "5183"],
        ["3", "using phone", "7472"],
        ["4", "bowing the head", "1017"],
        ["5", "leaning over the table", "1099"],
    ]),
    heading("4.2 基线模型训练", 2),
    para("基线模型采用YOLOv8m预训练权重yolov8m.pt进行迁移学习。训练轮数设置为100，输入尺寸为640×640，batch size为8，优化器为AdamW，初始学习率为0.0005，权重衰减为0.0005，warmup轮数为5。数据增强包括HSV颜色扰动、平移、尺度缩放、轻微旋转、水平翻转、mosaic、mixup和copy-paste等。"),
    para("基线模型在测试集上取得了较好的综合性能，mAP@0.5达到0.8961，Precision达到0.9032，Recall达到0.8512。该结果说明YOLOv8m能够较好适应课堂行为检测场景，并可作为后续改进实验的比较对象。"),
    heading("4.3 模型改进实验设计", 2),
    para("为了进一步提升检测性能，本文尝试了三类改进方向。第一类是在YOLOv8m基础上加入轻量ECA通道注意力模块，期望增强网络对关键行为区域的特征选择能力；第二类是构建YOLOv8m-P2模型，在原有P3、P4、P5检测头之外增加P2小目标检测头，期望改善手部、手机等小尺度目标的识别；第三类是保持原模型结构不变，从强基线权重出发进行高分辨率弱增强微调，期望在不破坏预训练特征的情况下提升定位质量。"),
    para("实验结果表明，注意力模块和P2检测头均未超过基线模型。其原因可能在于新增结构带来了随机初始化参数和特征分布变化，而当前数据集规模和类别分布不足以支撑结构复杂度增加。相比之下，高分辨率弱增强微调在验证集mAP@0.5:0.95上优于基线，说明对于本任务而言，优化训练策略比简单增加网络结构更有效。"),
]

# Chapter 5
content += [
    heading("第5章 系统功能实现", 1),
    heading("5.1 模型加载与检测流程", 2),
    para("系统启动时调用YOLO接口加载训练得到的权重文件，并使用一张空白图像进行预热推理，以减少首次检测时的延迟。用户选择图片后，系统读取图片路径并调用模型进行推理，得到检测框坐标、类别编号和置信度。检测结果经解析后存入列表，用于界面显示和结果保存。"),
    para("对于视频和摄像头输入，系统使用OpenCV的VideoCapture逐帧读取画面，并通过QTimer控制帧处理节奏。每一帧均调用YOLO模型进行检测，检测完成后在界面中更新图像、表格和专注度显示。视频结束时，系统根据历史专注度记录计算整个视频的平均专注度并进行提示。"),
    heading("5.2 可视化界面实现", 2),
    para("系统界面基于PyQt5实现，主要包含图像显示区域、功能按钮、检测信息表格和统计信息区域。用户可通过图片按钮选择单张图片，通过视频按钮选择视频文件，通过摄像头按钮打开或关闭实时检测。检测结果表格显示序号、文件路径、类别、置信度和目标坐标等信息，便于用户查看每个检测目标的详细情况。"),
    para("系统还支持批量图片检测。用户选择文件夹后，程序遍历其中的图片文件，逐张执行检测并将结果图像保存到指定目录。该功能便于对大量课堂图片进行离线分析，提高数据处理效率。"),
    heading("5.3 专注度计算方法", 2),
    para("为了将行为检测结果转化为课堂状态指标，系统设计了基于行为类别的专注度计算方法。对于静态图片，阅读、书写、举手被视为高专注行为，赋予较高基础分；低头作为中性或轻度低专注行为，赋予中等分；使用手机和趴桌被视为低专注行为，赋予较低分。系统根据所有检测目标的行为得分计算班级平均专注度。"),
    para("对于视频流场景，系统进一步引入时序追踪思想。FocusTracker根据目标框中心点匹配前后帧目标，记录每个目标近期专注度变化。当某一目标连续多帧处于低专注状态时，系统给予一定惩罚；当班级整体专注度趋势上升或下降时，通过趋势缓冲系数进行修正。该方法避免了单帧检测误差对结果造成过大影响，使视频专注度显示更加平滑。"),
    heading("5.4 结果保存功能", 2),
    para("系统支持将检测结果图像保存到本地磁盘。保存时程序会在检测图像左上角添加班级专注度和人数信息，并保留检测框和类别标签。对于视频保存，系统通过独立线程处理，避免界面阻塞。结果保存功能使系统不仅能够实时展示检测结果，还能够为后续教学分析和实验报告提供可追溯材料。"),
]

# Chapter 6
content += [
    heading("第6章 实验结果与分析", 1),
    heading("6.1 实验环境与评价指标", 2),
    para("本文实验基于Python、PyTorch、Ultralytics YOLO、OpenCV和PyQt5环境完成。评价指标采用Precision、Recall、mAP@0.5和mAP@0.5:0.95。其中mAP@0.5用于衡量模型在较宽松IoU条件下的检测能力，mAP@0.5:0.95用于衡量模型在更严格定位要求下的综合性能。"),
    heading("6.2 测试集实验结果", 2),
    para("表6-1给出了主要模型在测试集上的对比结果。其中YOLOv8m基线模型取得最佳综合结果，轻量注意力模型和P2检测头模型均低于基线。这说明在当前数据集上，模型结构增加并不必然带来性能提升，新增层的随机初始化和特征分布扰动可能抵消其理论优势。"),
    para("表6-1 不同模型测试集结果对比", align="center", first_line=False),
    table([
        ["模型", "mAP@0.5", "mAP@0.5:0.95", "Precision", "Recall"],
        ["baseline_mAP_100epochs", "0.8961", "0.7382", "0.9032", "0.8512"],
        ["optimized_attention_light_m_pretrained", "0.8353", "0.6534", "0.8090", "0.8114"],
        ["yolov8m_p2_100epochs", "0.8377", "0.6547", "0.8130", "0.8005"],
    ]),
    heading("6.3 训练策略优化结果", 2),
    para("在后续训练策略优化中，本文基于baseline_mAP_100epochs的最优权重进行imgsz=800的弱增强微调。该实验使用较低学习率、关闭mosaic、mixup和copy-paste，并适当提高分类损失权重。验证集结果显示，微调模型的mAP@0.5:0.95最高达到0.75943，高于基线验证集最高值0.75291，说明高分辨率输入和弱增强微调有助于提升边界框定位质量。"),
    para("表6-2 训练策略优化验证集结果", align="center", first_line=False),
    table([
        ["实验名称", "训练轮数", "最佳mAP@0.5", "最佳mAP@0.5:0.95", "说明"],
        ["baseline_mAP_100epochs", "100", "0.91551", "0.75291", "YOLOv8m基线"],
        ["baseline_finetune_img800_weakaug", "25", "0.91402", "0.75852", "高分辨率弱增强微调"],
        ["baseline_finetune_img800_weakaug2", "29", "0.91402", "0.75943", "继续微调实验"],
    ]),
    heading("6.4 结果分析", 2),
    para("从测试集结果看，baseline模型具有更高Precision和Recall，说明其分类与检出能力较均衡。注意力模型和P2模型的Precision、Recall均有所下降，表明其并非只是在某一指标上存在权衡，而是整体检测能力受到影响。结合训练过程分析，新增结构虽然在理论上可增强特征表达，但会改变原YOLOv8m预训练权重对应的特征流动路径，使部分层无法完全继承预训练知识。"),
    para("从验证集微调结果看，在不改变网络结构的情况下提高输入分辨率可以让模型获得更丰富的局部细节，对手机、手部、低头等小区域目标更友好；弱化mosaic和mixup能够减少不真实课堂组合图像对后期收敛的干扰。因此，本文最终建议以YOLOv8m基线模型作为系统主模型，并将高分辨率弱增强微调作为后续优化方向。"),
]

# Chapter 7
content += [
    heading("第7章 总结与展望", 1),
    heading("7.1 总结", 2),
    para("本文围绕学生课堂行为检测任务，完成了基于YOLOv8的检测模型训练、改进实验和桌面端系统实现。系统能够识别举手、阅读、书写、使用手机、低头、趴桌六类课堂行为，并支持图片、视频、摄像头和批量检测等功能。通过将检测结果与行为专注度规则结合，系统能够进一步输出班级专注度，为课堂教学状态分析提供辅助依据。"),
    para("实验结果表明，YOLOv8m基线模型在测试集上取得mAP@0.5为0.8961、mAP@0.5:0.95为0.7382的检测效果，能够较好满足项目需求。对比实验显示，简单加入ECA注意力和P2检测头未能超过基线，而高分辨率弱增强微调在验证集mAP@0.5:0.95上取得提升。这一结果说明，针对本项目数据集，合理的训练策略优化比盲目增加模型结构更具实际价值。"),
    heading("7.2 展望", 2),
    para("本文仍存在一些不足。首先，数据集中不同类别样本数量差异明显，低头和趴桌等类别样本较少，后续可通过补充采集、定向增强和类别均衡采样提升少数类检测能力。其次，当前专注度计算方法主要基于行为类别和规则权重，仍具有一定经验性，后续可结合人工标注的专注度评分或时序模型学习更客观的评分函数。最后，系统目前主要面向桌面端应用，后续可考虑模型轻量化、ONNX部署、Web端展示和数据库存储，以提高系统部署能力和实际应用范围。"),
]

# References and acknowledgements
refs = [
    "[1] Redmon J, Divvala S, Girshick R, et al. You Only Look Once: Unified, Real-Time Object Detection[C]//CVPR, 2016.",
    "[2] Redmon J, Farhadi A. YOLO9000: Better, Faster, Stronger[C]//CVPR, 2017.",
    "[3] Bochkovskiy A, Wang C Y, Liao H Y M. YOLOv4: Optimal Speed and Accuracy of Object Detection[J]. arXiv:2004.10934, 2020.",
    "[4] Wang C Y, Bochkovskiy A, Liao H Y M. YOLOv7: Trainable Bag-of-Freebies Sets New State-of-the-Art for Real-Time Object Detectors[C]//CVPR, 2023.",
    "[5] Jocher G, Chaurasia A, Qiu J. Ultralytics YOLOv8. Ultralytics, 2023.",
    "[6] Ren S, He K, Girshick R, et al. Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks[J]. IEEE TPAMI, 2017.",
    "[7] Liu W, Anguelov D, Erhan D, et al. SSD: Single Shot MultiBox Detector[C]//ECCV, 2016.",
    "[8] Lin T Y, Dollar P, Girshick R, et al. Feature Pyramid Networks for Object Detection[C]//CVPR, 2017.",
    "[9] Woo S, Park J, Lee J Y, et al. CBAM: Convolutional Block Attention Module[C]//ECCV, 2018.",
    "[10] Wang Q, Wu B, Zhu P, et al. ECA-Net: Efficient Channel Attention for Deep Convolutional Neural Networks[C]//CVPR, 2020.",
    "[11] Hou Q, Zhou D, Feng J. Coordinate Attention for Efficient Mobile Network Design[C]//CVPR, 2021.",
    "[12] Yang L, Zhang R Y, Li L, et al. SimAM: A Simple, Parameter-Free Attention Module for Convolutional Neural Networks[C]//ICML, 2021.",
    "[13] Paszke A, Gross S, Massa F, et al. PyTorch: An Imperative Style, High-Performance Deep Learning Library[C]//NeurIPS, 2019.",
    "[14] Bradski G. The OpenCV Library[J]. Dr. Dobb's Journal of Software Tools, 2000.",
    "[15] Riverbank Computing. PyQt5 Reference Guide[EB/OL].",
]
content += [heading("参考文献", 1)]
content += [para(r, first_line=False) for r in refs]
content += [
    heading("致    谢", 1),
    para("在本论文完成过程中，指导教师在选题确定、系统设计、实验分析和论文撰写等方面给予了耐心指导和帮助。在项目实现过程中，同学和朋友也在数据整理、系统测试和问题排查方面提供了支持。在此向所有给予帮助的老师、同学和家人表示诚挚感谢。"),
]


markdown_lines = [
    f"# {TITLE}",
    "",
    "## 摘要",
    "随着智慧教育和计算机视觉技术的发展，课堂教学状态的自动感知逐渐成为教育信息化建设中的重要内容。本文设计并实现了一套基于YOLOv8的学生课堂行为检测系统，支持图片、视频、摄像头和批量检测，并结合检测结果完成课堂专注度分析。",
    "",
    "关键词：YOLOv8；课堂行为检测；目标检测；深度学习；PyQt5；专注度分析",
    "",
    "## 主要实验结果",
    "| 模型 | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall |",
    "|---|---:|---:|---:|---:|",
    "| baseline_mAP_100epochs | 0.8961 | 0.7382 | 0.9032 | 0.8512 |",
    "| optimized_attention_light_m_pretrained | 0.8353 | 0.6534 | 0.8090 | 0.8114 |",
    "| yolov8m_p2_100epochs | 0.8377 | 0.6547 | 0.8130 | 0.8005 |",
    "",
    "完整正文请以生成的 docx 为准。",
]

OUT_MD.write_text("\n".join(markdown_lines), encoding="utf-8")

shutil.copyfile(TEMPLATE, OUT_DOCX)
xml = body_xml(content).encode("utf-8")
tmp = OUT_DOCX.with_suffix(".tmp.docx")
with zipfile.ZipFile(OUT_DOCX, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "word/document.xml":
            zout.writestr(item, xml)
        else:
            zout.writestr(item, zin.read(item.filename))
tmp.replace(OUT_DOCX)

print(OUT_DOCX)
print(OUT_MD)
