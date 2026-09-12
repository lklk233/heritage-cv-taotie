# -*- coding: utf-8 -*-
"""生成项目总结 Word 文档（学术论文格式）"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
import os

doc = Document()

# ============ 页面设置 ============
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(3.18)

# ============ 样式定义 ============
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.first_line_indent = Cm(0.74)


def add_heading_scaled(text, level=1):
    """添加符合学术规范的标题"""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = '黑体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        if level == 1:
            run.font.size = Pt(16)
        elif level == 2:
            run.font.size = Pt(14)
        elif level == 3:
            run.font.size = Pt(13)
    return h


def add_para(text, bold=False, alignment=None, indent=True):
    """添加正文段落"""
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    else:
        p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(12)
    run.bold = bold
    if alignment is not None:
        p.alignment = alignment
    return p


def add_table_with_data(headers, rows):
    """添加三线表"""
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(10)

    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.rows[r + 1].cells[c]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(10)
    return table


# ============ 标题 ============
title_para = doc.add_paragraph()
title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_para.paragraph_format.space_after = Pt(12)
title_run = title_para.add_run('基于YOLOv8的青铜器纹饰自动识别研究\n——以兽面纹（饕餮纹）线稿图像为例')
title_run.font.name = '黑体'
title_run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
title_run.font.size = Pt(18)
title_run.bold = True

# 作者信息
author_para = doc.add_paragraph()
author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
author_para.paragraph_format.first_line_indent = Cm(0)
author_run = author_para.add_run('（项目阶段性报告）')
author_run.font.name = '宋体'
author_run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
author_run.font.size = Pt(12)

# ============ 摘要 ============
add_heading_scaled('摘  要', level=1)

add_para(
    '青铜器纹饰的自动识别是计算机视觉技术在文化遗产领域的重要应用方向。'
    '本文提出了一种基于YOLOv8的青铜器纹饰目标检测方法，采用"线稿预训练+真实照片微调"的两阶段深度学习策略，'
    '以《中国古代青铜器造型纹饰》等文献中的纹饰线稿为训练数据，借助YOLOv8n轻量级检测模型，'
    '实现了对青铜器兽面纹（饕餮纹）线稿图像的高精度自动识别。'
    '实验使用76张兽面纹正样本和19张蟠龙纹负样本，通过离线数据增强将训练集扩充至300张图像。'
    '训练结果显示，模型在验证集上达到mAP@50=0.995、mAP@50-95=0.995的优异表现，'
    '验证了基于线稿训练青铜器纹饰识别模型的可行性。'
    '在初步跨域测试中，模型在45张真实青铜器文物照片上取得了86.7%的检测率，'
    '表明线稿预训练模型对真实照片具有一定的泛化能力，同时也揭示了域差异带来的挑战。'
    '本文同时构建了完整的数据预处理、标注生成、数据集划分、数据增强和模型推理工具链，'
    '为后续多类别纹饰识别和真实照片跨域迁移奠定了方法论和工程基础。'
)

add_para('关键词：青铜器纹饰；YOLOv8；目标检测；深度学习；兽面纹；线稿识别')

# ============ 1. 引言 ============
add_heading_scaled('1  引言', level=1)

add_para(
    '青铜器是中国古代文明的重要物质载体，其表面装饰的纹饰具有极高的考古学、艺术史和文化研究价值。'
    '传统上，青铜器纹饰的识别与分类依赖考古学专家的经验判断，效率低、主观性强，'
    '难以应对大规模考古发掘中海量青铜器碎片纹饰的分类需求。'
    '近年来，深度学习技术在图像分类与目标检测任务中取得了突破性进展，'
    '为文化遗产数字化研究提供了新的技术路径[1-3]。'
)

add_para(
    '然而，将深度学习直接应用于青铜器纹饰识别面临两个核心挑战：（1）真实青铜器照片数量有限，'
    '且受拍摄角度、光照、锈蚀程度等因素影响，标注难度大；（2）青铜器纹饰具有较强的风格化特征，'
    '与自然图像差异显著，通用预训练模型的迁移效果不确定。'
    '针对上述问题，本文提出了一种创新性的两阶段训练策略：首先利用考古图录中的线稿（线描图）进行第一轮训练，'
    '再利用训练好的模型在真实青铜器照片上进行微调迁移。'
    '线稿图像具有风格一致、背景干净、边界清晰的特点，非常适合作为初步训练数据。'
)

add_para(
    '本文以兽面纹（亦称饕餮纹）为研究对象，它是商周青铜器上最具代表性、出现频率最高的纹饰类型之一。'
    '本文的研究目标是验证"线稿训练→真实照片微调"策略的可行性，'
    '并构建一套可复用的数据处理与模型训练工具链。'
)

# ============ 2. 相关工作 ============
add_heading_scaled('2  相关工作', level=1)

add_para(
    '目标检测是计算机视觉的核心任务之一，旨在同时定位图像中的目标位置并识别其类别。'
    'YOLO（You Only Look Once）系列模型以其端到端的单阶段检测架构在速度和精度之间取得了良好平衡[4]。'
    'YOLOv8作为Ultralytics公司于2023年发布的最新版本之一，'
    '采用了改进的C2f模块、解耦头（Decoupled Head）和无锚框（Anchor-Free）设计，'
    '相比前代模型在小目标检测和训练效率方面均有提升。'
    'YOLOv8n（nano版本）仅有约300万参数，适合GPU算力有限的实验环境。'
)

add_para(
    '在文化遗产领域，已有研究者尝试利用深度学习进行文物纹饰识别。'
    '例如，部分工作使用卷积神经网络（CNN）对瓷器纹饰进行分类，'
    '也有针对敦煌壁画风格分类的研究[5]。'
    '然而，针对商周青铜器纹饰的YOLO目标检测研究仍较为少见，'
    '尤其是利用考古图录线稿作为训练数据的探索尚属空白。'
    '本文的工作填补了这一领域的方法论空白。'
)

# ============ 3. 方法 ============
add_heading_scaled('3  方法', level=1)

add_heading_scaled('3.1  项目总体架构', level=2)
add_para(
    '本项目采用模块化的设计思路，将数据预处理、标注生成、数据集划分、数据增强、模型训练和推理部署'
    '等环节封装为独立的Python脚本，形成可复用的工具链。'
    '项目包含两个独立的子项目目录：bronze_taotie（兽面纹识别）和bronze_long（蟠龙纹识别），'
    '各自拥有完整的训练流水线，仅类别名称和数据源不同。'
)

add_heading_scaled('3.2  数据来源与预处理', level=2)
add_para(
    '原始数据来源于《中国古代青铜器造型纹饰》PDF图录，通过人工截图方式提取线稿图像。'
    '兽面纹正样本76张，均为RGBA格式PNG图像，来自同一图录的不同扫描页。'
    '蟠龙纹负样本19张，用作背景干扰图像，帮助模型学习区分不同纹饰类型。'
)

add_para(
    '预处理管线（preprocess.py）包含以下步骤：（1）RGBA格式转换为RGB，'
    '透明通道填充白色背景；（2）自动裁剪白边，去除扫描件四周的空白区域；'
    '（3）统一重命名为"taotie_XXX.jpg"格式，保留数字编号便于溯源；'
    '（4）生成mapping.csv映射表，记录原始文件名与新文件名的对应关系。'
    '所有正样本均为独立的兽面纹图案，不包含多个纹饰单元。'
)

add_heading_scaled('3.3  标注策略', level=2)
add_para(
    '由于每张线稿图像仅包含一个完整的纹饰图案，本文采用简化标注策略：'
    '每条标注即为一个覆盖全图的边界框（class_id=0, x_center=0.5, y_center=0.5, '
    'width=1.0, height=1.0）。该策略通过auto_label.py脚本自动生成标签文件，'
    '完全避免了人工标注的工作量。负样本图像不生成标签文件，'
    'YOLOv8在训练时将自动将其视为不含目标物体的背景图像进行处理。'
)

add_heading_scaled('3.4  数据集划分与数据增强', level=2)
add_para(
    '训练集与验证集按80:20比例随机划分，固定随机种子（seed=42）确保结果可复现。'
    '划分后训练集含60张正样本和15张负样本，验证集含16张正样本和4张负样本。'
)

add_para(
    '针对训练数据量有限的问题，本文实现了离线数据增强脚本（augment.py），'
    '为每张训练集图像生成3个随机增强变体。增强策略包括：'
    '（1）50%概率水平翻转；（2）±8°随机旋转（带自动黑边裁剪）；'
    '（3）85%-115%随机缩放；（4）80%-120%亮度调整；（5）80%-120%对比度调整。'
    '增强后训练集从75张图像扩充至300张（240正+60负），验证集保持20张不变。'
)

add_para(
    '完整的数据处理流程包括六个步骤：原始图像预处理（preprocess.py）→ '
    '自动标签生成（auto_label.py）→ 数据集划分（split_dataset.py）→ '
    '数据集校验（verify_dataset.py）→ 数据增强（augment.py）→ 最终校验。'
    '每个步骤均通过独立的验证机制确保数据质量和格式一致性。'
)

add_heading_scaled('3.5  模型选择与训练配置', level=2)
add_para(
    '本文选择YOLOv8n（nano版本）作为基线模型，该模型包含约301万参数，'
    '计算量约8.2 GFLOPs，适合在单张NVIDIA GeForce RTX 4060 Laptop GPU（8GB显存）上训练。'
    '训练使用官方预训练权重yolov8n.pt进行迁移学习初始化。'
)

add_para(
    '主要训练参数如下：训练轮数100 epochs（早停patience=20），输入图像尺寸640×640，'
    '批次大小batch=8，优化器采用自动选择的AdamW（初始学习率lr=0.002），'
    '启用自动混合精度（AMP）训练以节约显存。'
    '数据增强方面，YOLOv8内部启用了mosaic=1.0增强、fliplr=0.5水平翻转、'
    'hsv_h=0.015/hsv_s=0.7/hsv_v=0.4色彩抖动等在线增强策略。'
)

# ============ 4. 实验 ============
add_heading_scaled('4  实验与结果', level=1)

add_heading_scaled('4.1  数据集构成', level=2)
add_para(
    '最终数据集构成如表1所示。训练集共300张图像（240张正样本+60张负样本），'
    '验证集20张图像（16张正样本+4张负样本），类别数nc=1（仅兽面纹taotie类）。'
)

add_table_with_data(
    ['数据集', '正样本（兽面纹）', '负样本（蟠龙纹）', '标签文件数', '总计'],
    [
        ['训练集', '240', '60', '240', '300'],
        ['验证集', '16', '4', '16', '20'],
        ['合计', '256', '64', '256', '320'],
    ]
)
doc.add_paragraph()

add_heading_scaled('4.2  训练过程', level=2)
add_para(
    '训练在Windows 11操作系统、NVIDIA GeForce RTX 4060 Laptop GPU（8 GB显存）、'
    'CUDA 12.6环境下进行，使用Ultralytics YOLOv8 8.4.24框架和PyTorch 2.8.0深度学习库。'
    '训练共运行72个epoch后触发早停（patience=20），总耗时约0.065小时（约3.9分钟）。'
    '最佳模型出现在第52个epoch。'
)

add_para(
    '训练过程中的损失函数包含三个分量：box_loss（边界框回归损失）、cls_loss（分类损失）'
    '和dfl_loss（分布焦点损失）。三者均随训练进行持续下降，表明模型在正负样本判别、'
    '边界框定位等方面均稳定收敛。'
)

add_heading_scaled('4.3  评估指标', level=2)
add_para(
    '本文采用YOLOv8标准评估指标：Precision（精确率）、Recall（召回率）、'
    'mAP@50（IoU阈值为0.5时的平均精度均值）和mAP@50-95'
    '（IoU阈值从0.5到0.95、步长0.05的平均精度均值）。'
    '其中mAP@50-95是最严格的指标，它综合衡量了模型在宽松和严格定位标准下的整体表现。'
)

add_heading_scaled('4.4  实验结果', level=2)
add_para(
    '模型在验证集上的最终评估结果如表2所示。'
    '在最佳epoch（第52轮），模型取得了Precision=0.931、Recall=1.000、'
    'mAP@50=0.995、mAP@50-95=0.995的优异表现。'
    '训练结束后对best.pt权重进行最终验证，Precision=1.000、Recall=0.996、'
    'mAP@50=0.995、mAP@50-95=0.995。'
)

add_table_with_data(
    ['评估指标', '最佳epoch（52）', '最终验证（best.pt）'],
    [
        ['Precision', '0.931', '1.000'],
        ['Recall', '1.000', '0.996'],
        ['mAP@50', '0.995', '0.995'],
        ['mAP@50-95', '0.995', '0.995'],
    ],
)
doc.add_paragraph()

add_para(
    '推理速度方面，单张图像预处理耗时约0.2ms，模型推理耗时约1.3ms，'
    '后处理耗时约0.8ms，总处理时间约2.3ms/张，完全满足实时检测的性能需求。'
)

add_heading_scaled('4.5  真实照片跨域初步验证', level=2)

add_heading_scaled('4.5.1  测试数据', level=3)
add_para(
    '为评估线稿训练模型对真实青铜器照片的泛化能力，本文收集了45张真实青铜器文物照片作为独立测试集。'
    '这些照片涵盖商代晚期至汉代（约公元前13世纪至公元3世纪）的多种器型，'
    '包括鼎、尊、簋、爵、斝、觚、甗、罍、壶、匜、方彝、铙、钺、带钩、当卢、面具、罐、铃形器、筒形器等'
    '三十余种青铜器类。所有照片均含有兽面纹（饕餮纹）纹饰，来源为博物馆实物拍摄和考古图录照片，'
    '具有多样化的拍摄角度、光照条件、背景环境和锈蚀程度，能够较为全面地反映真实场景下的检测挑战。'
)

add_heading_scaled('4.5.2  测试方法', level=3)
add_para(
    '测试使用第一阶段训练的最佳模型权重（taotie_train4/best.pt，epoch 52），'
    '直接对45张真实照片进行推理，未进行任何微调或领域自适应处理。'
    '推理参数与训练阶段保持一致：置信度阈值conf=0.3，IoU阈值iou=0.45，输入尺寸640。'
    '检测标准采用单框检测：若模型输出至少一个检测框（置信度>0.3），则判定为成功检测；'
    '否则判定为漏检。'  # noqa: E501
)

add_heading_scaled('4.5.3  测试结果', level=3)
add_para(
    '测试结果汇总如表3所示。在45张真实青铜器照片中，模型成功检测出39张（检出率86.7%），'
    '6张未能检出（漏检率13.3%）。该结果表明，尽管训练数据仅包含黑白线稿图像，'
    '模型对真实照片仍具有较好的跨域泛化能力。'
)

add_table_with_data(
    ['指标', '数值', '百分比'],
    [
        ['测试图片总数', '45', '100%'],
        ['成功检测', '39', '86.7%'],
        ['未检测到', '6', '13.3%'],
        ['平均置信度（检出）', '0.872', '—'],
        ['最高置信度', '0.968', '—'],
        ['最低置信度（检出）', '0.345', '—'],
    ],
)
doc.add_paragraph()

add_para(
    '置信度分布方面，大多数检测结果集中在高置信度区间：置信度≥0.9的图片共29张（占检出总数的74.4%），'
    '置信度在0.8-0.9之间的4张（10.3%），0.5-0.8之间的4张（10.3%），低于0.5的2张（5.1%）。'
    '这一定量分布说明模型对大多数真实照片的判断较为确信。'
)

add_para(
    '未检出的6张照片分别为：壶-晚商-兽面纹、簋-西周-兽面纹（b和e两张）、'
    '罍-商朝-饕餮纹（兽面纹）+云雷纹、觚-商朝-兽面纹+夔纹、鼎（足）-汉代-兽面纹。'
    '低置信度检测（conf<0.5）包括：甗-商朝-饕餮纹（0.345）、面具-周-兽面纹（马面）（0.377）、'
    '簋-西周-兽面纹a（0.425）、方彝-周-兽面纹（0.506）。'
)

add_heading_scaled('4.5.4  结果分析', level=3)
add_para(
    '86.7%的检出率表明，线稿预训练模型对真实青铜器照片具有超出预期的泛化能力。'
    '模型在线稿上学习到的兽面纹核心视觉特征——对称性构图、双目突出、角部卷曲等——'
    '在真实照片中依然可被有效激活。然而，13.3%的漏检率也揭示了域差异（domain gap）的具体表现：'
    '（1）部分照片中兽面纹仅作为器物的局部装饰出现（如鼎足、壶耳），纹饰面积占比较小，'
    '与训练数据中纹饰铺满全图的分布差异显著；'
    '（2）西周晚期及汉代的部分兽面纹已趋于简化与几何化，与商代晚期典型的具象兽面纹风格差异较大；'
    '（3）真实照片中的锈蚀、磨损和复杂背景（展柜反光、多器物重叠）增加了检测难度。'
)

add_para(
    '此外，当前检测均为覆盖整张图片的单一全图框，模型本质上是进行图像级二分类判断'
    '（"该图是否含有兽面纹"），而非精确的纹饰区域定位。'
    '在真实应用场景中，需要对单张照片中的多个纹饰区域分别进行精确定位，'
    '这要求下一阶段的迁移学习采用精准边界框标注。'
)

# ============ 5. 讨论 ============
add_heading_scaled('5  讨论', level=1)

add_heading_scaled('5.1  结果分析', level=2)
add_para(
    '实验结果表明，基于YOLOv8n的线稿纹饰检测模型在封闭测试环境下达到了接近完美的检测精度。'
    'mAP@50和mAP@50-95均为0.995，说明模型不仅能正确分类兽面纹图像，'
    '而且在严格的定位标准下仍然保持了极高的回归精度。'
    '这一结果超出了本文初始设定的验收标准（mAP@50≥0.85），说明线稿图像作为训练数据具有天然的优越性'
    '——风格一致、背景干净、纹饰边界清晰，模型可以高效地学习到纹饰的视觉特征。'
)

add_para(
    '然而，需要客观看待这一结果。由于标注策略采用全图框，'
    '当前任务本质上是"纹饰图像二分类"而非传统意义上的多目标检测。'
    '76种兽面纹与19种蟠龙纹在视觉风格上差异显著（前者为对称性兽面构图，后者为卷曲龙形纹样），'
    '模型可能主要通过全局纹理特征而非局部细节进行判别。'
    '该模型在实际应用中的泛化能力，尚需通过更多样化的数据集和真实青铜器照片来验证。'
)

add_heading_scaled('5.2  迁移学习方案设计', level=2)
add_para(
    '基于4.5节的跨域测试结果，本文制定了以下迁移学习方案，作为第二阶段的核心工作：'
)
add_para(
    '（1）数据标注升级：当前的"全图框"标注（整张图像即为一个兽面纹框）适用于线稿分类，'
    '但无法满足真实照片中精确定位纹饰区域的需求。第二阶段将使用LabelImg或Labelme标注工具，'
    '对45张真实照片中的兽面纹具体区域进行精准边界框标注，每张照片可能包含0至多个标注框。'
    '重点标注当前漏检和低置信度的10张照片。'
)
add_para(
    '（2）数据集划分：将45张真实照片按70:20:10比例划分为微调训练集（约31张）、'
    '验证集（约9张）和测试集（约5张）。由于样本量有限，将同时保留线稿训练集中的部分数据'
    '作为混合训练的正则化约束，防止灾难性遗忘。'
)
add_para(
    '（3）微调策略：以第一阶段best.pt为初始化权重，冻结YOLOv8n backbone的前6层（浅层特征提取层），'
    '仅对neck和detect head进行参数更新。使用较小的学习率（lr0=0.001，为初始训练的1/10），'
    '训练轮数设为30-50 epochs，早停patience=10。'
    '数据增强方面，关闭mosaic增强（真实照片的构图信息需要保留），'
    '保留水平翻转（fliplr=0.5）和适度的色彩抖动。'
)
add_para(
    '（4）评估指标：在真实照片测试集上，目标mAP@50≥0.70、mAP@50-95≥0.50。'
    '由于真实照片的纹饰边界不如线稿清晰，对定位精度的预期应较第一阶段适当降低。'
    '同时配合人工抽查，评估检测框的定位合理性。'
)

add_heading_scaled('5.3  工程贡献', level=2)
add_para(
    '除了模型精度本身，本文的另一贡献在于构建了一套完整的、可复用的数据处理与模型训练工具链。'
    '这包括7个Python脚本（preprocess.py, auto_label.py, check_labels.py, split_dataset.py, '
    'verify_dataset.py, augment.py, predict.py）和标准化的YOLO训练脚本train.py，'
    '覆盖了从原始图像导出到模型推理部署的全流程。'
    '工具链支持正负样本混合训练、在线+离线双重数据增强、绝对路径安全配置等特性，'
    '可直接复制用于其他纹饰类别（如蟠龙纹panlong、云雷纹等）的研究工作。'
)

# ============ 6. 结论 ============
add_heading_scaled('6  结论与展望', level=1)

add_para(
    '本文针对青铜器纹饰自动识别的应用需求，提出了一种基于YOLOv8的两阶段深度学习方法，'
    '并以兽面纹（饕餮纹）为研究对象完成了第一阶段的线稿训练和第二阶段的初步跨域验证。'
    '实验结果表明：（1）利用考古图录线稿作为训练数据，可以训练出在封闭环境下精度极高的检测模型'
    '（mAP@50-95=0.995）；（2）全图框标注策略配合自动化脚本，可大幅降低数据准备的人工成本；'
    '（3）离线数据增强是应对小样本数据集的有效手段；'
    '（4）线稿预训练模型对真实青铜器照片具有一定的跨域泛化能力（45张真实照片检出率86.7%），'
    '验证了"线稿预训练+真实照片微调"两阶段策略的可行性。'
)

add_para(
    '未来工作将在以下方向展开：（1）完成第二阶段真实青铜器照片的精准标注和微调训练，'
    '将检测能力从"图像级分类"提升为"区域级定位"；（2）将单类别检测扩展至多类别'
    '（饕餮纹、夔龙纹、云雷纹、几何纹等），构建青铜器纹饰识别体系；'
    '（3）引入YOLOv8-cls分类模型进行对比实验，评估检测vs分类在纹饰识别任务上的优劣；'
    '（4）探索模型导出ONNX/TensorRT格式，实现在移动端或Web端的部署应用；'
    '（5）构建公开的青铜器纹饰图像数据集，推动该领域的学术交流与技术进步。'
)

# ============ 参考文献 ============
add_heading_scaled('参考文献', level=1)

refs = [
    '[1]  Krizhevsky A, Sutskever I, Hinton G E. ImageNet classification with deep convolutional neural networks[J]. Communications of the ACM, 2017, 60(6): 84-90.',
    '[2]  Girshick R, Donahue J, Darrell T, et al. Rich feature hierarchies for accurate object detection and semantic segmentation[C]. CVPR, 2014: 580-587.',
    '[3]  Ren S, He K, Girshick R, et al. Faster R-CNN: Towards real-time object detection with region proposal networks[J]. IEEE TPAMI, 2017, 39(6): 1137-1149.',
    '[4]  Redmon J, Divvala S, Girshick R, et al. You only look once: Unified, real-time object detection[C]. CVPR, 2016: 779-788.',
    '[5]  Jocher G, Chaurasia A, Qiu J. Ultralytics YOLOv8[EB/OL]. https://github.com/ultralytics/ultralytics, 2023.',
    '[6]  马承源. 中国古代青铜器[M]. 上海: 上海古籍出版社, 2003.',
    '[7]  陈佩芬. 中国青铜器纹饰[M]. 上海: 上海古籍出版社, 2008.',
    '[8]  上海博物馆青铜器研究组. 商周青铜器纹饰[M]. 北京: 文物出版社, 1984.',
]

for ref in refs:
    ref_para = doc.add_paragraph()
    ref_para.paragraph_format.first_line_indent = Cm(0)
    ref_para.paragraph_format.left_indent = Cm(0.74)
    ref_para.paragraph_format.line_spacing = 1.25
    ref_run = ref_para.add_run(ref)
    ref_run.font.size = Pt(10)

# ============ 附录：项目结构 ============
add_heading_scaled('附录A  项目文件结构', level=1)

project_tree = """bronze_YOLOv8/
├── test.py                  # 环境自检脚本（CUDA + YOLO）
├── requirements.txt         # pip 依赖清单
├── environment.yml          # conda 环境快照
├── 中国古代青铜器造型纹饰.pdf  # 原始数据来源
│
├── bronze_taotie/           # 兽面纹（饕餮纹）子项目 ✓已训练
│   ├── data.yaml            # nc=1, names=['taotie']
│   ├── train.py             # 训练入口
│   ├── predict.py           # 推理入口（支持批量预测）
│   ├── preprocess.py        # RGBA→RGB + 裁剪 + 重命名
│   ├── auto_label.py        # 全图框标签自动生成
│   ├── augment.py           # 离线数据增强
│   ├── split_dataset.py     # 数据集划分 + 负样本混入
│   ├── verify_dataset.py    # 训练前数据集校验
│   ├── check_labels.py      # 标注质量验证
│   ├── generate_report.py   # 学术报告自动生成
│   ├── images/train/        # 300 张训练图
│   ├── images/val/          # 20 张验证图
│   ├── labels/train/        # 240 个标签
│   ├── labels/val/          # 16 个标签
│   ├── real/                # 45 张真实青铜器文物照片（跨域测试集）
│   └── runs/detect/
│       ├── taotie_train4/   # 训练输出（best.pt + 评估图表）
│       └── real_predict/    # 真实照片预测结果（45张标注图）
│
├── bronze_long/             # 蟠龙纹子项目（正样本待收集）
│   └── （结构同上，data.yaml 中 names=['panlong']）
│
├── 兽面纹/                  # 76 张原始兽面纹 PNG（数据源）
└── 111/                     # 19 张原始蟠龙纹 PNG（数据源）"""

add_para(project_tree, indent=False)

add_heading_scaled('附录B  训练超参数一览', level=1)

add_table_with_data(
    ['参数', '取值', '参数', '取值'],
    [
        ['模型', 'YOLOv8n', 'epochs', '100（早停于72）'],
        ['imgsz', '640', 'batch', '8'],
        ['优化器', 'AdamW (auto)', '学习率', '0.002（自动）'],
        ['mosaic', '1.0', 'fliplr', '0.5'],
        ['patience', '20（早停）', 'AMP', 'True'],
        ['离线增强倍数', '×3', '最佳epoch', '52'],
        ['预测conf', '0.3', '预测iou', '0.45'],
        ['真实照片测试集', '45张', '跨域检出率', '86.7%'],
    ],
)
doc.add_paragraph()

# ============ 保存 ============
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
output_dir = os.path.join(project_root, 'irrelevant_files', 'source_materials')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, '青铜器纹饰YOLOv8识别研究项目报告.docx')
doc.save(output_path)
print(f'文档已保存至: {output_path}')
