# -*- coding: utf-8 -*-
"""Generate a Word document summarizing six YOLOv8 training strategies."""

from __future__ import annotations

import html
import zipfile
from datetime import datetime
from pathlib import Path


OUT_DOCX = Path("六种模型训练策略总结.docx")


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def run_props(size: int = 24, bold: bool = False, font: str = "宋体") -> str:
    bold_xml = "<w:b/>" if bold else ""
    return (
        f'<w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" '
        f'w:eastAsia="{font}" w:cs="{font}"/>{bold_xml}'
        f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>'
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
        f'<w:p><w:pPr><w:jc w:val="{align}"/>'
        f'<w:spacing w:line="360" w:lineRule="auto"/>{indent}</w:pPr>'
        f"<w:r>{run_props(size, bold)}"
        f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
    )


def heading(text: str, level: int) -> str:
    size = {1: 34, 2: 28, 3: 25}.get(level, 24)
    align = "center" if level == 1 else "left"
    return paragraph(text, align=align, size=size, bold=True, first_line=False)


def bullet(text: str) -> str:
    return paragraph("（1）" + text, first_line=False)


def table(rows: list[list[object]], widths: list[int] | None = None) -> str:
    if widths is None:
        widths = [2200] * max(len(row) for row in rows)
    xml = [
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="4"/>'
        '<w:left w:val="single" w:sz="4"/>'
        '<w:bottom w:val="single" w:sz="4"/>'
        '<w:right w:val="single" w:sz="4"/>'
        '<w:insideH w:val="single" w:sz="4"/>'
        '<w:insideV w:val="single" w:sz="4"/>'
        "</w:tblBorders></w:tblPr>"
    ]
    for row_index, row in enumerate(rows):
        xml.append("<w:tr>")
        for col_index, cell in enumerate(row):
            width = widths[min(col_index, len(widths) - 1)]
            xml.append(f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>')
            xml.append(
                paragraph(
                    str(cell),
                    align="center",
                    size=19,
                    bold=(row_index == 0),
                    first_line=False,
                )
            )
            xml.append("</w:tc>")
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def body_xml(parts: list[str]) -> str:
    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1000" w:bottom="1440" '
        'w:left="1000" w:header="851" w:footer="992" w:gutter="0"/>'
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

    parts.append(heading("六种模型训练策略总结", 1))
    parts.append(paragraph(f"生成时间：{now}", align="center", first_line=False))
    parts.append(
        paragraph(
            "本文档根据项目中的训练脚本、模型配置和 runs/detect 实验结果整理，"
            "汇总六种主要模型训练策略的实验目标、模型来源、训练参数、数据增强方式、测试结果和适用场景。"
        )
    )

    parts.append(heading("一、六种模型总览", 2))
    parts.append(
        table(
            [
                ["序号", "模型/实验", "对应脚本", "输出目录", "核心策略"],
                ["1", "YOLOv8m基线模型", "train_baseline_100epochs.py", "baseline_mAP_100epochs", "从yolov8m.pt训练100轮，作为所有改进实验的对照组"],
                ["2", "轻量ECA注意力模型", "train_optimized_attention.py", "optimized_attention_light_m_pretrained", "在部分特征层加入ECA通道注意力，验证轻量注意力效果"],
                ["3", "YOLOv8m-P2小目标模型", "train_p2.py", "yolov8m_p2_100epochs", "增加P2检测分支，提高小目标感知能力"],
                ["4", "800分辨率弱增强微调模型", "train_finetune_img800.py", "baseline_finetune_img800_weakaug", "从baseline best.pt继续训练，提高输入分辨率并关闭强增强"],
                ["5", "CoordAtt+ECA组合注意力模型", "train_coordatt_backbone_eca_neck.py", "coordatt_backbone_eca_neck_m_pretrained", "Backbone加入CoordAtt，Neck加入ECA"],
                ["6", "Strong高精度最终模型", "train_strong_img800_tail_weakaug.py", "strong_img800_tail_weakaug", "长尾均衡训练集+800分辨率+弱增强+二阶段微调"],
            ],
            widths=[600, 1900, 2300, 2600, 3800],
        )
    )

    parts.append(heading("二、统一实验基础", 2))
    common_points = [
        "检测任务为学生课堂行为目标检测，共6类：举手、阅读、书写、使用手机、低头、趴桌。",
        "主要模型尺度为YOLOv8m，在精度、显存占用和推理速度之间相对平衡。",
        "评价指标包括Precision、Recall、mAP@0.5和mAP@0.5:0.95，其中mAP@0.5:0.95对定位质量要求更严格。",
        "多数实验使用AdamW优化器、AMP混合精度、seed=42，并将训练结果保存到runs/detect下的独立目录。",
        "结构改进模型使用手动权重迁移，尽可能加载yolov8m.pt中shape-compatible的预训练参数。",
    ]
    for point in common_points:
        parts.append(paragraph(point))

    parts.append(heading("三、训练策略详细说明", 2))
    strategy_tables = [
        (
            "1. YOLOv8m基线模型",
            [
                ["项目", "设置"],
                ["训练脚本", "train_baseline_100epochs.py"],
                ["初始权重", "yolov8m.pt"],
                ["训练轮数", "epochs=100，patience=30"],
                ["输入尺寸/批量", "imgsz=640，batch=8"],
                ["优化器", "AdamW，lr0=0.0005，lrf=0.01，weight_decay=0.0005"],
                ["增强策略", "HSV、旋转、平移、缩放、水平翻转、mosaic=0.8、mixup=0.1、copy_paste=0.05"],
                ["实验定位", "正式对照组，为后续微调和结构改进提供baseline"],
            ],
            "基线模型不引入额外结构，能够完整继承YOLOv8m预训练优势，训练稳定、推理开销可控，是后续实验判断是否真正提升的参考标准。",
        ),
        (
            "2. 轻量ECA注意力模型",
            [
                ["项目", "设置"],
                ["训练脚本", "train_optimized_attention.py"],
                ["模型配置", "ultralytics/cfg/models/v8/yolov8m-optimized-attention.yaml"],
                ["初始权重", "yolov8m.pt，按层号映射迁移可匹配参数"],
                ["训练轮数", "epochs=100，patience=30"],
                ["输入尺寸/批量", "imgsz=640，batch=8"],
                ["结构改进", "在部分P3/P4特征位置加入轻量ECA通道注意力"],
                ["实验定位", "验证轻量通道注意力是否能增强课堂行为关键特征"],
            ],
            "该方案参数量增加较小，但测试结果低于baseline，说明简单插入注意力层并不一定适合当前数据集，新增随机初始化层可能破坏预训练特征分布。",
        ),
        (
            "3. YOLOv8m-P2小目标模型",
            [
                ["项目", "设置"],
                ["训练脚本", "train_p2.py"],
                ["模型配置", "ultralytics/cfg/models/v8/yolov8m-p2-classroom.yaml"],
                ["初始权重", "yolov8m.pt，迁移Backbone、Neck和原P3/P4/P5检测分支"],
                ["训练轮数", "epochs=100，patience=30"],
                ["输入尺寸/批量", "imgsz=640，batch=4"],
                ["结构改进", "增加P2检测分支，用更高分辨率特征检测小目标"],
                ["实验定位", "面向举手、手机等小目标行为的结构改进实验"],
            ],
            "P2模型理论上有利于小目标检测，但新增分支随机初始化、显存压力增大和batch减小都会增加训练难度。实际结果说明，仅增加检测尺度不足以解决课堂行为检测问题。",
        ),
        (
            "4. 800分辨率弱增强微调模型",
            [
                ["项目", "设置"],
                ["训练脚本", "train_finetune_img800.py"],
                ["初始权重", "runs/detect/baseline_mAP_100epochs/weights/best.pt"],
                ["训练轮数", "epochs=50，patience=20"],
                ["输入尺寸/批量", "imgsz=800，batch=4"],
                ["优化器", "AdamW，lr0=0.0001，lrf=0.05，cos_lr=True"],
                ["增强策略", "关闭mosaic、mixup、copy_paste，降低旋转、平移、缩放和颜色扰动强度"],
                ["实验定位", "保留baseline特征基础，通过高分辨率和弱增强提升细节表达"],
            ],
            "该策略强调二阶段微调：先用baseline学习稳定课堂行为特征，再用800输入进行低学习率精修。前期实验显示其验证集定位指标有提升，但测试集提升不够稳定。",
        ),
        (
            "5. CoordAtt+ECA组合注意力模型",
            [
                ["项目", "设置"],
                ["训练脚本", "train_coordatt_backbone_eca_neck.py"],
                ["模型配置", "ultralytics/cfg/models/v8/yolov8m-coordatt-backbone-eca-neck.yaml"],
                ["初始权重", "yolov8m.pt，按层号映射迁移可匹配参数"],
                ["训练轮数", "epochs=100，patience=30"],
                ["输入尺寸/批量", "imgsz=640，batch=8"],
                ["结构改进", "Backbone加入CoordAtt，Neck加入ECA"],
                ["实验定位", "同时验证坐标注意力和通道注意力组合效果"],
            ],
            "该模型结构变化比单ECA更大，对数据规模、权重迁移和训练稳定性要求更高。实验结果仍未超过baseline，说明复杂结构并不是当前任务的主要突破口。",
        ),
        (
            "6. Strong高精度最终模型",
            [
                ["项目", "设置"],
                ["训练脚本", "train_strong_img800_tail_weakaug.py"],
                ["初始权重", "runs/detect/baseline_mAP_100epochs/weights/best.pt"],
                ["数据集", "datasets/classroom_tail_oversampled，使用绝对路径yaml避免中文路径编码问题"],
                ["训练轮数", "epochs=60，patience=25"],
                ["输入尺寸/批量", "imgsz=800，batch=4"],
                ["优化器", "AdamW，lr0=0.0001，lrf=0.05，cos_lr=True"],
                ["增强策略", "弱增强：mosaic=0，mixup=0，copy_paste=0，degrees=3，translate=0.05，scale=0.15"],
                ["损失权重", "box=7.5，cls=0.65，dfl=1.5"],
                ["实验定位", "最终推荐高精度模型，解决小目标细节和类别长尾问题"],
            ],
            "该模型的核心不是修改网络结构，而是组合使用强baseline权重、800高分辨率、长尾均衡训练集和弱增强二阶段微调。测试集结果明显超过baseline，是当前项目中最有效的训练策略。",
        ),
    ]

    for title, rows, note in strategy_tables:
        parts.append(heading(title, 3))
        parts.append(table(rows, widths=[2300, 7800]))
        parts.append(paragraph(note))

    parts.append(heading("四、测试集指标对比", 2))
    parts.append(
        table(
            [
                ["模型", "Precision", "Recall", "mAP@0.5", "mAP@0.5:0.95", "结论"],
                ["baseline_mAP_100epochs(imgsz=640)", "0.9032", "0.8512", "0.8961", "0.7382", "原始基线，稳定对照"],
                ["optimized_attention_light_m_pretrained", "0.8090", "0.8114", "0.8353", "0.6534", "低于基线"],
                ["yolov8m_p2_100epochs", "0.8130", "0.8005", "0.8377", "0.6547", "低于基线"],
                ["baseline_finetune_img800_weakaug", "0.8975", "0.8527", "0.8898", "0.7278", "接近基线但未全面超过"],
                ["coordatt_backbone_eca_neck_m_pretrained", "0.8269", "0.8106", "0.8480", "0.6601", "低于基线"],
                ["baseline_mAP_100epochs(imgsz=800)", "0.8859", "0.8616", "0.8993", "0.7297", "高分辨率推理收益有限"],
                ["strong_img800_tail_weakaug", "0.9345", "0.9419", "0.9673", "0.8240", "当前最优"],
            ],
            widths=[2800, 1250, 1250, 1250, 1400, 2100],
        )
    )

    parts.append(heading("五、关键结论", 2))
    conclusions = [
        "当前项目中，效果提升最大的不是复杂结构改造，而是训练策略优化。",
        "ECA、P2、CoordAtt+ECA等结构改进均未超过baseline，主要原因可能包括预训练权重迁移不完整、新增层随机初始化、训练难度增加以及数据规模有限。",
        "单独提高输入分辨率可以改善部分召回和小目标细节，但不足以充分解决类别长尾问题。",
        "strong_img800_tail_weakaug将二阶段微调、高分辨率输入、弱增强和长尾均衡结合，在测试集上取得Precision=0.9345、Recall=0.9419、mAP@0.5=0.9673、mAP@0.5:0.95=0.8240，是当前最终推荐模型。",
        "论文中可将strong策略概括为：面向课堂行为检测的长尾均衡高分辨率弱增强二阶段微调方法。",
    ]
    for item in conclusions:
        parts.append(paragraph(item))

    make_docx(body_xml(parts), OUT_DOCX)
    print(OUT_DOCX.resolve())


if __name__ == "__main__":
    main()
