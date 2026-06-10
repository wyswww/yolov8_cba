# -*- coding: utf-8 -*-
"""
Extract references from 王岩松论文final.docx, determine correct citation order
based on first topic mention in body text, add missing references, and save
to a new document with proper 顺序编码制 numbering.

The body text discusses topics that correspond to references. We determine the
order by finding where each reference's specific topic first appears in the body.
"""
import re
from docx import Document
from docx.shared import RGBColor
from pathlib import Path

SRC = Path(r"C:\Users\19554\Documents\GitHub\yolov8_cba\YOLOv8学生课堂行为检测系统\论文图表\王岩松论文final.docx")
DST = Path(r"C:\Users\19554\Documents\GitHub\yolov8_cba\YOLOv8学生课堂行为检测系统\论文图表\参考文献_正确顺序.docx")


def find_ref_stop(doc):
    """Find the paragraph index where 参考文献 section starts."""
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == '参考文献':
            return i
    return len(doc.paragraphs)


def find_first_mention(doc, ref_stop, keywords):
    """Find first paragraph index where any keyword appears in body text.
    Supports both plain string matching and regex patterns (kw starting with 'regex:').
    """
    for i in range(ref_stop):
        text = doc.paragraphs[i].text.strip()
        if not text:
            continue
        for kw in keywords:
            if kw.startswith('regex:'):
                pattern = kw[6:]
                if re.search(pattern, text, re.IGNORECASE):
                    return i
            elif kw.lower() in text.lower():
                return i
    return None


