# -*- coding: utf-8 -*-
"""Generate a Word report for training scripts, parameters, and YOLO source changes."""

from __future__ import annotations

import html
import zipfile
from datetime import datetime
from pathlib import Path


OUT_DOCX = Path("训练程序与YOLO源码修改分析.docx")


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def run_props(size: int = 24, bold: bool = False, font: str = "宋体") -> str:
    b = "<w:b/>" if bold else ""
    return (
        f'<w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>'
        f"{b}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
    )


def p(text: str = "", align: str = "both", size: int = 24, bold: bool = False, first_line: bool = True) -> str:
    indent = '<w:ind w:firstLine="480"/>' if first_line else ""
    return (
        f'<w:p><w:pPr><w:jc w:val="{align}"/><w:spacing w:line="360" w:lineRule="auto"/>'
        f"{indent}</w:pPr><w:r>{run_props(size, bold)}"
        f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
    )


def h(text: str, level: int) -> str:
    size = {1: 32, 2: 28, 3: 24}.get(level, 24)
    align = "center" if level == 1 else "left"
    return p(text, align=align, size=size, bold=True, first_line=False)


def bullet(text: str) -> str:
    return p("· " + text, first_line=False)


def code(text: str) -> str:
    return p(text, align="left", size=20, first_line=False)


