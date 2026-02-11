# 🚀 デプロイ手順

本番環境（Cloud Run および Firebase Hosting）へのデプロイ手順です。

## 事前準備

1. **プロジェクトID** の確認:
   ```bash
   gcloud config get-value project
   ```
   *(以下、`[PROJECT_ID]` と表記します)*

2. **プロジェクト番号** の確認:
   ```bash
   gcloud projects describe [PROJECT_ID] --format="value(projectNumber)"
   ```
   *(以下、`[PROJECT_NUMBER]` と表記します)*

---

## フロントエンドのビルドとデプロイ

1. `frontend/.env.production` を作成し、バックエンドのURLを設定します。
   ```env
   VITE_API_BASE_URL=https://personal-book-brain-[PROJECT_NUMBER].asia-northeast1.run.app
   ```

2. ヒルドとデプロイを実行します。
   ```bash
   cd frontend
   npm install
   npm run build
   firebase deploy --only hosting
   ```

---

## バックエンドのデプロイ

1. `backend` ディレクトリに移動します。
   ```bash
   cd ../backend
   ```

2. デプロイコマンドを実行します。

   フロントエンドのURLを許可設定（CORS）に含めてデプロイします。

   `gcloud` コマンドの制約を回避するため、複数のURLを指定する場合は **セミコロン (`;`)** で区切ります。

   ```bash
   gcloud run deploy personal-book-brain \
   --source . \
   --project [PROJECT_ID] \
   --region asia-northeast1 \
   --allow-unauthenticated \
   --set-env-vars "GOOGLE_CLOUD_PROJECT=[PROJECT_ID],VERTEX_AI_DATA_STORE_ID=[VERTEX_AI_DATA_STORE_ID],CORS_ORIGINS=https://[PROJECT_ID].web.app;https://[PROJECT_ID].firebaseapp.com"
   ```

---

## 完了

ブラウザで `https://[PROJECT_ID].web.app` にアクセスし、動作を確認してください。
