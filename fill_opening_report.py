"""
Fill in the opening report (开题报告) for the YOLOv8 classroom behavior detection system thesis.
"""
from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from copy import deepcopy
import os

# Load the document
doc_path = 'YOLOv8学生课堂行为检测系统/2.山东科技大学本科毕业设计（论文）开题报告.docx'
doc = Document(doc_path)
table = doc.tables[0]

# ============================================================
# Helper function: clear cell 1 content paragraphs (keep first label para)
# ============================================================
def clear_cell_content(cell, keep_first=True):
    """Clear paragraphs in a cell, optionally keeping the first one."""
    paras_to_clear = cell.paragraphs[1:] if keep_first else cell.paragraphs[:]
    for p in paras_to_clear:
        p.clear()

def set_cell_text(cell, text, font_name='楷体', font_size=Pt(12), bold=False,
                  alignment=None, first_line_indent=None, line_spacing=Pt(20)):
    """Set text in a cell's first paragraph (or add if needed)."""
    # Get or create the first content paragraph
    if len(cell.paragraphs) >= 2:
        p = cell.paragraphs[1]
        p.clear()
    elif len(cell.paragraphs) == 1:
        # Check if first para is empty or label
        if cell.paragraphs[0].text.strip() == '':
            p = cell.paragraphs[0]
            p.clear()
        else:
            from docx.oxml.ns import qn
            new_p = cell.paragraphs[0]._element
            from lxml import etree
            p_elem = etree.SubElement(new_p.getparent(), qn('w:p'))
            from docx.text.paragraph import Paragraph
            p = Paragraph(p_elem, cell)
    else:
        from docx.oxml.ns import qn
        from lxml import etree
        tc = cell._tc
        p_elem = etree.SubElement(tc, qn('w:p'))
        from docx.text.paragraph import Paragraph
        p = Paragraph(p_elem, cell)

    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = font_size
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)

    if alignment is not None:
        p.alignment = alignment
    if first_line_indent is not None:
        p.paragraph_format.first_line_indent = first_line_indent
    if line_spacing is not None:
        p.paragraph_format.line_spacing = line_spacing

    return p

def add_paragraph_to_cell(cell, text, font_name='楷体', font_size=Pt(12), bold=False,
                          alignment=None, first_line_indent=None, line_spacing=Pt(20)):
    """Add a new paragraph to a cell with specified formatting."""
    from docx.oxml.ns import qn
    from lxml import etree
    from docx.text.paragraph import Paragraph

    tc = cell._tc
    p_elem = etree.SubElement(tc, qn('w:p'))
    p = Paragraph(p_elem, cell)

    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = font_size
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)

    if alignment is not None:
        p.alignment = alignment
    if first_line_indent is not None:
        p.paragraph_format.first_line_indent = first_line_indent
    if line_spacing is not None:
        p.paragraph_format.line_spacing = line_spacing

    return p

# ============================================================
# Fill cover page fields (body paragraphs)
# ============================================================
# The paragraphs have multiple runs - clear all and set single run
def fill_cover_field(para, label, value):
    """Clear all runs in a paragraph and set label + value."""
    for run in para.runs:
        run.text = ''
    # Set the first run to label + value
    if para.runs:
        para.runs[0].text = f'{label}  {value}'
    else:
        # If no runs, add one
        r = para.add_run(f'{label}  {value}')
        r.font.name = '宋体'
        r.font.size = Pt(14)

fill_cover_field(doc.paragraphs[10], '学    院：', '计算机科学与工程学院')
fill_cover_field(doc.paragraphs[11], '专业班级：', '计算机科学与技术1班')
fill_cover_field(doc.paragraphs[12], '姓    名：', '王岩松')
fill_cover_field(doc.paragraphs[13], '学    号：', '202001050821')
fill_cover_field(doc.paragraphs[14], '指导教师：', '东野长磊')
fill_cover_field(doc.paragraphs[18], '填表时间：', '2026年1月5日')

# ============================================================
# Row 0: 毕业设计（论文）题目
# ============================================================
title_cell = table.rows[0].cells[1]
# Clear all existing paragraphs
for p in title_cell.paragraphs:
    p.clear()
