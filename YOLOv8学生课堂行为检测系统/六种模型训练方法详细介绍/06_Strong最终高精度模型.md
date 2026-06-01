# 06 Strong最终高精度模型

## 1. 对应文件

- 训练脚本：`train_strong_img800_tail_weakaug.py`
- 输出目录：`runs/detect/strong_img800_tail_weakaug`
- 测试结果目录：`runs/detect/test_strong_img800_tail_weakaug_img800`
- 初始权重：`runs/detect/baseline_mAP_100epochs/weights/best.pt`
- 模型结构：标准YOLOv8m，不修改网络结构

## 2. 核心策略

该模型是当前项目中效果最好的训练方案。它的核心不是修改网络结构，而是组合使用四个训练策略：

```text
强baseline权重 + 800高分辨率 + 长尾均衡训练集 + 弱增强二阶段微调
```

## 3. 训练配置

| 配置项 | 设置 |
|---|---|
| 初始权重 | `runs/detect/baseline_mAP_100epochs/weights/best.pt` |
| fallback权重 | `yolov8m.pt` |
| 数据集 | `datasets/classroom_tail_oversampled` |
| 动态yaml | `datasets/data_strong_img800_tail_abs.yaml` |
| 训练轮数 | `epochs=60` |
| 早停 | `patience=25` |
| 输入尺寸 | `imgsz=800` |
| batch size | `batch=4` |
| 优化器 | `AdamW` |
| 初始学习率 | `lr0=0.0001` |
| 最终学习率比例 | `lrf=0.05` |
| 学习率策略 | `cos_lr=True` |
| warmup | `warmup_epochs=2.0` |
| 损失权重 | `box=7.5, cls=0.65, dfl=1.5` |

## 4. 长尾均衡数据集

该模型使用：

```python
DATASET_DIR = Path("datasets/classroom_tail_oversampled")
```

课堂行为数据存在类别不均衡问题。多数类如阅读、书写、使用手机数量较多，少数类如低头、趴桌数量较少。直接训练时，模型容易偏向多数类，导致少数类召回不足。

长尾均衡训练集通过对少数类相关样本进行过采样，让模型在训练阶段更多看到少数类，从而改善类别学习不均衡问题。

## 5. 绝对路径yaml

脚本会动态生成：

```python
datasets/data_strong_img800_tail_abs.yaml
```

原因是项目路径中包含中文字符。Windows环境下，某些yaml路径可能出现编码问题。脚本通过 `Path.resolve()` 写入绝对路径，可以降低YOLO读取数据集失败的风险。

## 6. 高分辨率输入

该模型使用：

```python
imgsz=800
batch=4
```

相比640输入，800输入可以保留更多局部细节。这对课堂行为检测尤其重要：

- 举手依赖手臂和手部细节。
- 使用手机依赖小物体和手部区域。
- 低头和趴桌依赖头部、肩部、桌面的姿态关系。

代价是显存占用更高，因此batch size设置为4。

## 7. 弱增强策略

该模型关闭强增强：

```python
mosaic=0.0
mixup=0.0
copy_paste=0.0
```

只保留轻微增强：

```python
hsv_h=0.01
hsv_s=0.30
hsv_v=0.30
degrees=3.0
translate=0.05
scale=0.15
shear=1.0
perspective=0.0
fliplr=0.5
```

课堂行为检测不同于普通物体检测，它强依赖真实人体姿态和上下文关系。强mosaic或mixup可能制造不真实的课堂组合图像，破坏行为语义。因此，弱增强更符合该任务特点。

## 8. 二阶段微调原理

该模型优先加载baseline最优权重：

```python
BASELINE_WEIGHTS = Path("runs/detect/baseline_mAP_100epochs/weights/best.pt")
```

训练过程可以理解为：

```text
第一阶段：baseline在课堂数据上学习基础检测能力
第二阶段：strong模型在长尾均衡数据集和800输入下精细微调
```

低学习率 `lr0=0.0001` 的作用是避免破坏baseline已经学到的有效特征，只做小幅、稳定的参数更新。