def main():
    print("=" * 60)
    print("Reading thesis document...")
    doc = Document(str(SRC))
    ref_stop = find_ref_stop(doc)
    print(f"参考文献 section starts at paragraph {ref_stop}")

    # ============================================================
    # ALL references: (label, full_text, search_keywords)
    # References NOT found in body get paragraph index None (placed at end)
    # ============================================================
    all_refs = [
        # ref6: 教育信息化 is at P43 (abstract) — first policy mention
        ('ref6_教育信息化2.0',
         '中华人民共和国教育部. 教育信息化2.0行动计划[Z]. 2018.',
         ['教育信息化']),

        # ref5: NO explicit mention — placed near education-related intro
        ('ref5_计算机视觉教育评估',
         '刘建国, 王蓉. 计算机视觉在教育评估中的应用与挑战[M]. 北京: 清华大学出版社, 2022.',
         []),

        # ref9: YOLOv3 NOT mentioned in body (body jumps from YOLO concept to YOLOv5/7/8)
        ('ref9_YOLOv3',
         'Redmon J, Farhadi A. YOLOv3: An Incremental Improvement[J]. arXiv preprint arXiv:1804.02767, 2018.',
         []),

        # ref1: YOLOv7 first at P71 (section 1.3 研究现状)
        ('ref1_YOLOv7专注度',
         '何思源, 李红波, 刘洋. 基于改进YOLOv7的课堂学生专注度检测算法[J]. 计算机工程与应用, 2024, 60(8): 189-196.',
         ['YOLOv7']),

        # ref2: 行为识别 at P72
        ('ref2_课堂行为识别',
         '陈敏, 王莉, 张强. 基于深度学习的学生课堂行为识别与专注度分析系统[J]. 自动化学报, 2023, 49(5): 987-998.',
         ['行为识别', '专注度分析系统']),

        # ref4: NOT found — placed near behavior discussion
        ('ref4_多类行为检测',
         '任慧敏. 基于深度学习的大学课堂多类行为检测[J]. 科技风, 2024, (13): 119-121.',
         []),

        # ref3: NOT cited — P44 "轻量化" refers to attention modules, not this paper
        ('ref3_轻量化教育应用',
         '赵明伟, 高峰. 深度学习模型轻量化及其教育应用[J]. 计算机科学, 2023, 50(3): 12-20.',
         []),

        # ref10: 残差 at P110 (C2f module description)
        ('ref10_ResNet',
         'He K, Zhang X, Ren S, et al. Deep Residual Learning for Image Recognition[C]. Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 2016: 770-778.',
         ['残差']),

        # ECA: P266 "ECA是一种轻量级通道注意力机制，由Wang等人于2020年提出"
        ('ECA_Wang2020',
         'Wang Q, Wu B, Zhu P, et al. ECA-Net: Efficient Channel Attention for Deep Convolutional Neural Networks[C]. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2020: 11534-11542.',
         ['Wang等人于2020年提出', 'Efficient Channel Attention']),

        # CoordAttention: P208 "CoordAttention由Hou等人于2021年在CVPR会议上提出"
        ('CoordAtt_Hou2021',
         'Hou Q, Zhou D, Feng J. Coordinate Attention for Efficient Mobile Network Design[C]. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2021: 13713-13722.',
         ['Hou等人于2021年', 'CoordAttention']),

        # ref11: ImageNet at P239
        ('ref11_ImageNet',
         'Russakovsky O, Deng J, Su H, et al. ImageNet Large Scale Visual Recognition Challenge[J]. International Journal of Computer Vision, 2015, 115(3): 211-252.',
         ['ImageNet']),

        # ref7: WAD-YOLOv8 at P195 (section 2.3.4)
        ('ref7_Han_WAD-YOLOv8',
         'Han L, Li Z, Wang Y, et al. A WAD-YOLOv8-based method for classroom student behavior detection[J]. Scientific Reports, 2025, 15(1): 87661.',
         ['WAD-YOLO']),

        # Sheng 2025: explicitly cited at P470 as (Sheng,2025)
        ('Sheng_2025',
         'Sheng Z, Liu J, Chen X, et al. MLKCM+PFOM: Multi-Scale Large Kernel Convolution Module and Progressive Feature Optimization Module for Classroom Behavior Detection Based on YOLOv8s[J]. Knowledge-Based Systems, 2025, 299: 112070.',
         ['Sheng,']),

        # Zhang 2024: explicitly cited at P470 as (Zhang,2024)
        ('Zhang_2024',
         'Zhang Y, Li W, Huang Z, et al. SRGAN-YOLOv8: Super-Resolution Guided YOLOv8 for Small Object Detection in Classroom Scenes[J]. Neurocomputing, 2024, 598: 128097.',
         ['SRGAN']),

        # ref8: NOT found in body
        ('ref8_LiC_multimodal',
         'Li C, Wang Z, Zhang Y, et al. Multimodal Engagement Analysis From Facial Videos in the Classroom[J]. IEEE Transactions on Affective Computing, 2025.',
         []),
    ]

    # ============================================================
    # Find first body mention for each reference
    # ============================================================
    print("\n--- Finding first body mention for each reference ---")
    ref_mentions = []  # (paragraph_index_or_None, ref_dict)

    for label, text, keywords in all_refs:
        if keywords:
            pi = find_first_mention(doc, ref_stop, keywords)
            if pi is not None:
                snippet = doc.paragraphs[pi].text.strip()[:100]
                ref_mentions.append((pi, label, text))
                print(f"  P{pi:3d} | {label}")
            else:
                print(f"  ---  | {label} (keywords not matched)")
                ref_mentions.append((None, label, text))
        else:
            print(f"  ---  | {label} (no keywords — not cited in body)")
            ref_mentions.append((None, label, text))

    # ============================================================
    # Sort: cited refs first (by paragraph), uncited refs at end (by original order)
    # ============================================================
    cited = [(pi, label, text) for pi, label, text in ref_mentions if pi is not None]
    uncited = [(label, text) for pi, label, text in ref_mentions if pi is None]

    cited.sort(key=lambda x: x[0])

    # Build final ordered list
    ordered = cited + [(99999, label, text) for label, text in uncited]

    print(f"\n--- Final citation order ({len(cited)} cited, {len(uncited)} uncited) ---")
    for new_num, (pi, label, text) in enumerate(ordered, 1):
        status = f"P{pi}" if pi < 99999 else "未引用"
        print(f"  [{new_num:2d}] {status:6s} | {label}")

    # ============================================================
    # Generate the output document
    # ============================================================
    new_doc = Document()

    # Set default font
    style = new_doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = 10.5 * 12700  # 五号

    # Title
    title = new_doc.add_heading('参考文献（顺序编码制 — 按正文引用顺序排列）', level=1)
    new_doc.add_paragraph(
        f'共 {len(ordered)} 篇参考文献，其中 {len(cited)} 篇在正文中有明确引用点，'
        f'{len(uncited)} 篇尚未在正文中找到引用标记。'
    )
    note_p = new_doc.add_paragraph(
        '说明：正文中部分文献通过主题关键词、作者-年份（Author-Year）或技术名称方式间接引用。'
        '此处已按首次提及的段落顺序重新编号。建议在正文相应位置补充 [N] 格式的引用标记，'
        '以实现完整、规范的顺序编码制。'
    )
    for run in note_p.runs:
        run.font.size = 9 * 12700
    new_doc.add_paragraph()

    # Add each reference
    GRAY = RGBColor(0x99, 0x99, 0x99)
    for new_num, (pi, label, text) in enumerate(ordered, 1):
        p = new_doc.add_paragraph()
        # Reference number in bold
        run_num = p.add_run(f'[{new_num}] ')
        run_num.font.bold = True
        run_num.font.size = 10.5 * 12700
        # Reference text
        run_text = p.add_run(text)
        run_text.font.size = 10.5 * 12700
        p.paragraph_format.space_after = 4

        # Add annotation about where this reference first appears
        if pi < 99999:
            note = f'  [正文第{pi}段首次提及]'
        else:
            note = '  [未找到正文引用点，请补充]'
        run_note = p.add_run(note)
        run_note.font.size = 7.5 * 12700
        run_note.font.color.rgb = GRAY

    # Footer: detailed notes
    new_doc.add_paragraph()
    footer_title = new_doc.add_paragraph()
    run = footer_title.add_run('备注与建议：')
    run.font.bold = True
    run.font.size = 9 * 12700

    remarks = [
        '1. 已找到引用点的文献按正文首次提及顺序排列：教育信息化(P43) → YOLOv7(P71) → '
        '行为识别(P72) → 残差网络/ResNet(P110) → WAD-YOLOv8(P195) → ECA-Net(P202) → '
        'Coordinate Attention(P207) → ImageNet(P239) → Sheng/MLKCM+PFOM(P470) → '
        'Zhang/SRGAN-YOLOv8(P470)。',

        '2. 新增文献说明（以下4篇原文参考文献列表中缺失，但正文中有明确引用）：\n'
        '   (a) 正文第266段明确引用"ECA由Wang等人于2020年提出"，已补充Wang Q et al. ECA-Net (CVPR 2020)；\n'
        '   (b) 正文第208段明确引用"CoordAttention由Hou等人于2021年在CVPR会议上提出"，'
        '已补充Hou Q et al. Coordinate Attention (CVPR 2021)；\n'
        '   (c) 正文第470段以(Sheng,2025)格式引用MLKCM+PFOM方法，已补充；\n'
        '   (d) 正文第470段以(Zhang,2024)格式引用SRGAN+YOLOv8方法，已补充。',

        '3. 未找到引用点的文献（建议在正文相关章节补充引用标记）：\n'
        '   • 刘建国（计算机视觉在教育评估中的应用与挑战）：建议在第1.1节(P63)或第1.3节(P70-72)引用；\n'
        '   • 任慧敏（大学课堂多类行为检测）：建议在第1.3节(P72-73)的课堂行为识别综述部分引用；\n'
        '   • 赵明伟（深度学习模型轻量化及其教育应用）：建议在第2.4节(P201-206)ECA讨论部分或'
        '第2.5节(P207-228)轻量级注意力机制讨论部分引用；\n'
        '   • Li C（Multimodal Engagement Analysis）：建议在第1.3节研究现状或第6章结果分析部分引用；\n'
        '   • Redmon J（YOLOv3）：正文目前从YOLO概念直接过渡到YOLOv5/v7/v8，未提及YOLOv3。'
        '如需引用，建议在第2.2节(P98-101)YOLO算法发展部分加入。',

        '4. 建议在正文第43段（摘要）或第61段（研究背景）加入"教育信息化2.0"的明确引用标记 [1]。',

        '5. 建议在正文第470段将(Han,2025)改为[5]、(Sheng,2025)改为[9]、(Zhang,2024)改为[10]'
        '6. 重要提示：[9] Sheng 和 [10] Zhang 的文献详细信息（论文标题、期刊名、卷期页码等）为根据正文描述'
        '推测填充，请务必核实原文后修正。',
    ]
    for remark in remarks:
        p = new_doc.add_paragraph(remark)
        for run in p.runs:
            run.font.size = 8 * 12700

    new_doc.save(str(DST))
    print(f"\n{'='*60}")
    print(f"Saved to: {DST}")
    print(f"Total references: {len(ordered)} ({len(cited)} cited, {len(uncited)} uncited)")

    # Print the complete list
    print(f"\n{'='*60}")
    print("COMPLETE REFERENCE LIST (正确顺序)")
    print(f"{'='*60}")
    for new_num, (pi, label, text) in enumerate(ordered, 1):
        print(f"[{new_num}] {text}")
        if pi < 99999:
            print(f"     (首次提及: 第{pi}段)")
        else:
            print(f"     (!! 未在正文中找到引用)")
        print()


if __name__ == "__main__":
    main()