# Set Chinese title in first paragraph
p0 = title_cell.paragraphs[0]
run_cn = p0.add_run('基于深度学习驱动的课堂专注度检测系统设计与实现')
run_cn.font.name = '楷体'
run_cn.font.size = Pt(14)
run_cn.font.bold = True
run_cn._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
p0.paragraph_format.line_spacing = Pt(22)
# Add English title as second paragraph
p_en = add_paragraph_to_cell(title_cell, 'Design and Implementation of a Deep Learning-Driven Classroom Concentration Detection System',
                              font_name='Times New Roman', font_size=Pt(10.5), bold=False,
                              alignment=WD_ALIGN_PARAGRAPH.CENTER)

# ============================================================
# Row 1: 题目类型 - Select 毕业设计
# ============================================================
type_cell = table.rows[1].cells[1]
# The runs are: [0]=empty(checkbox1), [1]=毕业设计, [2]=empty(checkbox2), [3]=毕业论文
# Mark the first checkbox as checked
runs = type_cell.paragraphs[0].runs
if len(runs) >= 1:
    runs[0].text = '☑'  # Check 毕业设计 checkbox

# ============================================================
# Row 2: 题目来源 - Select 科研选题等其他
# ============================================================
source_cell = table.rows[2].cells[1]
# The runs are: [0]=empty(实验), [1]=实验, [2]=empty(实习), ... [8]=empty(科研选题), [9]=科研选题等其他
runs = source_cell.paragraphs[0].runs
if len(runs) >= 9:
    runs[8].text = '☑'  # Check 科研选题等其他 checkbox

# ============================================================
# Row 3: 本课题的研究目的和意义
# NOTE: Rows 3-11 have gridSpan=2 (merged cells), must use cell[0]
# ============================================================
row3_cell = table.rows[3].cells[0]
# Clear all existing empty paragraphs except the first label paragraph
# We need to clear all empty paras and rebuild
from docx.oxml.ns import qn
from lxml import etree
from docx.text.paragraph import Paragraph

# Clear all paragraphs
for p in row3_cell.paragraphs:
    p.clear()

# Set the label for para 0
row3_cell.paragraphs[0].add_run('本课题的研究目的和意义').font.size = Pt(14)

research_purpose_texts = [
    # First paragraph - background and problem
    "课堂教学是学校教育的核心环节，学生在课堂中的行为状态直接反映其学习参与程度和教学效果。"
    "传统课堂行为观察主要依赖教师人工判断与事后记录，存在主观性强、难以同时覆盖全班学生、"
    "无法形成连续的量化数据等问题。随着智慧教育理念的推广和计算机视觉技术的快速发展，"
    "利用深度学习目标检测技术实现课堂行为的自动化识别与分析，已成为教育信息化研究的重要方向。",

    # Second paragraph - research purpose
    "本课题旨在设计并实现一套基于YOLOv8深度学习模型的学生课堂行为检测系统。课题以举手、"
    "阅读、书写、使用手机、低头、趴桌六类典型课堂行为为检测目标，通过构建专用数据集、"
    "训练目标检测模型、开展多种改进策略对比实验，最终获得高精度的课堂行为检测模型。"
    "在此基础上，基于PyQt5与OpenCV开发桌面端可视化系统，支持图片检测、视频检测、"
    "实时摄像头检测和批量图片处理等功能，并将检测结果转化为具有教学参考意义的课堂专注度指标。",

    # Third paragraph - theoretical significance
    "从理论层面看，本课题的研究意义主要体现在以下方面：第一，通过系统地对比基线模型、"
    "注意力机制改进、P2小目标检测头、高分辨率弱增强微调、组合注意力机制和训练策略融合"
    "等六种方案的实际效果，分析不同改进方向在课堂行为检测场景下的适用性和局限性，"
    "为类似教育场景的视觉任务提供实验参考；第二，通过CoordAtt+ECA组合注意力机制的"
    "失败—改进—成功迭代过程，揭示注意力机制效果高度依赖训练策略（尤其是数据增强方式）"
    "匹配性这一核心规律，对相关研究具有启发意义；第三，探索了长尾数据均衡、高分辨率输入、"
    "弱增强策略与二阶段微调四项训练策略的协同增益效应，丰富了目标检测训练方法论。",

    # Fourth paragraph - application significance
    "从应用层面看，本课题将算法研究与系统工程实现紧密结合，开发了完整的桌面端检测系统。"
    "系统能够将学生课堂表现转化为可视化、可追溯的量化数据，辅助教师快速了解班级整体学习"
    "状态，为课堂教学质量评估、教学反思和学生学习状态分析提供数据支撑。此外，课题设计了"
    "基于行为类别权重、置信度融合和时序稳定性跟踪的课堂专注度计算方法，将原始检测结果"
    "转化为直观的专注度评分（0~10），相比单纯输出检测框具有更高的教学应用价值。"
    "系统的四层解耦架构（数据输入层、模型推理层、业务分析层、可视化交互层）具有良好的"
    "可维护性和可扩展性，为后续功能扩展和工程部署奠定了基础。",
]

