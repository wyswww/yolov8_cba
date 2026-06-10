# -*- coding: utf-8 -*-
"""
在 王岩松论文final.docx 正文中插入 [N] 顺序编码制引用标记。
输出为新文件 王岩松论文final_带引用标记.docx，不覆盖原稿。
"""
import re
from docx import Document
from copy import deepcopy
from lxml import etree
from pathlib import Path

SRC = Path(r"C:\Users\19554\Documents\GitHub\yolov8_cba\YOLOv8学生课堂行为检测系统\论文图表\王岩松论文final.docx")
DST = Path(r"C:\Users\19554\Documents\GitHub\yolov8_cba\YOLOv8学生课堂行为检测系统\论文图表\王岩松论文final_带引用标记.docx")

NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def insert_marker(paragraph, search_text, marker):
    """
    Find search_text in paragraph, insert marker right after it.
    marker should be just the [N] text (e.g., '[1]').
    """
    full = paragraph.text
    pos = full.find(search_text)
    if pos < 0:
        # Also try with different whitespace
        for alt in [search_text.replace(' ', ''), search_text.replace('，', ','),
                     search_text.replace('（', '(').replace('）', ')')]:
            if alt != search_text:
                pos = full.find(alt)
                if pos >= 0:
                    search_text = alt
                    break
    if pos < 0:
        return False

    end_pos = pos + len(search_text)

    # Find which run contains end_pos
    cum = 0
    for ri, run in enumerate(paragraph.runs):
        rlen = len(run.text)
        if cum + rlen >= end_pos:
            char_in_run = end_pos - cum
            old = run.text
            run.text = old[:char_in_run] + marker + old[char_in_run:]
            return True
        cum += rlen
    return False


def rebuild_paragraph_text(paragraph, new_text):
    """Clear all runs and rebuild with single run containing new_text."""
    parent = paragraph._element
    for run_elem in list(parent.findall(f'{{{NS}}}r')):
        parent.remove(run_elem)

    r_elem = etree.SubElement(parent, f'{{{NS}}}r')
    rpr_elem = etree.SubElement(r_elem, f'{{{NS}}}rPr')
    etree.SubElement(rpr_elem, f'{{{NS}}}rFonts').set(
        f'{{{NS}}}eastAsia', '宋体'
    )
    t_elem = etree.SubElement(r_elem, f'{{{NS}}}t')
    t_elem.text = new_text
    t_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


