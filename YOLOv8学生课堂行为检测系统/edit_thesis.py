# -*- coding: utf-8 -*-
"""Edit wangyansong thesis docx to update CoordAtt+ECA v2 results and narrative."""

import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
from copy import deepcopy
from docx.oxml.ns import qn

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "王岩松论文final_1y.docx")
DST = os.path.join(ROOT, "王岩松论文final_1y_updated.docx")

print("Loading document...")
doc = Document(SRC)

# ===== HELPER =====
def find_para(doc, fragment):
    """Return (index, para) of first paragraph containing fragment."""
    for i, p in enumerate(doc.paragraphs):
        if fragment in p.text:
            return i, p
    return None, None

def full_text(para):
    return "".join(r.text for r in para.runs)

def replace_in_runs(para, old, new):
    """Replace old->new in paragraph runs."""
    for r in para.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return True
    return False

def insert_para_after(para, text):
    """Insert a new paragraph after the given paragraph element."""
    new_elem = deepcopy(para._element)
    for r in new_elem.findall(qn('w:r')):
        for t in r.findall(qn('w:t')):
            t.text = ""
    first_t = new_elem.find('.//' + qn('w:t'))
    if first_t is not None:
        first_t.text = text
        first_t.set(qn('xml:space'), 'preserve')
    para._element.addnext(new_elem)

def clear_para(para):
    """Clear all text in a paragraph's runs."""
    for r in para.runs:
        r.text = ""

def set_first_run(para, text):
    """Set text on first run, clear others."""
    clear_para(para)
    if para.runs:
        para.runs[0].text = text

# ===== STEP 1: Chinese Abstract =====
print("[1/8] Chinese abstract...")
idx, para = find_para(doc, "高分辨率推理测试以及高分辨率弱增强二阶段微调实验")
if idx and "CoordAtt" not in para.text:
    replaced = False
    for r in para.runs:
        if "高分辨率推理测试以及高分辨率弱增强二阶段微调实验" in r.text:
            r.text = r.text.replace(
                "高分辨率推理测试以及高分辨率弱增强二阶段微调实验",
                "CoordAtt与ECA组合注意力实验、高分辨率推理测试以及高分辨率弱增强二阶段微调实验")
            print("  OK Chinese abstract updated")
            replaced = True
            break
    if not replaced:
        print("  WARN: target run not found")
else:
    print("  SKIP: already updated or not found")

# ===== STEP 2: English Abstract =====
print("[2/8] English abstract...")
idx, para = find_para(doc, "high-resolution inference testing")
if idx and "CoordAtt" not in para.text:
    for r in para.runs:
        if "high-resolution inference testing, and high-resolution weak-augmentation two-stage fine-tuning" in r.text:
            r.text = r.text.replace(
                "high-resolution inference testing, and high-resolution weak-augmentation two-stage fine-tuning",
                "CoordAtt+ECA combined attention experiments, high-resolution inference testing, and high-resolution weak-augmentation two-stage fine-tuning")
            print("  OK English abstract updated")
            break
else:
    print("  SKIP: already updated or not found")

# ===== STEP 3: Add weak aug paragraph after 3.5.3 =====
print("[3/8] Adding weak augmentation explanation to 3.5.3...")
idx, para = find_para(doc, "互补的信息增强路径")
if idx:
    # Check if already added
    next_p = doc.paragraphs[idx + 1] if idx + 1 < len(doc.paragraphs) else None
    if next_p and ("Mosaic" in next_p.text or "强增强" in next_p.text or "数据增强策略" in next_p.text):
        print("  SKIP: already exists")
    else:
        new_text = (
            "在数据增强策略方面，由于CoordAtt的核心机制是沿X轴和Y轴分别编码空间位置信息，"
            "其生成的注意力权重直接依赖于特征图中目标的真实空间位置。Mosaic增强将四张不同图像"
            "随机拼接为一张训练样本，MixUp将两张图像按比例混合——这两种强增强手段产生的训练"
            "样本不具备真实的X/Y位置对应关系，会严重破坏CoordAtt所需的空间坐标信息，导致"
            "注意力权重学习到错误的位置映射。因此，本文在该实验中完全关闭了Mosaic、MixUp和"
            "Copy-Paste增强（均设为0），并将旋转角度降至3.0度、平移降至0.05、尺度缩放降至"
            "0.15、剪切降至1.0度，仅保留轻微的HSV颜色扰动和水平翻转，以在数据多样性和空间"
            "信息保真之间取得平衡。这一针对性调整是CoordAtt+ECA组合方案成功的关键前提。"
        )
        insert_para_after(para, new_text)
        print("  OK added weak augmentation paragraph")
