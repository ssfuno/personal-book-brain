# 🛠️ 環境構築・セットアップ

このアプリケーションをローカルで動作させるためのセットアップ手順です。

## 📋 前提条件

- **Node.js**: v18以上
- **Python**: v3.13以上
- **uv**: Python パッケージマネージャ
- **gcloud CLI**: インストール済みで、Google Cloud プロジェクトに認証されていること

## 🔑 1. 必要なID・キーの取得

Google Cloud と Firebase の設定が必要です。

### A. Google Cloud (Vertex AI) 関連
このアプリの検索機能には Vertex AI Search を使用します。

> [!NOTE]
> 本手順では、**Google Cloud プロジェクトの作成** および **Vertex AI Search でのデータストア作成** は完了しているものとして進めます。これらが未実施の場合は、先に作成を行ってください。
>
> **データストアの設定について**:
> - **データストアの種類**: 構造化データ (Structured Data) を選択してください。
> - **データのインポート**: アプリケーションからデータを登録するため、作成時は空で構いません。
> - **スキーマ**: アプリケーションが自動的に `title`, `isbn`, `toc_text`, `toc_json` などのフィールドを送信します。

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. **プロジェクトID** を確認 (例: `your-project-id`)
3. "AI Applications" の「データストア」画面を開く
4. 作成したデータストアの **データストアID** を確認 (例: `your-datastore-id`)

### B. Firebase 関連
認証機能とホスティングには Firebase を使用します。
1. [Firebase Console](https://console.firebase.google.com/) にアクセスし、プロジェクトを開く
2. 左上の歯車アイコン ⚙️ > 「プロジェクトを設定 (Project settings)」をクリック
3. 下にスクロールし、「マイアプリ (Your apps)」セクションを確認
4. "SDK setup and configuration" で `npm` を選択すると表示される `firebaseConfig` の値をメモする

---

## ⚙️ 2. 環境変数の設定

各ディレクトリに `.env` ファイルを作成します。

### Backend (`backend/.env`)

`backend` ディレクトリに `.env` ファイルを新規作成し、以下の内容を記述します。

```env
# Google Cloud プロジェクトID
GOOGLE_CLOUD_PROJECT=your-project-id

# 取得したデータストアID
VERTEX_AI_DATA_STORE_ID=your-datastore-id
```

### Frontend (`frontend/.env`)

`frontend` ディレクトリに `.env` ファイルを新規作成し、Firebase の設定値を記述します（`VITE_` プレフィックスが必要です）。

```env
# Firebase Console で取得した値をコピー
VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=000000000
VITE_FIREBASE_APP_ID=1:000000:web:000000

# ローカル開発用（空にしておくことでプロキシが有効になります）
VITE_API_BASE_URL=
```

---

## 📦 3. インストール

依存関係をインストールします。

```bash
# リポジトリのクローン
git clone <repo-url>
cd personal-book-brain

# バックエンド依存関係インストール
cd backend
uv sync
cd ..

# フロントエンド依存関係インストール
cd frontend
npm install
cd ..
```

---

## 🚀 4. ローカルでの起動

ターミナルを2つ開き、それぞれでバックエンドとフロントエンドを起動します。

**ターミナル1 (バックエンド)**:
```bash
cd backend
uv run uvicorn src.main:app --reload --port 8080
```

**ターミナル2 (フロントエンド)**:
```bash
cd frontend
npm run dev
```

ブラウザで `http://localhost:5173` を開くとアプリが起動します。