def table(rows: list[list[object]]) -> str:
    xml = [
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/>'
        '<w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/>'
        '<w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/>'
        "</w:tblBorders></w:tblPr>"
    ]
    for row_idx, row in enumerate(rows):
        xml.append("<w:tr>")
        for cell in row:
            xml.append('<w:tc><w:tcPr><w:tcW w:w="2600" w:type="dxa"/></w:tcPr>')
            xml.append(p(str(cell), align="center", size=20, bold=(row_idx == 0), first_line=False))
            xml.append("</w:tc>")
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


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
    parts: list[str] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    parts.append(h("训练程序与YOLO源码修改分析", 1))
    parts.append(p(f"生成时间：{now}", align="center", first_line=False))
    parts.append(p("本文档根据当前项目目录中的训练脚本、runs/detect结果文件和本地Ultralytics源码整理，便于论文撰写和毕业答辩时说明实验路线。"))

    parts.append(h("一、总体训练思路", 2))
    parts.append(p("项目围绕学生课堂行为检测任务，以YOLOv8m为主干模型，识别六类课堂行为：hand-raising、reading、writing、using phone、bowing the head、leaning over the table。训练路线不是只做单次训练，而是先建立YOLOv8m基线，再分别尝试轻量注意力机制、P2小目标检测头、高分辨率弱增强训练和高分辨率微调，最后用统一test.py在独立测试集上对比。"))
    parts.append(bullet("核心原则：最终模型选择以独立测试集泛化表现为准，而不是只看验证集最优指标。"))
    parts.append(bullet("系统默认推荐模型：runs/detect/baseline_mAP_100epochs/weights/best.pt。"))
    parts.append(bullet("验证集上最优mAP50-95来自baseline_finetune_img800_weakaug2，但测试集综合稳定性仍以基线模型更可靠。"))

    parts.append(h("二、训练与数据处理脚本总览", 2))
    parts.append(table([
        ["脚本", "作用", "关键说明"],
        ["train.py", "早期基线训练脚本", "使用yolov8m.pt、imgsz=640、epochs=100，增强较强，run name为baseline_mAP"],
        ["train_baseline_100epochs.py", "正式100轮基线训练", "YOLOv8m、AdamW、imgsz=640、batch=8、损失权重7.5/0.5/1.5"],
        ["train_optimized_attention.py", "轻量ECA注意力实验", "使用yolov8m-optimized-attention.yaml，在P3/P4插入ECA并层映射迁移权重"],
        ["train_p2.py", "P2小目标检测头实验", "使用yolov8-p2-classroom.yaml，增加P2/4检测分支，batch降为4"],
        ["train_finetune_img800.py", "基线权重高分辨率弱增强微调", "从baseline best.pt继续训练，imgsz=800，关闭mosaic/mixup/copy-paste"],
        ["train_img800_weakaug.py", "从yolov8m.pt直接高分辨率弱增强训练", "imgsz=800、epochs=120、mosaic=0.35，但当前缺少对应最终权重目录"],
        ["oversample_tail_classes.py", "长尾类别训练集过采样", "只增强训练集中的低头和趴桌类别，验证集和测试集保持不变"],
        ["split_dataset.py", "数据集划分", "按train/val/test=70%/20%/10%划分，固定随机种子"],
        ["augment_data.py", "离线数据增强工具", "包含基础变换、Mosaic、MixUp、Copy-Paste，可生成data_augmented.yaml"],
    ]))

    parts.append(h("三、各训练程序核心参数", 2))
    parts.append(h("3.1 train.py：早期基线脚本", 3))
    parts.append(table([
        ["参数", "取值"],
        ["模型", "yolov8m.pt"],
        ["数据", "datasets/data.yaml"],
        ["epochs / patience", "100 / 30"],
        ["batch / imgsz", "8 / 640"],
        ["optimizer / lr0 / lrf", "AdamW / 0.001 / 0.01"],
        ["增强", "hsv_s=0.7, degrees=10, scale=0.5, mosaic=1.0, mixup=0.1"],
        ["run name", "baseline_mAP"],
    ]))
    parts.append(p("该脚本属于早期基线训练，增强幅度相对更强，后续正式实验改用更规范的train_baseline_100epochs.py。"))

    parts.append(h("3.2 train_baseline_100epochs.py：正式基线训练", 3))
    parts.append(table([
        ["参数", "取值"],
        ["模型", "yolov8m.pt，pretrained=True"],
        ["数据", "datasets/data_tail_oversampled.yaml（脚本中配置）；部分历史run的args.yaml显示为datasets/data.yaml"],
        ["epochs / patience", "100 / 30"],
        ["batch / imgsz", "8 / 640"],
        ["optimizer", "AdamW"],
        ["lr0 / lrf", "0.0005 / 0.01"],
        ["momentum / weight_decay", "0.937 / 0.0005"],
        ["warmup", "warmup_epochs=5.0, warmup_momentum=0.8, warmup_bias_lr=0.1"],
        ["增强", "hsv_h=0.015, hsv_s=0.5, hsv_v=0.4, degrees=5, translate=0.1, scale=0.3, shear=2, perspective=0.0002, fliplr=0.5, mosaic=0.8, mixup=0.1, copy_paste=0.05, close_mosaic=10"],
        ["损失权重", "box=7.5, cls=0.5, dfl=1.5"],
        ["其他", "amp=True, cache=True, workers=0, seed=42"],
        ["输出", "runs/detect/baseline_mAP_100epochs"],
    ]))
    parts.append(p("该脚本是论文中最重要的基线实验。它在独立测试集上综合表现最稳定，因此适合作为系统默认模型。"))

    parts.append(h("3.3 train_optimized_attention.py：轻量ECA注意力实验", 3))
    parts.append(table([
        ["参数", "取值"],
        ["模型配置", "ultralytics/cfg/models/v8/yolov8m-optimized-attention.yaml"],
        ["预训练来源", "yolov8m.pt"],
        ["结构改动", "在P3和P4特征位置插入ECA通道注意力模块"],
        ["权重加载", "通过load_yolov8m_weights_by_layer_mapping按层号迁移可匹配权重"],
        ["epochs / batch / imgsz", "100 / 8 / 640"],
        ["优化器与学习率", "AdamW, lr0=0.0005, lrf=0.01"],
        ["增强", "与正式基线基本一致"],
        ["损失权重", "box=7.5, cls=0.5, dfl=1.5"],
        ["pretrained", "False（因为已手动迁移部分权重）"],
        ["输出", "runs/detect/optimized_attention_light_m_pretrained"],
    ]))
    parts.append(p("该实验的目的不是简单堆叠复杂模块，而是验证轻量通道注意力能否在课堂行为细粒度识别中提升有效特征表达。结果显示其测试集指标低于基线，说明当前数据规模和权重迁移条件下，新增注意力模块没有带来稳定收益。"))

    parts.append(h("3.4 train_p2.py：P2小目标检测头实验", 3))
    parts.append(table([
        ["参数", "取值"],
        ["模型配置", "ultralytics/cfg/models/v8/yolov8-p2-classroom.yaml"],
        ["预训练来源", "yolov8m.pt"],
        ["结构改动", "在默认P3/P4/P5检测头基础上增加P2/4小目标检测分支"],
        ["权重加载", "迁移Backbone、Neck和原P3/P4/P5检测头可匹配权重，新增P2分支随机初始化"],
        ["epochs / batch / imgsz", "100 / 4 / 640"],
        ["优化器与学习率", "AdamW, lr0=0.0005, lrf=0.01"],
        ["增强", "与正式基线基本一致"],
        ["损失权重", "box=7.5, cls=0.5, dfl=1.5"],
        ["输出", "runs/detect/yolov8m_p2_100epochs"],
    ]))
    parts.append(p("该实验针对手机、手部、远距离学生行为等小目标问题。结果没有超过基线，说明仅增加高分辨率检测尺度不足以解决小目标识别，还需要更高质量小目标标注、更稳定训练和更合理的样本分布。"))

    parts.append(h("3.5 train_finetune_img800.py：高分辨率弱增强微调", 3))
    parts.append(table([
        ["参数", "取值"],
        ["初始权重", "runs/detect/baseline_mAP_100epochs/weights/best.pt"],
        ["数据", "datasets/data.yaml"],
        ["epochs / patience", "50 / 20"],
        ["batch / imgsz", "4 / 800"],
        ["optimizer / lr0 / lrf", "AdamW / 0.0001 / 0.05"],
        ["学习率策略", "cos_lr=True，warmup_epochs=2.0"],
        ["弱增强", "hsv_h=0.01, hsv_s=0.3, hsv_v=0.3, degrees=3, translate=0.05, scale=0.15, shear=1, perspective=0, mosaic=0, mixup=0, copy_paste=0"],
        ["损失权重", "box=7.5, cls=0.65, dfl=1.5"],
        ["输出", "runs/detect/baseline_finetune_img800_weakaug"],
    ]))
    parts.append(p("该实验从较强基线继续训练，提高输入分辨率以保留局部细节，并降低增强强度，使后期训练更接近真实课堂图像分布。cls从0.5提高到0.65，是为了更强调类别区分。"))

    parts.append(h("3.6 train_img800_weakaug.py：从预训练权重直接高分辨率弱增强训练", 3))
    parts.append(table([
        ["参数", "取值"],
        ["初始权重", "yolov8m.pt"],
        ["epochs / patience", "120 / 40"],
        ["batch / imgsz", "4 / 800"],
        ["optimizer / lr0 / lrf", "AdamW / 0.0004 / 0.02"],
        ["学习率策略", "cos_lr=True，warmup_epochs=4.0"],
        ["增强", "mosaic=0.35, mixup=0, copy_paste=0, close_mosaic=20，其他几何/颜色增强较弱"],
        ["损失权重", "box=7.5, cls=0.65, dfl=1.5"],
        ["输出名称", "yolov8m_img800_weakaug_120epochs"],
    ]))
    parts.append(p("该脚本意图从yolov8m.pt直接进行高分辨率弱增强完整训练。但当前项目中没有对应weights/best.pt，test.py运行时会跳过该模型，因此论文中应避免把它描述为已有完整测试结果。"))

    parts.append(h("四、损失函数说明", 2))
    parts.append(p("本项目采用YOLOv8检测任务默认损失，由三部分组成：边界框回归损失box_loss、分类损失cls_loss和分布焦点损失dfl_loss。代码位置为ultralytics/utils/loss.py中的v8DetectionLoss和BboxLoss。"))
    parts.append(code("Loss = box_loss * box + cls_loss * cls + dfl_loss * dfl"))
    parts.append(table([
        ["损失项", "实现/含义", "基线权重", "微调权重"],
        ["box_loss", "CIoU边界框回归损失，衡量预测框与真实框定位质量", "7.5", "7.5"],
        ["cls_loss", "BCEWithLogitsLoss分类损失，衡量行为类别预测", "0.5", "0.65"],
        ["dfl_loss", "Distribution Focal Loss，用于提升边界框距离分布建模和定位精度", "1.5", "1.5"],
    ]))
    parts.append(p("答辩口径：本文没有自定义损失函数，而是使用YOLOv8检测任务成熟的组合损失；微调阶段提高cls权重，是为了让模型更关注阅读、书写、低头、趴桌等相似行为的类别区分。"))

    parts.append(h("五、对YOLO源码的主要修改", 2))
    parts.append(table([
        ["文件", "修改内容", "目的"],
        ["ultralytics/nn/modules/attention.py", "新增SimAM、ECA、CoordAtt、C3CBAM、C3ECA、EMA等注意力模块", "为注意力实验提供可被模型YAML调用的模块"],
        ["ultralytics/nn/modules/__init__.py", "导入并导出新增注意力模块", "使模块能被Ultralytics模块系统识别"],
        ["ultralytics/nn/tasks.py", "在顶部导入注意力模块；在parse_model中加入ECA、SimAM、CoordAtt、EMA、C3CBAM、C3ECA等解析逻辑", "让自定义YAML中的模块名可正常构建模型，并正确处理输入/输出通道参数"],
        ["ultralytics/cfg/models/v8/yolov8m-optimized-attention.yaml", "基于YOLOv8m，在P3、P4位置加入ECA注意力", "验证轻量通道注意力对课堂行为检测的影响"],
        ["ultralytics/cfg/models/v8/yolov8-p2-classroom.yaml", "增加P2/4检测分支，最终Detect输入为P2、P3、P4、P5四尺度", "增强小目标检测能力的实验设计"],
    ]))
    parts.append(p("源码修改的关键点在parse_model。原版Ultralytics只能解析内置模块，自定义ECA等模块如果不加入globals和参数处理，会在读取YAML时无法构建模型。你的修改让自定义注意力模块可以像Conv、C2f、Detect一样写入YAML并参与模型构建。"))

    parts.append(h("六、自定义模型结构说明", 2))
    parts.append(h("6.1 ECA注意力模型", 3))
    parts.append(p("yolov8m-optimized-attention.yaml设置nc=6、scale=m，整体保持YOLOv8m尺度，只在Backbone的P3和P4特征层后插入ECA。ECA通过全局平均池化和一维卷积建立局部跨通道交互，参数量较小，理论上可以增强模型对重要通道的选择。"))
    parts.append(h("6.2 P2小目标模型", 3))
    parts.append(p("yolov8-p2-classroom.yaml在常规P3/P4/P5检测基础上增加P2分支，使检测头输入变为P2、P3、P4、P5四个尺度。P2特征图分辨率更高，理论上有利于手机、手部动作、远距离学生行为等小目标检测，但也增加计算量和训练难度。"))

    parts.append(h("七、实验结果整理", 2))
    parts.append(table([
        ["实验目录", "最佳epoch", "Precision", "Recall", "mAP50", "mAP50-95", "说明"],
        ["baseline_finetune_img800_weakaug2", "41", "0.90243", "0.87622", "0.90775", "0.76517", "验证集最优，但测试集未全面超过基线"],
        ["baseline_finetune_img800_weakaug", "24", "0.89094", "0.87389", "0.90531", "0.75852", "高分辨率弱增强微调"],
        ["baseline_mAP_100epochs", "90", "0.89458", "0.87984", "0.91542", "0.75291", "正式基线，测试集综合最稳"],
        ["yolov8m_p2_100epochs", "99", "0.83866", "0.80510", "0.85593", "0.66459", "P2结构未超过基线"],
        ["optimized_attention_light_m_pretrained", "99", "0.82806", "0.82329", "0.85554", "0.66264", "ECA注意力未超过基线"],
    ]))
    parts.append(p("上表为训练/验证结果中按mAP50-95排序的代表性结果。论文最终模型选择还应结合test.py独立测试集结果。test.py结果显示baseline_mAP_100epochs在测试集上Precision=0.9032、Recall=0.8512、mAP50=0.8961、mAP50-95=0.7382，综合表现最稳定；weakaug2的Recall略高，但mAP50和mAP50-95没有全面超过基线。"))

    parts.append(h("八、答辩建议表述", 2))
    parts.append(bullet("如果老师问为什么改进没有提升：可以回答结构改进不一定在所有数据集有效，ECA和P2增加了随机初始化模块或新检测分支，可能破坏预训练特征迁移；当前数据规模、类别不均衡和小目标标注质量限制了收益。"))
    parts.append(bullet("如果老师问为什么最终用基线：可以回答最终选择以独立测试集综合指标为准，baseline_mAP_100epochs在Precision、mAP50-95和稳定性上更均衡，适合系统默认部署。"))
    parts.append(bullet("如果老师问高分辨率有什么意义：可以回答imgsz=800能保留更多局部细节，有助于提高部分目标召回，但也会增加计算开销，并可能带来误检或定位指标下降，因此作为离线高召回方案更合适。"))
    parts.append(bullet("如果老师问源码改动是否可靠：可以回答主要修改集中在模块注册、YAML解析和结构配置，不改变YOLOv8核心训练流程和损失函数，因此便于对比不同结构对同一任务的影响。"))
    parts.append(bullet("如果老师问数据过采样是否影响公平：可以回答过采样只作用于训练集，验证集和测试集保持不变，因此不会直接污染评估结果。"))

    parts.append(h("九、需要注意的问题", 2))
    parts.append(bullet("train_baseline_100epochs.py当前写的是datasets/data_tail_oversampled.yaml，但已有baseline_mAP_100epochs历史args.yaml显示为datasets/data.yaml；论文中引用实验结果时，应以对应run目录的args.yaml为准。"))
    parts.append(bullet("datasets/data_tail_oversampled.yaml中path包含中文路径乱码显示，若后续重新训练，建议改成稳定的相对路径或正确UTF-8路径。"))
    parts.append(bullet("train_img800_weakaug.py对应的yolov8m_img800_weakaug_120epochs权重当前缺失，不能作为已有测试结果重点陈述。"))
    parts.append(bullet("attention.py中的中文注释在PowerShell中显示为乱码，但代码逻辑可读；论文和答辩中只需说明新增模块和parse_model支持即可。"))

    parts.append(h("十、结论", 2))
    parts.append(p("本项目的训练工作形成了从基线模型、结构改进、训练策略优化到独立测试评估的完整实验链条。源码层面主要扩展了注意力模块注册和自定义模型结构解析，训练层面通过统一参数和权重迁移尽量保证公平对比。实验结果说明，在当前学生课堂行为数据集上，稳定的YOLOv8m基线模型比简单加入注意力或P2检测头更可靠；高分辨率弱增强可改善部分验证集指标，但最终仍需以测试集泛化能力决定部署模型。"))

    make_docx(body_xml(parts), OUT_DOCX)
    print(OUT_DOCX.resolve())


if __name__ == "__main__":
    main()
