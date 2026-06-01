# -*- coding: utf-8 -*-
"""Generate a Word document summarizing five model training strategies."""

from __future__ import annotations

import html
import zipfile
from datetime import datetime
from pathlib import Path


OUT_DOCX = Path("五种模型训练策略总结.docx")


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def run_props(size: int = 24, bold: bool = False, font: str = "宋体") -> str:
    bold_xml = "<w:b/>" if bold else ""
    return (
        f'<w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>'
        f"{bold_xml}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
    )


def paragraph(
    text: str = "",
    *,
    align: str = "both",
    size: int = 24,
    bold: bool = False,
    first_line: bool = True,
) -> str:
    indent = '<w:ind w:firstLine="480"/>' if first_line else ""
    return (
        f'<w:p><w:pPr><w:jc w:val="{align}"/><w:spacing w:line="360" w:lineRule="auto"/>'
        f"{indent}</w:pPr><w:r>{run_props(size, bold)}"
        f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
    )


def heading(text: str, level: int) -> str:
    size = {1: 34, 2: 28, 3: 25}.get(level, 24)
    align = "center" if level == 1 else "left"
    return paragraph(text, align=align, size=size, bold=True, first_line=False)


def bullet(text: str) -> str:
    return paragraph("• " + text, first_line=False)


