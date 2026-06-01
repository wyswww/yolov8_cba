# -*- coding: utf-8 -*-
"""Regenerate a clearer Figure 6-1 metric comparison chart."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "论文图表" / "图6-1_主要模型测试指标对比图.png"


MODELS = [
    ("Baseline 640", [0.9032, 0.8512, 0.8961, 0.7382]),
    ("ECA Attention", [0.8090, 0.8114, 0.8353, 0.6534]),
    ("YOLOv8m-P2", [0.8130, 0.8005, 0.8377, 0.6547]),
    ("WeakAug 800", [0.8975, 0.8527, 0.8898, 0.7278]),
    ("Baseline 800", [0.8859, 0.8616, 0.8993, 0.7297]),
    ("Strong 800", [0.9345, 0.9419, 0.9673, 0.8240]),
]

METRICS = ["Precision", "Recall", "mAP@0.5", "mAP@0.5:0.95"]
COLORS = ["#2f6db3", "#5aa469", "#df7f32", "#8d8d8d"]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        ROOT / "Font" / "platech.ttf",
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def main() -> None:
    width, height = 1800, 1180
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)

    title_font = font(42, True)
    axis_font = font(25)
    label_font = font(23)
    value_font = font(22)
    legend_font = font(24)
    note_font = font(20)

    d.text((width // 2, 48), "主要模型测试指标对比", font=title_font, fill="#1f2937", anchor="mm")
    d.text(
        (width // 2, 92),
        "同一测试集下的Precision、Recall、mAP@0.5和mAP@0.5:0.95对比",
        font=note_font,
        fill="#4b5563",
        anchor="mm",
    )

    plot_left = 315
    plot_right = 1640
    plot_top = 145
    plot_bottom = 1010
    plot_w = plot_right - plot_left
    x_max = 1.0

    # Vertical grid lines.
    for i in range(0, 11):
        x = plot_left + plot_w * i / 10
        color = "#cfd8e3" if i in {0, 10} else "#e6ebf2"
        d.line((x, plot_top, x, plot_bottom), fill=color, width=2 if i in {0, 10} else 1)
        d.text((x, plot_bottom + 22), f"{i / 10:.1f}", font=axis_font, fill="#374151", anchor="mt")

    group_h = (plot_bottom - plot_top) / len(MODELS)
    bar_h = 23
    metric_gap = 7

    for model_idx, (model_name, values) in enumerate(MODELS):
        group_y = plot_top + model_idx * group_h
        center_y = group_y + group_h / 2
        d.text((plot_left - 18, center_y), model_name, font=label_font, fill="#111827", anchor="rm")

        first_bar_y = center_y - (len(values) * bar_h + (len(values) - 1) * metric_gap) / 2
        for metric_idx, value in enumerate(values):
            y1 = first_bar_y + metric_idx * (bar_h + metric_gap)
            y2 = y1 + bar_h
            x2 = plot_left + plot_w * value / x_max
            d.rounded_rectangle((plot_left, y1, x2, y2), radius=5, fill=COLORS[metric_idx])
            # Put values outside the bar with enough right-side margin.
            value_x = min(x2 + 12, plot_right + 18)
            d.text((value_x, (y1 + y2) / 2), f"{value:.4f}", font=value_font, fill="#111827", anchor="lm")

        if model_idx < len(MODELS) - 1:
            sep_y = group_y + group_h
            d.line((plot_left - 260, sep_y, plot_right + 95, sep_y), fill="#f0f2f5", width=1)

    # Axis label.
    d.text((plot_left + plot_w / 2, plot_bottom + 70), "指标值", font=axis_font, fill="#374151", anchor="mm")

    # Legend.
    legend_y = 1100
    total_legend_w = 0
    legend_items = []
    for metric in METRICS:
        text_w = d.textbbox((0, 0), metric, font=legend_font)[2]
        item_w = 34 + 10 + text_w + 36
        legend_items.append((metric, item_w))
        total_legend_w += item_w

    x = (width - total_legend_w) / 2
    for idx, (metric, item_w) in enumerate(legend_items):
        d.rounded_rectangle((x, legend_y - 12, x + 34, legend_y + 12), radius=4, fill=COLORS[idx])
        d.text((x + 44, legend_y), metric, font=legend_font, fill="#111827", anchor="lm")
        x += item_w

    OUT.parent.mkdir(exist_ok=True)
    img.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