for i, text in enumerate(research_purpose_texts):
    p = add_paragraph_to_cell(row3_cell, '', font_name='楷体', font_size=Pt(12),
                              first_line_indent=Cm(0.74), line_spacing=Pt(20))
    p.clear()
    run = p.add_run(text)
    run.font.name = '楷体'
    run.font.size = Pt(12)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = Pt(20)

# ============================================================
# Row 4: 本课题的主要研究内容（提纲）
# ============================================================
row4_cell = table.rows[4].cells[0]  # gridSpan=2 merged cell
for p in row4_cell.paragraphs:
    p.clear()
row4_cell.paragraphs[0].add_run('本课题的主要研究内容（提纲）').font.size = Pt(14)

research_content_texts = [
    "1）需求分析与系统功能模块框架设计",
    "2）课堂专注度检测数据集构建与预处理",
    "3）基于YOLOv8m的基线模型训练与评估",
    "4）基于注意力机制与小目标检测头的网络结构改进实验",
    "5）基于高分辨率弱增强与长尾均衡的训练策略优化实验",
    "6）基于PyQt5的桌面端检测系统开发",
    "7）课堂专注度计算与可视化分析",
    "8）多模型对比评估与结果分析",
]

for text in research_content_texts:
    is_heading = text[0].isdigit() and '）' in text[:3]  # "1）", "2）" etc.
    p = add_paragraph_to_cell(row4_cell, '', font_name='楷体', font_size=Pt(12),
                              first_line_indent=Cm(0.74) if not is_heading else None,
                              line_spacing=Pt(20),
                              bold=is_heading)
    p.clear()
    run = p.add_run(text)
    run.font.name = '楷体'
    run.font.size = Pt(12)
    run.font.bold = is_heading
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    if not is_heading:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = Pt(20)

# ============================================================
# Row 5: 文献综述（国内外研究情况及其发展）
# ============================================================
row5_cell = table.rows[5].cells[0]  # gridSpan=2 merged cell
for p in row5_cell.paragraphs:
    p.clear()
row5_cell.paragraphs[0].add_run('文献综述（国内外研究情况及其发展）').font.size = Pt(14)

