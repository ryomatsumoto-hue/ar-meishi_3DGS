#!/usr/bin/env python3
"""
MindAR用マーカー画像生成スクリプト
QRコードの周囲に特徴的なデザインを追加して認識率を向上させる
"""

import sys
import subprocess

def install_if_needed(package):
    try:
        __import__(package.split('[')[0])
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install_if_needed("qrcode[pil]")
install_if_needed("Pillow")

import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import math

TARGET_URL = "https://ryomatsumoto-hue.github.io/ar-meishi_3DGS/"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_rich_marker(url, output_path, canvas_size=1000):
    """
    MindAR認識率を高めるため、QRコードの周囲に
    豊富なテクスチャ（幾何学模様・テキスト）を追加したマーカーを生成
    """
    # --- QRコード生成 ---
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # QRコードを中央に配置（全体の50%サイズ）
    qr_size = int(canvas_size * 0.50)
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

    # --- キャンバス作成（白背景） ---
    canvas = Image.new("RGB", (canvas_size, canvas_size), "white")
    draw = ImageDraw.Draw(canvas)

    # --- 外枠の装飾パターン（特徴点を増やす） ---
    # 1. 外周に濃いボーダー
    border_w = 30
    draw.rectangle([0, 0, canvas_size-1, canvas_size-1], outline="black", width=border_w)

    # 2. コーナーに大きな黒い四角（MindARのコーナー検出に有効）
    corner_size = 80
    corners = [
        (border_w, border_w),
        (canvas_size - border_w - corner_size, border_w),
        (border_w, canvas_size - border_w - corner_size),
        (canvas_size - border_w - corner_size, canvas_size - border_w - corner_size),
    ]
    for cx, cy in corners:
        draw.rectangle([cx, cy, cx + corner_size, cy + corner_size], fill="black")
        # コーナー内に白い小四角
        inner = 20
        draw.rectangle([cx + inner, cy + inner, cx + corner_size - inner, cy + corner_size - inner], fill="white")

    # 3. 上下左右に特徴的なパターン（ドット列）
    dot_r = 8
    dot_spacing = 40
    margin = border_w + corner_size + 20

    # 上辺ドット列
    x = margin
    while x < canvas_size - margin:
        draw.ellipse([x - dot_r, border_w + 15 - dot_r, x + dot_r, border_w + 15 + dot_r], fill="black")
        x += dot_spacing

    # 下辺ドット列
    x = margin
    while x < canvas_size - margin:
        draw.ellipse([x - dot_r, canvas_size - border_w - 15 - dot_r, x + dot_r, canvas_size - border_w - 15 + dot_r], fill="black")
        x += dot_spacing

    # 左辺ドット列
    y = margin
    while y < canvas_size - margin:
        draw.ellipse([border_w + 15 - dot_r, y - dot_r, border_w + 15 + dot_r, y + dot_r], fill="black")
        y += dot_spacing

    # 右辺ドット列
    y = margin
    while y < canvas_size - margin:
        draw.ellipse([canvas_size - border_w - 15 - dot_r, y - dot_r, canvas_size - border_w - 15 + dot_r, y + dot_r], fill="black")
        y += dot_spacing

    # 4. 中央エリアの背景（薄いグレー）
    center_margin = 120
    draw.rectangle(
        [center_margin, center_margin, canvas_size - center_margin, canvas_size - center_margin],
        fill="#f0f0f0"
    )

    # 5. テキスト追加（特徴点として機能）
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    except:
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 22)
        except:
            font_large = ImageFont.load_default()
            font_small = font_large

    # 上部テキスト
    text_top = "AR MEISHI"
    draw.text((canvas_size // 2, center_margin + 20), text_top,
              fill="black", font=font_large, anchor="mt")

    # 下部テキスト
    text_bottom = "Scan to see 3D"
    draw.text((canvas_size // 2, canvas_size - center_margin - 20), text_bottom,
              fill="#333333", font=font_small, anchor="mb")

    # 6. 左右にダイヤモンド形状
    diamond_size = 25
    # 左
    lx, ly = center_margin + 30, canvas_size // 2
    draw.polygon([
        (lx, ly - diamond_size),
        (lx + diamond_size, ly),
        (lx, ly + diamond_size),
        (lx - diamond_size, ly)
    ], fill="black")
    # 右
    rx, ry = canvas_size - center_margin - 30, canvas_size // 2
    draw.polygon([
        (rx, ry - diamond_size),
        (rx + diamond_size, ry),
        (rx, ry + diamond_size),
        (rx - diamond_size, ry)
    ], fill="black")

    # --- QRコードを中央に貼り付け ---
    qr_x = (canvas_size - qr_size) // 2
    qr_y = (canvas_size - qr_size) // 2
    canvas.paste(qr_img, (qr_x, qr_y))

    # --- 保存 ---
    canvas.save(output_path, "PNG")
    print(f"✅ マーカー画像生成: {output_path} ({canvas_size}x{canvas_size}px)")
    return canvas

if __name__ == "__main__":
    print(f"🎯 ターゲットURL: {TARGET_URL}")
    print()

    marker_path = os.path.join(OUTPUT_DIR, "marker_rich.png")
    img = generate_rich_marker(TARGET_URL, marker_path, canvas_size=1000)

    print()
    print("=" * 50)
    print("次のステップ:")
    print("1. marker_rich.png を MindAR Compiler でコンパイル")
    print("   https://hiukim.github.io/mind-ar-js-doc/tools/compile")
    print("2. 生成された targets.mind を ar-meishi/ フォルダに配置")
    print("3. git add targets.mind && git commit -m 'update marker' && git push")
    print("=" * 50)
