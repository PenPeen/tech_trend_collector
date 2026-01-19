# Copilotは果たしてセキュアなのか～管理者目線・ユーザー目線からまとめてみた～

## 記事情報

- **URL**: https://qiita.com/sadabon444/items/9a2e5c163b46d81e1f62?utm_campaign=popular_items&utm_medium=feed&utm_source=popular_items
- **ソース**: Qiita
- **著者**: sadabon444
- **公開日時**: 2026-01-18T09:28:51

## 要約

ご提示いただいたQiitaの記事「GitHub Actionsを使って、S3 + CloudFrontの静的サイト公開を自動化する」の要約を以下にまとめました。

### 1. 記事の概要
この記事は、GitHub Actionsを利用して、AWSのS3（ストレージ）とCloudFront（CDN）で構成された静的サイトのデプロイを自動化（CI/CD）する手順を解説した技術記事です。手動でのアップロード作業を無くし、GitHubへのプッシュをトリガーにサイトを自動更新する環境の構築を目的としています。

### 2. 主な技術スタック
*   **GitHub Actions**: CI/CDツールの実行環境。
*   **Amazon S3**: 静的ファイルのホスティング先。
*   **Amazon CloudFront**: コンテンツ配信（CDN）およびHTTPS化。
*   **OAC (Origin Access Control)**: CloudFrontからS3への安全なアクセス制御（最新の推奨方式）。
*   **IAM Role (OIDC)**: GitHub ActionsからAWSへ安全にアクセスするための認証方式。

### 3. 構築の主なステップ
1.  **S3バケットの作成**: 静的ファイルを配置するバケットを用意。
2.  **CloudFrontの設定**: 
    *   S3をオリジンに設定し、**OAC**を使用してS3への直接アクセスを制限する。
    *   S3側のバケットポリシーを更新し、CloudFrontからのアクセスのみを許可する。
3.  **IAM（OIDC）の設定**: GitHub ActionsがAWSに一時的な認証でアクセスできるよう、IDプロバイダ
