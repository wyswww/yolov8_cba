# -*- coding: utf-8 -*-
"""Find ALL citation mentions in the thesis body text."""
import re, sys
from docx import Document
from pathlib import Path

SRC = Path(r"C:\Users\19554\Documents\GitHub\yolov8_cba\YOLOv8学生课堂行为检测系统\论文图表\王岩松论文final.docx")
doc = Document(str(SRC))

# Find 参考文献 boundary
ref_stop = len(doc.paragraphs)
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == '参考文献':
        ref_stop = i
        break

# ==========================================
# Helper: get context around a match
# ==========================================
def get_context(text, keyword, before=50, after=120):
    """Get text context around a keyword match."""
    idx = text.lower().find(keyword.lower())
    if idx < 0:
        return text[:200]
    start = max(0, idx - before)
    end = min(len(text), idx + len(keyword) + after)
    ctx = text[start:end]
    if start > 0:
        ctx = "..." + ctx
    if end < len(text):
        ctx = ctx + "..."
    return ctx

# ==========================================
# 1. ALL Author-Year style citations
# ==========================================
print("=" * 70)
print("一、Author-Year 格式引用")
print("=" * 70)

pat_chinese = re.compile(r'（([A-Z][a-z]+[\s,]*\d{4})）')
pat_english = re.compile(r'\(([A-Z][a-z]+[\s,]*\d{4})\)')

found = []
for pi in range(ref_stop):
    text = doc.paragraphs[pi].text
    for m in pat_chinese.finditer(text):
        found.append((pi, m.group(1), "中文括号（）", m.start()))
    for m in pat_english.finditer(text):
        found.append((pi, m.group(1), "英文括号()", m.start()))

# Filter non-citation matches
valid = []
for pi, cit, style, pos in found:
    # Must start with capital letter
    if re.match(r'^[A-Z][a-z]+', cit.strip()):
        valid.append((pi, cit, style))

for pi, cit, style in valid:
    ctx = get_context(doc.paragraphs[pi].text, cit)
    print("第{}段 ({}): ({})".format(pi, style, cit))
    print("   上下文: {}".format(ctx))
    print()

if not valid:
    print("  (未找到 Author-Year 格式引用)")
    print()

# ==========================================
# 2. Specific paper/model/author mentions
# ==========================================
print("=" * 70)
print("二、文献/模型/作者的具体提及")
print("=" * 70)

# (label, keywords, corresponding_reference)
targets = [
    ("教育信息化2.0 (教育部, 2018)", ["教育信息化2.0", "教育信息化 2.0"], "[原1] / 现[1]"),
    ("YOLOv7 (何思源等, 2024)", ["YOLOv7"], "[原1] / 现[2]"),
    ("课堂行为识别 (陈敏等, 2023)", ["行为识别"], "[原2] / 现[3]"),
    ("模型轻量化 (赵明伟等, 2023)", ["模型轻量化"], "[原3] / 现[14]"),
    ("多类行为检测 (任慧敏, 2024)", ["多类行为"], "[原4] / 现[13]"),
    ("计算机视觉在教育评估 (刘建国等, 2022)", ["教育评估"], "[原5] / 现[11]"),
    ("YOLOv3 (Redmon等, 2018)", ["YOLOv3"], "[原9] / 现[12]"),
    ("ResNet/残差网络 (He等, 2016)", ["残差"], "[原10] / 现[4]"),
    ("ImageNet (Russakovsky等, 2015)", ["ImageNet"], "[原11] / 现[8]"),
    ("WAD-YOLOv8 (Han等, 2025)", ["WAD-YOLO"], "[原7] / 现[5]"),
    ("ECA-Net (Wang等, 2020) **新增**", ["Wang等人于2020", "Efficient Channel Attention"], "新增 → 现[6]"),
    ("CoordAttention (Hou等, 2021) **新增**", ["Hou等人于2021", "CoordAttention", "Coordinate Attention"], "新增 → 现[7]"),
    ("MLKCM+PFOM (Sheng等, 2025) **新增**", ["Sheng,", "MLKCM"], "新增 → 现[9]"),
    ("SRGAN+YOLOv8 (Zhang等, 2024) **新增**", ["SRGAN", "Zhang,.*2024"], "新增 → 现[10]"),
    ("多模态参与度分析 (Li等, 2025)", ["Multimodal", "多模态"], "[原8] / 现[15]"),
    ("SENet", ["SENet"], "未列入参考文献"),
    ("Faster R-CNN", ["Faster R-CNN"], "未列入参考文献"),
    ("Fast R-CNN", ["Fast R-CNN"], "未列入参考文献"),
    ("SSD", ["SSD"], "未列入参考文献"),
    ("YOLOv5", ["YOLOv5"], "未列入参考文献"),
    ("YOLOv8 (Ultralytics)", ["Ultralytics"], "未列入参考文献(工具/框架)"),
    ("COCO (Microsoft)", ["COCO"], "未列入参考文献(数据集)"),
]

