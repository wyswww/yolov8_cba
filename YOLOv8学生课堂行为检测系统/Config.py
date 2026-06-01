#coding:utf-8

# 图片及视频检测结果保存路径
save_path = 'D:'

# 使用的模型路径
model_path = 'runs/detect/baseline_finetune_img800_weakaug2/weights/best.pt'

# ROI裁剪推理开关。只有使用 train_baseline_roi_crop.py 训练出的模型时才建议开启。
roi_crop_enabled = False
roi_crop = {
    'left': 0.0,
    'top': 0.06,
    'right': 1.0,
    'bottom': 1.0,
}


names = {0: 'hand-raising',1:'reading',2:'writing',3:'using phone',4:'bowing the head',5:'leaning over the table'}

CH_names =  ['举手', '阅读', '写作', '看手机', '低头', '趴桌子上']
