# -*- coding: utf-8 -*-
"""Insert test.py output figures into a thesis docx without third-party deps."""

from __future__ import annotations

import html
import re
import shutil
import struct
import zipfile
from pathlib import Path


SOURCE_DOCX = Path("本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版.docx")
OUT_DOCX = Path("本科毕业论文_基于YOLOv8的学生课堂行为检测系统_扩展版_插入Test结果图.docx")
FIGURE_DIR = Path("论文图表")
INSERT_BEFORE = "6.11 系统性能与可用性分析"

FIGURES = [
    (
        Path("runs/detect/test_baseline_mAP_100epochs/val_batch0_pred.jpg"),
        "图6-2 test.py测试集样本预测结果图",
        "图6-2_test.py测试集样本预测结果图.jpg",
    ),
    (
        Path("runs/detect/test_baseline_mAP_100epochs/PR_curve.png"),
        "图6-3 test.py测试集PR曲线",
        "图6-3_test.py测试集PR曲线.png",
    ),
    (
        Path("runs/detect/test_baseline_mAP_100epochs/confusion_matrix_normalized.png"),
        "图6-4 test.py测试集归一化混淆矩阵",
        "图6-4_test.py测试集归一化混淆矩阵.png",
    ),
    (
        Path("runs/detect/test_baseline_finetune_img800_weakaug2/val_batch0_pred.jpg"),
        "图6-5 weakaug2模型测试集样本预测结果图",
        "图6-5_weakaug2模型测试集样本预测结果图.jpg",
    ),
]


EMU_PER_INCH = 914400
MAX_WIDTH_EMU = int(5.8 * EMU_PER_INCH)


def xml_escape(text: str) -> str:
    return html.escape(text, quote=True)


def paragraph(text: str, align: str = "both", first_line: bool = True, size: int = 24) -> str:
    jc = f'<w:jc w:val="{align}"/>'
    indent = '<w:ind w:firstLine="480"/>' if first_line else ""
    return (
        f"<w:p><w:pPr>{jc}<w:spacing w:line=\"360\" w:lineRule=\"auto\"/>"
        f"{indent}</w:pPr><w:r><w:rPr><w:rFonts w:ascii=\"宋体\" w:hAnsi=\"宋体\" "
        f"w:eastAsia=\"宋体\" w:cs=\"宋体\"/><w:sz w:val=\"{size}\"/>"
        f"<w:szCs w:val=\"{size}\"/></w:rPr><w:t xml:space=\"preserve\">"
        f"{xml_escape(text)}</w:t></w:r></w:p>"
    )


def image_size(path: Path) -> tuple[int, int]:
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


def image_para(rid: str, name: str, docpr_id: int, path: Path) -> str:
    width, height = image_size(path)
    cx = MAX_WIDTH_EMU
    cy = int(cx * height / width)
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


def ensure_content_type(content_types: str, extension: str, content_type: str) -> str:
    if f'Extension="{extension}"' in content_types:
        return content_types
    return content_types.replace(
        "</Types>",
        f'<Default Extension="{extension}" ContentType="{content_type}"/></Types>',
    )


def next_docpr_id(doc_xml: str) -> int:
    ids = [int(match) for match in re.findall(r"<wp:docPr[^>]* id=\"(\d+)\"", doc_xml)]
    return max(ids, default=0) + 1


def build_insert_xml(figures: list[tuple[Path, str, str]], rid_start: int, docpr_start: int) -> str:
    parts = [
        paragraph(
            "为进一步增强实验结果的直观性，本文选取test.py在测试集上生成的预测可视化图、PR曲线和归一化混淆矩阵作为补充说明。"
            "其中预测图能够展示模型在真实课堂样本中的检测框和类别判断，PR曲线与混淆矩阵则从整体性能和类别混淆角度反映模型表现。",
            first_line=True,
        )
    ]
    for offset, (path, caption, _) in enumerate(figures):
        rid = f"rIdTestFig{rid_start + offset}"
        parts.append(image_para(rid, caption, docpr_start + offset, path))
        parts.append(paragraph(caption, align="center", first_line=False, size=20))
    return "".join(parts)


def insert_before_heading(doc_xml: str, insert_xml: str, heading: str) -> str:
    pos = doc_xml.find(heading)
    if pos == -1:
        raise RuntimeError(f"Could not find insertion heading: {heading}")
    p_start = doc_xml.rfind("<w:p", 0, pos)
    if p_start == -1:
        raise RuntimeError("Could not locate paragraph boundary before heading")
    return doc_xml[:p_start] + insert_xml + doc_xml[p_start:]


def main() -> None:
    if not SOURCE_DOCX.exists():
        raise FileNotFoundError(SOURCE_DOCX)
    for path, _, _ in FIGURES:
        if not path.exists():
            raise FileNotFoundError(path)

    FIGURE_DIR.mkdir(exist_ok=True)
    archive_figures = []
    for src, caption, archive_name in FIGURES:
        dst = FIGURE_DIR / archive_name
        shutil.copyfile(src, dst)
        archive_figures.append((dst, caption, archive_name))

    shutil.copyfile(SOURCE_DOCX, OUT_DOCX)
    tmp_docx = OUT_DOCX.with_suffix(".tmp.docx")

    with zipfile.ZipFile(OUT_DOCX, "r") as zin:
        doc_xml = zin.read("word/document.xml").decode("utf-8")
        rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        content_types = zin.read("[Content_Types].xml").decode("utf-8")

        rid_start = 1000
        while f"rIdTestFig{rid_start}" in rels:
            rid_start += 100
        docpr_start = next_docpr_id(doc_xml)

        insert_xml = build_insert_xml(FIGURES, rid_start, docpr_start)
        doc_xml = insert_before_heading(doc_xml, insert_xml, INSERT_BEFORE)

        content_types = ensure_content_type(content_types, "png", "image/png")
        content_types = ensure_content_type(content_types, "jpg", "image/jpeg")
        content_types = ensure_content_type(content_types, "jpeg", "image/jpeg")

        rel_insert = []
        media_entries = []
        for offset, (path, _, archive_name) in enumerate(FIGURES):
            rid = f"rIdTestFig{rid_start + offset}"
            media_name = f"test_figure_{offset + 1}{path.suffix.lower()}"
            rel_insert.append(
                f'<Relationship Id="{rid}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="media/{media_name}"/>'
            )
            media_entries.append((path, f"word/media/{media_name}"))
        rels = rels.replace("</Relationships>", "".join(rel_insert) + "</Relationships>")

        with zipfile.ZipFile(tmp_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc_xml.encode("utf-8"))
                elif item.filename == "word/_rels/document.xml.rels":
                    zout.writestr(item, rels.encode("utf-8"))
                elif item.filename == "[Content_Types].xml":
                    zout.writestr(item, content_types.encode("utf-8"))
                else:
                    zout.writestr(item, zin.read(item.filename))
            for path, target in media_entries:
                zout.write(path, target)

    tmp_docx.replace(OUT_DOCX)
    print(OUT_DOCX)
    for path, _, _ in archive_figures:
        print(path)


if __name__ == "__main__":
    main()
