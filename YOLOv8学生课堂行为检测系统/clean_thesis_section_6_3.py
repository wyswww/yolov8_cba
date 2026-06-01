# -*- coding: utf-8 -*-
"""Remove redundant intermediate experiment data from section 6.3."""

from __future__ import annotations

import copy
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SOURCE_DOCX = Path("本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版_加入第六模型.docx")
OUT_DOCX = Path("本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版_加入第六模型_6-3去冗余.docx")

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

ET.register_namespace("w", NS["w"])


REPLACEMENTS = {
    "在训练策略优化实验中，baseline_finetune_img800_weakaug": (
        "在训练策略优化实验中，本文保留具有代表性的基线模型和最终第六模型进行对比。"
        "baseline_mAP_100epochs作为标准YOLOv8m训练结果，用于反映原始训练策略的性能；"
        "strong_img800_tail_weakaug则在该基线权重基础上，引入classroom_tail_oversampled长尾均衡训练集，"
        "并采用imgsz=800、弱增强和低学习率二阶段微调。验证集结果显示，strong_img800_tail_weakaug的最佳mAP@0.5:0.95为0.75936，"
        "高于基线模型的0.75291，说明该训练策略在定位质量上具有一定提升。"
    ),
    "需要注意的是，验证集最优并不必然代表测试集最优": (
        "需要注意的是，验证集结果主要用于观察训练收敛和模型选择趋势，最终模型优劣仍应以独立测试集结果为主要依据。"
        "从测试集结果看，strong_img800_tail_weakaug在Precision、Recall、mAP@0.5和mAP@0.5:0.95四项指标上均明显超过baseline，"
        "因此本文将其作为最终推荐的高精度检测模型。"
    ),
    "表6-2 训练策略优化验证集结果": "表6-2 代表性训练策略验证集结果",
}

TABLE_ROWS = [
    ["实验名称", "最佳轮次", "最佳mAP@0.5", "最佳mAP@0.5:0.95", "说明"],
    ["baseline_mAP_100epochs", "90", "0.91542", "0.75291", "YOLOv8m基线"],
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


def main() -> None:
    if not SOURCE_DOCX.exists():
        raise FileNotFoundError(SOURCE_DOCX)

    with zipfile.ZipFile(SOURCE_DOCX, "r") as zin:
        root = ET.fromstring(zin.read("word/document.xml"))

        for p in root.findall(".//w:p", NS):
            text = paragraph_text(p).strip()
            for prefix, replacement in REPLACEMENTS.items():
                if text.startswith(prefix):
                    set_paragraph_text(p, replacement)
                    break

        for tbl in root.findall(".//w:tbl", NS):
            txt = table_text(tbl)
            if "baseline_finetune_img800_weakaug2" in txt and "strong_img800_tail_weakaug" in txt:
                set_table_rows(tbl, TABLE_ROWS)

        doc_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        tmp_docx = OUT_DOCX.with_suffix(".tmp.docx")
        with zipfile.ZipFile(tmp_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc_xml)
                else:
                    zout.writestr(item, zin.read(item.filename))

    tmp_docx.replace(OUT_DOCX)
    print(OUT_DOCX)


if __name__ == "__main__":
    main()
