# Personal Book Brain 🧠

**AI駆動の書籍管理・学習リソースキュレーションシステム**

書籍名を入力するだけでAIが目次を自動取得し、学びたいテーマを入力すると蔵書から最適な学習リソースをレポートしてくれるアプリケーションです。

---

## 🎯 主な機能

| 機能 | 説明 |
|------|------|
| **📚 本の登録** | 書籍名/ISBNを入力 → Gemini + Google検索で目次を自動取得 |
| **📋 蔵書一覧** | 登録した書籍と目次を一覧表示 |
| **🔍 検索＆レポート** | テーマを入力 → Vertex AI Searchで関連書籍を検索 → AIが学習リソースレポートを生成 |

---

## 🛠️ 技術スタック

### Frontend
- **Vue.js 3** / **TypeScript** / **Tailwind CSS**
- **Vite** (Build Tool)
- **Firebase Auth** (Authentication)

### Backend
- **Python 3.13** / **FastAPI**
- **uv** (Package Manager)
- **Pydantic** (Validation)

### Google Cloud & Firebase
- **Cloud Run** (Backend Hosting)
- **Firestore** (NoSQL Database)
- **Vertex AI Agent Builder** (Semantic Search)
- **Gemini** (AI Model)
- **Firebase Hosting** (Frontend Hosting)

---

## 🚀 クイックスタート

詳細なセットアップ手順は [docs/SETUP.md](docs/SETUP.md) を参照してください。

### 前提条件
- Node.js 18+
- Python 3.13+
- uv
- gcloud CLI

### セットアップ概要

1. リポジトリをクローン
2. バックエンド依存関係をインストール (`uv sync`)
3. フロントエンド依存関係をインストール (`npm install`)
4. 環境変数を設定 (詳細は `docs/SETUP.md` 参照)
5. サーバーを起動

```bash
# Backend
cd backend && uv run uvicorn src.main:app --reload

# Frontend
cd frontend && npm run dev

```

---

## 📦 デプロイ

本番環境へのデプロイ手順は [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) を参照してください。

- **Backend**: Cloud Run
- **Frontend**: Firebase Hosting

---

## 📝 ライセンス

MIT License