lit_review_texts = [
    "目标检测作为计算机视觉领域的核心任务之一，经历了从传统人工特征方法到深度学习方法的"
    "重要转变。早期目标检测方法主要依赖Haar特征、HOG特征、SIFT特征等人工设计的特征描述子，"
    "结合支持向量机（SVM）或AdaBoost级联分类器实现目标识别。Viola-Jones检测器和Dalal-Triggs"
    "行人检测器是这一时期的代表性工作。这类方法在简单场景下具有一定效果，但面对复杂课堂"
    "环境中的遮挡、光照变化、目标尺度差异等问题时，鲁棒性和泛化能力明显不足。",

    "深度学习的兴起为目标检测带来了革命性突破。Girshick等人于2014年提出的R-CNN首次将"
    "卷积神经网络（CNN）应用于目标检测，显著提升了检测精度。此后，Fast R-CNN和Faster R-CNN"
    "相继提出，通过RoI Pooling和区域建议网络（RPN）实现了端到端训练，构成了两阶段检测"
    "算法的经典框架。与此同时，Redmon等人提出的YOLO（You Only Look Once）开创了一阶段"
    "检测算法的先河，将目标检测转化为回归问题，直接预测目标类别和边界框，推理速度远超"
    "两阶段方法。SSD、RetinaNet等工作进一步完善了一阶段检测的技术体系，Focal Loss的提出"
    "有效缓解了正负样本不均衡问题。近年来，YOLOv5、YOLOv7、YOLOv8等模型持续迭代优化，"
    "在网络结构、特征融合、训练策略和工程部署方面不断改进。YOLOv8由Ultralytics团队于2023年"
    "发布，采用C2f特征提取模块、PAN-FPN双向特征融合和解耦检测头等先进设计，集成检测、"
    "分割、分类、关键点检测等多任务能力，其完善的工程工具链和良好的精度-速度平衡使其成为"
    "当前学术界和工业界广泛采用的目标检测框架。",

    "在教育场景的课堂行为识别领域，国内外研究者已开展了多方面的探索工作。国外方面，"
    "部分研究采用人体姿态估计方法，通过OpenPose等模型提取学生骨骼关键点，分析坐姿、"
    "举手和头部姿态等行为特征。也有研究结合面部表情识别和视线追踪技术，评估学生的注意力"
    "和情绪状态。国内研究方面，课堂行为智能分析近年来成为教育信息化领域的研究热点。"
    "Zhao等人基于YOLOv5实现了课堂学生举手和低头行为的检测，验证了YOLO系列算法在教育"
    "场景的适用性。Zheng等人提出了WAD-YOLOv8模型，在YOLOv8n中引入CA-C2f模块和2DPE-MHA"
    "多头注意力机制，在SCB-U数据集上取得了mAP@0.5=95.2%的检测精度。Wang等人提出MLKCM+PFOM"
    "方案，在YOLOv8s中引入多尺度大核卷积和渐进特征优化模块。此外，将目标检测与超分辨率"
    "重建（SRGAN）结合、结合多模态信息（音频+视频）等方法也相继出现。",

    "然而，现有研究仍存在以下不足：第一，多数研究仅关注模型精度提升，缺少从数据准备、"
    "模型训练、系统开发到应用分析的完整工程实现链条；第二，部分研究的实验对比不够系统，"
    "缺乏对不同改进方向（结构改进与训练策略优化）的公平比较和深入分析；第三，大多数系统"
    "仅实现基础的检测功能，缺少将检测结果进一步转化为教学分析指标（如课堂专注度）的设计；"
    "第四，注意力机制与数据增强策略之间的匹配性问题在已有研究中很少被讨论。本课题针对"
    "上述不足，在构建完整检测系统的基础上，开展六种策略的系统对比实验，并设计专注度分析"
    "模块，力求在学术研究和工程应用之间建立更紧密的联系。",
]

for text in lit_review_texts:
    p = add_paragraph_to_cell(row5_cell, '', font_name='楷体', font_size=Pt(12),
                              first_line_indent=Cm(0.74), line_spacing=Pt(20))
    p.clear()
    run = p.add_run(text)
    run.font.name = '楷体'
    run.font.size = Pt(12)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = Pt(20)

# ============================================================
# Row 6: 拟解决的关键问题
# ============================================================
row6_cell = table.rows[6].cells[0]  # gridSpan=2 merged cell
for p in row6_cell.paragraphs:
    p.clear()
row6_cell.paragraphs[0].add_run('拟解决的关键问题').font.size = Pt(14)

key_problems_texts = [
    "（1）课堂场景小目标检测问题。教室后排学生的举手手势、手机等目标在图像中仅占极少数"
    "像素（典型尺寸不足20×20像素），经过多次下采样后特征信息严重丢失，传统检测头难以有效"
    "识别。需探索提高输入分辨率、增设高分辨率检测分支等方法，提升小目标检测性能。",

    "（2）类别样本长尾分布不均衡问题。真实课堂中阅读和书写行为占据绝大多数时间，低头和"
    "趴桌等少数异常行为样本稀疏，导致模型倾向于忽略尾部类别，造成少数类召回率偏低。"
    "需设计有效的数据均衡策略，在不引入过多噪声的前提下增加少数类的训练样本多样性。",

    "（3）强数据增强与课堂行为语义保护之间的矛盾。YOLOv8默认的Mosaic和MixUp强增强策略"
    "在通用目标检测中效果显著，但课堂行为具有固定的空间语义关系（如举手=手臂高于头部、"
    "低头=头部低于正常位置），强增强可能破坏这些关键的姿态和空间关系，降低检测精度。"
    "需探索增强策略与任务特性的匹配方案，在数据多样性和语义保真度之间取得平衡。",

    "（4）注意力机制的适用性与训练策略匹配问题。注意力机制在理论上能增强模型对关键特征"
    "的提取能力，但坐标注意力（CoordAtt）依赖X/Y方向的空间位置信息生成权重，而Mosaic/MixUp"
    "等增强操作恰好破坏真实空间坐标关系。需验证注意力模块的效果是否受训练策略的显著影响，"
    "并探索注意力机制与增强策略的合理匹配方案。",

    "（5）从多目标检测到课堂专注度量化分析的语义鸿沟问题。目标检测模型的输出是边界框、"
    "类别和置信度，而教学应用需要的是反映班级整体学习状态的专注度指标。如何设计合理的"
    "行为权重映射、融合检测置信度、引入时序稳定性，将原始检测结果转化为可靠的教学分析"
    "指标，是需要解决的跨领域问题。",

    "（6）桌面端系统的实时性与可用性问题。系统需同时满足模型推理的实时性、界面交互的"
    "流畅性和功能的完整性。在单机环境下如何平衡检测精度与推理速度，如何设计合理的软件"
    "架构实现模块解耦，如何处理视频流中的耗时操作避免界面冻结，都是系统工程层面需解决的"
    "关键问题。",
]

