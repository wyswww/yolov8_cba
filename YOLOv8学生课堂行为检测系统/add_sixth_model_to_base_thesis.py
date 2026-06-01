# -*- coding: utf-8 -*-
"""Add the sixth model section to the base expanded thesis docx."""

from __future__ import annotations

import copy
import html
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
SOURCE_DOCX = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版.docx"
OUT_DOCX = ROOT / "本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版_加入第六模型.docx"
NEW_FIG_6_1 = ROOT / "论文图表" / "图6-1_主要模型测试指标对比图.png"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

for prefix, uri in NS.items():
    if prefix != "rel":
        ET.register_namespace(prefix, uri)


TEXT_REPLACEMENTS = {
    "本文围绕学生课堂行为检测任务，构建了包含举手": (
        "本文围绕学生课堂行为检测任务，构建了包含举手、阅读、书写、使用手机、低头、趴桌六类行为的数据集配置与训练流程。"
        "系统以YOLOv8m为核心检测模型，完成了基线训练、轻量注意力机制实验、P2小目标检测头实验、高分辨率弱增强微调实验、"
        "组合注意力实验以及长尾均衡高分辨率弱增强二阶段微调实验。实验结果表明，strong_img800_tail_weakaug模型在测试集上取得"
        "mAP@0.5为0.9673、mAP@0.5:0.95为0.8240、Precision为0.9345、Recall为0.9419的结果，综合性能最优。"
    ),
    "YOLOv8m is adopted as the core detection model. Six classroom behavior categories": (
        "YOLOv8m is adopted as the core detection model. Six classroom behavior categories are considered, including hand-raising, reading, writing, using phone, bowing the head and leaning over the table. "
        "This thesis completes baseline training, lightweight attention experiments, P2 detection-head experiments, high-resolution weak-augmentation fine-tuning, combined attention experiments and tail-balanced high-resolution two-stage fine-tuning. "
        "The final strong_img800_tail_weakaug model achieves 0.9673 mAP@0.5, 0.8240 mAP@0.5:0.95, 0.9345 precision and 0.9419 recall on the test set."
    ),
    "4.7 训练过程可复现性": "4.8 训练过程可复现性",
    "4.8 本章小结": "4.9 本章小结",
    "为了保证实验可复现，本文为不同实验分别编写独立训练脚本": (
        "为了保证实验可复现，本文为不同实验分别编写独立训练脚本，包括train_baseline_100epochs.py、train_optimized_attention.py、"
        "train_p2.py、train_finetune_img800.py、train_img800_weakaug.py、train_coordatt_backbone_eca_neck.py和"
        "train_strong_img800_tail_weakaug.py。每个脚本中明确记录模型路径、数据集路径、训练轮数、batch size、输入尺寸、优化器、"
        "学习率和数据增强参数。"
    ),
    "在模型训练方面，本章以YOLOv8m作为基线模型": (
        "在模型训练方面，本章以YOLOv8m作为基线模型，说明了训练参数、数据增强策略和结果保存方式；同时介绍了轻量注意力机制、"
        "P2小目标检测头、高分辨率弱增强微调、CoordAtt+ECA组合注意力以及长尾均衡高分辨率弱增强二阶段微调等改进实验。"
        "实验设计表明，模型优化不能只依赖结构堆叠，还需要结合数据规模、类别分布、预训练权重迁移和真实测试结果综合判断。"
    ),
    "表6-1展示了主要模型在测试集上的检测结果": (
        "表6-1展示了主要模型在测试集上的检测结果。YOLOv8m基线模型在原始imgsz=640测试口径下取得mAP@0.5为0.8961、"
        "mAP@0.5:0.95为0.7382、Precision为0.9032、Recall为0.8512的结果；strong_img800_tail_weakaug模型在测试集上取得"
        "mAP@0.5为0.9673、mAP@0.5:0.95为0.8240、Precision为0.9345、Recall为0.9419，是本文实验中的最优模型。"
    ),
    "高分辨率弱增强微调模型在测试集上的mAP@0.5为0.8898": (
        "高分辨率弱增强微调模型在测试集上的mAP@0.5为0.8898，mAP@0.5:0.95为0.7278，说明单独提高输入分辨率和关闭强增强仍不够稳定。"
        "进一步加入长尾均衡训练集后，strong_img800_tail_weakaug模型的mAP@0.5提升到0.9673，mAP@0.5:0.95提升到0.8240，"
        "表明少数类样本均衡、高分辨率输入和弱增强二阶段微调的组合更适合本数据集。"
    ),
    "在训练策略优化实验中，baseline_finetune_img800_weakaug": (
        "在训练策略优化实验中，baseline_finetune_img800_weakaug从基线best.pt出发，以imgsz=800进行弱增强微调；"
        "strong_img800_tail_weakaug进一步使用classroom_tail_oversampled长尾均衡训练集。验证集结果显示，"
        "baseline_finetune_img800_weakaug2的最佳mAP@0.5:0.95达到0.76517，strong_img800_tail_weakaug达到0.75936。"
        "虽然strong模型验证集指标略低于weakaug2，但其测试集指标显著更高，说明其泛化能力更强。"
    ),
    "需要注意的是，该验证集收益没有在最新测试集结果中同步体现": (
        "需要注意的是，验证集最优并不必然代表测试集最优。baseline_finetune_img800_weakaug2在验证集mAP@0.5:0.95上达到0.76517，"
        "但strong_img800_tail_weakaug在测试集上取得mAP@0.5:0.95为0.8240，表现更优。该现象说明最终模型选择应以独立测试集结果为主要依据。"
    ),
    "综合实验结果，本文得到以下结论": (
        "综合实验结果，本文得到以下结论：第一，YOLOv8m基线模型具有较强稳定性，是后续实验的重要起点；第二，简单增加注意力模块或P2检测头并未提升性能，"
        "说明结构改进需要结合数据规模和预训练权重迁移充分设计；第三，strong_img800_tail_weakaug采用长尾均衡训练集、高分辨率输入、弱增强和二阶段微调，"
        "在测试集上取得mAP@0.5为0.9673、mAP@0.5:0.95为0.8240的最优结果；第四，最终系统可优先采用该模型作为高精度检测方案，"
        "若更重视实时性，可继续保留baseline作为轻量备选。"
    ),
    "输入尺寸是影响小目标检测的重要参数": (
        "输入尺寸是影响小目标检测的重要参数。imgsz=640是YOLO常用默认设置，训练速度较快；imgsz=800能够保留更多局部细节，有助于手机、手部和低头区域检测，"
        "但显存开销和推理时间也会增加。本文最新实验显示，单独提高baseline推理分辨率收益有限，而在imgsz=800基础上结合长尾均衡训练与弱增强二阶段微调后，"
        "测试集mAP@0.5:0.95提升到0.8240，说明输入尺寸需要与训练数据分布优化共同发挥作用。"
    ),
    "小目标问题主要体现在使用手机和举手行为中": (
        "小目标问题主要体现在使用手机和举手行为中。手机在课堂图像中面积较小，且可能被手部遮挡或与桌面颜色接近；举手行为虽然动作明显，但手部区域较细，"
        "远距离拍摄时可能只占很少像素。P2检测头理论上有助于小目标检测，但本文实验未提升，说明仅增加检测尺度不足以解决问题。"
        "最新strong模型通过高分辨率输入保留更多局部细节，同时通过长尾均衡训练改善少数类学习，取得了更稳定的测试集提升。"
    ),
    "输入分辨率提高会增加推理时间。最新测试结果显示": (
        "输入分辨率提高会增加推理时间。最新测试结果显示，strong_img800_tail_weakaug模型在imgsz=800测试口径下取得mAP@0.5为0.9673、"
        "mAP@0.5:0.95为0.8240、Precision为0.9345、Recall为0.9419，明显超过baseline。考虑到该模型仍采用YOLOv8m结构，额外开销主要来自800输入尺寸，"
        "系统可将其作为高精度默认方案；在显存或实时性要求更严格的场景中，可切换到640输入的baseline模型。"
    ),
    "本章对模型实验结果和系统测试情况进行了综合分析": (
        "本章对模型实验结果和系统测试情况进行了综合分析。首先说明了实验环境和评价指标，然后对YOLOv8m基线模型、轻量注意力模型、P2检测头模型、"
        "高分辨率弱增强微调模型、高分辨率推理结果以及strong_img800_tail_weakaug模型进行了对比。实验表明，长尾均衡训练集、高分辨率输入、"
        "弱增强和二阶段微调组合能够显著提升测试集综合性能，strong_img800_tail_weakaug可作为本文最终推荐模型。"
    ),
    "在算法实验方面，本文首先训练YOLOv8m基线模型": (
        "在算法实验方面，本文首先训练YOLOv8m基线模型，并取得较稳定的测试集综合结果。随后尝试轻量ECA注意力、P2小目标检测头和高分辨率弱增强微调，"
        "发现单纯结构改进或单独微调并不能稳定超过基线。在此基础上，本文进一步提出strong_img800_tail_weakaug训练策略，将长尾均衡训练集、"
        "高分辨率输入、弱增强和二阶段微调结合，最终在测试集上取得mAP@0.5为0.9673、mAP@0.5:0.95为0.8240的最优结果。"
    ),
    "在论文实验分析中，不能只依赖终端输出": (
        "在论文实验分析中，不能只依赖终端输出，还应结合results.csv查看每轮指标变化。例如baseline_mAP_100epochs在第90轮取得最佳mAP@0.5:0.95，"
        "baseline_finetune_img800_weakaug2在第41轮取得最佳mAP@0.5:0.95，strong_img800_tail_weakaug在第39轮取得最佳mAP@0.5:0.95。"
        "通过这些信息可以更准确地描述模型训练过程。"
    ),
    "结果管理还涉及命名规范": (
        "结果管理还涉及命名规范。本文为不同实验设置独立run name，例如baseline_mAP_100epochs、optimized_attention_light_m_pretrained、"
        "yolov8m_p2_100epochs、baseline_finetune_img800_weakaug和strong_img800_tail_weakaug。清晰的命名能够减少实验混淆，"
        "方便后续复现实验和撰写论文表格。"
    ),
}

