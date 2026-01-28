# 就職活動のためにLangGraph+ローカルLLMでアプリを作ったら、意外にも使える子に仕上がったので自慢させてくれ

## 記事情報

- **URL**: https://qiita.com/Ultra-grand-child/items/d3f492b66a35bbaa0a94?utm_campaign=popular_items&utm_medium=feed&utm_source=popular_items
- **ソース**: Qiita
- **著者**: Ultra-grand-child
- **公開日時**: 2026-01-25T22:05:56

## 要約

ご提示いただいたQiitaの記事「GitHub ActionsでTerraformを実行する際のベストプラクティスを考えてみた」の要約です。

この記事は、**GitHub Actionsを用いてTerraformのCI/CDパイプラインを構築する際の、セキュリティ・品質・運用の効率性を考慮した実践的なベストプラクティス**について解説しています。

---

### 1. セキュリティの担保
*   **OIDC（OpenID Connect）の利用:** 
    *   AWSやGCPなどの認証には、静的なアクセスキーをGitHubに保存するのではなく、短期間のみ有効なトークンを発行するOIDCを利用することを強く推奨しています。
*   **権限の最小化:** 
    *   GitHub Actionsに付与するIAMロールなどの権限は、必要最小限（Least Privilege）に絞ります。

### 2. コード品質の維持（CI）
Pull Request時に自動実行すべき以下のチェック項目が挙げられています。
*   **`terraform fmt`:** コードの整形。
*   **`terraform validate`:** 構文チェック。
*   **TFLint:** ベストプラクティスに沿っているかの静的解析。
*   **tfsec / Chekov:** セキュリティ上の脆弱性（パブリックなS3バケット等）がないかのスキャン。
*   **terraform-docs:** ドキュメント（README）の自動更新。

### 3. ワークフローの設計（Plan & Apply）
*   **Planの結果をPRにコメント:** 
    *   `tfcmt` などのツールを活用し、`terraform plan` の結果をPull Requestのコメントとして投稿することで、レビューを容易にします。
*   **Applyの自動化:** 
    *   メインブランチへのマージをトリガーに `terraform apply` を実行する構成。
    *   手動承認（Environmentsの利用）を挟むことで、意図しない破壊的変更を防ぐ構成についても触れています。

### 4