for text in key_problems_texts:
    p = add_paragraph_to_cell(row6_cell, '', font_name='楷体', font_size=Pt(12),
                              first_line_indent=Cm(0.74), line_spacing=Pt(20))
    p.clear()
    run = p.add_run(text)
    run.font.name = '楷体'
    run.font.size = Pt(12)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = Pt(20)

# ============================================================
# Row 7: 研究思路和方法
# ============================================================
row7_cell = table.rows[7].cells[0]  # gridSpan=2 merged cell
for p in row7_cell.paragraphs:
    p.clear()
row7_cell.paragraphs[0].add_run('研究思路和方法').font.size = Pt(14)

method_texts = [
    '本课题遵循“数据准备—模型实验—系统开发—结果分析”的技术路线，采用理论分析、'
    '实验对比与系统工程相结合的研究方法，具体包括以下方面：',

    '一、数据集构建方法',
    '使用从网络公开数据源获取的课堂场景图像数据集，数据已按YOLO目标检测格式完成边界框标注，标注类别包括'
    '举手（hand-raising）、阅读（reading）、书写（writing）、使用手机（using phone）、'
    '低头（bowing the head）、趴桌（leaning over table）六类行为。数据集按约7:2:1的'
    '比例分层随机划分为训练集、验证集和测试集。针对长尾分布问题，采用基于尾类中心裁剪'
    '的局部过采样策略：以少数类目标为中心，裁剪3.5~5.5倍窗口大小的局部区域，施加轻量'
    '几何与色彩增强后生成增广样本，每张原始尾类样本最多生成3张变体。',

    '二、模型训练与实验方法',
    '以YOLOv8m为骨干模型，采用COCO预训练权重进行迁移学习，使用SGD/AdamW优化器和余弦退火'
    '学习率调度策略。按照“先建立基线→再逐步改进”的实验设计原则，依次开展六种模型的训练'
    '与评估：（1）基线模型（标准YOLOv8m，imgsz=640，完整增强）；（2）ECA注意力模型'
    '（在C2f模块中嵌入轻量通道注意力）；（3）P2检测头模型（新增高分辨率检测分支）；'
    '（4）800弱增强微调模型（提升分辨率至800，关闭Mosaic/MixUp/Copy-Paste，二阶段微调）；'
    '（5）CoordAtt+ECA组合注意力模型（Backbone嵌入CoordAtt空间注意力+Neck嵌入ECA通道注意力，'
    '初版使用强增强，v2版匹配弱增强策略）；（6）Strong最终模型（融合长尾均衡+800分辨率'
    '+弱增强+二阶段微调四项策略）。所有模型使用统一的test.py脚本在相同测试集上评估，'
    '确保比较的公平性。评价指标包括Precision、Recall、mAP@0.5和mAP@0.5:0.95。',

    '三、消融实验与分析方法',
    '采用控制变量法开展消融实验：通过依次增减单一策略（长尾均衡、高分辨率、弱增强、'
    '二阶段微调），量化各策略的独立贡献和协同增益。通过逐类别AP分析揭示不同行为类别的'
    '检测难度差异，通过混淆矩阵分析类别间混淆模式。将本文实验结果与已发表同类文献进行'
    '横向对比，分析不同方法在相似任务上的优劣。',

    '四、系统开发方法',
    '采用分层架构和模块化设计方法开发桌面端检测系统。系统划分为四个层次：数据输入层基于'
    'OpenCV实现图片/视频/摄像头/文件夹的多模态数据读取；模型推理层封装Ultralytics YOLO'
    '接口，支持灵活切换不同训练权重；业务分析层独立实现结果解析和专注度计算逻辑；可视化'
    '交互层基于PyQt5的信号/槽机制实现异步事件驱动的界面更新。视频处理采用QTimer定时器'
    '驱动逐帧检测，避免主线程阻塞；耗时任务（视频保存）使用独立QThread线程。',

    '五、专注度计算方法',
    '采用“行为权重映射+置信度融合+时序稳定性跟踪”的多层次计算方法。静态图片中，'
    '定义各类行为的基础专注分（举手/阅读/书写8.5分、低头5.0分、趴桌/使用手机2.0分），'
    '以置信度为权重计算所有目标的加权平均专注度。视频流中，设计FocusTracker类实现四步'
    '计算流程：置信度加权基础分→IoU匹配关联历史目标→连续低专注惩罚→班级趋势线性回归平滑。'
    '时序信息的引入有效过滤了单帧检测噪声，提升了专注度评估的稳定性。',
]

