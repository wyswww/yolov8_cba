# -*- coding: utf-8 -*-
"""Generate an expanded thesis draft and thesis figures without external services."""

from __future__ import annotations

import html
import math
import re
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "12.王岩松山东科技大学本科毕业设计（论文）规范格式.docx"
FIG_DIR = ROOT / "论文图表"
OUT_DOCX = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版.docx"
OUT_MD = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版.md"
PROMPTS = FIG_DIR / "gpt_image2_prompts.md"


TITLE = "基于YOLOv8的学生课堂行为检测系统设计与实现"
EN_TITLE = "Design and Implementation of a Student Classroom Behavior Detection System Based on YOLOv8"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        ROOT / "Font" / "platech.ttf",
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def rounded_box(draw: ImageDraw.ImageDraw, xy, fill, outline="#285078", radius=18, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def centered(draw: ImageDraw.ImageDraw, xy, text: str, fnt, fill="#172033", spacing=6):
    x1, y1, x2, y2 = xy
    lines = []
    for raw in text.split("\n"):
        while len(raw) > 13:
            lines.append(raw[:13])
            raw = raw[13:]
        lines.append(raw)
    heights = []
    widths = []
    for line in lines:
        box = draw.textbbox((0, 0), line, font=fnt)
        widths.append(box[2] - box[0])
        heights.append(box[3] - box[1])
    total_h = sum(heights) + spacing * (len(lines) - 1)
    y = y1 + (y2 - y1 - total_h) / 2
    for line, w, h in zip(lines, widths, heights):
        draw.text((x1 + (x2 - x1 - w) / 2, y), line, font=fnt, fill=fill)
        y += h + spacing


def arrow(draw: ImageDraw.ImageDraw, start, end, fill="#2f5d8c", width=4):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 14
    pts = [
        (x2, y2),
        (x2 - size * math.cos(ang - math.pi / 6), y2 - size * math.sin(ang - math.pi / 6)),
        (x2 - size * math.cos(ang + math.pi / 6), y2 - size * math.sin(ang + math.pi / 6)),
    ]
    draw.polygon(pts, fill=fill)


def save_svg_placeholder(path: Path, title: str, lines: list[str]):
    h = 120 + 42 * len(lines)
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{h}" viewBox="0 0 1400 {h}">',
        '<rect width="100%" height="100%" fill="#f8fbff"/>',
        f'<text x="700" y="58" text-anchor="middle" font-family="Microsoft YaHei, SimHei" font-size="34" font-weight="700" fill="#1d3557">{html.escape(title)}</text>',
    ]
    y = 118
    for line in lines:
        body.append(f'<text x="70" y="{y}" font-family="Microsoft YaHei, SimHei" font-size="25" fill="#23364d">{html.escape(line)}</text>')
        y += 42
    body.append("</svg>")
    path.write_text("\n".join(body), encoding="utf-8")


