# Case A: MindAR.js + 自前 .splat レンダラー

## 概要

名刺のQRコードをiOSカメラで読み取ると、QRコードの上に3D Gaussian Splatting（3DGS）データがニョキッと出現するWebARアプリ。

- **ARフレームワーク**: MindAR.js v1.2.5（画像トラッキング型）
- **3Dエンジン**: Three.js r158
- **3DGSレンダラー**: 自前実装（ビルボード + ガウシアンシェーダー）
- **ホスティング**: GitHub Pages
- **URL**: https://ryomatsumoto-hue.github.io/ar-meishi_3DGS/

---

## ✅ 達成できたこと

1. **WebARの基本動作**: MindAR.jsによる画像マーカートラッキングが動作
2. **カメラ映像表示**: iOSのSafariでカメラ映像が全画面表示される
3. **マーカー認識**: `marker_rich.png`（QRコード＋装飾デザイン）を認識
4. **3DGSデータの表示**: `.splat`ファイルをfetchしてThree.jsのMeshとして表示
5. **出現アニメーション**: マーカー認識時にBack.Outイージングでニョキッと出現
6. **向き・位置の調整**: Y軸反転、回転補正（`-PI/4 + PI`）

---

## ❌ 未解決の問題

### 主要問題: 3DGSの描画品質が低い

**原因**: `@mkkellogg/gaussian-splats-3d`ライブラリの`addSplatScene()`がiOS Safariで失敗する。

```
Viewer::addSplatScene -> Could not load file ./ryo_ss60_edit.splat
```

**根本原因**: ライブラリ内部でWeb Workerを使ってファイルをダウンロード・パースしているが、iOSのSafariではWorkerのblob URLからのfetchが制限されている。

**フォールバック**: 自前の`.splat`パーサー（ビルボード + ガウシアンシェーダー）を実装したが、以下の問題がある：
- 深度ソートなし（透明度の重ね合わせが不正確）
- 楕円形スプラットの正確な計算なし（回転行列未使用）
- 全体的に白っぽく見える（ガウシアンアルファ計算の精度不足）

### 技術的詳細

| 項目 | 状況 |
|---|---|
| `.splat`ファイルのfetch | ✅ HTTP 200、正常取得 |
| `GaussianSplats3D.Viewer`初期化 | ✅ 成功 |
| `addSplatScene()`実行 | ❌ Worker内部でfetch失敗 |
| 自前パーサー（32bytes/splat） | ✅ 動作するが品質低 |
| 深度ソート | ❌ 未実装 |
| 楕円形スプラット | ❌ 未実装（円形のみ） |

---

## ファイル構成

```
ar-meishi/
├── index.html              # メインWebARページ
├── ryo_ss60_edit.splat     # 3DGSデータ（3.5MB、109,671スプラット）
├── targets.mind            # MindARマーカーファイル（marker_rich.pngから生成）
├── marker_rich.png         # ARマーカー画像（QRコード＋装飾）
├── qr_marker.png           # QRコードのみ（旧マーカー）
├── qr_print.png            # 印刷用QRコード
├── three.min.js            # Three.js r158（ローカル）
├── three.module.min.js     # Three.js r158 ESモジュール版
├── mindar-image-three.umd.js  # MindAR.js（rollupでIIFEバンドル済み）
├── mindar-image-three.prod.js # MindAR.js（ESモジュール版、使用不可）
├── gaussian-splats-3d.umd.js  # GaussianSplats3D（window.THREE共有版）
├── generate_qr.py          # QRコード生成スクリプト
└── generate_marker.py      # マーカー画像生成スクリプト
```

---

## 技術的知見

### MindAR.jsのロード方法
- `mindar-image-three.prod.js`はESモジュール形式（`import from "three"`）
- `<script src>`では動作しない
- **解決策**: rollupでThree.jsと一緒にIIFEバンドル → `mindar-image-three.umd.js`

### .splatファイルフォーマット（mkkellogg形式）
```
32バイト/スプラット:
  offset  0: x,y,z          (float32 x3 = 12bytes)
  offset 12: scale_0,1,2    (float32 x3 = 12bytes) ← log scale
  offset 24: r,g,b,a        (uint8  x4 =  4bytes)
  offset 28: rot_0,1,2,3    (uint8  x4 =  4bytes)
```

### QRコードのマーカー認識
- QRコードのみでは特徴点が少なくMindARが認識しにくい
- **解決策**: QRコードの周囲に装飾（コーナー四角、ドット列、テキスト）を追加した`marker_rich.png`を使用

---

## 残課題（次のCaseで解決を目指す）

1. **3DGSの高品質レンダリング**: Luma AI Web SDKまたはSplatParser+SplatBufferGeneratorでWorkerなし処理
2. **深度ソート**: カメラからの距離でスプラットをソートして正確なアルファブレンディング
3. **楕円形スプラット**: 回転行列（rot_0〜3）を使った正確な楕円形描画
4. **スケール調整**: 3DGSの表示サイズ・位置の最終調整

---

## 次のアプローチ候補

### Case B: Luma AI Web SDK
- `@lumaai/luma-web`の`LumaSplatsThree`を使用
- iOSのSafariを明示的にサポート
- MindARとの統合実績あり

### Case C: SplatParser + SplatBufferGenerator（Workerなし）
- `GaussianSplats3D.SplatParser`でメインスレッドパース
- `SplatBufferGenerator`でSplatBufferを生成
- `Viewer`に直接渡す
