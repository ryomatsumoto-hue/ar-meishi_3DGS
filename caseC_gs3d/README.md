# Case C: MindAR.js + GaussianSplats3D (SplatParser メインスレッドパース)

## 概要

名刺の`marker_rich.png`をiOSカメラで読み取ると、マーカーの上に3D Gaussian Splatting（3DGS）データがニョキッと出現するWebARアプリ。

- **ARフレームワーク**: MindAR.js v1.2.5（画像トラッキング型）
- **3Dエンジン**: Three.js r158
- **3DGSレンダラー**: `@mkkellogg/gaussian-splats-3d`（SplatParserでメインスレッドパース）
- **ホスティング**: GitHub Pages
- **URL**: https://ryomatsumoto-hue.github.io/ar-meishi_3DGS/caseC_gs3d/
- **バージョン**: Ver1（検証品質）

---

## ✅ 達成できたこと

1. **WebARの基本動作**: MindAR.jsによる画像マーカートラッキングが動作
2. **カメラ映像表示**: iOSのSafariでカメラ映像が全画面表示される
3. **マーカー認識**: `marker_rich.png`（QRコード＋装飾デザイン）を認識
4. **3DGSデータの表示**: `.splat`ファイルをメインスレッドでパースしてGS3D Viewerで表示
5. **出現アニメーション**: マーカー認識時にBack.Outイージングでニョキッと出現
6. **前後関係の改善**: カメラ位置をanchorGroupのローカル座標系に変換してソートに渡す

---

## 技術的な解決過程

### 問題1: MindAR.jsのロード失敗
- **原因**: `mindar-image-three.prod.js`はESモジュール形式（`import from "three"`）
- **解決**: rollupでThree.jsと一緒にIIFEバンドル → `mindar-image-three.umd.js`

### 問題2: GaussianSplats3DのWorker制限（iOS Safari）
- **原因**: `addSplatScene()`が内部でWorkerを使ってfetchするが、iOSのSafariではblob URLからのWorkerのfetchが制限される
- **解決**: `SplatParser.parseStandardSplatToUncompressedSplatArray(buffer)`でメインスレッドパース
  ```javascript
  // fetchでArrayBufferを取得（メインスレッド）
  const buffer = await fetch(url).then(r => r.arrayBuffer());
  // SplatParserでUncompressedSplatArrayに変換（メインスレッド、Workerなし）
  const splatArray = GS3D.SplatParser.parseStandardSplatToUncompressedSplatArray(buffer);
  // SplatBufferGeneratorでSplatBufferに変換
  const generator = GS3D.SplatBufferGenerator.getStandardGenerator(5, 0);
  const splatBuffer = generator.generateFromUncompressedSplatArray(splatArray);
  // ViewerにSplatBufferを直接渡す（Workerなし）
  viewer.addSplatBuffers([splatBuffer], [{}], true, false, false, false, false);
  ```

### 問題3: splatMeshの2重表示
- **原因**: `Viewer`が内部sceneにsplatMeshを追加し、さらにanchorGroupにも追加していた
- **解決**: `splatMesh.parent.remove(splatMesh)`でViewerの内部sceneから削除してからanchorGroupに追加

### 問題4: sortWorkerのblob URL制限
- **原因**: `createSortWorker()`がblob URLでWorkerを生成するが、iOSのSafariで制限される
- **解決**: `gaussian-splats-3d.umd.js`内のblob URLを`./sort-worker.js`に置き換え
  ```python
  # gaussian-splats-3d.umd.js の修正
  old = "const worker = new Worker(URL.createObjectURL(new Blob(['(', sortWorker.toString(), ')(self)'], {...})));"
  new = "const worker = new Worker('./sort-worker.js');"
  ```
  - `sort-worker.js`はsortWorker関数を抽出して別ファイルとして保存

### 問題5: カメラ角度によって3DGSの向きが変わる
- **原因**: `splatViewer.update()`がワールド座標系のカメラ位置でsplatをソートするが、splatMeshはanchorGroupの子（マーカーのローカル座標系）に配置されているため不整合が発生
- **解決**: カメラ位置をanchorGroupの逆行列で変換してからupdate()を呼ぶ
  ```javascript
  renderer.setAnimationLoop(function() {
    // anchorGroupのワールド行列を更新
    anchorGroup.updateWorldMatrix(true, false);
    // カメラのワールド位置をsplatのローカル座標系に変換
    var invMatrix = new THREE.Matrix4().copy(anchorGroup.matrixWorld).invert();
    var localCamPos = camera.position.clone().applyMatrix4(invMatrix);
    // 元のカメラ位置を保存して一時的に変換
    var origCamPos = camera.position.clone();
    camera.position.copy(localCamPos);
    splatViewer.update();
    // カメラ位置を元に戻す
    camera.position.copy(origCamPos);
    renderer.render(scene, camera);
  });
  ```

---

## ファイル構成

```
caseC_gs3d/
├── index.html                  # メインWebARページ（Ver1）
├── ryo_ss60_edit.splat         # 3DGSデータ（3.5MB、109,671スプラット）
├── targets.mind                # MindARマーカーファイル（marker_rich.pngから生成）
├── marker_rich.png             # ARマーカー画像（QRコード＋装飾）
├── three.min.js                # Three.js r158（ローカル）
├── mindar-image-three.umd.js   # MindAR.js（rollupでIIFEバンドル済み）
├── gaussian-splats-3d.umd.js   # GaussianSplats3D（sortWorkerをblob URLから./sort-worker.jsに変更済み）
├── sort-worker.js              # sortWorker関数（blob URL回避のため分離）
└── README.md                   # このファイル
```

---

## .splatファイルフォーマット（mkkellogg形式）

```
32バイト/スプラット:
  offset  0: x,y,z          (float32 x3 = 12bytes)
  offset 12: scale_0,1,2    (float32 x3 = 12bytes) ← log scale
  offset 24: r,g,b,a        (uint8  x4 =  4bytes)
  offset 28: rot_0,1,2,3    (uint8  x4 =  4bytes)
```

---

## 現在の設定値（Ver1）

```javascript
var CONFIG = {
  splatPath:      "./ryo_ss60_edit.splat",
  mindFilePath:   "./targets.mind",
  targetScale:    0.5,
  positionOffset: { x: 0, y: 0.1, z: 0 },
  rotationY:      -Math.PI / 2,   // Y軸 -90度
  rotationZ:      Math.PI,        // Z軸 180度
  animDuration:   800
};
```

---

## 残課題

1. **前後関係の完全な修正**: カメラ位置変換で改善されたが、完全ではない
2. **sortWorkerのWASM問題**: `sort-worker.js`はWASMバイナリ（`SorterWasm`）を参照しているが、メインスレッドから渡されないため完全には動作していない可能性がある
3. **向きの最終調整**: `rotationY`と`rotationZ`の最適値を名刺の実際の向きに合わせて調整が必要
4. **スケール調整**: `targetScale: 0.5`は暫定値。名刺サイズに対して適切なスケールに調整が必要
5. **デバッグオーバーレイの削除**: 本番環境では`#debug-overlay`を非表示にする

---

## 次のステップ（Ver2に向けて）

- 向きと位置の最終調整
- デバッグオーバーレイの削除
- QRコードを使った実際の名刺でのテスト
- パフォーマンス最適化（スプラット数の削減など）