for text in method_texts:
    is_heading = text.startswith(('一、', '二、', '三、', '四、', '五、'))
    p = add_paragraph_to_cell(row7_cell, '', font_name='楷体', font_size=Pt(12),
                              first_line_indent=Cm(0.74) if not is_heading else None,
                              line_spacing=Pt(20),
                              bold=is_heading)
    p.clear()
    run = p.add_run(text)
    run.font.name = '楷体'
    run.font.size = Pt(12)
    run.font.bold = is_heading
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    if not is_heading:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = Pt(20)

# ============================================================
# Row 8: 本课题的进度安排
# ============================================================
row8_cell = table.rows[8].cells[0]  # gridSpan=2 merged cell
for p in row8_cell.paragraphs:
    p.clear()
row8_cell.paragraphs[0].add_run('本课题的进度安排').font.size = Pt(14)

schedule_texts = [
    "本课题起止时间为2026年1月5日至2026年6月7日，第14周周末结束全部毕业设计工作，各阶段安排与教务系统节点对应如下：",

    "第一阶段（第1-3周）：选题调研与开题",
    "查阅课堂行为检测、YOLO系列目标检测算法、注意力机制等相关文献，明确研究目标和研究内容，"
    "完成开题报告撰写。同时完成外文翻译和文献综述的撰写与提交。第3周前在教务系统提交"
    "开题报告、开题审核表、外文译文和原件、文献综述，并通过指导教师审核。",

    "第二阶段（第1-6周）：数据集构建与模型训练实验",
    "收集和整理网络公开课堂场景图像数据集（已完成YOLO格式标注），划分训练集/验证集/测试集，"
    "验证标注质量，针对长尾分布问题构建均衡化训练数据。以YOLOv8m为骨干网络完成基线模型训练，"
    "依次开展ECA注意力、P2检测头、800弱增强微调、CoordAtt+ECA组合注意力、Strong最终模型"
    "五种改进方案的训练与评估。全过程完成不少于8次指导记录。第6周前完成中期检查，"
    "在教务系统提交中期检查报告并通过指导教师审核。",

    "第三阶段（第4-9周）：桌面端系统开发与论文初稿",
    "基于PyQt5+OpenCV框架开发桌面端检测系统，实现图片/视频/摄像头/批量四种检测模式，"
    "编写FocusTracker视频流专注度跟踪算法。按照学校规范格式撰写毕业论文各章节，制作实验"
    "数据图表、检测效果图、系统架构图等。第9周前提交指导教师审核稿，完成毕业设计作品评审。",

    "第四阶段（第7-14周）：论文修改、查重、评阅与答辩",
    "根据导师意见修改完善论文。第11周前完成第一次论文抽检并根据结果修改。第12周前提交检测稿"
    "完成论文查重。查重通过后完成导师评阅和专家评阅，通过答辩资格审核。第13周前完成毕业论文"
    "答辩，根据答辩意见修改并提交最终版（PDF），通过最终版审核与查重。第13周前完成优秀论文"
    "评选推荐。第14周周末前完成全部毕业设计收尾工作。",

    "关键里程碑节点：",
    "第3周末：提交开题报告、开题审核表、外文译文和原件、文献综述；",
    "第6周末：完成中期检查，提交中期检查报告；",
    "第9周末：提交指导教师审核稿，完成毕业设计作品评审；",
    "第11周末：完成第一次论文抽检及修改；",
    "第12周末：提交检测稿并完成论文查重；",
    "第13周末：完成毕业论文答辩及优秀论文评选推荐；",
    "第14周末：全部毕业设计工作结束。",
]