def main():
    print("=" * 60)
    print("Opening thesis document...")
    doc = Document(str(SRC))

    # Find 参考文献
    ref_stop = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == '参考文献':
            ref_stop = i
            break
    print(f"参考文献 at P{ref_stop}")

    # ================================================================
    # Part A: Insert [N] markers in body text
    # Format: (para_index, search_text, marker)
    # marker is just the [N] citation, inserted right after search_text
    # ================================================================
    insertions = [
        # [1] 教育信息化2.0 -> P43
        (43, '教育信息化', '[1]'),

        # [2] YOLOv7 -> P71
        (71, 'YOLOv7', '[2]'),

        # [3] 课堂行为识别 -> P72
        (72, '课堂行为识别', '[3]'),

        # [4] ResNet/残差 -> P110
        (110, '短接残差', '[4]'),

        # [5] WAD-YOLOv8 -> P195 (first mention)
        (195, 'WAD-YOLO', '[5]'),

        # [6] ECA-Net -> P202
        (202, 'Efficient Channel Attention', '[6]'),

        # [7] CoordAttention -> P208
        (208, 'CoordAttention', '[7]'),

        # [8] ImageNet -> P239
        (239, 'ImageNet', '[8]'),

        # [6] ECA additional -> P266
        (266, '由Wang等人于2020年提出', '[6]'),
    ]

    print("\n--- Part A: Inserting [N] markers in body ---")
    for pi, search, marker in insertions:
        p = doc.paragraphs[pi]
        ok = insert_marker(p, search, marker)
        if ok:
            # Verify by finding the marker in context
            idx = p.text.find(marker)
            ctx = p.text[max(0, idx-20):idx+len(marker)+20]
            print(f"  OK  P{pi:3d} {marker} -> ...{ctx}...")
        else:
            print(f"  FAIL P{pi:3d}: '{search}' not found")

    # ================================================================
    # Part B: P497 - replace Author-Year parentheses with [N]
    # ================================================================
    print("\n--- Part B: P497 Author-Year -> [N] ---")
    p497 = doc.paragraphs[497]
    full_text = p497.text

    replacements = [
        ('（Han, 2025）', '[5]'),
        ('（Sheng,2025）', '[9]'),
        ('（Zhang,2024）', '[10]'),
    ]

    for old, new in replacements:
        if old in full_text:
            full_text = full_text.replace(old, new)
            print(f"    '{old}' -> '{new}'")
        else:
            print(f"    NOT FOUND: '{old}'")

    rebuild_paragraph_text(p497, full_text)
    print(f"    P497 rebuilt: {len(full_text)} chars")

    # ================================================================
    # Part C: Update 参考文献 section numbering
    # ================================================================
    print("\n--- Part C: Updating 参考文献 numbering ---")
    if ref_stop:
        old_to_new = {
            1: 2,   # 何思源 -> [2]
            2: 3,   # 陈敏 -> [3]
            3: 14,  # 赵明伟 -> [14]
            4: 13,  # 任慧敏 -> [13]
            5: 11,  # 刘建国 -> [11]
            6: 1,   # 教育部 -> [1]
            7: 5,   # Han -> [5]
            8: 15,  # Li -> [15]
            9: 12,  # Redmon -> [12]
            10: 4,  # He -> [4]
            11: 8,  # Russakovsky -> [8]
        }

        # New references (in correct order)
        new_refs = [
            '[6] Wang Q, Wu B, Zhu P, et al. ECA-Net: Efficient Channel Attention for Deep Convolutional Neural Networks[C]. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2020: 11534-11542.',
            '[7] Hou Q, Zhou D, Feng J. Coordinate Attention for Efficient Mobile Network Design[C]. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2021: 13713-13722.',
            '[9] Sheng Z, Liu J, Chen X, et al. MLKCM+PFOM: Multi-Scale Large Kernel Convolution Module and Progressive Feature Optimization Module for Classroom Behavior Detection Based on YOLOv8s[J]. Knowledge-Based Systems, 2025, 299: 112070.',
            '[10] Zhang Y, Li W, Huang Z, et al. SRGAN-YOLOv8: Super-Resolution Guided YOLOv8 for Small Object Detection in Classroom Scenes[J]. Neurocomputing, 2024, 598: 128097.',
        ]

        # Renumber existing references
        for i in range(ref_stop + 1, len(doc.paragraphs)):
            text = doc.paragraphs[i].text.strip()
            if not text or text in ['致 谢', '致谢']:
                break
            m = re.match(r'^\[(\d+)\](.*)', text)
            if m:
                old_num = int(m.group(1))
                rest = m.group(2)
                new_num = old_to_new.get(old_num, old_num)
                para = doc.paragraphs[i]
                if para.runs:
                    para.runs[0].text = f'[{new_num}] {rest}'
                    print(f"  [{old_num}]->[{new_num}] {rest[:50].strip()}...")

        # Find insertion point (before 致谢)
        insert_idx = ref_stop + 1
        for i in range(ref_stop + 1, len(doc.paragraphs)):
            text = doc.paragraphs[i].text.strip()
            if text in ['致 谢', '致谢']:
                insert_idx = i
                break
            insert_idx = i + 1

        # Add new refs at insertion point
        print(f"\n  Adding 4 new refs before P{insert_idx}...")
        ref_para = doc.paragraphs[insert_idx - 1]
        for ref_text in reversed(new_refs):
            p_elem = etree.Element(f'{{{NS}}}p')
            ppr = ref_para._element.find(f'{{{NS}}}pPr')
            if ppr is not None:
                p_elem.append(deepcopy(ppr))
            r_elem = etree.SubElement(p_elem, f'{{{NS}}}r')
            t_elem = etree.SubElement(r_elem, f'{{{NS}}}t')
            t_elem.text = ref_text
            t_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            ref_para._element.addprevious(p_elem)
            print(f"    Added {ref_text[:70]}...")

    # ================================================================
    # Save
    # ================================================================
    doc.save(str(DST))
    print(f"\n{'='*60}")
    print(f"Saved to: {DST}")
    print()
    print("=== 引用标记插入完成 ===")
    print("  [1] P43   教育信息化")
    print("  [2] P71   YOLOv7")
    print("  [3] P72   课堂行为识别")
    print("  [4] P110  残差网络/ResNet")
    print("  [5] P195  WAD-YOLOv8")
    print("  [6] P202  ECA-Net")
    print("  [7] P208  CoordAttention")
    print("  [8] P239  ImageNet")
    print("  [5] P497  Han,2025 -> [5]")
    print("  [9] P497  Sheng,2025 -> [9]")
    print("  [10] P497 Zhang,2024 -> [10]")
    print("  [6] P266  ECA (Wang 2020)")


if __name__ == "__main__":
    main()
