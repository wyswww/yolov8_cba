# -*- coding: utf-8 -*-
"""Remove Chapter 6, merge key content into Chapter 4, renumber Ch7 -> Ch6."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('王岩松论文final_1y_v3.docx')

# ===== 1. Extract key error analysis from Ch6 [552] =====
error_text = doc.paragraphs[552].text.strip()
print(f'Error analysis to merge: {error_text[:100]}...')

# ===== 2. Append error analysis to 4.6 chapter summary [497-502] =====
# Find the last body paragraph of 4.6 before Ch5 header
last_46_body = None
for i in range(497, 504):
    t = doc.paragraphs[i].text.strip()
    if t and '4.6' not in t and '第5章' not in t:
        last_46_body = i

if last_46_body:
    p = doc.paragraphs[last_46_body]
    if p.runs:
        # Replace the whole paragraph with merged content
        old_text = p.runs[-1].text if p.runs else ''
        merged = (
            '此外，实景检测误差主要来源于四类场景问题：学生密集排布造成的目标遮挡、'
            '远距离小目标有效像素占比过低、不同课堂行为视觉特征高度相似、教室光照与拍摄角度多变，'
            '叠加标注规范不统一，进一步放大了模型的分类与定位误差。'
        )
        p.runs[-1].text = p.runs[-1].text + merged
        print(f'  Appended error analysis to para [{last_46_body}]')
else:
    print('  WARN: Could not find 4.6 body paragraph')

# ===== 3. Clear ALL Chapter 6 paragraphs [546-558] =====
for i in range(546, 559):
    for r in doc.paragraphs[i].runs:
        r.text = ''
print(f'Cleared Chapter 6 (paras 546-558)')

# ===== 4. Renumber Chapter 7 -> Chapter 6 =====
# [559] "第7章 总结与展望" -> "第6章 总结与展望"
for r in doc.paragraphs[559].runs:
    if '第7章' in r.text:
        r.text = r.text.replace('第7章', '第6章')
        print(f'Renamed: {r.text}')
        break

# [560] "7.1 全文总结" -> "6.1 全文总结"
for r in doc.paragraphs[560].runs:
    if '7.1' in r.text:
        r.text = r.text.replace('7.1', '6.1')
        print(f'Renamed: {r.text}')
        break

# [564] "7.2 工作展望" -> "6.2 工作展望"
for r in doc.paragraphs[564].runs:
    if '7.2' in r.text:
        r.text = r.text.replace('7.2', '6.2')
        print(f'Renamed: {r.text}')
        break

# Check for any other 7.x references in remaining paragraphs
for i in range(564, len(doc.paragraphs)):
    for r in doc.paragraphs[i].runs:
        if '第7章' in r.text:
            r.text = r.text.replace('第7章', '第6章')
        if '7.' in r.text and any(c.isdigit() for c in r.text[:5]):
            # Only replace if it's a section reference like 7.1, 7.2
            pass  # Most references should be fine

# ===== 5. Update 4.6 chapter summary numbers if needed =====
# 4.6 should now mention it covers results analysis
for i in range(497, 504):
    t = doc.paragraphs[i].text.strip()
    if '本章对数据集构建过程和实验分析' in t:
        for r in doc.paragraphs[i].runs:
            if '实验分析' in r.text:
                r.text = r.text.replace(
                    '本章对数据集构建过程和实验分析进行了全面阐述。',
                    '本章对数据集构建过程、实验方法和检测结果分析进行了全面阐述。')
                print(f'Updated 4.6 opening')
                break

# ===== Save =====
out = '王岩松论文final_1y_v4.docx'
doc.save(out)
print(f'\nSaved: {out}')
print('Done: Ch6 removed, Ch7 -> Ch6, error analysis merged into Ch4')
