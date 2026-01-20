# なぜ、MCPよりも「ファイルベースで扱うSkills」の方が便利なのか

## 記事情報

- **URL**: https://zenn.dev/karamage/articles/db488ca6362eb2
- **ソース**: Zenn
- **著者**: karamage
- **公開日時**: 2026-01-19T11:45:14

## 要約

ご提示いただいた記事「GitHub Actions + OIDC で AWS への認証をセキュアにする」の要約を以下にまとめます。

### 記事の概要
GitHub ActionsからAWSを操作する際、従来の「IAMユーザーのアクセスキー」を使用する方法に代わり、**OIDC（OpenID Connect）**を利用して一時的な認証情報を取得する、より安全な設定方法を解説している記事です。

---

### 要点

#### 1. なぜOIDCを使うのか（従来の課題とメリット）
*   **従来の課題:** IAMユーザーのアクセスキーをGitHubのSecretsに保存する方法は、キーの漏洩リスクや、定期的な更新作業の手間（運用負荷）がある。
*   **OIDCのメリット:** 
    *   **キーレス:** 長期的なアクセスキーをGitHub側に保存する必要がない。
    *   **短寿命:** 有効期限が短い一時的なトークンを使用するため、万が一漏洩しても被害が限定的。
    *   **管理の簡略化:** キーのローテーション（更新）が不要。

#### 2. 認証の仕組み
1.  GitHub Actions実行時に、GitHubから**OIDCトークン（JWT）**が発行される。
2.  AWSの**STS（Security Token Service）**に対して、そのトークンを提示してRoleの引き受け（AssumeRole）を要求する。
3.  AWS側でトークンの正当性を検証し、問題なければ**一時的な認証情報**を発行する。

#### 3. 主な設定手順
*   **AWS側の設定:**
    1.  **IDプロバイダの作成:** AWS IAMでGitHub（`token.actions.githubusercontent.com`）を信頼できるプロバイダとして登録。
    2.  **IAMロールの作成:** GitHub Actionsが利用するためのロールを作成し、信頼ポリシー（Trust Policy）を設定する。
*   **GitHub Actions側の設定:**
    1.  `permissions` 設定で `id-token: write` を許可する
