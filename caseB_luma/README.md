# Case B: MindAR.js + Luma AI Web SDK

## 概要

名刺のQRコードをiOSカメラで読み取ると、QRコードの上に3D Gaussian Splatting（3DGS）データがニョキッと出現するWebARアプリ。

- **ARフレームワーク**: MindAR.js v1.2.5（画像トラッキング型）
- **3Dエンジン**: Three.js r158
- **3DGSレンダラー**: Luma AI Web SDK（`@lumaai/luma-web` v0.x）
- **ホスティング**: GitHub Pages
- **URL**: https://ryomatsumoto-hue.github.io/ar-meishi_3DGS/caseB_luma/

---

## ✅ 達成できたこと

1. **WebARの基本動作**: MindAR.jsによる画像マーカートラッキングが動作
2. **カメラ映像表示**: iOSのSafariでカメラ映像が全画面表示される
3. **マーカー認識**: `marker_rich.png`を認識（`onTargetFound`が発火）
4. **Luma SDKの初期化**: `window.LumaWeb.LumaSplatsThree`が正常に取得できる
5. **`LumaSplatsThree`インスタンス作成**: エラーなく初期化できる

---

## ❌ 未解決の問題

### 主要問題: splatファイルの読み込みが完了しない

**症状**: `onLoad`も`onProgress`も発火しない。splatが表示されない。

**根本原因**: Luma AI Web SDKは内部でWebAssembly（WASM）+ Web Workerを使ってsplatをダウンロード・パースしています。

```javascript
// Luma SDK内部のWorker生成コード
this.worker = new Worker(URL.createObjectURL(new Blob([workerCode])));
```

iOSのSafariでは、**blob URLから生成されたWorkerがfetchを実行できない**制限があります。このため、splatファイルのダウンロードが完了しません。

### 技術的詳細

| 項目 | 状況 |
|---|---|
| `window.LumaWeb`の公開 | ✅ rollupでIIFEバンドル後に解決 |
| `LumaSplatsThree`の取得 | ✅ 成功 |
| `LumaSplatsThree`インスタンス作成 | ✅ 成功 |
| マーカー認識 | ✅ 成功 |
| splatファイルのダウンロード | ❌ Worker内部でfetch失敗 |
| `onLoad`イベント | ❌ 発火しない |
| `onProgress`イベント | ❌ 発火しない |

---

## Luma AI Web SDKが使えるシーン

| 環境 | 対応 | 備考 |
|---|---|---|
| Mac/PC Chrome | ✅ 完全動作 | Workerの制限なし |
| Mac/PC Safari | ✅ 動作 | Safari 16以降 |
| Android Chrome | ✅ 動作 | Workerの制限なし |
| **iOS Safari** | ❌ Worker制限 | 今回の問題 |
| iOS Chrome | ❌ WebKitベース | Safariと同じ制限 |

**結論**: Luma AI Web SDKはデスクトップWebARやAndroid向けには有効だが、iOSのSafariには不向き。

---

## ファイル構成

```
caseB_luma/
├── index.html              # メインWebARページ
├── ryo_ss60_edit.splat     # 3DGSデータ（3.5MB、109,671スプラット）
├── targets.mind            # MindARマーカーファイル（marker_rich.pngから生成）
├── marker_rich.png         # ARマーカー画像（QRコード＋装飾）
├── three.min.js            # Three.js r158（ローカル）
├── mindar-image-three.umd.js  # MindAR.js（rollupでIIFEバンドル済み）
└── luma-web.js             # Luma AI Web SDK（rollupでIIFEバンドル済み）
```

---

## 技術的知見

### luma-web.jsのグローバル公開方法

元の`luma-web.js`は`window.LumaWeb`を公開していなかった。以下の手順で解決：

1. rollupで`@lumaai/luma-web`をIIFEバンドル（`window.THREE`を外部依存として使用）
2. バンドル内の`dA`オブジェクト（エクスポートオブジェクト）を`window.LumaWeb`に代入

```javascript
// rollup設定
export default {
  input: 'luma-entry.mjs',
  output: {
    format: 'iife',
    name: 'LumaWeb',
    globals: { 'three': 'THREE' }
  },
  external: ['three']
};
```

### LumaSplatsThreeの使い方（デスクトップ向け）

```javascript
var splat = new LumaWeb.LumaSplatsThree({
  source: 'https://example.com/path/to/file.splat',
  enableThreeShaderIntegration: false,
  particleRevealEnabled: false
});
splat.onLoad = function() { console.log('loaded'); };
scene.add(splat);
```

---

## 残課題・次のアプローチ候補

### Case C: gsplat.js
- iOSのSafariで動作実績あり
- Workerなしでメインスレッドで動作可能
- Three.jsと統合可能
- MindARと組み合わせられる

### Case D: antimatter15/splat
- 軽量なsplatビューア
- Workerなし版あり
- Three.jsとの統合が必要

### Case E: SplatParser + SplatBufferGenerator（Workerなし）
- `GaussianSplats3D.SplatParser`でメインスレッドパース
- `SplatBufferGenerator`でSplatBufferを生成
- `Viewer`に直接渡す