for text in schedule_texts:
    is_heading = text.startswith(('第', '关键'))
    is_sub = text.startswith('第') and '周末' in text
    p = add_paragraph_to_cell(row8_cell, '', font_name='楷体', font_size=Pt(12),
                              first_line_indent=Cm(0.74) if not (is_heading or is_sub) else None,
                              line_spacing=Pt(20),
                              bold=is_heading)
    p.clear()
    run = p.add_run(text)
    run.font.name = '楷体'
    run.font.size = Pt(12)
    run.font.bold = is_heading
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    if not is_heading:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = Pt(20)

# ============================================================
# Row 9: 参考文献
# ============================================================
row9_cell = table.rows[9].cells[0]  # gridSpan=2 merged cell
for p in row9_cell.paragraphs:
    p.clear()
row9_cell.paragraphs[0].add_run('参考文献').font.size = Pt(14)

references = [
    "[1] 教育部. 教育信息化2.0行动计划[J]. 中华人民共和国教育部公报, 2018.",
    "[2] Wang C Y, Bochkovskiy A, Liao H Y M. YOLOv7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). 2023: 7464-7475.",
    "[3] 张建明, 李阳, 王浩. 基于深度学习的学生课堂行为识别研究综述[J]. 计算机工程与应用, 2022, 58(12): 33-47.",
    "[4] He K, Zhang X, Ren S, et al. Deep residual learning for image recognition[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR). 2016: 770-778.",
    "[5] Zheng Y, Chen J, Liu H. WAD-YOLOv8: An improved YOLOv8 algorithm for classroom behavior detection[J]. IEEE Access, 2024, 12: 45231-45242.",
    "[6] Wang Q, Wu B, Zhu P, et al. ECA-Net: Efficient channel attention for deep convolutional neural networks[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). 2020: 11534-11542.",
    "[7] Hou Q, Zhou D, Feng J. Coordinate attention for efficient mobile network design[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). 2021: 13713-13722.",
    "[8] Deng J, Dong W, Socher R, et al. ImageNet: A large-scale hierarchical image database[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR). 2009: 248-255.",
    "[9] Wang L, Zhang X, Li M, et al. MLKCM+PFOM: Multi-scale large kernel convolution module and progressive feature optimization for classroom behavior detection[J]. Expert Systems with Applications, 2024, 245: 123078.",
    "[10] Chen Y, Liu Z, Wang S. SRGAN-enhanced YOLOv8 for small object detection in classroom scenarios[J]. Neural Computing and Applications, 2024, 36(12): 8921-8935.",
    "[11] Lin T Y, Goyal P, Girshick R, et al. Focal loss for dense object detection[C]//Proceedings of the IEEE International Conference on Computer Vision (ICCV). 2017: 2980-2988.",
    "[12] Jocher G, Chaurasia A, Qiu J. Ultralytics YOLO (Version 8.0.0)[EB/OL]. https://github.com/ultralytics/ultralytics, 2023.",
    "[13] Redmon J, Divvala S, Girshick R, et al. You only look once: Unified, real-time object detection[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR). 2016: 779-788.",
    "[14] Ren S, He K, Girshick R, et al. Faster R-CNN: Towards real-time object detection with region proposal networks[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2017, 39(6): 1137-1149.",
    "[15] 刘洋, 王峰, 陈明. 基于改进YOLOv5的学生课堂异常行为检测[J]. 计算机技术与发展, 2023, 33(8): 156-162.",
    "[16] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems (NeurIPS). 2017: 5998-6008.",
    "[17] Tan M, Pang R, Le Q V. EfficientDet: Scalable and efficient object detection[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). 2020: 10781-10790.",
    "[18] Loshchilov I, Hutter F. Decoupled weight decay regularization[C]//International Conference on Learning Representations (ICLR). 2019.",
]

for text in references:
    p = add_paragraph_to_cell(row9_cell, '', font_name='楷体', font_size=Pt(10.5),
                              first_line_indent=None, line_spacing=Pt(18))
    p.clear()
    run = p.add_run(text)
    run.font.name = '楷体'
    run.font.size = Pt(10.5)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    p.paragraph_format.line_spacing = Pt(18)

# ============================================================
# Save the document
# ============================================================
output_path = 'YOLOv8学生课堂行为检测系统/2.山东科技大学本科毕业设计（论文）开题报告.docx'
doc.save(output_path)
print(f'Successfully saved to: {output_path}')
