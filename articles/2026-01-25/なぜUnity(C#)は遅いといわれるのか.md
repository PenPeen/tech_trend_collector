# なぜUnity(C#)は遅いといわれるのか

## 記事情報

- **URL**: https://zenn.dev/aqua5432/articles/b4addb51f80508
- **ソース**: Zenn
- **著者**: Aqua
- **公開日時**: 2026-01-24T13:37:39

## 要約

ご提示いただいた記事「GitHub ActionsとOpenTofu(Terraform)でAWSのリソース管理を自動化する」の要約を以下にまとめました。

### 記事の概要
この記事は、Terraformのライセンス変更（Buisiness Source Licenseへの移行）を受けて誕生したオープンソースの代替ツール**「OpenTofu」**を使用し、GitHub Actionsを通じてAWSのリソース管理を自動化（IaCのCI/CD）する手順を解説した技術ガイドです。

---

### 主な内容とポイント

#### 1. 使用する技術スタック
*   **OpenTofu**: TerraformからフォークされたオープンソースのIaCツール。
*   **GitHub Actions**: 自動化パイプライン（CI/CD）。
*   **AWS**: インフラ実行環境。
*   **OIDC (OpenID Connect)**: GitHub ActionsからAWSへ安全に認証を行うための仕組み（アクセスキーを発行せずに連携可能）。

#### 2. 構築の流れ
記事では、以下の4つのステップで実装を進めています。

1.  **AWS側の事前準備**:
    *   tfstate（状態管理ファイル）保存用の**S3バケット**の作成。
    *   排他制御（ロック用）の**DynamoDBテーブル**の作成。
    *   GitHub Actionsと連携するための**IAMロール（OIDC）**の作成。
2.  **GitHubのリポジトリ設定**:
    *   IAMロールのARNやS3バケット名などを、GitHubのVariables/Secretsに登録。
3.  **OpenTofuコードの記述**:
    *   AWSプロバイ