def table(rows: list[list[object]], widths: list[int] | None = None) -> str:
    if widths is None:
        widths = [2400] * max(len(row) for row in rows)
    xml = [
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/>'
        '<w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/>'
        '<w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/>'
        "</w:tblBorders></w:tblPr>"
    ]
    for row_index, row in enumerate(rows):
        xml.append("<w:tr>")
        for col_index, cell in enumerate(row):
            width = widths[min(col_index, len(widths) - 1)]
            xml.append(f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>')
            xml.append(paragraph(str(cell), align="center", size=20, bold=(row_index == 0), first_line=False))
            xml.append("</w:tc>")
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def body_xml(parts: list[str]) -> str:
    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1200" w:bottom="1440" w:left="1200" w:header="851" w:footer="992" w:gutter="0"/>'
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


def make_docx(doc_xml: str, out_path: Path) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("word/document.xml", doc_xml)


def main() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts: list[str] = []

    parts.append(heading("五种模型训练策略总结", 1))
    parts.append(paragraph(f"生成时间：{now}", align="center", first_line=False))
    parts.append(paragraph(
        "本文档根据项目中的训练脚本、模型配置和 runs/detect 实验目录整理，概括五种主要模型的训练目标、模型来源、参数设置、增强策略和实验定位。"
    ))

    parts.append(heading("一、五种模型总览", 2))
    parts.append(table([
        ["序号", "模型/实验", "对应脚本", "输出目录", "核心策略"],
        ["1", "YOLOv8m 正式基线模型", "train_baseline_100epochs.py", "runs/detect/baseline_mAP_100epochs", "稳定 100 轮迁移训练，作为后续实验对照"],
        ["2", "轻量 ECA 注意力模型", "train_optimized_attention.py", "runs/detect/optimized_attention_light_m_pretrained", "在 P3/P4 加入 ECA，手动迁移可匹配权重"],
        ["3", "YOLOv8m-P2 小目标模型", "train_p2.py", "runs/detect/yolov8m_p2_100epochs", "增加 P2 检测分支，提升小尺度目标感知能力"],
        ["4", "800 分辨率弱增强微调模型", "train_finetune_img800.py", "runs/detect/baseline_finetune_img800_weakaug", "从 baseline best.pt 继续训练，提高分辨率并减弱增强"],
        ["5", "CoordAtt Backbone + ECA Neck 模型", "train_coordatt_backbone_eca_neck.py", "runs/detect/coordatt_backbone_eca_neck_m_pretrained", "Backbone 加 CoordAtt，Neck 加 ECA，保留统一训练超参数"],
    ], widths=[700, 2100, 2300, 2800, 3300]))

    parts.append(heading("二、共同训练基础", 2))
    parts.append(bullet("基础任务：学生课堂行为目标检测，类别数 nc=6。"))
    parts.append(bullet("主干尺度：以 YOLOv8m 为主要模型尺度，兼顾精度和显存开销。"))
    parts.append(bullet("主要评价指标：Precision、Recall、mAP@0.5、mAP@0.5:0.95。"))
    parts.append(bullet("训练设备设置：device='0'，workers=0，便于在 Windows 本地环境稳定运行。"))
    parts.append(bullet("多数 640 分辨率实验统一使用 AdamW、lr0=0.0005、lrf=0.01、patience=30、seed=42，尽量保证公平对比。"))
    parts.append(bullet("大多数结构改进模型设置 pretrained=False，是因为脚本已经通过层号映射手动加载了可迁移的 yolov8m.pt 权重。"))

    parts.append(heading("三、模型一：YOLOv8m 正式基线模型", 2))
    parts.append(table([
        ["项目", "设置"],
        ["训练脚本", "train_baseline_100epochs.py"],
        ["初始权重", "yolov8m.pt，pretrained=True"],
        ["数据配置", "脚本中为 datasets/data_tail_oversampled.yaml；已有 baseline_mAP_100epochs 运行记录 args.yaml 显示为 datasets/data.yaml"],
        ["训练轮数", "epochs=100，patience=30"],
        ["输入尺寸与批量", "imgsz=640，batch=8"],
        ["优化器", "AdamW，lr0=0.0005，lrf=0.01，momentum=0.937，weight_decay=0.0005"],
        ["Warmup", "warmup_epochs=5.0，warmup_momentum=0.8，warmup_bias_lr=0.1"],
        ["增强策略", "hsv_h=0.015，hsv_s=0.5，hsv_v=0.4，degrees=5，translate=0.1，scale=0.3，shear=2，perspective=0.0002，fliplr=0.5，mosaic=0.8，mixup=0.1，copy_paste=0.05，close_mosaic=10"],
        ["损失权重", "box=7.5，cls=0.5，dfl=1.5"],
    ], widths=[2300, 7600]))
    parts.append(paragraph(
        "该模型是整个实验体系的正式对照组。相比早期 train.py，它降低了初始学习率，弱化了过强的数据增强，并在最后 10 个 epoch 关闭 Mosaic，使训练后期更接近真实课堂图像分布。该模型不引入额外结构，推理开销稳定，适合作为系统默认模型。"
    ))

    parts.append(heading("四、模型二：轻量 ECA 注意力模型", 2))
    parts.append(table([
        ["项目", "设置"],
        ["训练脚本", "train_optimized_attention.py"],
        ["模型配置", "ultralytics/cfg/models/v8/yolov8m-optimized-attention.yaml"],
        ["初始权重", "yolov8m.pt"],
        ["结构改进", "在 Backbone 的 P3、P4 特征层后插入 ECA 通道注意力模块"],
        ["权重迁移", "通过 load_yolov8m_weights_by_layer_mapping 按原 YOLOv8m 层号到新模型层号进行映射迁移"],
        ["训练轮数", "epochs=100，patience=30"],
        ["输入尺寸与批量", "imgsz=640，batch=8"],
        ["优化器与增强", "与正式基线基本一致：AdamW，lr0=0.0005，lrf=0.01，mosaic=0.8，mixup=0.1，copy_paste=0.05，close_mosaic=10"],
        ["pretrained 参数", "pretrained=False，因为已经在训练前手动迁移权重"],
    ], widths=[2300, 7600]))
    parts.append(paragraph(
        "该模型的目的在于验证轻量通道注意力是否能提升课堂行为中关键区域的特征选择能力。ECA 参数量较小，理论上不会显著增加计算量。为了避免新增注意力层导致预训练权重无法直接加载，脚本采用显式层映射，只加载形状匹配的原 YOLOv8m 参数。"
    ))

    parts.append(heading("五、模型三：YOLOv8m-P2 小目标模型", 2))
    parts.append(table([
        ["项目", "设置"],
        ["训练脚本", "train_p2.py"],
        ["模型配置", "ultralytics/cfg/models/v8/yolov8m-p2-classroom.yaml"],
        ["初始权重", "yolov8m.pt"],
        ["结构改进", "在原 P3/P4/P5 检测头之外增加 P2/4 小目标检测分支"],
        ["权重迁移", "迁移 Backbone、Neck 和原 P3/P4/P5 检测分支权重；新增 P2 分支随机初始化"],
        ["训练轮数", "epochs=100，patience=30"],
        ["输入尺寸与批量", "imgsz=640，batch=4"],
        ["优化器与增强", "AdamW，lr0=0.0005，lrf=0.01，增强策略与正式基线基本一致"],
        ["训练定位", "针对手机、手部动作、远距离学生行为等小目标识别问题"],
    ], widths=[2300, 7600]))
    parts.append(paragraph(
        "P2 模型通过引入更高分辨率的检测特征图来改善小目标检测能力。由于检测分支增多，显存占用和计算量增加，所以 batch 从 8 降为 4。该策略的关键不是改变数据增强，而是改变检测尺度，使模型能在更细粒度特征上输出目标框。"
    ))

    parts.append(heading("六、模型四：800 分辨率弱增强微调模型", 2))
    parts.append(table([
        ["项目", "设置"],
        ["训练脚本", "train_finetune_img800.py"],
        ["初始权重", "runs/detect/baseline_mAP_100epochs/weights/best.pt"],
        ["数据配置", "datasets/data.yaml"],
        ["训练轮数", "epochs=50，patience=20"],
        ["输入尺寸与批量", "imgsz=800，batch=4"],
        ["优化器", "AdamW，lr0=0.0001，lrf=0.05，cos_lr=True"],
        ["Warmup", "warmup_epochs=2.0，warmup_bias_lr=0.01"],
        ["弱增强策略", "hsv_h=0.01，hsv_s=0.3，hsv_v=0.3，degrees=3，translate=0.05，scale=0.15，shear=1，perspective=0，mosaic=0，mixup=0，copy_paste=0，close_mosaic=0"],
        ["损失权重", "box=7.5，cls=0.65，dfl=1.5"],
    ], widths=[2300, 7600]))
    parts.append(paragraph(
        "该模型不是从 yolov8m.pt 重新训练，而是从正式基线 best.pt 继续训练。它的核心思想是：在已有较好特征的基础上提高输入分辨率，让模型获得更多局部细节；同时降低学习率并关闭强增强，避免破坏已学到的课堂场景分布。cls 权重由 0.5 提高到 0.65，用于强化相似行为类别之间的区分。"
    ))

    parts.append(heading("七、模型五：CoordAtt Backbone + ECA Neck 模型", 2))
    parts.append(table([
        ["项目", "设置"],
        ["训练脚本", "train_coordatt_backbone_eca_neck.py"],
        ["模型配置", "ultralytics/cfg/models/v8/yolov8m-coordatt-backbone-eca-neck.yaml"],
        ["初始权重", "yolov8m.pt"],
        ["结构改进", "Backbone 在 P3、P4 后加入 CoordAtt；Neck 在 P3/P4/P5 融合特征后加入 ECA"],
        ["权重迁移", "通过层号映射加载 shape-compatible 的 YOLOv8m 预训练权重"],
        ["训练轮数", "epochs=100，patience=30"],
        ["输入尺寸与批量", "imgsz=640，batch=8"],
        ["优化器与增强", "AdamW，lr0=0.0005，lrf=0.01，增强策略与正式基线基本一致"],
        ["pretrained 参数", "pretrained=False，因为训练前已手动加载匹配权重"],
    ], widths=[2300, 7600]))
    parts.append(paragraph(
        "该模型属于更完整的注意力组合实验。CoordAtt 用于 Backbone，保留位置信息并增强坐标方向感知；ECA 用于 Neck，强化多尺度融合后的通道选择。该方案相比单纯 ECA 插入点更多，结构变化更大，因此更依赖权重迁移和稳定训练参数。"
    ))

    parts.append(heading("八、策略对比与实验结论", 2))
    parts.append(table([
        ["模型", "主要改进方向", "优点", "潜在问题"],
        ["YOLOv8m 基线", "训练策略稳定化", "结构简单，预训练迁移充分，推理开销稳定", "对小目标和相似动作的细节建模仍有限"],
        ["ECA 注意力", "通道注意力", "参数量小，理论上增强关键通道选择", "新增层随机初始化，测试集未全面超过基线"],
        ["P2 小目标", "增加高分辨率检测头", "更关注小尺度目标", "显存和计算量增加，新分支训练难度更高"],
        ["800 微调", "高分辨率 + 弱增强", "更保留细节，验证集定位指标有提升空间", "推理开销增加，测试集泛化不一定全面超过基线"],
        ["CoordAtt + ECA", "坐标注意力 + 通道注意力组合", "同时考虑空间方向和通道选择", "结构变化更大，对数据量和训练稳定性要求更高"],
    ], widths=[2000, 2200, 3000, 3000]))
    parts.append(paragraph(
        "总体来看，项目训练路线体现了先建立强基线，再分别从注意力机制、小目标检测头和高分辨率微调三个方向进行实验的思路。最终模型选择不能只看理论结构是否复杂，而应以独立测试集综合指标和系统部署需求为准。当前项目中，baseline_mAP_100epochs 的综合稳定性更适合作为默认部署模型；800 分辨率微调可作为离线高精度分析方向；注意力和 P2 实验则为论文提供了结构改进对比和失败原因分析。"
    ))

    make_docx(body_xml(parts), OUT_DOCX)
    print(OUT_DOCX.resolve())


if __name__ == "__main__":
    main()