def make_figures() -> list[tuple[str, Path]]:
    FIG_DIR.mkdir(exist_ok=True)
    f_title = font(34, True)
    f_box = font(23)
    f_small = font(20)
    figs: list[tuple[str, Path]] = []

    # Figure 1: architecture
    img = Image.new("RGB", (1600, 950), "#f7fbff")
    d = ImageDraw.Draw(img)
    d.text((430, 35), "学生课堂行为检测系统总体架构图", font=f_title, fill="#17324d")
    boxes = [
        ((80, 160, 360, 300), "数据输入层\n图片/视频/摄像头", "#d8ecff"),
        ((460, 160, 740, 300), "模型推理层\nYOLOv8m行为检测", "#e5f4df"),
        ((840, 160, 1120, 300), "业务分析层\n结果解析/专注度计算", "#fff1d6"),
        ((1220, 160, 1500, 300), "可视化交互层\nPyQt5界面展示", "#f0e5ff"),
        ((260, 470, 560, 630), "结果管理\n图片保存/视频保存/批量导出", "#edf7f3"),
        ((650, 470, 950, 630), "配置与资源\n模型权重/类别名称/字体", "#f8e8e8"),
        ((1040, 470, 1340, 630), "实验支撑\n训练脚本/测试脚本/结果CSV", "#e8eff8"),
    ]
    for xy, text, fill in boxes:
        rounded_box(d, xy, fill)
        centered(d, xy, text, f_box)
    for s, e in [((360, 230), (460, 230)), ((740, 230), (840, 230)), ((1120, 230), (1220, 230)),
                 ((600, 300), (500, 470)), ((980, 300), (800, 470)), ((980, 300), (1190, 470))]:
        arrow(d, s, e)
    d.text((115, 760), "说明：系统以YOLOv8m模型为核心，完成课堂行为检测，并将检测框、类别、置信度等结果转化为界面信息和专注度指标。", font=f_small, fill="#314862")
    p = FIG_DIR / "图3-1_系统总体架构图.png"
    img.save(p)
    save_svg_placeholder(FIG_DIR / "图3-1_系统总体架构图.svg", "学生课堂行为检测系统总体架构图",
                         ["数据输入层 -> 模型推理层 -> 业务分析层 -> 可视化交互层",
                          "结果管理、配置资源、实验支撑共同服务于系统运行与论文实验。"])
    figs.append(("图3-1 系统总体架构图", p))

    # Figure 2: training pipeline
    img = Image.new("RGB", (1600, 900), "#fbfcff")
    d = ImageDraw.Draw(img)
    d.text((500, 35), "模型训练与评估流程图", font=f_title, fill="#17324d")
    flow = [
        ((80, 210, 300, 330), "原始课堂图片\nYOLO标签", "#e4f1ff"),
        ((380, 210, 600, 330), "数据集划分\ntrain/val/test", "#eaf7e4"),
        ((680, 210, 900, 330), "参数配置\nimgsz/epoch/增强", "#fff2d8"),
        ((980, 210, 1200, 330), "YOLOv8m训练\n迁移学习", "#f2e8ff"),
        ((1280, 210, 1500, 330), "测试评估\nP/R/mAP", "#fde9e9"),
        ((530, 520, 760, 650), "改进实验\nECA/P2/微调", "#f5f8df"),
        ((850, 520, 1080, 650), "结果对比\n选择最优模型", "#e8f8f6"),
    ]
    for xy, text, fill in flow:
        rounded_box(d, xy, fill)
        centered(d, xy, text, f_box)
    for s, e in [((300, 270), (380, 270)), ((600, 270), (680, 270)), ((900, 270), (980, 270)), ((1200, 270), (1280, 270)),
                 ((790, 330), (645, 520)), ((1090, 330), (965, 520)), ((760, 585), (850, 585))]:
        arrow(d, s, e)
    p = FIG_DIR / "图4-1_模型训练与评估流程图.png"
    img.save(p)
    save_svg_placeholder(FIG_DIR / "图4-1_模型训练与评估流程图.svg", "模型训练与评估流程图",
                         ["原始数据与YOLO标签 -> 数据集划分 -> 参数配置 -> YOLOv8m训练 -> 测试评估",
                          "改进实验包括轻量注意力、P2检测头和高分辨率弱增强微调。"])
    figs.append(("图4-1 模型训练与评估流程图", p))

    # Figure 3: inference workflow
    img = Image.new("RGB", (1500, 1000), "#f8fbff")
    d = ImageDraw.Draw(img)
    d.text((470, 35), "系统检测业务流程图", font=f_title, fill="#17324d")
    coords = [
        ((120, 160, 400, 285), "用户选择输入\n图片/视频/摄像头", "#dff0ff"),
        ((580, 160, 860, 285), "读取图像帧\n格式转换与预处理", "#eaf8e2"),
        ((1040, 160, 1320, 285), "YOLO模型推理\n输出检测结果", "#fff1d6"),
        ((1040, 430, 1320, 555), "解析结果\n类别/坐标/置信度", "#f2e7ff"),
        ((580, 430, 860, 555), "绘制检测框\n更新表格信息", "#fdeaea"),
        ((120, 430, 400, 555), "计算专注度\n显示人数和均值", "#e8f8f6"),
        ((580, 700, 860, 825), "保存结果\n图片/视频/批量导出", "#f6f0df"),
    ]
    for xy, text, fill in coords:
        rounded_box(d, xy, fill)
        centered(d, xy, text, f_box)
    for s, e in [((400, 222), (580, 222)), ((860, 222), (1040, 222)), ((1180, 285), (1180, 430)),
                 ((1040, 492), (860, 492)), ((580, 492), (400, 492)), ((720, 555), (720, 700))]:
        arrow(d, s, e)
    p = FIG_DIR / "图5-1_系统检测业务流程图.png"
    img.save(p)
    save_svg_placeholder(FIG_DIR / "图5-1_系统检测业务流程图.svg", "系统检测业务流程图",
                         ["输入选择 -> 图像帧读取 -> YOLO模型推理 -> 结果解析 -> 界面展示/专注度计算 -> 结果保存"])
    figs.append(("图5-1 系统检测业务流程图", p))

    # Figure 4: focus algorithm
    img = Image.new("RGB", (1500, 960), "#fbfdff")
    d = ImageDraw.Draw(img)
    d.text((430, 35), "课堂专注度计算流程图", font=f_title, fill="#17324d")
    nodes = [
        ((90, 160, 360, 290), "检测结果输入\n类别/置信度/目标框", "#e3f1ff"),
        ((470, 160, 740, 290), "类别基础分\n高/中/低专注行为", "#e7f7df"),
        ((850, 160, 1120, 290), "置信度加权\n基础分×confidence", "#fff1d6"),
        ((470, 430, 740, 560), "目标匹配\n中心点距离关联", "#f0e7ff"),
        ((850, 430, 1120, 560), "时序惩罚\n连续低专注扣分", "#fdeaea"),
        ((470, 700, 740, 830), "趋势缓冲\n班级变化平滑", "#e8f8f6"),
        ((850, 700, 1120, 830), "输出结果\n人数/平均专注度", "#f7f0df"),
    ]
    for xy, text, fill in nodes:
        rounded_box(d, xy, fill)
        centered(d, xy, text, f_box)
    for s, e in [((360, 225), (470, 225)), ((740, 225), (850, 225)), ((985, 290), (985, 430)),
                 ((850, 495), (740, 495)), ((605, 560), (605, 700)), ((740, 765), (850, 765))]:
        arrow(d, s, e)
    p = FIG_DIR / "图5-2_课堂专注度计算流程图.png"
    img.save(p)
    save_svg_placeholder(FIG_DIR / "图5-2_课堂专注度计算流程图.svg", "课堂专注度计算流程图",
                         ["检测结果 -> 类别基础分 -> 置信度加权 -> 目标匹配 -> 时序惩罚 -> 趋势缓冲 -> 输出专注度"])
    figs.append(("图5-2 课堂专注度计算流程图", p))

    # Figure 5: module structure
    img = Image.new("RGB", (1600, 900), "#f7fbff")
    d = ImageDraw.Draw(img)
    d.text((500, 35), "系统软件模块结构图", font=f_title, fill="#17324d")
    center = (650, 170, 950, 290)
    rounded_box(d, center, "#dfeeff", radius=22)
    centered(d, center, "主程序 main.py\n界面调度与业务控制", f_box)
    modules = [
        ((90, 420, 360, 550), "Config.py\n模型路径/类别配置", "#e8f8e2"),
        ((460, 420, 730, 550), "detect_tools.py\n绘图/保存/格式转换", "#fff1d6"),
        ((830, 420, 1100, 550), "Ultralytics YOLO\n模型训练与推理", "#f1e8ff"),
        ((1200, 420, 1470, 550), "UIProgram\n界面文件与样式", "#fdeaea"),
        ((460, 660, 730, 790), "train/test脚本\n训练评估与对比", "#e8f8f6"),
        ((830, 660, 1100, 790), "runs/detect\n权重与结果文件", "#f6f0df"),
    ]
    for xy, text, fill in modules:
        rounded_box(d, xy, fill)
        centered(d, xy, text, f_box)
        arrow(d, ((center[0] + center[2]) // 2, center[3]), ((xy[0] + xy[2]) // 2, xy[1]))
    p = FIG_DIR / "图5-3_系统软件模块结构图.png"
    img.save(p)
    save_svg_placeholder(FIG_DIR / "图5-3_系统软件模块结构图.svg", "系统软件模块结构图",
                         ["main.py作为调度核心，连接配置模块、工具模块、YOLO推理模块、UI模块和训练评估模块。"])
    figs.append(("图5-3 系统软件模块结构图", p))

    # Figure 6: experiment chart
    img = Image.new("RGB", (1500, 900), "#ffffff")
    d = ImageDraw.Draw(img)
    d.text((430, 35), "主要模型测试指标对比图", font=f_title, fill="#17324d")
    names = ["Baseline", "ECA注意力", "P2检测头", "img800微调", "Baseline 800推理"]
    vals = [0.8961, 0.8353, 0.8377, 0.8898, 0.8998]
    colors = ["#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756"]
    x0, y0, w, h = 230, 150, 1050, 560
    d.line((x0, y0 + h, x0 + w, y0 + h), fill="#334", width=3)
    d.line((x0, y0, x0, y0 + h), fill="#334", width=3)
    for i in range(6):
        y = y0 + h - i * h / 5
        d.line((x0 - 8, y, x0 + w, y), fill="#e5e9f0", width=1)
        d.text((90, y - 14), f"{i * 0.2:.1f}", font=f_small, fill="#344")
    bar_w = 120
    gap = 70
    for i, (name, val, color) in enumerate(zip(names, vals, colors)):
        x = x0 + 70 + i * (bar_w + gap)
        bh = val * h
        d.rounded_rectangle((x, y0 + h - bh, x + bar_w, y0 + h), radius=10, fill=color)
        d.text((x + 10, y0 + h - bh - 38), f"{val:.4f}", font=f_small, fill="#172033")
        d.text((x - 20, y0 + h + 28), name, font=f_small, fill="#172033")
    d.text((600, 820), "指标：mAP@0.5（测试集）", font=f_small, fill="#172033")
    p = FIG_DIR / "图6-1_主要模型测试指标对比图.png"
    img.save(p)
    save_svg_placeholder(FIG_DIR / "图6-1_主要模型测试指标对比图.svg", "主要模型测试指标对比图",
                         ["Baseline mAP@0.5=0.8961；ECA注意力=0.8353；P2检测头=0.8377；img800微调=0.8898；Baseline 800推理=0.8998。"])
    figs.append(("图6-1 主要模型测试指标对比图", p))

    return figs


def xml_escape(text: str) -> str:
    return html.escape(text, quote=False)


def wr(text: str, bold: bool = False, size: int = 21) -> str:
    b = "<w:b/>" if bold else ""
    return (
        "<w:r><w:rPr>"
        '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>'
        f"{b}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{xml_escape(text)}</w:t></w:r>"
    )


def p(text: str = "", align: str = "both", bold: bool = False, size: int = 21, first_line: bool = True) -> str:
    ind = '<w:ind w:firstLine="420"/>' if first_line else ""
    return (
        "<w:p><w:pPr>"
        f"<w:jc w:val=\"{align}\"/>"
        '<w:spacing w:line="360" w:lineRule="auto"/>'
        f"{ind}</w:pPr>{wr(text, bold, size)}</w:p>"
    )


def h(text: str, level: int = 1) -> str:
    if level == 1:
        return p(text, "center", True, 28, False)
    if level == 2:
        return p(text, "left", True, 24, False)
    return p(text, "left", True, 21, False)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table(rows: list[list[str]]) -> str:
    out = ["<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/>"
           "<w:tblBorders><w:top w:val=\"single\" w:sz=\"4\"/><w:left w:val=\"single\" w:sz=\"4\"/>"
           "<w:bottom w:val=\"single\" w:sz=\"4\"/><w:right w:val=\"single\" w:sz=\"4\"/>"
           "<w:insideH w:val=\"single\" w:sz=\"4\"/><w:insideV w:val=\"single\" w:sz=\"4\"/>"
           "</w:tblBorders></w:tblPr>"]
    for i, row in enumerate(rows):
        out.append("<w:tr>")
        for cell in row:
            out.append("<w:tc><w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>")
            out.append(p(cell, "center", i == 0, 20, False))
            out.append("</w:tc>")
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def image_para(rid: str, name: str, docpr_id: int, width_px: int = 1000, height_px: int = 620) -> str:
    cx = int(width_px * 9525)
    cy = int(height_px * 9525)
    return f"""
<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>
<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>
<wp:docPr id="{docpr_id}" name="{xml_escape(name)}"/><wp:cNvGraphicFramePr/>
<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:nvPicPr><pic:cNvPr id="{docpr_id}" name="{xml_escape(name)}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
</pic:pic></a:graphicData></a:graphic>
</wp:inline></w:drawing></w:r></w:p>
"""


def body_xml(parts: list[str]) -> str:
    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="851" w:footer="992" w:gutter="0"/>'
        '<w:cols w:space="425"/><w:docGrid w:type="lines" w:linePitch="312"/>'
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


def add_section(parts: list[str], md: list[str], title: str, paragraphs: list[str], level: int = 2):
    parts.append(h(title, level))
    md.append("\n" + "#" * level + " " + title)
    for text in paragraphs:
        parts.append(p(text))
        md.append(text)


def build_doc(figs: list[tuple[str, Path]]):
    global OUT_DOCX
    parts: list[str] = []
    md: list[str] = []
    figure_rids = {path.name: f"rIdFig{i+1}" for i, (_, path) in enumerate(figs)}

    # Cover and declarations
    parts += [
        p("本科毕业设计（论文）", "center", True, 36, False),
        p("", first_line=False),
        p(TITLE, "center", True, 32, False),
        p(EN_TITLE, "center", False, 24, False),
        p("", first_line=False),
        p("学    院：  计算机科学与工程学院", "left", False, 28, False),
        p("专业班级：  计算机科学与技术（请填写班级）", "left", False, 28, False),
        p("姓    名：  （请填写姓名）", "left", False, 28, False),
        p("学    号：  （请填写学号）", "left", False, 28, False),
        p("指导教师：  （请填写指导教师）", "left", False, 28, False),
        p("完成日期：  2026年5月", "left", False, 28, False),
        p("教务处制", "center", False, 24, False),
        page_break(),
        h("学位论文原创性声明", 1),
        p("本人呈交给山东科技大学的学位论文，除所列参考文献和世所公认的文献外，全部是本人攻读学位期间在导师指导下的研究成果。除文中已经标明引用的内容外，本论文不包含任何其他个人或集体已经发表或撰写过的研究成果。对本文的研究做出贡献的个人和集体，均已在文中以明确方式标明。本人完全意识到本声明的法律结果由本人承担。"),
        p("若有不实之处，本人愿意承担相关法律责任。"),
        p("本人签名：                         日 期：     年   月   日", first_line=False),
        h("学位论文使用授权声明", 1),
        p("本人完全了解山东科技大学有关保留、使用学位论文的规定，同意本人所撰写的学位论文的使用授权按照学校的管理规定处理。作为申请学位的条件之一，学校有权保留学位论文并向国家有关部门或其指定机构送交论文的电子版和纸质版；有权将学位论文的全部或部分内容编入有关数据库发表，并可以以电子、网络及其他数字媒体形式公开出版。"),
        p("作者签名：                          导师签名：", first_line=False),
        p("日   期：    年   月   日           日   期：    年   月   日", first_line=False),
        page_break(),
    ]
    md += [f"# {TITLE}", "", "## 摘要"]

    abstract = [
        "随着智慧教育、人工智能和计算机视觉技术的快速发展，课堂教学状态的自动感知逐渐成为教育信息化建设的重要内容。传统课堂行为观察主要依赖教师人工记录或课后抽样分析，存在主观性强、实时性差、工作量大、难以长期量化等问题。针对这些不足，本文设计并实现了一套基于YOLOv8的学生课堂行为检测系统，利用深度学习目标检测模型识别课堂场景中的典型学生行为，并结合检测结果完成课堂专注度的辅助分析与可视化展示。",
        "本文围绕学生课堂行为检测任务，构建了包含举手、阅读、书写、使用手机、低头、趴桌六类行为的数据集配置与训练流程。系统以YOLOv8m为核心检测模型，完成了基线训练、轻量注意力机制实验、P2小目标检测头实验、高分辨率弱增强微调实验以及高分辨率推理实验。实验结果表明，YOLOv8m基线模型在测试集上取得mAP@0.5为0.8961、mAP@0.5:0.95为0.7382、Precision为0.9032、Recall为0.8512的结果，综合性能稳定，能够较好满足课堂行为检测任务需求。进一步实验显示，ECA注意力、P2检测头和高分辨率弱增强微调在测试集上均未全面超过基线模型；直接使用基线权重进行imgsz=800推理时，mAP@0.5提升至0.8998，Recall提升至0.8614，但mAP@0.5:0.95和Precision下降。说明高分辨率推理有助于提升目标命中能力，最终应用中需要在召回率、误检控制和定位精度之间进行权衡。",
        "在系统实现方面，本文基于Python、PyTorch、OpenCV和PyQt5完成了桌面端检测系统开发。系统支持图片检测、视频检测、实时摄像头检测、批量图片处理、检测结果保存、行为类别展示、置信度显示和班级专注度计算等功能。针对视频流场景，系统设计了融合类别权重、检测置信度、时序稳定性和班级趋势的专注度计算方法，使检测结果能够进一步转化为课堂状态分析指标。系统测试表明，该系统具有较好的检测准确性、交互性和实用性，可为智慧课堂、教学质量分析和学生行为研究提供参考。",
    ]
    parts += [h("摘    要", 1)] + [p(x) for x in abstract] + [p("关键词：YOLOv8；课堂行为检测；目标检测；深度学习；PyQt5；专注度分析", first_line=False), page_break()]
    md += abstract + ["关键词：YOLOv8；课堂行为检测；目标检测；深度学习；PyQt5；专注度分析", "", "## ABSTRACT"]
    en_abs = [
        "With the rapid development of smart education, artificial intelligence and computer vision, automatic perception of classroom teaching status has become an important part of educational informatization. Traditional classroom behavior observation mainly relies on manual recording or post-class sampling, which is subjective, inefficient and difficult to quantify continuously. To address these problems, this thesis designs and implements a student classroom behavior detection system based on YOLOv8. The system detects typical student behaviors in classroom scenes and provides auxiliary analysis and visual display of classroom concentration.",
        "YOLOv8m is adopted as the core detection model. Six classroom behavior categories are considered, including hand-raising, reading, writing, using phone, bowing the head and leaning over the table. This thesis completes baseline training, lightweight attention experiments, P2 detection-head experiments and high-resolution weak-augmentation fine-tuning. The YOLOv8m baseline achieves 0.8961 mAP@0.5, 0.7382 mAP@0.5:0.95, 0.9032 precision and 0.8512 recall on the test set. Further experiments show that simply adding ECA attention or a P2 detection head does not improve the overall performance, while fine-tuning with higher image resolution and weaker augmentation improves mAP@0.5:0.95 on the validation set.",
        "The system is implemented with Python, PyTorch, OpenCV and PyQt5. It supports image detection, video detection, real-time camera detection, batch image processing, result saving, behavior category display, confidence display and class concentration calculation. For video streams, a concentration evaluation method integrating behavior weights, detection confidence, temporal stability and class-level trend is designed. The system test shows that the proposed system has good accuracy, interactivity and practical value.",
    ]
    parts += [h("ABSTRACT", 1)] + [p(x) for x in en_abs] + [p("KEY WORDS: YOLOv8; Classroom Behavior Detection; Object Detection; Deep Learning; PyQt5; Concentration Analysis", first_line=False), page_break()]
    md += en_abs + ["KEY WORDS: YOLOv8; Classroom Behavior Detection; Object Detection; Deep Learning; PyQt5; Concentration Analysis"]

    toc = ["摘    要", "ABSTRACT", "第1章 绪论", "第2章 相关技术基础", "第3章 系统需求分析与总体设计", "第4章 数据集构建与模型训练", "第5章 系统功能实现", "第6章 实验结果与分析", "第7章 总结与展望", "参考文献", "致谢"]
    parts += [h("目    录", 1)] + [p(x, first_line=False) for x in toc] + [page_break()]

    # Main content
    chapters = [
        ("第1章 绪论", [
            ("1.1 研究背景", [
                "课堂教学是学校教育活动中最基础、最核心的环节，学生在课堂中的行为状态直接反映其学习参与程度和课堂教学效果。随着信息技术在教育领域的深入应用，智慧课堂、智能教学评价和个性化学习分析逐渐成为教育信息化的重要方向。在这一背景下，如何通过技术手段实时、客观、连续地获取学生课堂行为状态，成为提升教学管理精细化水平的重要问题。",
                "在传统课堂中，教师通常通过肉眼观察判断学生是否认真听讲、是否阅读或书写、是否低头、趴桌或使用手机。这种方式虽然符合教师日常教学习惯，但存在明显局限。首先，教师的主要精力需要放在授课和课堂组织上，难以同时对所有学生进行持续观察；其次，人工观察不可避免地受到主观经验、观察角度和课堂规模影响；再次，人工记录难以形成细粒度、可追溯的数据，无法满足后续教学质量分析和学生行为研究的需要。",
                "计算机视觉技术为课堂状态自动感知提供了新的解决思路。通过摄像头采集课堂图像或视频，并使用深度学习模型自动识别学生行为，可以在不额外增加教师工作负担的情况下获得较为客观的课堂行为数据。目标检测模型不仅能够判断行为类别，还能够定位行为发生的位置，适合处理多人课堂场景中的多目标识别问题。与人工观察相比，基于视觉的自动检测方法具有实时性强、可量化、可保存和便于统计分析等优势。",
                "YOLO系列算法是近年来应用广泛的一阶段目标检测算法，具有推理速度快、工程实现成熟、部署方便等特点。YOLOv8在模型结构、训练流程和工具链方面进一步完善，能够较好地适应自定义目标检测任务。本文将YOLOv8应用于学生课堂行为检测，结合桌面端可视化系统实现图片、视频和摄像头检测，并基于行为类别构建课堂专注度指标，为智慧课堂应用提供一种可行方案。",
            ]),
            ("1.2 研究意义", [
                "本文研究具有一定的理论意义和应用价值。从理论层面看，课堂行为检测是目标检测技术在教育场景中的具体应用，涉及多目标检测、小目标识别、类别不均衡、复杂背景干扰等问题。通过对YOLOv8m基线模型、注意力机制、P2检测头和训练策略优化进行实验比较，可以分析不同改进方向在课堂行为数据集上的适用性，为类似教育场景视觉任务提供参考。",
                "从应用层面看，课堂行为检测系统能够将学生的课堂表现转化为可视化、可统计的数据。教师可通过系统快速了解班级整体状态，例如阅读和书写行为占比、低头或使用手机行为出现情况等。对于学校教学管理而言，系统可辅助开展课堂质量评估、教学反思和学生学习状态分析。对于学生个体而言，长期行为数据也可为学习习惯改进提供参考。",
                "此外，本项目将模型训练、算法评估和软件系统实现结合起来，不仅关注检测模型的精度，还关注系统的可用性和完整性。系统支持图片检测、视频分析、摄像头监测、批量处理和结果保存，能够较完整地覆盖实际使用流程。这种从算法到应用的实现方式符合本科毕业设计对综合实践能力的要求。",
            ]),
            ("1.3 国内外研究现状", [
                "目标检测技术的发展经历了传统人工特征方法和深度学习方法两个阶段。早期方法通常使用Haar、HOG、SIFT等人工特征描述图像，再结合支持向量机或级联分类器完成目标识别。这类方法对简单场景有效，但面对复杂课堂环境中的遮挡、光照变化和目标尺度差异时，鲁棒性较差。",
                "深度学习兴起后，卷积神经网络显著提升了视觉任务性能。以R-CNN、Fast R-CNN、Faster R-CNN为代表的两阶段检测算法先生成候选区域，再进行分类和回归，检测精度较高；以YOLO和SSD为代表的一阶段算法直接预测目标类别和边界框，速度更快，更适合实时应用。近年来，YOLOv5、YOLOv7、YOLOv8等模型不断改进网络结构、特征融合和训练策略，使一阶段检测算法在精度和速度之间取得较好平衡。",
                "在教育场景中，课堂行为识别研究主要包括学生姿态估计、表情识别、课堂专注度评估、异常行为检测等方向。有的研究使用人体关键点分析学生坐姿和手部动作，有的研究使用面部表情判断情绪状态，也有研究通过目标检测识别低头、举手、阅读、使用手机等行为。由于真实课堂中通常存在多人密集、遮挡明显、目标尺度差异大等问题，单纯分类方法难以满足定位和多目标识别需求，因此目标检测方法具有更强适应性。",
                "现有研究也存在一些不足。一方面，部分方法只关注模型精度，没有形成完整的交互系统；另一方面，部分系统只实现检测功能，缺少对课堂状态的进一步分析。本文在检测模型训练的基础上，进一步设计专注度计算方法和可视化界面，力求形成从数据输入、模型推理到结果展示和保存的完整流程。",
            ]),
            ("1.4 本文主要研究内容与章节安排", [
                "本文主要完成以下工作：第一，整理课堂行为检测数据集，明确六类行为标签，并完成训练集、验证集和测试集配置；第二，基于YOLOv8m训练学生课堂行为检测基线模型，并使用Precision、Recall、mAP等指标进行评价；第三，设计并验证轻量ECA注意力、P2小目标检测头、高分辨率弱增强微调和高分辨率推理等改进方案；第四，基于PyQt5实现桌面端检测系统，支持图片、视频、摄像头和批量检测；第五，设计专注度计算方法，将检测结果转化为课堂状态分析指标。",
                "全文结构如下：第1章介绍研究背景、意义和研究现状；第2章介绍深度学习、目标检测、YOLOv8和系统开发技术；第3章进行系统需求分析和总体设计；第4章介绍数据集构建、模型训练和改进实验；第5章说明系统主要功能实现；第6章给出实验结果与分析；第7章总结全文并展望后续研究方向。",
            ]),
        ]),
        ("第2章 相关技术基础", [
            ("2.1 深度学习基础", [
                "深度学习是一类以多层神经网络为核心的数据驱动建模方法。与传统机器学习依赖人工特征设计不同，深度学习能够直接从大量样本中自动学习特征表示。在图像领域，卷积神经网络通过局部感受野、权值共享和池化操作有效提取空间特征，使模型能够从低层边缘、纹理逐步学习到高层语义信息。",
                "卷积层是卷积神经网络的基本组成部分，通过卷积核在输入特征图上滑动实现局部特征提取。激活函数用于引入非线性表达能力，常见激活函数包括ReLU、SiLU等。归一化层可以稳定训练过程，减少内部协变量偏移。池化或步长卷积用于降低特征图分辨率并扩大感受野。通过这些模块的组合，网络可以获得对目标形状、纹理和上下文信息的表达能力。",
                "在目标检测任务中，模型需要同时完成分类和定位。分类分支负责判断目标属于哪个类别，回归分支负责预测目标边界框位置。检测模型的训练通常需要定义损失函数，将分类损失、定位损失和置信度或分布损失组合起来。模型通过反向传播不断更新参数，使预测结果逐渐接近人工标注。",
            ]),
            ("2.2 目标检测算法", [
                "目标检测算法按照处理流程通常分为两阶段算法和一阶段算法。两阶段算法先生成候选区域，再对候选区域进行分类和边界框回归。该类算法精度较高，但流程较复杂，推理速度相对较慢。一阶段算法不显式生成候选区域，而是直接在特征图上预测目标类别和边界框，因此速度更快，适合实时检测任务。",
                "YOLO算法是典型的一阶段检测算法，其核心思想是将目标检测视为单次前向传播即可完成的回归问题。输入图像经过神经网络后，模型直接输出各尺度特征图上的目标边界框、类别概率和置信度。由于结构简洁、速度较快，YOLO系列广泛应用于工业检测、交通监控、安防识别和智能教育等场景。",
                "目标检测模型的性能评价不能只看单一指标。Precision表示预测为正样本的结果中有多少是真正目标，Recall表示真实目标中有多少被模型成功检出。mAP综合衡量不同类别的平均精度，mAP@0.5使用IoU阈值0.5，mAP@0.5:0.95则在多个IoU阈值下取平均，更严格地衡量定位质量。本文同时使用这些指标，以全面评价模型效果。",
            ]),
            ("2.3 YOLOv8模型结构", [
                "YOLOv8是Ultralytics推出的新一代YOLO模型实现，支持目标检测、实例分割、图像分类、姿态估计等多种任务。YOLOv8检测模型主要由Backbone、Neck和Head三部分组成。Backbone用于提取图像多层特征，Neck用于融合不同尺度特征，Head用于输出目标类别和边界框。",
                "YOLOv8使用C2f模块增强特征表达和梯度流动。C2f模块在保持较高计算效率的同时，能够融合更多中间特征，有助于提升检测精度。YOLOv8还采用解耦头结构，将分类和回归任务分开处理，有利于提高模型收敛稳定性和检测效果。对于课堂行为检测任务而言，YOLOv8m在模型容量和推理速度之间较为平衡，因此本文选择YOLOv8m作为主要实验模型。",
                "YOLOv8训练流程较为完善，支持预训练权重加载、数据增强、自动混合精度、训练过程可视化、结果保存等功能。本文基于本地Ultralytics代码完成模型训练，并根据项目需求扩展了自定义注意力模块、P2模型配置和训练脚本，使实验过程更加可控。",
            ]),
            ("2.4 PyQt5与OpenCV技术", [
                "PyQt5是Python常用的桌面图形界面开发框架，提供按钮、标签、表格、文件选择器、定时器、线程等丰富组件。本文使用PyQt5构建系统主界面，使用户能够通过可视化方式选择输入、查看检测图像、读取检测结果并保存输出文件。与命令行检测相比，桌面界面更适合实际演示和普通用户使用。",
                "OpenCV是广泛使用的计算机视觉库，能够完成图像读取、视频解码、摄像头调用、图像格式转换和结果保存等操作。本文在视频检测和摄像头检测中使用OpenCV逐帧读取画面，并将帧图像送入YOLO模型推理。OpenCV与PyQt5结合，可以实现检测结果的实时刷新。",
                "PIL主要用于中文文字绘制。OpenCV默认中文支持不完善，因此系统通过PIL字体将班级专注度、人数等中文信息绘制到结果图像上，再转换回OpenCV格式进行显示或保存。该方式提高了结果图像的可读性，也使系统更符合中文课堂场景需求。",
            ]),
        ]),
        ("第3章 系统需求分析与总体设计", [
            ("3.1 系统需求分析", [
                "本系统面向课堂行为检测与专注度辅助分析场景，主要用户包括教师、教学管理人员和研究人员。系统需要让用户能够方便地输入课堂图片、视频或实时摄像头画面，并快速获得检测结果。对于单张图片，系统应显示检测框、行为类别、置信度和目标坐标；对于视频和摄像头，系统应连续处理帧图像并动态更新结果；对于批量图片，系统应自动遍历文件夹并保存输出。",
                "系统功能需求可以划分为输入管理、模型推理、结果展示、专注度计算和结果保存五类。输入管理负责处理图片、视频、摄像头和文件夹路径。模型推理负责调用YOLO模型并得到检测结果。结果展示负责在界面中绘制检测框、更新表格和显示统计信息。专注度计算负责根据行为类别和置信度输出班级平均专注度。结果保存负责将检测后的图片或视频保存到本地。",
                "非功能需求包括准确性、实时性、稳定性和可扩展性。准确性要求模型能够较好识别六类课堂行为；实时性要求视频和摄像头检测尽可能流畅；稳定性要求系统在输入为空、文件不存在或检测结果为空时能够正常提示；可扩展性要求模型路径、类别名称、训练脚本和界面功能具有一定可修改性，便于后续升级。",
            ]),
            ("3.2 系统总体架构设计", [
                "系统总体架构如图3-1所示，可分为数据输入层、模型推理层、业务分析层和可视化交互层。数据输入层负责接收图片、视频、摄像头或批量文件夹。模型推理层以YOLOv8m权重为核心，通过Ultralytics接口完成检测。业务分析层解析检测框、类别、置信度等结果，并计算课堂专注度。可视化交互层通过PyQt5界面展示图像、表格、统计信息和保存状态。",
            ]),
        ]),
    ]

    # Add first 3 chapters with figure after architecture section
    for ch_title, sections in chapters:
        parts.append(h(ch_title, 1)); md.append(f"\n# {ch_title}")
        for sec_title, paras in sections:
            add_section(parts, md, sec_title, paras, 2)
            if sec_title == "3.2 系统总体架构设计":
                parts.append(image_para(figure_rids["图3-1_系统总体架构图.png"], "图3-1", 1))
                parts.append(p("图3-1 系统总体架构图", "center", False, 20, False))

    # Remaining chapters with rich text
    remaining = [
        ("3.3 系统功能结构设计", [
            "从功能结构看，系统以主界面为入口，通过不同按钮触发对应业务流程。图片检测功能适用于单帧课堂图像分析；视频检测功能适用于录播课堂或监控视频分析；摄像头检测功能适用于实时课堂状态观察；批量检测功能适用于实验数据处理和结果归档。不同功能共用同一模型推理接口和结果解析逻辑，减少代码重复。",
            "系统将配置项集中放在Config.py中，包括模型路径、英文类别名称和中文类别名称。这样做的优点是当模型权重或类别名称发生变化时，不需要修改主程序逻辑。检测工具函数集中放在detect_tools.py中，包括图片保存、中文绘制、格式转换等功能。主程序main.py主要负责界面事件响应和业务流程调度。",
            "在界面设计方面，系统将图像显示区域和结果表格结合起来。用户既可以直观看到检测框位置，也可以从表格中获得精确坐标和置信度。系统还设置了人数和班级专注度显示区域，使用户能够快速了解课堂整体状态。这种设计兼顾了直观性和数据完整性。",
        ]),
        ("3.4 系统数据流设计", [
            "系统数据流从输入文件或摄像头开始。对于图片输入，程序读取图像路径并调用模型推理；对于视频输入，程序使用VideoCapture逐帧读取；对于摄像头输入，程序打开默认摄像头并按定时器节奏处理帧。每一帧图像都会被送入YOLO模型，模型输出boxes、cls和conf等属性。",
            "检测结果解析后，系统将边界框坐标转换为整数列表，将类别编号映射为行为名称，将置信度转换为百分比字符串。随后，结果被用于三类输出：第一类是图像绘制，即在画面上绘制检测框和标签；第二类是界面表格，即显示每个目标的类别、置信度和坐标；第三类是专注度计算，即根据行为类别和置信度得到班级专注度。",
            "对于视频和摄像头场景，系统还维护focus_history列表，用于记录每秒专注度变化。当视频结束时，系统可以计算整个视频的平均专注度，并以弹窗方式展示结果。这种设计使系统不仅能够提供即时检测结果，还能够给出一段时间内的整体分析。",
        ]),
        ("第4章 数据集构建与模型训练", []),
        ("4.1 数据集格式与类别定义", [
            "本文数据集采用YOLO格式标注。每张图片对应一个同名txt标签文件，标签文件中每一行表示一个目标，格式为类别编号、中心点横坐标、中心点纵坐标、目标宽度和目标高度。这些坐标均经过归一化处理，取值范围为0到1。YOLO格式结构简单，适合与Ultralytics训练框架直接配合使用。",
            "数据集包含六类课堂行为：hand-raising表示举手，reading表示阅读，writing表示书写，using phone表示使用手机，bowing the head表示低头，leaning over the table表示趴桌。前几类通常代表较积极或正常的课堂行为，后几类则可能反映专注度下降或课堂异常状态。通过识别这些行为，系统能够为课堂专注度分析提供基础数据。",
            "数据集路径通过datasets/data.yaml配置。该文件指定训练集、验证集和测试集图片路径，同时给出类别数量和类别名称。本文将数据集路径设置为项目相对路径，避免绝对路径导致不同设备上运行失败，提高项目可移植性。",
        ]),
        ("4.2 数据集统计分析", [
            "经统计，训练集标签文件数量为4202个，验证集标签文件数量为1207个，测试集标签文件数量为209个。训练集标注目标数量在不同类别之间存在明显差异，其中reading类别数量最多，达到13553个；bowing the head和leaning over the table数量较少，分别为1017个和1099个。这种长尾分布是课堂行为数据中较常见的问题。",
            "类别不均衡会影响模型训练。数量较多的类别在训练过程中提供更多梯度信号，模型更容易学习其外观特征；数量较少的类别则可能出现漏检或误检。对于本文任务而言，低头和趴桌类别较少，但它们对专注度分析又十分重要，因此需要在训练策略中适当考虑少数类识别能力。",
            "本文没有简单地对少数类进行过度复制，因为过度复制可能导致模型过拟合少量样本。相反，本文在后续实验中尝试通过调整输入分辨率、减弱不真实增强和提高分类损失权重来改善模型对细粒度行为的学习效果。",
        ]),
        ("4.3 基线模型训练方案", [
            "基线模型选择YOLOv8m，使用COCO预训练权重yolov8m.pt进行迁移学习。迁移学习能够利用大规模通用数据集上学到的边缘、纹理和目标结构特征，减少自定义数据集训练难度。训练轮数设置为100，输入尺寸为640，batch size为8，优化器为AdamW，初始学习率为0.0005，最终学习率比例为0.01。",
            "数据增强方面，基线训练使用HSV颜色扰动、轻微旋转、平移、尺度缩放、水平翻转、mosaic、mixup和copy-paste等策略。这些增强能够提升模型对光照、位置和尺度变化的适应能力。但课堂场景具有一定固定性，过强的数据增强也可能制造不符合真实课堂的组合图像，因此后续微调实验降低了增强强度。",
            "训练完成后，Ultralytics会在runs/detect/baseline_mAP_100epochs目录下保存args.yaml、results.csv、weights/best.pt和weights/last.pt等文件。args.yaml记录训练参数，results.csv记录每轮训练和验证指标，best.pt保存验证指标最优的模型权重。这些文件为实验复现和论文分析提供了依据。",
        ]),
        ("4.4 改进实验一：轻量注意力机制", [
            "注意力机制的基本思想是让网络更加关注重要特征，抑制无关背景干扰。本文尝试在YOLOv8m中加入轻量ECA通道注意力模块。ECA通过一维卷积建模局部跨通道交互，不需要大规模全连接降维，参数量较小，理论上适合在不显著增加计算量的情况下增强通道特征选择能力。",
            "在工程实现上，本文在ultralytics/nn/modules/attention.py中补充注意力模块，并在tasks.py的parse_model逻辑中加入自定义模块解析，使模型配置文件能够识别ECA等模块。随后构建yolov8m-optimized-attention.yaml，在P3和P4特征位置插入ECA模块，并通过层映射方式迁移YOLOv8m预训练权重。",
            "实验结果显示，轻量注意力模型在测试集上的mAP@0.5为0.8353，低于基线模型0.8961。该结果表明，在本项目数据集上，简单插入注意力模块并没有提升性能。可能原因是新增模块随机初始化，改变了原预训练模型的特征分布；同时课堂行为类别之间差异较细，注意力模块若缺少充分数据支撑，可能无法学习到稳定有效的通道权重。",
        ]),
        ("4.5 改进实验二：P2小目标检测头", [
            "课堂行为检测中，手机、手部、低头区域等目标往往尺度较小。YOLOv8默认使用P3、P4、P5三个检测尺度，对中小目标具有一定检测能力，但对于更小目标可能存在细节不足。为此，本文尝试构建YOLOv8m-P2模型，在原有检测头基础上增加P2检测分支，以利用更高分辨率特征图检测小目标。",
            "P2模型配置参考Ultralytics提供的yolov8-p2结构，并结合课堂行为类别进行修改。由于新增P2检测分支无法完全继承原YOLOv8m检测头权重，本文设计了层映射加载方法，将可对齐的Backbone、Neck和P3/P4/P5检测分支权重从yolov8m.pt迁移到P2模型中，新增P2分支则随机初始化。",
            "实验结果显示，YOLOv8m-P2模型在测试集上的mAP@0.5为0.8377，mAP@0.5:0.95为0.6547，仍低于基线模型。说明在当前数据和训练设置下，增加高分辨率检测头并未带来预期收益。可能原因包括模型结构变化较大、batch size下降影响训练稳定性、新增检测头引入更多参数以及数据集中小目标标注质量不足等。",
        ]),
        ("4.6 改进实验三：高分辨率弱增强微调", [
            "在注意力和P2结构实验均未超过基线后，本文将改进重点转向训练策略优化。该实验保持模型结构不变，从baseline_mAP_100epochs的best.pt出发进行微调，将输入尺寸从640提高到800，并显著减弱数据增强强度。这样做的目的是保留强基线模型已经学习到的特征，同时通过更高输入分辨率提升局部细节表达。",
            "微调实验使用较低初始学习率0.0001，训练轮数设置为50，batch size设置为4。为了避免后期训练受到不真实增强样本干扰，mosaic、mixup和copy-paste均设置为0，颜色扰动、旋转、平移和尺度缩放也相应降低。同时将分类损失权重cls从0.5提高到0.65，希望模型更关注类别区分，特别是低头和趴桌等少数类。",
            "验证集结果显示，baseline_finetune_img800_weakaug实验的最佳mAP@0.5:0.95达到0.75852，继续微调实验baseline_finetune_img800_weakaug2达到0.75943，高于基线验证集最佳0.75291。然而在独立测试集上，baseline_finetune_img800_weakaug的mAP@0.5为0.8898、mAP@0.5:0.95为0.7278、Precision为0.8975、Recall为0.8527，除Recall略高于基线外，其余综合指标均低于baseline_mAP_100epochs。这说明高分辨率弱增强微调对验证集定位质量有一定帮助，但该收益没有完全泛化到测试集，最终模型选择仍应以基线模型为准。",
        ]),
        ("4.7 训练过程可复现性", [
            "为了保证实验可复现，本文为不同实验分别编写独立训练脚本，包括train_baseline_100epochs.py、train_optimized_attention.py、train_p2.py、train_finetune_img800.py和train_img800_weakaug.py。每个脚本中明确记录模型路径、数据集路径、训练轮数、batch size、输入尺寸、优化器、学习率和数据增强参数。",
            "测试阶段使用test.py统一加载不同权重文件，并在同一数据集配置上计算Precision、Recall、mAP@0.5和mAP@0.5:0.95。统一测试脚本避免了不同实验之间因评估方式不一致导致的结果偏差。对于训练结果，本文同时保存results.csv和args.yaml，便于后续查看每轮指标变化和训练参数。",
            "在实际训练过程中，本文还处理了PyTorch 2.6权重加载兼容问题。由于新版本torch.load默认weights_only=True，直接加载Ultralytics旧格式权重可能报错，因此训练和测试脚本中加入兼容补丁，将weights_only设置为False，并添加DetectionModel安全全局对象，确保本地权重能够正常加载。",
        ]),
        ("第5章 系统功能实现", []),
        ("5.1 主界面与资源初始化", [
            "系统主界面由main.py中的MainWindow类负责管理。程序启动后首先加载UI文件和样式表，然后初始化YOLO检测模型、字体资源、定时器和专注度追踪器。为了减少第一次检测的延迟，系统在初始化阶段使用一张空白图像进行模型预热，使模型加载和推理图构建提前完成。",
            "界面按钮通过PyQt5信号与槽机制连接到对应函数。例如图片按钮连接图片选择与检测函数，视频按钮连接视频文件选择函数，摄像头按钮连接摄像头开关函数，保存按钮连接结果保存函数。通过这种事件驱动方式，用户操作能够触发相应检测流程，界面逻辑清晰。",
            "系统在界面上设置检测结果显示区域、结果表格和统计标签。检测图像通过QLabel显示，表格用于展示检测目标的详细信息，统计标签用于显示人数和班级专注度。为了增强可读性，系统还对按钮、表格和主窗口背景进行了简单美化，使整体界面更加清晰。",
        ]),
        ("5.2 图片检测功能实现", [
            "图片检测是系统最基础的功能。用户点击图片按钮后，系统通过QFileDialog打开文件选择窗口，支持选择常见图片格式。获得图片路径后，系统调用YOLO模型进行推理，得到检测结果对象。该对象包含检测框坐标、类别编号和置信度等信息。",
            "系统将检测框坐标转换为整数列表，将类别编号转换为Config.py中定义的类别名称，将置信度转换为百分比格式。随后，系统调用results.plot生成带检测框的图像，并将其转换为界面可显示格式。与此同时，系统更新结果表格，显示每个目标的序号、类别、置信度和坐标。",
            "图片检测完成后，系统调用静态专注度计算函数，根据检测目标的行为类别计算班级平均专注度。对于阅读、书写、举手等积极行为赋予较高分值；对于低头赋予中等分值；对于使用手机和趴桌赋予较低分值。最终界面显示检测人数和班级专注度。",
        ]),
        ("5.3 视频与摄像头检测功能实现", [
            "视频检测和摄像头检测均采用逐帧处理方式。系统使用OpenCV的VideoCapture打开视频文件或摄像头设备，并使用QTimer定时触发帧处理函数。每次触发时，程序读取一帧图像，调用YOLO模型进行推理，并更新界面显示。",
            "视频检测需要兼顾处理速度和界面响应。如果在主线程中长时间处理视频，可能导致界面卡顿。本文通过定时器控制帧处理节奏，使界面能够在检测过程中持续响应用户操作。对于保存视频结果等耗时任务，系统使用独立线程处理，降低界面阻塞风险。",
            "摄像头检测与视频检测类似，但输入源为设备编号0。用户点击摄像头按钮后，系统打开默认摄像头并开始实时检测；再次点击则关闭摄像头并释放资源。摄像头检测适用于课堂实时演示，但实际部署时还需要考虑摄像头位置、光照和隐私保护等问题。",
        ]),
        ("5.4 批量检测与结果保存", [
            "批量检测功能用于处理文件夹中的多张图片。用户选择文件夹后，系统遍历其中符合格式要求的图片文件，逐张调用模型进行检测，并将结果图像保存到输出目录。处理过程中系统可显示当前进度，使用户了解批量任务执行情况。",
            "结果保存功能包括单张图片保存和视频结果保存。单张图片保存时，系统会在检测图像上添加班级专注度和人数信息，然后写入本地磁盘。视频保存时，系统需要逐帧检测并写入新视频文件，因此耗时较长，使用线程执行更加合理。保存功能提高了系统结果的可追溯性，便于后续论文展示和教学分析。",
            "为了支持中文显示，系统使用PIL字体在图片上绘制中文文本。OpenCV原生putText对中文支持较弱，容易出现乱码或无法显示的问题。通过PIL绘制后再转换为OpenCV图像，可以稳定显示“班级专注度”“人数”等中文内容。",
        ]),
        ("5.5 专注度计算模块实现", [
            "专注度计算模块是本文系统相较于普通目标检测程序的重要扩展。普通检测程序只输出目标框和类别，而课堂应用更关心这些行为反映出的学习状态。因此，系统将行为类别映射为基础专注度分值，并结合置信度、时序稳定性和趋势变化计算最终专注度。",
            "在静态图片中，专注度计算较简单。系统遍历所有检测目标，根据类别名称调用calculate_single_focus函数得到基础分，再计算平均值。若图片中没有检测目标，则专注度返回0或提示无检测结果。该方法直观易懂，适合单张图片分析。",
            "在视频流中，单帧结果容易受到误检、漏检和目标短暂遮挡影响。因此系统设计FocusTracker类，记录最近若干帧目标状态。该类通过目标框中心点距离匹配同一目标，维护每个目标的历史分数。当某目标连续低专注时增加惩罚，避免偶然检测结果造成误判；当班级整体专注度变化时，使用趋势缓冲平滑输出。",
        ]),
    ]

    for title, paras in remaining:
        if title.startswith("第"):
            parts.append(h(title, 1)); md.append(f"\n# {title}")
            continue
        add_section(parts, md, title, paras, 2)
        if title == "4.1 数据集格式与类别定义":
            parts.append(p("表4-1 训练集类别分布", "center", False, 20, False))
            parts.append(table([["类别编号", "类别名称", "训练集标注数量"], ["0", "hand-raising", "8083"], ["1", "reading", "13553"], ["2", "writing", "5183"], ["3", "using phone", "7472"], ["4", "bowing the head", "1017"], ["5", "leaning over the table", "1099"]]))
        if title == "4.3 基线模型训练方案":
            parts.append(image_para(figure_rids["图4-1_模型训练与评估流程图.png"], "图4-1", 2))
            parts.append(p("图4-1 模型训练与评估流程图", "center", False, 20, False))
        if title == "5.1 主界面与资源初始化":
            parts.append(image_para(figure_rids["图5-3_系统软件模块结构图.png"], "图5-3", 5))
            parts.append(p("图5-3 系统软件模块结构图", "center", False, 20, False))
        if title == "5.2 图片检测功能实现":
            parts.append(image_para(figure_rids["图5-1_系统检测业务流程图.png"], "图5-1", 3))
            parts.append(p("图5-1 系统检测业务流程图", "center", False, 20, False))
        if title == "5.5 专注度计算模块实现":
            parts.append(image_para(figure_rids["图5-2_课堂专注度计算流程图.png"], "图5-2", 4))
            parts.append(p("图5-2 课堂专注度计算流程图", "center", False, 20, False))

    # Chapter 6 and 7
    ch6_sections = [
        ("第6章 实验结果与分析", []),
        ("6.1 实验环境与评价指标", [
            "本文实验在本地Python环境中完成，主要依赖PyTorch、Ultralytics YOLO、OpenCV、PyYAML、scipy等库。模型权重包括yolov8m.pt、yolov8l.pt等预训练文件，其中主要实验采用YOLOv8m。训练结果保存在runs/detect目录下，每个实验对应独立子目录，便于查看参数和指标。",
            "评价指标包括Precision、Recall、mAP@0.5和mAP@0.5:0.95。Precision越高，说明模型预测结果中误检越少；Recall越高，说明真实目标被检出的比例越高。mAP@0.5更关注整体检测是否命中目标，mAP@0.5:0.95则对定位精度要求更高。课堂行为检测既需要识别行为类别，也需要准确定位学生区域，因此需要综合分析这些指标。",
        ]),
        ("6.2 测试集结果对比", [
            "表6-1展示了主要模型在测试集上的检测结果。YOLOv8m基线模型取得mAP@0.5为0.8961、mAP@0.5:0.95为0.7382、Precision为0.9032、Recall为0.8512的结果。该模型在准确率和召回率之间较为平衡，是当前系统最适合采用的主模型。",
            "轻量注意力模型和P2检测头模型均未超过基线。optimized_attention_light_m_pretrained的mAP@0.5为0.8353，yolov8m_p2_100epochs的mAP@0.5为0.8377，二者均低于基线约6个百分点。这说明模型结构改动并不一定带来性能提升，尤其是在数据集规模有限且预训练权重迁移不完全的情况下，新增结构可能破坏原有特征表达。",
            "高分辨率弱增强微调模型在测试集上的mAP@0.5为0.8898，mAP@0.5:0.95为0.7278，Precision为0.8975，Recall为0.8527。该结果最接近基线，并且Recall比基线高0.0015，但mAP@0.5、mAP@0.5:0.95和Precision均有所下降。因此，本文不将该实验描述为测试集性能提升，而是将其作为训练策略消融和后续优化方向进行分析。",
            "在不重新训练模型的情况下，本文进一步测试了基线权重在imgsz=800下的推理效果，实验目录为runs/detect/baseline_test_img800。结果显示，该策略取得mAP@0.5为0.8998、mAP@0.5:0.95为0.7300、Precision为0.8862、Recall为0.8614。与原始imgsz=640基线相比，mAP@0.5提升0.0037，Recall提升0.0102，说明更高输入分辨率有助于检测更多目标；但Precision下降0.0170，mAP@0.5:0.95下降0.0082，说明高分辨率推理也可能带来更多低质量检测框或定位偏差。",
        ]),
        ("6.3 验证集训练策略结果", [
            "在训练策略优化实验中，baseline_finetune_img800_weakaug从基线best.pt出发，以imgsz=800进行弱增强微调。验证集结果显示，其最佳mAP@0.5:0.95达到0.75852；继续微调版本baseline_finetune_img800_weakaug2达到0.75943，均高于基线验证集最佳0.75291。虽然mAP@0.5没有明显提升，但更严格的mAP@0.5:0.95提高，说明边界框定位质量在验证集上有所改善。",
            "需要注意的是，该验证集收益没有在最新测试集结果中同步体现。微调模型测试集mAP@0.5:0.95为0.7278，低于基线0.7382，说明该策略可能更贴合验证集分布，存在一定泛化差距。对于课堂行为检测这类场景固定、目标细节重要的数据集，弱增强和高分辨率仍具有参考价值，但后续需要结合更多测试样本、类别均衡和更稳健的超参数搜索验证其有效性。",
        ]),
        ("6.4 结果可视化与系统测试", [
            "系统测试包括图片检测、视频检测、摄像头检测、批量检测和结果保存。图片检测能够正确显示行为类别和检测框；视频检测能够逐帧更新结果并记录专注度变化；摄像头检测能够实时采集画面并进行推理；批量检测能够自动处理文件夹中的多张图片。",
            "从系统运行效果看，YOLOv8m模型能够在普通GPU环境下完成较流畅推理。界面表格能够显示每个目标的类别、置信度和坐标，图像区域能够显示检测框和标签。保存功能能够输出带有中文专注度信息的结果图片，满足论文展示和实际分析需求。",
        ]),
        ("6.5 实验结论", [
            "综合实验结果，本文得到以下结论：第一，YOLOv8m基线模型在测试集上具有最稳定的综合性能，应作为系统默认检测模型；第二，简单增加注意力模块或P2检测头并未提升性能，说明结构改进需要结合数据规模和预训练权重迁移充分设计；第三，高分辨率弱增强微调能够改善验证集定位指标，但测试集综合指标未超过基线，后续仍需进一步验证其泛化能力；第四，基线权重直接采用imgsz=800推理可以将mAP@0.5提升到0.8998、Recall提升到0.8614，适合更重视目标检出率的离线分析场景；第五，将检测结果与专注度计算结合，能够增强系统应用价值。",
        ]),
        ("第7章 总结与展望", []),
        ("7.1 全文总结", [
            "本文设计并实现了一套基于YOLOv8的学生课堂行为检测系统。围绕课堂行为识别任务，本文完成了数据集配置、模型训练、改进实验、系统开发和结果分析。系统能够识别举手、阅读、书写、使用手机、低头、趴桌六类行为，并支持图片、视频、摄像头和批量检测。",
            "在算法实验方面，本文首先训练YOLOv8m基线模型，并取得较稳定的测试集综合结果。随后尝试轻量ECA注意力、P2小目标检测头和高分辨率弱增强微调，但三类训练或结构改进在测试集上均未全面超过基线。进一步分析后发现，微调策略虽然在验证集mAP@0.5:0.95上取得提升，但测试集mAP和Precision下降；而基线权重直接进行imgsz=800推理时，mAP@0.5和Recall超过原始基线，但Precision和mAP@0.5:0.95下降。因此本文最终选择baseline_mAP_100epochs作为系统默认模型，同时将imgsz=800推理作为高召回离线分析方案。通过这些实验，本文不仅获得了可用于系统的检测模型，也总结了当前数据条件下模型优化的边界和后续方向。",
            "在系统实现方面，本文基于PyQt5构建桌面端界面，基于OpenCV处理图像和视频输入，基于Ultralytics YOLO完成模型推理，并设计专注度计算方法。系统功能完整，能够完成从输入选择、模型检测、结果展示到结果保存的完整流程，具有一定应用价值。",
        ]),
        ("7.2 不足与展望", [
            "本文仍存在一些不足。首先，数据集中类别分布不均衡，低头和趴桌类别样本较少，模型对少数类的识别能力仍有提升空间。后续可通过补充采集、定向增强和类别均衡采样改善这一问题。其次，当前专注度计算主要基于规则设计，虽然直观可解释，但仍带有经验性。后续可结合人工评分数据，训练更加客观的专注度评估模型。",
            "再次，系统目前主要在本地桌面端运行，部署范围有限。后续可考虑将模型导出为ONNX或TensorRT格式，提高推理速度，并开发Web端或移动端应用，使系统更容易在真实课堂中部署。最后，课堂行为检测还可以结合人体姿态估计、目标跟踪和多摄像头融合等技术，进一步提升复杂遮挡场景下的识别能力。",
        ]),
    ]
    for title, paras in ch6_sections:
        if title.startswith("第"):
            parts.append(h(title, 1)); md.append(f"\n# {title}")
            continue
        add_section(parts, md, title, paras, 2)
        if title == "6.2 测试集结果对比":
            parts.append(p("表6-1 不同模型测试集结果对比", "center", False, 20, False))
            parts.append(table([["模型", "mAP@0.5", "mAP@0.5:0.95", "Precision", "Recall"], ["baseline_mAP_100epochs", "0.8961", "0.7382", "0.9032", "0.8512"], ["optimized_attention_light_m_pretrained", "0.8353", "0.6534", "0.8090", "0.8114"], ["yolov8m_p2_100epochs", "0.8377", "0.6547", "0.8130", "0.8005"], ["baseline_finetune_img800_weakaug", "0.8898", "0.7278", "0.8975", "0.8527"], ["baseline_test_img800", "0.8998", "0.7300", "0.8862", "0.8614"]]))
            parts.append(image_para(figure_rids["图6-1_主要模型测试指标对比图.png"], "图6-1", 6))
            parts.append(p("图6-1 主要模型测试指标对比图", "center", False, 20, False))
        if title == "6.3 验证集训练策略结果":
            parts.append(p("表6-2 训练策略优化验证集结果", "center", False, 20, False))
            parts.append(table([["实验名称", "训练轮数", "最佳mAP@0.5", "最佳mAP@0.5:0.95", "说明"], ["baseline_mAP_100epochs", "100", "0.91551", "0.75291", "YOLOv8m基线"], ["baseline_finetune_img800_weakaug", "25", "0.91402", "0.75852", "高分辨率弱增强微调"], ["baseline_finetune_img800_weakaug2", "29", "0.91402", "0.75943", "继续微调实验"]]))

    extra_sections = [
        ("6.6 数据预处理影响分析", [
            "数据预处理是目标检测任务中容易被忽视但非常关键的环节。对于课堂行为检测而言，图像来源可能包括固定摄像头、手机拍摄、网络公开数据或人工整理的课堂截图，不同来源在分辨率、亮度、拍摄角度和压缩质量上存在差异。如果直接将这些数据混合训练，模型可能会学习到与行为无关的成像特征，从而影响泛化能力。因此，在训练前应尽量保证数据路径规范、标签格式一致、无效图片和空标签得到合理处理。",
            "本文数据集采用YOLO格式，标签中的坐标均为归一化坐标。训练前需要检查标签类别编号是否超出范围，检查标签行是否存在缺失字段，检查图片与标签文件是否一一对应。若图片存在但标签缺失，模型可能将该图视为无目标样本；若标签存在但图片缺失，训练过程可能报错。通过规范数据目录结构，可以减少训练过程中的不确定性。",
            "课堂图片中存在大量多人目标，同一张图中可能出现几十个学生行为框。对于这类密集目标，如果标注框过小或边界不准确，会直接影响定位指标mAP@0.5:0.95。本文在分析结果时发现，高分辨率微调在验证集mAP@0.5:0.95上有提升，但测试集未超过基线，说明更清晰的输入可能有助于定位，但其效果会受到测试分布和标注一致性的影响。因此后续数据预处理也可考虑统一图片质量、减少过度压缩，并对小目标类别进行重点复核。",
            "此外，数据集中不同类别数量差异较大，reading类别数量明显多于bowing the head和leaning over the table。类别不均衡不仅会影响分类分支学习，也会影响专注度统计结果的可靠性。后续若继续优化数据集，可优先补充低头、趴桌和使用手机等低专注行为样本，使模型对课堂异常或低专注行为更加敏感。",
        ]),
        ("6.7 数据增强策略讨论", [
            "数据增强可以提升模型对复杂环境的适应能力，但增强强度需要与应用场景匹配。YOLO训练中常用的mosaic增强会将多张图片拼接在一起，能够增加目标尺度变化和背景组合，提高模型鲁棒性。然而课堂场景具有较强空间规律，例如学生通常排列在教室座位上，过强mosaic可能生成不符合真实课堂结构的图像，从而干扰模型后期收敛。",
            "mixup增强通过图像混合生成训练样本，可以缓解过拟合，但对于课堂行为检测中的细粒度动作，混合图像可能使手部、手机和头部姿态变得模糊。copy-paste增强将目标复制到其他图像中，也可能破坏课堂空间关系。本文基线训练使用了一定强度的mosaic、mixup和copy-paste，而微调阶段关闭这些强增强后，验证集定位指标得到提升，但测试集综合结果没有同步提升。这说明后期训练更贴近真实分布是值得尝试的方向，但不能只依据验证集单项指标判断模型优劣。",
            "颜色增强对课堂场景仍然有必要。不同教室光照条件、摄像头白平衡和屏幕反光会导致颜色差异，适度HSV扰动可以提升模型对光照变化的鲁棒性。但颜色扰动不宜过强，否则可能改变学生服装、桌面和背景的自然外观。本文微调脚本中降低了hsv_s和hsv_v，保留轻微颜色变化，同时减少不真实样本。",
            "尺度缩放和平移增强有助于模型适应不同拍摄距离和学生位置。课堂摄像头可能安装在教室前方、后方或侧方，同一行为在图像中的尺度和位置会发生变化。本文微调阶段将scale和translate设置为较低值，既保留一定几何扰动，又避免目标被过度裁切。总体看，数据增强不是越强越好，而应结合实际场景进行调节。",
        ]),
        ("6.8 训练参数选择依据", [
            "训练参数直接影响模型收敛速度和最终效果。本文基线训练初始学习率设置为0.0005，优化器采用AdamW。AdamW在权重衰减处理上与传统Adam有所区别，能够在一定程度上改善泛化能力。对于自定义数据集，过高学习率可能破坏预训练特征，过低学习率又可能收敛缓慢，因此需要在稳定性和收敛速度之间平衡。",
            "batch size受到显存限制影响。基线模型使用batch size为8，P2模型和高分辨率微调使用batch size为4。batch size减小会增加梯度噪声，有时有助于泛化，但也可能导致训练不稳定。为了弥补高分辨率带来的显存开销，微调实验降低batch size，并采用较低学习率，使训练过程更加平稳。",
            "输入尺寸是影响小目标检测的重要参数。imgsz=640是YOLO常用默认设置，训练速度较快；imgsz=800能够保留更多局部细节，有助于手机、手部和低头区域检测，但显存开销和推理时间也会增加。本文实验显示，提高输入尺寸并进行弱增强微调可以提升验证集mAP@0.5:0.95，但测试集mAP@0.5:0.95从基线的0.7382下降到0.7278，说明该策略对定位质量的帮助还需要更稳健的测试验证。",
            "训练轮数方面，基线训练设置为100轮，微调实验设置为50轮并使用patience控制早停。对于从预训练权重开始的模型，100轮通常足以完成收敛；对于从强基线继续微调的模型，过多轮数可能导致过拟合，因此采用较少轮数和较低学习率更合理。训练轮数的设置应结合results.csv中的指标曲线判断，而不是固定追求更长训练。",
        ]),
        ("6.9 模型误差来源分析", [
            "课堂行为检测的误差来源主要包括遮挡、目标尺度小、类别外观相似、标注边界不一致和光照变化。遮挡是课堂场景中最常见的问题，前排学生、桌椅或其他物体可能遮挡后排学生身体，使模型难以判断其具体行为。尤其是低头和阅读在视觉上可能非常相似，若只看到头部和书本区域，模型容易混淆。",
            "小目标问题主要体现在使用手机和举手行为中。手机在课堂图像中面积较小，且可能被手部遮挡或与桌面颜色接近；举手行为虽然动作明显，但手部区域较细，远距离拍摄时可能只占很少像素。P2检测头理论上有助于小目标检测，但本文实验未提升，说明仅增加检测尺度不足以解决问题，还需要更高质量的小目标标注和更合适的训练策略。",
            "类别外观相似也是重要误差来源。阅读和书写都可能表现为学生低头看桌面，二者区别可能只在手部动作和纸笔位置；低头和趴桌也存在连续变化，标注时边界可能不够清晰。如果标注人员对类别定义理解不一致，模型学习到的类别边界也会模糊。后续可通过制定更严格的标注规范和复核机制改善这一问题。",
            "光照和拍摄角度也会影响检测效果。教室中可能存在窗户强光、投影仪暗光、摄像头逆光等情况，学生脸部和手部细节可能不清晰。侧后方拍摄时，部分行为特征被遮挡，正面拍摄时则可能更容易识别表情和头部姿态。因此，实际部署时应合理选择摄像头位置，并尽量保证画面清晰稳定。",
        ]),
        ("6.10 系统测试用例设计", [
            "为了验证系统功能完整性，本文设计了多类测试用例。图片检测测试选择包含单人、多人与无明显目标的图片，检查系统是否能够正常显示检测结果、目标数量、类别名称和专注度。对于无检测目标的图片，系统应避免访问空列表导致错误，并给出合理提示或显示默认值。",
            "视频检测测试选择不同长度和不同分辨率的视频，检查系统是否能够正常打开视频、逐帧检测、显示结果并在视频结束时释放资源。测试过程中需要关注界面是否卡顿、检测结果是否实时更新、视频结束后是否能计算平均专注度。若视频文件损坏或路径为空，系统应能够提示用户重新选择。",
            "摄像头测试主要检查设备调用和释放逻辑。用户点击摄像头按钮后，系统应打开默认摄像头并开始检测；再次点击后，应停止定时器并释放VideoCapture资源。如果摄像头被其他程序占用，系统应避免崩溃并提示用户。摄像头检测还应关注长时间运行稳定性，避免内存持续增长。",
            "批量检测测试选择包含多种格式图片的文件夹，检查系统是否能过滤非图片文件、逐张处理图片并保存结果。结果保存测试则检查输出路径是否正确、文件名是否重复、中文专注度文字是否正常绘制。通过这些测试，可以验证系统在常见使用场景下的可靠性。",
        ]),
        ("6.11 系统性能与可用性分析", [
            "系统性能主要受模型大小、输入分辨率、硬件环境和界面刷新频率影响。YOLOv8m相较于YOLOv8n和YOLOv8s具有更高精度，但推理速度较慢；相较于YOLOv8l和YOLOv8x又具有更低计算开销。因此本文选择YOLOv8m作为折中方案，既保证检测效果，又便于在普通实验环境中运行。",
            "输入分辨率提高会增加推理时间。最新测试结果显示，imgsz=800微调模型虽然Recall略高，但mAP@0.5、mAP@0.5:0.95和Precision均低于基线模型；而基线权重直接采用imgsz=800推理时，mAP@0.5和Recall有所提高，但Precision和mAP@0.5:0.95下降。因此本文系统默认采用imgsz=640的baseline_mAP_100epochs权重，以保证实时性和误检控制；当应用场景更重视漏检控制和离线分析时，可将推理尺寸提高到800。系统保留模型路径和推理参数配置，也便于后续在获得更好权重后进行切换。",
            "可用性方面，桌面界面降低了模型使用门槛。用户无需记忆命令行参数，只需点击按钮即可完成检测。检测结果同时以图像和表格形式展示，既直观又便于查看详细数据。保存功能使结果能够用于报告、教学反馈或后续分析。对于本科毕业设计而言，这种完整交互系统比单纯训练模型更能体现工程实现能力。",
            "系统仍有进一步优化空间。例如，视频检测可加入跳帧策略以提高速度；表格结果可支持导出CSV；专注度曲线可实时绘制；模型加载可加入进度提示；摄像头检测可支持选择不同设备编号。这些优化能够提升系统在真实使用中的体验。",
        ]),
        ("6.12 隐私与应用边界讨论", [
            "课堂行为检测系统涉及学生图像和行为数据，实际应用时必须重视隐私保护。系统采集的视频和图片可能包含学生面部、座位位置和课堂表现等敏感信息，若管理不当可能造成隐私泄露。因此在真实部署前，应明确数据采集目的、使用范围、保存周期和访问权限，并取得学校、教师、学生和家长的知情同意。",
            "本文系统主要用于教学研究和毕业设计演示，不应将检测结果直接作为评价学生个人表现的唯一依据。模型检测存在误差，专注度计算也带有规则假设，若直接用于惩罚或排名，可能产生不公平结果。更合理的应用方式是将系统作为教师观察课堂状态的辅助工具，为教学改进提供参考，而不是替代教师判断。",
            "系统还应注意算法偏差问题。不同座位、不同光照、不同服装和不同拍摄角度可能导致识别效果差异。如果某些学生长期处于画面边缘或被遮挡，系统对其行为判断可能不稳定。因此在使用检测结果时，应结合具体课堂环境进行解释，避免过度依赖单一技术指标。",
            "未来若系统进入真实课堂应用，可考虑在本地设备上完成推理，减少原始图像上传；保存结果时尽量只保存统计信息或模糊化图像；对数据访问设置权限；对模型输出进行人工复核。这些措施有助于在技术应用和隐私保护之间取得平衡。",
        ]),
        ("6.13 与传统课堂观察方法比较", [
            "传统课堂观察方法通常由教师或教研人员记录学生行为。这种方法的优点是观察者能够结合课堂语境理解学生行为，例如某个学生低头可能是在阅读教材，也可能是在使用手机；教师能够根据教学内容、提问互动和学生表情综合判断专注度。其缺点是记录工作量大、难以覆盖全体学生，并且结果容易受到主观因素影响。",
            "本文系统的优势在于自动化和可量化。模型可以在较短时间内处理大量图片或视频帧，输出每个目标的位置、类别和置信度，并进一步计算班级专注度。系统结果可保存、可复查，适合进行长期课堂状态统计。对于大班课堂或录播课堂，自动检测能够显著降低人工分析成本。",
            "然而，自动检测系统也不能完全替代人工观察。模型只能根据视觉特征判断行为类别，难以理解教学语境和学生心理状态。例如学生低头可能是在认真做笔记，也可能是在走神；举手可能表示积极参与，也可能只是伸展动作。因此，系统输出应作为辅助信息，与教师经验和课堂实际情况结合使用。",
            "综合来看，人工观察和自动检测各有优势。未来更理想的课堂分析模式是人机协同：系统负责连续记录和初步统计，教师负责结合教学目标进行解释和决策。本文系统为这种人机协同课堂分析提供了一个基础实现。",
        ]),
        ("6.14 后续实验优化路线", [
            "根据本文实验结果，后续模型优化应优先从数据和训练策略入手。首先，可补充少数类样本，尤其是bowing the head和leaning over the table类别。补充样本时应覆盖不同座位、不同拍摄角度、不同光照和不同遮挡情况，使模型学习到更稳定的类别特征。",
            "其次，可进行类别定向增强。对于使用手机等小目标类别，可以对包含手机的图像进行适度裁剪放大、清晰度增强或局部复制，但需要避免生成不真实样本。对于低头和趴桌类别，可以增加相似负样本，帮助模型区分阅读、书写和低头之间的细微差异。",
            "再次，可尝试更系统的超参数搜索。例如在imgsz=800基础上比较batch size、学习率、cls权重、mosaic强度和close_mosaic轮数的影响；也可尝试YOLOv8l作为容量上限实验，判断性能瓶颈来自模型容量还是数据质量。若YOLOv8l仍无明显提升，则说明主要瓶颈可能在数据和标注。",
            "最后，可引入时序信息进行行为稳定性判断。当前YOLO模型逐帧检测，视频中的行为连续性只在专注度计算中使用。后续可结合目标跟踪算法或轻量时序模型，对同一学生的连续行为进行分析，减少单帧误检对结果的影响。",
        ]),
        ("7.3 工程部署展望", [
            "从工程部署角度看，当前系统仍处于本地桌面端原型阶段。若要在真实教学环境中推广，需要进一步考虑模型推理速度、硬件成本、系统稳定性和维护便利性。可以将模型导出为ONNX或TensorRT格式，在支持GPU加速的设备上提高推理速度，也可以训练更轻量的YOLOv8s模型用于低算力设备。",
            "系统架构也可以从桌面端扩展到Web端。Web端部署后，教师可通过浏览器上传课堂视频或查看分析结果，学校也可将多个课堂数据集中管理。后端负责模型推理和数据存储，前端负责结果展示和统计图表。这种架构更适合多用户和多班级场景，但也对服务器性能和数据安全提出更高要求。",
            "对于实时课堂监测，可考虑边缘计算方案，即在教室本地设备上完成视频采集和模型推理，只上传统计结果而不上传原始视频。这样既能降低网络压力，也有助于保护学生隐私。边缘端设备可根据实际需求选择小型GPU主机、嵌入式AI设备或高性能工控机。",
            "系统后续还可以加入数据库模块，保存每节课的检测统计结果、专注度变化曲线和异常行为片段。通过长期数据积累，可以分析不同课程、不同时间段和不同教学方式下的课堂状态变化，为教学研究提供更丰富的数据基础。",
        ]),
        ("7.4 研究创新点归纳", [
            "本文的创新点主要体现在三个方面。第一，面向课堂行为检测场景构建了较完整的YOLOv8训练与评估流程，不仅训练了基线模型，还对注意力机制、P2检测头和训练策略优化进行了对比实验，分析了不同方案在本项目数据集上的实际效果。",
            "第二，本文将目标检测结果与课堂专注度计算结合起来，设计了基于行为类别、检测置信度、时序惩罚和趋势缓冲的专注度计算方法。该方法虽然仍属于规则模型，但具有较好的可解释性，能够将检测框结果转化为更符合教学应用需求的课堂状态指标。",
            "第三，本文完成了桌面端可视化系统开发，实现图片、视频、摄像头、批量检测和结果保存等功能。相比单纯训练模型，完整系统能够更直观地展示研究成果，也更接近实际应用流程。这种算法实验与工程系统结合的方式体现了较强的综合实践价值。",
        ]),
        ("7.5 核心代码实现说明", [
            "本项目代码组织较为清晰，主要由训练脚本、测试脚本、系统主程序和工具模块构成。训练脚本负责模型训练和实验复现，测试脚本负责统一评估不同模型权重，main.py负责桌面端业务逻辑，detect_tools.py负责图像处理和保存辅助函数，Config.py负责系统配置。这样的组织方式使模型训练和系统运行相互独立，便于调试和维护。",
            "在训练脚本中，train_baseline_100epochs.py是最重要的基线训练文件。该脚本从yolov8m.pt加载预训练权重，设置数据集路径、训练轮数、batch size、输入尺寸、优化器和数据增强参数，并将训练结果保存到runs/detect/baseline_mAP_100epochs目录下。由于该实验在测试集上具有较稳定的综合表现，并且不需要额外推理开销，因此也是系统默认推荐使用的模型来源。",
            "train_optimized_attention.py用于注意力机制实验。该脚本与普通训练脚本不同，需要先根据自定义yaml构建模型，再通过层号映射加载yolov8m.pt中的可迁移权重。这样做的原因是插入注意力层后模型层号发生变化，若直接加载权重，部分参数无法匹配。通过显式映射，可以尽可能复用原模型的预训练知识。",
            "train_p2.py用于P2小目标检测头实验。该脚本构建带P2检测分支的YOLOv8m模型，并迁移Backbone、Neck以及原有P3/P4/P5检测分支权重。新增P2分支随机初始化。虽然该实验最终未超过基线，但其实现过程体现了对YOLO模型结构和权重迁移机制的理解。",
            "test.py用于统一测试。该脚本以字典形式维护不同模型名称和权重路径，逐个加载模型并在测试集上调用model.val计算指标。统一测试脚本能够避免手动测试时路径写错或参数不一致的问题。本文前期实验中曾发现模型标签与路径不一致的问题，后续通过修正test.py保证了实验对比的可靠性。",
        ]),
        ("7.6 文件组织与结果管理", [
            "项目根目录下保存了模型权重、训练脚本、测试脚本、系统主程序、数据集目录和运行结果目录。datasets目录保存学生课堂行为检测数据集，其中images目录存放图片，labels目录存放YOLO格式标签，data.yaml提供训练框架需要的数据路径和类别名称。runs/detect目录保存每次训练或验证产生的结果。",
            "每个训练结果目录通常包含args.yaml、results.csv、weights文件夹和若干可视化图片。args.yaml记录训练参数，例如模型路径、数据集路径、轮数、输入尺寸、优化器、学习率和数据增强参数。results.csv记录每轮训练损失、验证损失和评价指标，是分析模型收敛趋势的重要依据。weights目录中的best.pt和last.pt分别表示最佳权重和最后一轮权重。",
            "在论文实验分析中，不能只依赖终端输出，还应结合results.csv查看每轮指标变化。例如baseline_mAP_100epochs在第86轮取得最佳mAP@0.5，在第90轮取得最佳mAP@0.5:0.95；baseline_finetune_img800_weakaug2在第28轮取得最佳mAP@0.5:0.95。通过这些信息可以更准确地描述模型训练过程。",
            "结果管理还涉及命名规范。本文为不同实验设置独立run name，例如baseline_mAP_100epochs、optimized_attention_light_m_pretrained、yolov8m_p2_100epochs和baseline_finetune_img800_weakaug。清晰的命名能够减少实验混淆，方便后续复现实验和撰写论文表格。",
        ]),
        ("7.7 界面交互流程说明", [
            "系统界面交互流程围绕用户输入展开。用户首先通过按钮选择检测模式，包括图片检测、视频检测、摄像头检测和批量检测。不同模式虽然输入来源不同，但最终都会调用统一的模型推理接口。这样既减少了重复代码，也保证不同模式下检测逻辑一致。",
            "在图片检测模式下，用户选择图片后系统立即执行推理并更新界面。检测图像显示在主区域，目标信息显示在表格中，专注度显示在统计标签中。用户可以查看单个目标的类别、置信度和坐标，也可以保存带检测框和专注度信息的结果图像。",
            "在视频检测模式下，系统需要连续处理帧图像。为了让用户能够直观看到检测过程，程序每处理一帧就刷新显示区域和统计信息。若视频较长，系统会持续记录每秒专注度，视频结束后计算平均值。这种设计使系统既能展示实时变化，也能给出整体评价。",
            "在摄像头模式下，用户可以打开或关闭实时检测。摄像头输入更接近实际课堂应用，但也更依赖硬件环境和光照条件。系统在关闭摄像头时需要释放设备资源，否则可能导致下次打开失败。本文在_stop_video_capture函数中统一处理资源释放，提高系统稳定性。",
            "批量检测模式适合处理实验图片或课堂截图集合。用户选择文件夹后，系统自动遍历图片并保存结果。该功能减少了重复手动操作，便于在论文中生成多张检测效果图，也便于教师对整批课堂图片进行离线分析。",
        ]),
        ("7.8 答辩展示建议", [
            "在本科毕业设计答辩中，展示内容应突出问题背景、系统功能、模型实验和实际效果。建议首先说明课堂行为检测的研究意义，指出人工观察存在主观性强和效率低的问题；随后介绍系统总体架构图，说明数据输入、模型推理、专注度计算和界面展示之间的关系。",
            "模型实验部分建议重点展示表6-1和图6-1。需要说明本文并非只展示成功实验，也对注意力机制和P2检测头进行了验证。虽然这两种结构改进未超过基线，但它们提供了有价值的消融分析，说明本项目最终选择YOLOv8m基线模型并非随意选择，而是基于实验结果做出的工程决策。",
            "对于训练策略优化，可展示表6-2，说明高分辨率弱增强微调在验证集mAP@0.5:0.95上有所提升，但必须同时说明最新测试集结果没有全面超过基线。还可以补充展示baseline_test_img800结果，说明不重新训练、只提高推理尺寸即可将mAP@0.5提升到0.8998、Recall提升到0.8614。答辩时可以解释为什么不能只看单项指标：mAP@0.5、mAP@0.5:0.95、Precision和Recall需要综合判断，最终系统默认选择baseline_mAP_100epochs，是因为它在实时性、误检控制和定位精度之间更平衡。",
            "系统演示部分建议准备一张图片、一段短视频和摄像头实时检测。演示时先展示图片检测，说明类别和置信度；再展示视频检测，说明专注度随时间变化；最后展示结果保存，说明系统不仅能实时检测，还能输出可追溯结果。若现场设备或环境不稳定，可提前录制演示视频作为备选。",
            "答辩中可能被问到为什么改进模型效果变差。可以回答：新增结构会改变预训练特征分布，新增层随机初始化需要更多数据支撑；当前数据集类别不均衡，简单增加结构不一定有效；高分辨率弱增强微调虽然改善了验证集定位指标，但测试集没有同步提升，说明仍存在泛化差距。最终选择基线模型，体现的是基于测试集证据的工程决策，而不是只追求表面创新。",
        ]),
        ("7.9 论文写作与格式检查要点", [
            "论文最终提交前需要根据学校模板进一步检查格式。封面中的学院、专业班级、姓名、学号、指导教师和完成日期必须填写准确。目录页应在Word中重新更新页码，确保章节标题和页码对应。正文标题层级应保持统一，例如第1章使用一级标题，1.1使用二级标题，1.1.1使用三级标题。",
            "图表需要按章节编号，例如图3-1、图4-1、表6-1等。图题通常放在图下方，表题放在表上方。图表在正文中应提前引用，不能只插入而不解释。本文生成的图表文件位于论文图表目录下，若Word排版中图片位置不合适，可以手动调整大小和环绕方式。",
            "参考文献应按学校要求统一格式。本文初稿列出了YOLO、目标检测、注意力机制、PyTorch、OpenCV和PyQt5相关文献，后续可根据指导教师要求增加中文文献和近三年文献。正文中若引用具体方法，应在相应位置标注文献序号。",
            "实验结果必须与实际运行结果一致。本文使用了你项目中已有的测试集结果和训练CSV结果，包括baseline、注意力模型、P2模型和微调模型。若后续继续训练得到更好结果，应同步更新摘要、实验表格、结果分析和结论部分，避免论文前后数据不一致。",
            "最后需要检查错别字、图表编号、英文摘要、关键词、页眉页脚和行距。由于自动生成文档可能无法完全满足学校Word模板的所有细节，建议用Word打开扩展版docx后，按照规范格式文件逐项核对，并在提交前导出PDF检查排版效果。",
        ]),
    ]
    for title, paras in extra_sections:
        add_section(parts, md, title, paras, 2)

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
    parts.append(h("参考文献", 1)); md.append("\n# 参考文献")
    for r in refs:
        parts.append(p(r, first_line=False)); md.append(r)
    parts.append(h("致    谢", 1)); md.append("\n# 致谢")
    thanks = "在本论文和系统开发完成过程中，指导教师在选题确定、研究思路、系统实现、实验分析和论文撰写等方面给予了耐心指导。项目实现过程中，同学和朋友在环境配置、模型训练、界面测试和问题排查方面提供了帮助。家人在学习和生活上给予了理解与支持。在此向所有关心和帮助过我的老师、同学、朋友和家人表示诚挚感谢。"
    parts.append(p(thanks)); md.append(thanks)

    OUT_MD.write_text("\n\n".join(md), encoding="utf-8")

    try:
        shutil.copyfile(TEMPLATE, OUT_DOCX)
    except PermissionError:
        OUT_DOCX = OUT_DOCX.with_name(f"{OUT_DOCX.stem}_最新实验结果{OUT_DOCX.suffix}")
        shutil.copyfile(TEMPLATE, OUT_DOCX)
    doc_xml = body_xml(parts).encode("utf-8")
    tmp = OUT_DOCX.with_suffix(".tmp.docx")
    with zipfile.ZipFile(OUT_DOCX, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        content_types = zin.read("[Content_Types].xml").decode("utf-8")
        if 'Extension="png"' not in content_types:
            content_types = content_types.replace(
                '<Default Extension="jpeg" ContentType="image/jpeg"/>',
                '<Default Extension="jpeg" ContentType="image/jpeg"/><Default Extension="png" ContentType="image/png"/>',
            )
        rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        insert = "".join(
            f'<Relationship Id="{figure_rids[path.name]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{path.name}"/>'
            for _, path in figs
        )
        rels = rels.replace("</Relationships>", insert + "</Relationships>")
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, doc_xml)
            elif item.filename == "word/_rels/document.xml.rels":
                zout.writestr(item, rels.encode("utf-8"))
            elif item.filename == "[Content_Types].xml":
                zout.writestr(item, content_types.encode("utf-8"))
            else:
                zout.writestr(item, zin.read(item.filename))
        for _, path in figs:
            zout.write(path, f"word/media/{path.name}")
    tmp.replace(OUT_DOCX)


def write_prompts():
    prompt_text = """# gpt-image-2 图像生成提示词

本机当前未设置 OPENAI_API_KEY，因此未实际调用 gpt-image-2。以下提示词可在设置 API key 后用于重新生成更具视觉设计感的论文配图。

## 1. 系统总体架构图
Use case: infographic-diagram
Asset type: undergraduate thesis figure
Primary request: Create a clean Chinese academic system architecture diagram for a YOLOv8 student classroom behavior detection system.
Style/medium: modern flat infographic, white background, blue-green academic palette.
Text (verbatim): “数据输入层”, “模型推理层”, “业务分析层”, “可视化交互层”, “结果管理”, “配置与资源”, “实验支撑”.
Constraints: all Chinese text must be accurate and legible; no watermark; no decorative classroom photo background.

## 2. 模型训练与评估流程图
Use case: infographic-diagram
Asset type: thesis flowchart
Primary request: Generate a Chinese flowchart showing dataset preparation, train/val/test split, parameter configuration, YOLOv8m training, model evaluation, improvement experiments, and result comparison.
Text (verbatim): “原始课堂图片”, “YOLO标签”, “数据集划分”, “参数配置”, “YOLOv8m训练”, “测试评估”, “改进实验”, “结果对比”.
Constraints: clean boxes and arrows, readable Chinese, white background, no watermark.

## 3. 系统检测业务流程图
Use case: infographic-diagram
Asset type: thesis workflow figure
Primary request: Create a workflow diagram for image/video/camera input, frame reading, YOLO inference, result parsing, drawing boxes, concentration calculation, and result saving.
Text (verbatim): “用户选择输入”, “读取图像帧”, “YOLO模型推理”, “解析结果”, “绘制检测框”, “计算专注度”, “保存结果”.
Constraints: academic style, clear arrows, no extra text.

## 4. 课堂专注度计算流程图
Use case: infographic-diagram
Asset type: algorithm flowchart
Primary request: Generate a Chinese algorithm flowchart explaining classroom concentration calculation from detection results, category base score, confidence weighting, object matching, temporal penalty, trend smoothing, and final output.
Text (verbatim): “检测结果输入”, “类别基础分”, “置信度加权”, “目标匹配”, “时序惩罚”, “趋势缓冲”, “输出结果”.
Constraints: readable Chinese labels, professional thesis style.

## 5. 系统软件模块结构图
Use case: infographic-diagram
Asset type: software module diagram
Primary request: Create a module diagram for a Python PyQt5 YOLOv8 project, centered on main.py and connected to Config.py, detect_tools.py, Ultralytics YOLO, UIProgram, train/test scripts, and runs/detect.
Text (verbatim): “main.py”, “Config.py”, “detect_tools.py”, “Ultralytics YOLO”, “UIProgram”, “train/test脚本”, “runs/detect”.
Constraints: no code screenshots, diagram only, clean academic style.
"""
    PROMPTS.write_text(prompt_text, encoding="utf-8")


def main():
    figs = make_figures()
    write_prompts()
    build_doc(figs)
    raw = OUT_MD.read_text(encoding="utf-8")
    cn_chars = len(re.findall(r"[\u4e00-\u9fff]", raw))
    print(OUT_DOCX)
    print(OUT_MD)
    print(FIG_DIR)
    print(f"Chinese characters in markdown: {cn_chars}")


if __name__ == "__main__":
    main()