for label, keywords, ref_mapping in targets:
    found_paras = []
    for pi in range(ref_stop):
        text = doc.paragraphs[pi].text
        if not text.strip():
            continue
        for kw in keywords:
            if kw.startswith("Zhang,"):
                if re.search(kw, text):
                    found_paras.append((pi, kw))
                    break
            elif kw.lower() in text.lower():
                found_paras.append((pi, kw))
                break

    if found_paras:
        pi_first, kw_first = found_paras[0]
        ctx = get_context(doc.paragraphs[pi_first].text, kw_first)
        print("【{}】 -> {}".format(label, ref_mapping))
        print("  首次: 第{}段 (匹配词: \"{}\")".format(pi_first, kw_first))
        print("  上下文: {}".format(ctx))
        if len(found_paras) > 1:
            other_paras = [str(p) for p, _ in found_paras[1:6]]
            print("  其他出现段落: {}".format(", ".join(other_paras)))
        print()

# ==========================================
# 3. Any numbered citation markers [N]
# ==========================================
print("=" * 70)
print("三、方括号 [N] 编号引用标记（正文中）")
print("=" * 70)
bracket_count = 0
for pi in range(ref_stop):
    text = doc.paragraphs[pi].text.strip()
    if not text:
        continue
    # Find standalone [number] patterns (not part of parameter ranges like [0.88, 1.12])
    matches = re.findall(r'(?<![a-zA-Z0-9.])\[(\d{1,2})\](?![a-zA-Z0-9.])', text)
    if matches:
        bracket_count += 1
        ctx = text[:250]
        print("第{}段: [{}] citations found".format(pi, ", ".join(matches)))
        print("  文本: {}".format(ctx))
        print()
if bracket_count == 0:
    print("  ** 正文中未找到任何 [N] 格式的编号引用标记！**")
    print("  论文目前使用的是主题/技术名称间接引用 + 少量Author-Year引用，")
    print("  尚需在正文中所有提及相关文献的位置插入 [1], [2], ... 引用标记。")
    print()

# ==========================================
# 4. Summary table
# ==========================================
print("=" * 70)
print("四、总结：正文引用情况一览")
print("=" * 70)
print()
print("  论文正文中【没有】使用 [N] 编号引用标记。")
print("  实际引用方式有两种：")
print()
print("  方式1 — Author-Year 引用（仅第470段）:")
print("    第470段出现 (Han, 2025)、(Sheng,2025)、(Zhang,2024) 三处")
print("    这是论文中唯一的显式作者-年份引用。")
print()
print("  方式2 — 主题/技术名称间接引用（散见于全文）:")
print("    教育信息化 → 第43段（摘要）、第61段（1.1节）")
print("    YOLOv7 → 第71段（1.3节 研究现状）")
print("    行为识别 → 第72段（1.3节）")
print("    残差 → 第110段（2.3.1节 C2f模块）")
print("    WAD-YOLO → 第195段（2.3.4节 训练策略）")
print("    ECA → 第202段（2.4节）、第266段（3.5节，提及Wang 2020）")
print("    CoordAttention → 第207段（2.5节）、第208段（提及Hou 2021 CVPR）")
print("    ImageNet → 第239段（2.7节 迁移学习）")
print("    Sheng / Zhang → 第470段（4.5节 对比实验）")
print()
print("  方式3 — 无任何引用标记（以下文献仅在参考文献列表中，正文未提及）:")
print("    刘建国(教育评估), 赵明伟(轻量化), 任慧敏(多类行为), Redmon(YOLOv3), Li(多模态)")
print()