## 9. 为什么提高cls损失

该模型设置：

```python
cls=0.65
```

相比baseline的 `cls=0.5` 更高。原因是课堂行为类别之间容易混淆：

- 阅读和书写视觉上相似。
- 低头和趴桌都包含头部下垂。
- 使用手机可能被误判为低头或阅读。

提高分类损失权重可以让模型更重视类别区分。

## 10. 测试结果

统一在test split和 `imgsz=800` 下测试：

| 模型 | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|---|---:|---:|---:|---:|
| baseline | 0.8859 | 0.8616 | 0.8993 | 0.7297 |
| strong_img800_tail_weakaug | 0.9345 | 0.9419 | 0.9673 | 0.8240 |

提升幅度：

| 指标           |      提升 |
| ------------ | ------: |
| Precision    | +0.0486 |
| Recall       | +0.0803 |
| mAP@0.5      | +0.0679 |
| mAP@0.5:0.95 | +0.0942 |

## 11. 特点

优点：

- 当前测试集效果最好。
- 不改网络结构，避免复杂结构带来的权重迁移问题。
- 同时解决小目标细节、类别长尾和强增强语义破坏问题。
- 适合作为论文最终推荐模型。

不足：

- 输入尺寸为800，推理开销高于640。
- batch size较小，对显存有一定要求。
- 依赖已经训练好的baseline权重。

## 12. 实验结论

`strong_img800_tail_weakaug` 的成功说明，当前项目的主要提升点不是复杂网络结构，而是更贴合数据集特点的训练策略。

论文中可以将该方法概括为：

```text
面向课堂行为检测的长尾均衡高分辨率弱增强二阶段微调方法
```

它是六种方法中最终推荐的高精度模型。
 从原始数据集生成的。

  输出目录是：

  datasets/classroom_tail_oversampled

  它的生成逻辑是：

  1. 先复制原始数据集

  原始数据集：

  datasets/学生课堂行为检测数据集

  脚本会把原始数据集的 train、val、test 都复制到新目录：

  datasets/classroom_tail_oversampled

  2. 只增强训练集，不动验证集和测试集

  脚本只对 train 里的图片做增强：

  for split in ("train", "val", "test"):
      copy_split(split)

  复制之后，只处理 train 中含有少数类目标的图片。val 和 test 保持原始不变，这样测试结果才公平。

  3. 只针对两个长尾类别增强

  脚本指定长尾类别：

  TAIL_CLASSES = {4, 5}

  对应：

  4: bowing the head        低头
  5: leaning over the table 趴桌

  这两个类别在原始训练集中样本数量较少，所以单独增强。

  4. 围绕少数类目标裁剪局部区域

  对于包含低头或趴桌的训练图片，脚本会随机选择一个少数类目标，然后围绕它裁剪一块局部区域。

  这样做不是简单复制整张图，而是让少数类目标在新样本中占比更高，同时保留桌面、身体、周围姿态等上下文。

  5. 对裁剪图做轻量增强

  每张含长尾类别的训练图最多生成 3 张增强图：

  AUGMENTATIONS_PER_TAIL_IMAGE = 3

  增强包括：

  轻微旋转
  轻微缩放
  轻微平移
  水平翻转
  亮度/对比度扰动
  轻微模糊
  轻微噪声

  不是强增强，避免破坏课堂行为语义。

  6. 同步重新计算标签

  裁剪和增强后，脚本会重新计算YOLO格式标注框，并写入新的 .txt 标签文件：

  write_labels(out_label, aug_boxes)

  所以新数据不是只有图片，标签也是对应更新过的。

  7. 生成新的 data.yaml

  最后生成：

  datasets/data_tail_oversampled.yaml

  用于训练时加载长尾均衡数据集。

  一句话总结：

  长尾均衡训练集 = 原始数据集复制版 + 只对训练集中“低头/趴桌”样本做局部裁剪和轻量增强，验证集和测试集保持不变。

  它的目的就是让模型在训练时更多看到少数类，从而缓解类别不均衡问题。