NEW_SECTION = [
    "4.7 改进实验四：长尾均衡高分辨率弱增强微调",
    (
        "在前述实验中，注意力机制和P2检测头均未稳定超过基线，单独采用高分辨率弱增强微调也存在测试集泛化不足的问题。"
        "进一步分析数据分布后发现，低头和趴桌等类别样本数量明显少于阅读、书写和使用手机等类别，类别长尾是影响模型泛化的重要因素。"
        "因此，本文设计第六个模型strong_img800_tail_weakaug，将长尾均衡训练集、高分辨率输入、弱增强和二阶段微调结合。"
    ),
    (
        "该模型以baseline_mAP_100epochs的best.pt作为初始权重，使用datasets/classroom_tail_oversampled作为训练集。"
        "该数据集由oversample_tail_classes.py生成，只对训练集中包含bowing the head和leaning over the table的图片进行局部裁剪和轻量增强，"
        "验证集和测试集保持原始分布不变，从而保证评估公平。"
    ),
    (
        "训练参数方面，strong_img800_tail_weakaug使用imgsz=800、batch=4、epochs=60、patience=25，优化器为AdamW，初始学习率为0.0001，"
        "并启用cos_lr。数据增强方面关闭mosaic、mixup和copy_paste，仅保留轻微颜色扰动、旋转、平移、缩放和水平翻转。"
        "同时将cls损失权重设置为0.65，以增强相似课堂行为类别之间的区分能力。"
    ),
    (
        "该策略的核心思想是不改变YOLOv8m网络结构，而是针对课堂行为检测中的小目标细节、类别长尾和强增强语义破坏问题进行训练策略优化。"
        "后续测试结果表明，该模型在独立测试集上取得最佳综合表现，说明数据分布优化和二阶段微调比单纯结构堆叠更适合当前任务。"
    ),
]

