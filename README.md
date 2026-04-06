# AR 名刺 - 3DGS WebAR

名刺のQRコードをiOSカメラで読み取ると、3D Gaussian Splattingのデータがニョキッと出現するWebARアプリです。

## 📁 ファイル構成

```
ar-meishi/
├── index.html              ← メインWebARページ
├── ryo_ss60_edit.splat     ← 3DGSデータ（3.3MB）
├── qr_marker.png           ← QRコード画像（MindARマーカー用）
├── qr_print.png            ← 名刺印刷用QRコード
├── targets.mind            ← MindARマーカーデータ ※要生成
├── generate_qr.py          ← QRコード生成スクリプト
└── README.md               ← このファイル
```

## 🚀 セットアップ手順

### Step 1: GitHub リポジトリ作成

```bash
# ar-meishi フォルダで実行
cd /Users/ryo_matsumoto/Desktop/ar-meishi
git init
git add .
git commit -m "Initial commit: AR meishi WebAR"
```

GitHubで `ar-meishi` という名前のリポジトリを作成し、プッシュ：

```bash
git remote add origin https://github.com/YOUR_USERNAME/ar-meishi.git
git branch -M main
git push -u origin main
```

### Step 2: GitHub Pages を有効化

1. GitHubリポジトリの **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / **/ (root)**
4. **Save** をクリック
5. 数分後に `https://YOUR_USERNAME.github.io/ar-meishi/` でアクセス可能になる

### Step 3: QRコードを最終版に更新

`generate_qr.py` の `TARGET_URL` を実際のURLに変更：

```python
TARGET_URL = "https://YOUR_USERNAME.github.io/ar-meishi/"
```

スクリプトを再実行：

```bash
python3 generate_qr.py
```

### Step 4: MindAR マーカーファイルを生成 ⚠️ 重要

1. ブラウザで以下のURLを開く：
   **https://hiukim.github.io/mind-ar-js-doc/tools/compile**

2. `qr_marker.png` をアップロード

3. **Start** をクリックして処理を待つ

4. 生成された `targets.mind` をダウンロード

5. `ar-meishi/` フォルダに配置

6. GitHubにプッシュ：
   ```bash
   git add targets.mind qr_marker.png
   git commit -m "Add MindAR marker file"
   git push
   ```

### Step 5: 動作確認

iOSのSafariで `https://YOUR_USERNAME.github.io/ar-meishi/` を開き、
名刺のQRコードにカメラを向ける。

---

## ⚙️ カスタマイズ

`index.html` の `CONFIG` オブジェクトで調整できます：

```javascript
const CONFIG = {
  splatPath: "./ryo_ss60_edit.splat",  // 3DGSファイルのパス
  mindFilePath: "./targets.mind",       // マーカーファイルのパス
  targetScale: 0.15,    // 3DGSの表示サイズ（大きくしたい場合は増やす）
  positionOffset: { x: 0, y: 0.1, z: 0 },  // 位置調整
  animDuration: 800,    // 出現アニメーション時間（ms）
};
```

---

## 🔧 技術スタック

| 役割 | ライブラリ |
|------|-----------|
| ARマーカートラッキング | [MindAR.js](https://hiukim.github.io/mind-ar-js-doc/) v1.2.5 |
| 3Dレンダリング | [Three.js](https://threejs.org/) r158 |
| 3DGS描画 | [@mkkellogg/gaussian-splats-3d](https://github.com/mkkellogg/GaussianSplats3D) v0.4.5 |
| アニメーション | [TWEEN.js](https://github.com/tweenjs/tween.js) v18 |
| ホスティング | GitHub Pages |

---

## ⚠️ 注意事項

- **HTTPS必須**: WebARはHTTPS環境でのみ動作します（GitHub Pagesは自動でHTTPS）
- **iOS Safari**: iOS 15.4以降のSafariで動作確認済み
- **カメラ許可**: 初回アクセス時にカメラ許可が必要です
- **QRコードの認識精度**: QRコードは特徴点が少ないため、明るい環境で使用してください
- **パフォーマンス**: 3DGSはGPU負荷が高いため、古いiOSデバイスでは動作が重くなる場合があります

---

## 🐛 トラブルシューティング

| 症状 | 対処法 |
|------|--------|
| `targets.mind が見つかりません` | Step 4 の手順でMindARマーカーを生成してください |
| カメラが起動しない | SafariでHTTPSのURLを使用しているか確認 |
| 3DGSが表示されない | `CONFIG.targetScale` の値を大きくしてみてください |
| QRコードを認識しない | 明るい環境で、QRコードを画面の中央に映してください |
