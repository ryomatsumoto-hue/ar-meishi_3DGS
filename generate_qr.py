#!/usr/bin/env python3
"""
名刺AR用QRコード生成スクリプト
MindARのマーカーとして使用するため、高解像度で生成する
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

# ===== 設定 =====
# GitHub PagesのURLに変更してください
# 例: https://yourusername.github.io/ar-meishi/
TARGET_URL = "https://ryomatsumoto-hue.github.io/ar-meishi/"

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
QR_FILENAME = "qr_marker.png"
QR_PRINT_FILENAME = "qr_print.png"  # 名刺印刷用（余白付き）

# ===== QRコード生成 =====
def generate_qr(url, output_path, size=800):
    """MindARマーカー用の高解像度QRコードを生成"""
    qr = qrcode.QRCode(
        version=None,  # 自動選択
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 最高エラー訂正（30%）
        box_size=20,
        border=4,  # quiet zone（最低4モジュール）
    )
    qr.add_data(url)
    qr.make(fit=True)

    # 白黒のシンプルなQRコード（MindARの特徴点認識に最適）
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 指定サイズにリサイズ
    img = img.resize((size, size), Image.LANCZOS)
    img.save(output_path)
    print(f"✅ QRコード生成: {output_path} ({size}x{size}px)")
    return img

def generate_print_version(qr_img, output_path):
    """名刺印刷用：QRコードにラベルを追加"""
    # 余白付きキャンバス
    padding = 60
    label_height = 80
    canvas_size = qr_img.width + padding * 2
    canvas_height = canvas_size + label_height
    
    canvas = Image.new("RGB", (canvas_size, canvas_height), "white")
    canvas.paste(qr_img, (padding, padding))
    
    draw = ImageDraw.Draw(canvas)
    
    # ラベルテキスト
    try:
        # macOSのシステムフォント
        font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 28)
        font_small = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 20)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    # QRコードの下にテキスト
    text_y = canvas_size + 10
    draw.text((canvas_size // 2, text_y), "📱 スキャンして3Dを体験", 
              fill="black", font=font, anchor="mt")
    draw.text((canvas_size // 2, text_y + 40), "Scan to see 3D AR", 
              fill="#666666", font=font_small, anchor="mt")
    
    canvas.save(output_path)
    print(f"✅ 印刷用QRコード生成: {output_path}")

if __name__ == "__main__":
    print(f"🎯 ターゲットURL: {TARGET_URL}")
    print()
    
    if "YOUR_GITHUB_USERNAME" in TARGET_URL:
        print("⚠️  警告: TARGET_URLをGitHub PagesのURLに変更してください")
        print("   このスクリプトの TARGET_URL 変数を編集してください")
        print()
        print("   例: TARGET_URL = 'https://yourusername.github.io/ar-meishi/'")
        print()
        print("   今はプレースホルダーURLでQRコードを生成します（テスト用）")
    
    # QRコード生成
    qr_path = os.path.join(OUTPUT_DIR, QR_FILENAME)
    qr_img = generate_qr(TARGET_URL, qr_path, size=800)
    
    # 印刷用バージョン生成
    print_path = os.path.join(OUTPUT_DIR, QR_PRINT_FILENAME)
    generate_print_version(qr_img, print_path)
    
    print()
    print("📋 次のステップ:")
    print("  1. GitHub リポジトリを作成して GitHub Pages を有効化")
    print("  2. このスクリプトの TARGET_URL を実際のURLに変更")
    print("  3. スクリプトを再実行して最終版QRコードを生成")
    print("  4. qr_marker.png を MindAR Compiler でコンパイル")
    print("     → https://hiukim.github.io/mind-ar-js-doc/tools/compile")