TEST_TABLE_ROWS = [
    ["模型", "mAP@0.5", "mAP@0.5:0.95", "Precision", "Recall"],
    ["baseline_mAP_100epochs(imgsz=640)", "0.8961", "0.7382", "0.9032", "0.8512"],
    ["optimized_attention_light_m_pretrained", "0.8353", "0.6534", "0.8090", "0.8114"],
    ["yolov8m_p2_100epochs", "0.8377", "0.6547", "0.8130", "0.8005"],
    ["baseline_finetune_img800_weakaug", "0.8898", "0.7278", "0.8975", "0.8527"],
    ["baseline_mAP_100epochs(imgsz=800)", "0.8993", "0.7297", "0.8859", "0.8616"],
    ["strong_img800_tail_weakaug", "0.9673", "0.8240", "0.9345", "0.9419"],
]

VAL_TABLE_ROWS = [
    ["实验名称", "最佳轮次", "最佳mAP@0.5", "最佳mAP@0.5:0.95", "说明"],
    ["baseline_mAP_100epochs", "90", "0.91542", "0.75291", "YOLOv8m基线"],
    ["baseline_finetune_img800_weakaug2", "41", "0.90775", "0.76517", "高分辨率弱增强二阶段微调"],
    ["strong_img800_tail_weakaug", "39", "0.90795", "0.75936", "长尾均衡+800弱增强二阶段微调"],
]


def q(name: str) -> str:
    prefix, local = name.split(":")
    return f"{{{NS[prefix]}}}{local}"


def paragraph_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(".//w:t", NS))


def set_paragraph_text(p: ET.Element, text: str) -> None:
    rpr = None
    first_run = p.find("w:r", NS)
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