else:
    print("  WARN: 3.5.3 ending not found, trying alternatives...")
    # Try to find 3.5.3 section
    idx, para = find_para(doc, "CoordAtt与ECA组合注意力模型")
    if idx:
        # Find the last paragraph before 3.6
        for i in range(idx, min(idx + 10, len(doc.paragraphs))):
            if "3.6" in doc.paragraphs[i].text and "训练策略" in doc.paragraphs[i].text:
                # Insert before 3.6
                target = doc.paragraphs[i - 1]
                new_text = (
                    "在数据增强策略方面，由于CoordAtt的核心机制是沿X轴和Y轴分别编码空间位置信息，"
                    "其生成的注意力权重直接依赖于特征图中目标的真实空间位置。Mosaic增强将四张不同图像"
                    "随机拼接为一张训练样本，MixUp将两张图像按比例混合——这两种强增强手段产生的训练"
                    "样本不具备真实的X/Y位置对应关系，会严重破坏CoordAtt所需的空间坐标信息，导致"
                    "注意力权重学习到错误的位置映射。因此，本文在该实验中完全关闭了Mosaic、MixUp和"
                    "Copy-Paste增强（均设为0），并将旋转角度降至3.0度、平移降至0.05、尺度缩放降至"
                    "0.15、剪切降至1.0度，仅保留轻微的HSV颜色扰动和水平翻转，以在数据多样性和空间"
                    "信息保真之间取得平衡。这一针对性调整是CoordAtt+ECA组合方案成功的关键前提。"
                )
                insert_para_after(target, new_text)
                print("  OK added weak augmentation paragraph (before 3.6)")
                break

# ===== STEP 4: Update Table 4.5 =====
print("[4/8] Updating Table 4.5 results...")
found = False
for ti, table in enumerate(doc.tables):
    for ri, row in enumerate(table.rows):
        cells_text = [cell.text.strip() for cell in row.cells]
        row_str = " ".join(cells_text)
        if "CoordAtt" in row_str and "ECA" in row_str:
            print(f"  Found CoordAtt+ECA row in table {ti}, row {ri}")
            print(f"  Current cells: {cells_text}")
            # Update: Precision, Recall, mAP50, mAP50-95
            # Find cells with percentage values
            for ci, cell in enumerate(row.cells):
                for p in cell.paragraphs:
                    for r in p.runs:
                        txt = r.text.strip()
                        if "82.82" in txt or "82.82%" in txt:
                            r.text = "93.92%"
                            print(f"    Updated cell {ci}: 82.82% -> 93.92%")
                        elif "80.17" in txt or "80.17%" in txt:
                            r.text = "92.04%"
                            print(f"    Updated cell {ci}: 80.17% -> 92.04%")
                        elif "84.59" in txt or "84.59%" in txt:
                            r.text = "96.25%"
                            print(f"    Updated cell {ci}: 84.59% -> 96.25%")
                        elif "65.59" in txt or "65.59%" in txt:
                            r.text = "78.49%"
                            print(f"    Updated cell {ci}: 65.59% -> 78.49%")
            found = True
            break
    if found:
        break

if not found:
    print("  WARN: CoordAtt+ECA row not found in any table")
    # Dump table info for debugging
    for ti, table in enumerate(doc.tables):
        for ri, row in enumerate(table.rows[:3]):
            cells = [c.text[:30] for c in row.cells]
            print(f"  Table {ti} Row {ri}: {cells}")

# ===== STEP 5: Rewrite section 4.3.2 =====
print("[5/8] Rewriting section 4.3.2...")
# Search for the section heading first
idx, para = find_para(doc, "4.3.2")
if not idx:
    idx, para = find_para(doc, "网络结构改进对检测精度的影响")

if idx:
    # Find all paragraphs in this section (until 4.3.3)
    section_paras = []
    for i in range(idx + 1, min(idx + 20, len(doc.paragraphs))):
        pi = doc.paragraphs[i]
        if "4.3.3" in pi.text and "训练策略" in pi.text:
            break
        if pi.text.strip():
            section_paras.append((i, pi))

    print(f"  Found {len(section_paras)} body paragraphs in 4.3.2")

    new_texts = [
        "从表4-5可以看出，三种网络结构改进方案呈现出了显著的分化。ECA注意力模型（方案2）在测试集上的mAP@0.5仅为83.53%，低于Baseline(800) 6.40个百分点。P2高分辨率检测头（方案3）的mAP@0.5为83.77%，低于Baseline 6.16个百分点。上述两种方案均未能超过Baseline。然而，CoordAtt与ECA组合注意力模型（方案5）在针对性调整数据增强策略后，取得了mAP@0.5为96.25%、mAP@0.5:0.95为78.49%、Precision为93.92%、Recall为92.04%的结果，mAP@0.5较Baseline(800)提升6.32个百分点，综合性能仅次于Strong模型（方案6），是三种结构改进方案中唯一超过Baseline的方案。",

        "CoordAtt+ECA组合方案取得成功的核心原因有三点。第一，空间与通道的互补设计有效——CoordAtt在Backbone中提供空间位置感知，ECA在Neck中提供通道特征筛选，二者分别关注'在哪里'和'是什么'，形成了互补的信息增强路径，而非简单堆叠同类模块。第二，数据增强策略与注意力机制相匹配——方案5关闭了Mosaic、MixUp和Copy-Paste等强增强，最大程度保留了CoordAtt所需的真实空间位置信息。而方案1（原版CoordAtt+ECA实验，使用完整强增强）在测试集上仅获得84.59%的mAP@0.5，与方案5相差超过11个百分点，充分验证了'注意力机制的特性决定增强策略选择'这一核心观点。第三，方案5采用Ultralytics内置的load()方法按名称和形状自动匹配预训练权重，相比手动层映射方式更完整地保留了YOLOv8m的COCO预训练知识。",

        "ECA单一通道注意力（方案2）未能提升的原因在于，课堂行为检测高度依赖空间位置信息（如举手位置、身体朝向、头部与桌面的相对关系），而通道注意力仅关注'哪些通道重要'，完全丧失了空间位置感知，无法满足行为判别的空间语义需求。P2检测头（方案3）虽然提高了浅层特征的空间分辨率，但P2层特征的语义抽象程度较低，引入的大量浅层特征可能稀释了深层语义信息，同时新增检测分支需要从头学习，在数据集规模有限时难以收敛到有效状态。",

        "综上，本节实验表明：在课堂行为检测任务中，并非所有注意力机制均有效，也并非简单增加检测尺度即可提升性能。CoordAtt+ECA组合方案经过针对性增强策略调整后，证明了空间-通道互补的注意力设计在当前任务中的有效性，充分说明了注意力机制的效果不仅取决于模块本身的结构设计，更取决于与之匹配的训练策略。"
    ]

    # Assign texts to existing paragraphs
    for i, (si, sp) in enumerate(section_paras):
        if i < len(new_texts):
            set_first_run(sp, new_texts[i])
            print(f"  OK replaced paragraph {si}")

    # If we have more new texts than existing paragraphs, add extras
    if len(new_texts) > len(section_paras):
        last_para = section_paras[-1][1] if section_paras else para
        for i in range(len(section_paras), len(new_texts)):
            insert_para_after(last_para, new_texts[i])
            print(f"  OK inserted extra paragraph")
