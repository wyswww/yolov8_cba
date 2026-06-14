# -*- coding: utf-8 -*-
"""Rebuild all thesis edits from original, using ONLY text replacement (no insertions)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('王岩松论文final_1y.docx')

def find_para(doc, fragment):
    for i, p in enumerate(doc.paragraphs):
        if fragment in p.text:
            return i, p
    return None, None

def replace_in_para(para, old, new):
    for r in para.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return True
    full = ''.join(r.text for r in para.runs)
    if old in full:
        for r in para.runs:
            r.text = ''
        para.runs[0].text = full.replace(old, new)
        return True
    return False

def set_para(para, text):
    for r in para.runs:
        r.text = ''
    if para.runs:
        para.runs[0].text = text

# ===== 1. Chinese Abstract =====
print('1. Chinese abstract...')
_, p = find_para(doc, '高分辨率推理测试以及高分辨率弱增强二阶段微调实验')
if p and 'CoordAtt' not in p.text:
    replace_in_para(p,
        '高分辨率推理测试以及高分辨率弱增强二阶段微调实验',
        'CoordAtt与ECA组合注意力实验、高分辨率推理测试以及高分辨率弱增强二阶段微调实验')
    print('  OK')

# ===== 2. English Abstract =====
print('2. English abstract...')
_, p = find_para(doc, 'lightweight attention experiments')
if p and 'CoordAtt' not in p.text:
    replace_in_para(p,
        'lightweight attention experiments, P2 detection-head experiments',
        'lightweight attention experiments, CoordAtt+ECA combined attention experiments, P2 detection-head experiments')
    print('  OK')

# ===== 3. 3.5.3 weak aug -- append to last para =====
print('3. 3.5.3 weak augmentation...')
_, p = find_para(doc, '互补的信息增强路径')
if p and p.runs:
    aug = (
        '在数据增强策略方面，由于CoordAtt的核心机制是沿X轴和Y轴分别编码空间位置信息，'
        '其生成的注意力权重直接依赖于特征图中目标的真实空间位置。Mosaic增强将四张不同图像'
        '随机拼接为一张训练样本，MixUp将两张图像按比例混合。这两种强增强手段产生的训练'
        '样本不具备真实的X或Y位置对应关系，会严重破坏CoordAtt所需的空间坐标信息，导致'
        '注意力权重学习到错误的位置映射。因此，本文在该实验中完全关闭了Mosaic、MixUp和'
        'Copy-Paste增强（均设为0），并将旋转角度降至3.0度、平移降至0.05、尺度缩放降至'
        '0.15、剪切降至1.0度，仅保留轻微的HSV颜色扰动和水平翻转，以在数据多样性和空间'
        '信息保真之间取得平衡。这一针对性调整是CoordAtt加ECA组合方案成功的关键前提。'
    )
    p.runs[-1].text = p.runs[-1].text + aug
    print('  OK')

# ===== 4. Fix transition para before 3.6 =====
print('4. 3.5->3.6 transition...')
_, p = find_para(doc, '在三种网络结构改进方案均未取得预期效果后')
if p:
    replace_in_para(p,
        '在三种网络结构改进方案均未取得预期效果后',
        '在ECA注意力和P2检测头两种结构改进方案未取得预期效果后')
    print('  OK')

# ===== 5. Table 3 (Training Config) =====
print('5. Table 3...')
tbl = doc.tables[3]
# Row 8: 训练轮数
for ci, v in [(4, '100+50'), (5, '60')]:
    for p in tbl.rows[8].cells[ci].paragraphs:
        for r in p.runs:
            r.text = v
# Row 9: 批量大小 col 3 = P2 -> 4
for p in tbl.rows[9].cells[3].paragraphs:
    for r in p.runs:
        r.text = '4'
# Row 10: Mosaic col 5 = method5 -> 0
for p in tbl.rows[10].cells[5].paragraphs:
    for r in p.runs:
        if '0.8' in r.text:
            r.text = '0'
# Row 11: MixUp col 5 = method5 -> 0
for p in tbl.rows[11].cells[5].paragraphs:
    for r in p.runs:
        if '0.1' in r.text:
            r.text = '0'
print('  OK')

# ===== 6. Table 4.5 (Test Results) =====
print('6. Table 4.5...')
for table in doc.tables:
    for row in table.rows:
        rt = ' '.join([c.text.strip() for c in row.cells])
        if 'CoordAtt' in rt and 'ECA' in rt and '82.82' in rt:
            cells = row.cells
            for ci, v in [(1, '93.92%'), (2, '92.04%'), (3, '96.25%'), (4, '78.49%')]:
                for p in cells[ci].paragraphs:
                    for r in p.runs:
                        r.text = v
            for p in cells[5].paragraphs:
                for r in p.runs:
                    if '6.66' in r.text:
                        r.text = '+6.32%'
            print('  OK')
            break

# ===== 7. Table 6: rename method5->method5B =====
print('7. Table 6...')
for row in doc.tables[6].rows:
    c0 = row.cells[0].text.strip()
    if '方法5' in c0 and '长尾均衡' in c0:
        for p in row.cells[0].paragraphs:
            for r in p.runs:
                r.text = r.text.replace('方法5', '方法5B')
        print('  OK')
        break

# ===== 8. Rewrite 4.3.2 =====
print('8. 4.3.2 rewrite...')
idx, p1 = find_para(doc, '三种网络结构改进方法')
if not idx:
    idx, p1 = find_para(doc, '网络结构改进方法')
if idx:
    # Collect body paragraphs until 4.3.3
    body = []
    for i in range(idx, min(idx + 10, len(doc.paragraphs))):
        pi = doc.paragraphs[i]
        if '4.3.3' in pi.text:
            break
        if pi.text.strip() and i > idx:
            body.append(pi)

    t0 = (
        '从表4-5可以看出，三种网络结构改进方案呈现出了显著的分化。ECA注意力模型（方案2）'
        '在测试集上的mAP@0.5仅为83.53%，低于Baseline(800) 6.40个百分点。P2高分辨率检测头'
        '（方案3）的mAP@0.5为83.77%，低于Baseline 6.16个百分点。上述两种方案均未能超过Baseline。'
        '然而，CoordAtt与ECA组合注意力模型（方案5）在针对性调整数据增强策略后，取得了'
        'mAP@0.5为96.25%、mAP@0.5:0.95为78.49%、Precision为93.92%、Recall为92.04%的结果，'
        'mAP@0.5较Baseline(800)提升6.32个百分点，综合性能仅次于Strong模型（方案6），'
        '是三种结构改进方案中唯一超过Baseline的方案。'
    )
    t1 = (
        'CoordAtt加ECA组合方案取得成功的核心原因有三点。第一，空间与通道的互补设计有效。'
        'CoordAtt在Backbone中提供空间位置感知，ECA在Neck中提供通道特征筛选，二者分别关注'
        '在哪里和是什么，形成了互补的信息增强路径，而非简单堆叠同类模块。第二，数据增强策略'
        '与注意力机制相匹配。方案5关闭了Mosaic、MixUp和Copy-Paste等强增强，最大程度保留了'
        'CoordAtt所需的真实空间位置信息。而方案1（原版CoordAtt加ECA实验，使用完整强增强）'
        '在测试集上仅获得84.59%的mAP@0.5，与方案5相差超过11个百分点，充分验证了注意力机制'
        '的特性决定增强策略选择这一核心观点。第三，方案5采用Ultralytics内置的load方法按名称'
        '和形状自动匹配预训练权重，相比手动层映射方式更完整地保留了YOLOv8m的COCO预训练知识。'
    )
    t2 = (
        'ECA单一通道注意力（方案2）未能提升的原因在于，课堂行为检测高度依赖空间位置信息'
        '（如举手位置、身体朝向、头部与桌面的相对关系），而通道注意力仅关注哪些通道重要，'
        '完全丧失了空间位置感知，无法满足行为判别的空间语义需求。P2检测头（方案3）虽然提高了'
        '浅层特征的空间分辨率，但P2层特征的语义抽象程度较低，引入的大量浅层特征可能稀释了'
        '深层语义信息，同时新增检测分支需要从头学习，在数据集规模有限时难以收敛到有效状态。'
    )

    set_para(p1, t0)
    if len(body) >= 1:
        set_para(body[0], t1)
    if len(body) >= 2:
        set_para(body[1], t2)
        # Append summary to last body para before 4.3.3
        summary = (
            '综上，本节实验表明：在课堂行为检测任务中，并非所有注意力机制均有效，'
            '也并非简单增加检测尺度即可提升性能。CoordAtt加ECA组合方案经过针对性增强策略调整后，'
            '证明了空间-通道互补的注意力设计在当前任务中的有效性，充分说明了注意力机制的效果'
            '不仅取决于模块本身的结构设计，更取决于与之匹配的训练策略。'
        )
        if body[1].runs:
            body[1].runs[-1].text = body[1].runs[-1].text + summary
    print('  OK')
else:
    print('  WARN: not found')

# ===== 9. 4.6 chapter summary =====
print('9. 4.6 chapter summary...')
_, p = find_para(doc, '三种网络结构改进方法（ECA注意力、P2检测头、CoordAtt+ECA组合注意力）均未能超越Baseline')
if p:
    replace_in_para(p,
        '（1）三种网络结构改进方法（ECA注意力、P2检测头、CoordAtt+ECA组合注意力）均未能超越Baseline，验证了网络结构堆叠并非课堂行为检测任务的有效改进方向。',
        '（1）三种网络结构改进方法中，ECA注意力（方法2）和P2检测头（方法3）未能在测试集上超越Baseline。然而，CoordAtt与ECA组合注意力（方法5）在针对性调整数据增强策略（关闭Mosaic和MixUp、降低几何增强强度）后，取得了mAP@0.5为96.25%、mAP@0.5:0.95为78.49%的显著提升，综合性能仅次于Strong模型。这说明结构改进并非无效，关键在于注意力机制的设计必须与数据增强策略相匹配。')
    print('  OK')
else:
    print('  WARN: not found')

# ===== 10. 6.4 chapter summary =====
print('10. 6.4 chapter summary...')
_, p = find_para(doc, '单纯修改网络结构的优化方式难以提升性能')
if p:
    replace_in_para(p,
        '单纯修改网络结构的优化方式难以提升性能',
        '单纯堆叠注意力模块或扩展检测头难以稳定提升性能，而CoordAtt与ECA的空间-通道互补组合在匹配弱增强策略后取得了接近Strong模型的优异表现')
    print('  OK')
else:
    print('  WARN: not found')

# ===== 11. 7.1 conclusion =====
print('11. 7.1 conclusion...')
_, p = find_para(doc, '随后尝试轻量ECA注意力、P2小目标检测头和高分辨率弱增强微调，但三类训练或结构改进在测试集上均未全面超过基线')
if p:
    new_71 = (
        '在算法实验方面，本文首先训练YOLOv8m基线模型，取得mAP@0.5为89.61%、mAP@0.5:0.95'
        '为73.82%的稳定测试集结果。随后依次开展轻量ECA注意力、P2小目标检测头、高分辨率弱增强'
        '微调、CoordAtt与ECA组合注意力以及长尾均衡高分辨率弱增强二阶段微调五组改进实验。'
        '实验结果表明：ECA注意力和P2检测头两种单纯结构改进均未超过基线；800分辨率弱增强微调'
        '在验证集mAP@0.5:0.95上有所提升，但测试集泛化性不足；CoordAtt加ECA组合注意力方案'
        '在匹配弱增强策略后取得mAP@0.5为96.25%、mAP@0.5:0.95为78.49%的显著提升，验证了'
        '空间-通道互补注意力设计的有效性；Strong模型进一步融合长尾均衡训练、800高分辨率、'
        '弱增强和二阶段微调四项策略，在测试集上取得mAP@0.5为96.73%、mAP@0.5:0.95为82.40%'
        '的最优结果。因此，本文将Strong模型作为高精度推荐方案，将Baseline（640推理）作为'
        '轻量实时备选方案。'
    )
    set_para(p, new_71)
    print('  OK')
else:
    print('  WARN: not found')

# ===== 12. 3.7 chapter summary =====
print('12. 3.7 chapter summary...')
_, p = find_para(doc, '三种方法分别从通道维度、空间尺度和混合注意力三个角度尝试提升YOLOv8m的特征表示能力')
if p:
    replace_in_para(p,
        '三种方法分别从通道维度、空间尺度和混合注意力三个角度尝试提升YOLOv8m的特征表示能力',
        '三种方法分别从通道维度、空间尺度和混合注意力三个角度尝试提升YOLOv8m的特征表示能力。其中，CoordAtt与ECA组合注意力方案在针对性调整增强策略后取得了显著效果，验证了空间-通道互补注意力设计的有效性')
    print('  OK')
else:
    print('  WARN: not found')

# ===== Save =====
out = '王岩松论文final_1y_v3.docx'
doc.save(out)
print(f'\nSaved: {out}')
print('Done - text replacement only, zero paragraph insertions.')