def make_para_like(template: ET.Element, text: str) -> ET.Element:
    new_p = copy.deepcopy(template)
    set_paragraph_text(new_p, text)
    return new_p


def cell_text(tc: ET.Element) -> str:
    return "".join(t.text or "" for t in tc.findall(".//w:t", NS))


def set_cell_text(tc: ET.Element, text: str) -> None:
    p = tc.find("w:p", NS)
    if p is None:
        p = ET.SubElement(tc, q("w:p"))
    set_paragraph_text(p, text)


def table_text(tbl: ET.Element) -> str:
    return " | ".join(cell_text(tc) for tc in tbl.findall(".//w:tc", NS))


def set_table_rows(tbl: ET.Element, rows: list[list[str]]) -> None:
    trs = tbl.findall("w:tr", NS)
    while len(trs) < len(rows):
        tbl.append(copy.deepcopy(trs[-1]))
        trs = tbl.findall("w:tr", NS)
    for extra in trs[len(rows):]:
        tbl.remove(extra)
    trs = tbl.findall("w:tr", NS)
    for tr, row in zip(trs, rows):
        cells = tr.findall("w:tc", NS)
        while len(cells) < len(row):
            tr.append(copy.deepcopy(cells[-1]))
            cells = tr.findall("w:tc", NS)
        for tc, value in zip(cells, row):
            set_cell_text(tc, value)


def replace_image_before_caption(root: ET.Element, rels_root: ET.Element, caption: str, media_name: str) -> None:
    paragraphs = root.findall(".//w:body/w:p", NS)
    for idx, p in enumerate(paragraphs):
        if caption in paragraph_text(p):
            for prev in reversed(paragraphs[:idx]):
                blip = prev.find(".//a:blip", NS)
                if blip is None:
                    continue
                rid = blip.get(q("r:embed"))
                if not rid:
                    continue
                for rel in rels_root.findall("rel:Relationship", NS):
                    if rel.get("Id") == rid:
                        rel.set("Target", f"media/{media_name}")
                        return
    raise RuntimeError(f"Could not replace image before caption: {caption}")


def main() -> None:
    if not SOURCE_DOCX.exists():
        raise FileNotFoundError(SOURCE_DOCX)
    if not NEW_FIG_6_1.exists():
        raise FileNotFoundError(NEW_FIG_6_1)

    with zipfile.ZipFile(SOURCE_DOCX, "r") as zin:
        doc_root = ET.fromstring(zin.read("word/document.xml"))
        rels_root = ET.fromstring(zin.read("word/_rels/document.xml.rels"))

        body = doc_root.find("w:body", NS)
        if body is None:
            raise RuntimeError("Missing document body")

        # Replace existing paragraphs and insert the new section before old 4.7.
        insert_done = False
        for idx, p in enumerate(list(body)):
            if p.tag != q("w:p"):
                continue
            text = paragraph_text(p).strip()
            if text == "4.7 训练过程可复现性" and not insert_done:
                template = p
                for offset, new_text in enumerate(NEW_SECTION):
                    body.insert(idx + offset, make_para_like(template, new_text))
                insert_done = True

        for p in doc_root.findall(".//w:p", NS):
            text = paragraph_text(p).strip()
            for prefix, replacement in TEXT_REPLACEMENTS.items():
                if text.startswith(prefix):
                    set_paragraph_text(p, replacement)
                    break

        for tbl in doc_root.findall(".//w:tbl", NS):
            txt = table_text(tbl)
            if "baseline_mAP_100epochs" in txt and "Precision" in txt:
                set_table_rows(tbl, TEST_TABLE_ROWS)
            elif "训练轮数" in txt and "最佳mAP@0.5:0.95" in txt:
                set_table_rows(tbl, VAL_TABLE_ROWS)

        replace_image_before_caption(doc_root, rels_root, "图6-1 主要模型测试指标对比图", "added_sixth_model_fig6_1.png")

        doc_xml = ET.tostring(doc_root, encoding="utf-8", xml_declaration=True)
        rels_xml = ET.tostring(rels_root, encoding="utf-8", xml_declaration=True)

        tmp_docx = OUT_DOCX.with_suffix(".tmp.docx")
        with zipfile.ZipFile(tmp_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc_xml)
                elif item.filename == "word/_rels/document.xml.rels":
                    zout.writestr(item, rels_xml)
                else:
                    zout.writestr(item, zin.read(item.filename))
            zout.write(NEW_FIG_6_1, "word/media/added_sixth_model_fig6_1.png")

    tmp_docx.replace(OUT_DOCX)
    print(OUT_DOCX)


if __name__ == "__main__":
    main()