else:
    print("  WARN: 4.3.2 section not found")

# ===== STEP 6: Update 3.7 chapter summary =====
print("[6/8] Updating 3.7 chapter summary...")
idx, para = find_para(doc, "三种方法分别从通道维度")
if idx:
    for r in para.runs:
        if "三种方法分别从通道维度" in r.text:
            r.text = r.text.replace(
                "三种方法分别从通道维度、空间尺度和混合注意力三个角度尝试提升YOLOv8m的特征表示能力",
                "三种方法分别从通道维度、空间尺度和混合注意力三个角度尝试提升YOLOv8m的特征表示能力。其中，CoordAtt与ECA组合注意力方案在针对性调整增强策略后取得了显著效果，验证了空间-通道互补注意力设计的有效性")
            print("  OK updated 3.7 summary")
            break
else:
    print("  WARN: 3.7 summary text not found")

# ===== STEP 7: Update 7.x conclusion =====
print("[7/8] Updating conclusion...")
idx, para = find_para(doc, "单纯嵌入ECA注意力机制、增设P2检测头等结构性改动无法有效提升模型精度")
if not idx:
    idx, para = find_para(doc, "结构性改动无法有效提升模型精度")

if idx:
    for r in para.runs:
        if "结构性改动无法有效提升模型精度" in r.text or "单纯嵌入ECA" in r.text:
            r.text = r.text.replace(
                "单纯嵌入ECA注意力机制、增设P2检测头等结构性改动无法有效提升模型精度",
                "单纯嵌入ECA注意力机制、增设P2检测头等结构性改动无法有效提升模型精度，但CoordAtt与ECA组合注意力方案在匹配弱增强策略后取得了显著提升，验证了空间-通道互补设计的有效性")
            print("  OK updated conclusion")
            break
else:
    print("  WARN: conclusion paragraph not found")
    # Try a broader search
    for i, p in enumerate(doc.paragraphs):
        if "结构性改动" in p.text and "ECA" in p.text and "无法" in p.text:
            print(f"  Found at para {i}: {p.text[:120]}...")
            for r in p.runs:
                if "结构性改动" in r.text and "无法" in r.text:
                    # Insert CoordAtt mention
                    r.text = r.text.replace(
                        "单纯嵌入ECA注意力机制、增设P2检测头等结构性改动无法有效提升模型精度",
                        "单纯嵌入ECA注意力机制、增设P2检测头等结构性改动无法有效提升模型精度，但CoordAtt与ECA组合注意力方案在匹配弱增强策略后取得了显著提升，验证了空间-通道互补设计的有效性")
                    print("  OK updated conclusion (alternative match)")
                    break
            break

# ===== STEP 8: Update chapter 4 summary =====
print("[8/8] Updating chapter 4 summary...")
idx, para = find_para(doc, "三种网络结构改进方案")
if idx:
    for r in para.runs:
        if "三种网络结构改进" in r.text:
            r.text = r.text.replace(
                "三种网络结构改进方案",
                "在网络结构改进层面，ECA和P2两种方案均未超过Baseline，但CoordAtt+ECA组合方案取得了显著效果。三种网络结构改进方案")
            print("  OK updated chapter 4 summary")
            break
else:
    print("  SKIP: chapter 4 summary text not found")

# ===== Save =====
print("=" * 60)
print(f"Saving to: {DST}")
doc.save(DST)
print("DONE! All edits complete.")
