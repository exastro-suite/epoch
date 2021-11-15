# EPOCH インストール

このガイドでは、EPOCH のインストール方法について説明します。以下のトピックについて説明します:

* [前提条件](#前提条件)
* [EPOCHのインストール](#epochのインストール)

## 前提条件

1. Kubernetes クラスター バージョン 1.18 ～ 1.21が必要です。

1. 使用するServiceAccountにcluster-adminロールを付与してください。


## EPOCHのインストール

次の手順の通り作業を進めてください。

1. 次のコマンドを実行して、EPOCH をインストールします:

    ```bash
    kubectl apply -f https://github.com/exastro-suite/epoch/releases/latest/download/epoch-install.yaml
    ```

    **注:** 以下のようなエラーが表示されたときは、もう一度コマンドを実行してください
    ```
    Error from server (InternalError): error when creating "epoch-install.yaml": Internal error occurred: failed calling webhook "webhook.triggers.tekton.dev": Post "https://tekton-triggers-webhook.tekton-pipelines.svc:443/defaulting?timeout=10s": dial tcp ***.***.***.***:443: connect: connection refused
    ```
   

1. すべてのコンポーネントがRunningステータスを表示するまで、次のコマンドを使用してインストールを監視します:

    - epoch-systemの監視
        ```bash
        kubectl get pods -n epoch-system --watch
        ```
        **注:** 監視を停止するには、CTRL+C を押します。


    - exastro-platform-authentication-infraの監視
        ```bash
        kubectl get pods -n exastro-platform-authentication-infra --watch
        ```

        **注:** 監視を停止するには、CTRL+C を押します。

1. パイプライン設定用の永続ボリュームを設定します:

    - 以下のマニフェストを我々のGitHubから取得してください。

        ```bash
        curl -OL https://github.com/exastro-suite/epoch/releases/latest/download/epoch-pv.yaml
        ```

    - `# Please specify the host name of the worker node #` の部分をご自身のホスト名に変換してください。

    - 以下のコマンドでkubernetes環境へ反映してください。

        ```bash
        kubectl apply -f epoch-pv.yaml
        ```

1. 次のコマンドを実行して、EPOCHの初期設定を行います:

    ```bash
    kubectl exec -it deploy/authentication-infra-setting -n epoch-system -- bash /app/setting-script.sh [your-host]
    ```
    **注:** [your-host]には、ご自身のホストに接続するためのサーバー名またはIPアドレスを指定してください。


これでEPOCHを使用する準備が整いました。

# EPOCHの起動

- 次のURLをブラウザに入力してアクセスします:

    ```bash
    https://your-host:30443/
    ```

- サインインの画面からユーザ登録のリンク(Register)をクリックして、ユーザ登録を行ってからご使用ください。

# ツールのユーザ・パスワードの確認方法

- ワークスペース作成後に、次のコマンドを実行してツールのユーザ・パスワードを表示します:

    ```bash
    kubectl exec -it -n epoch-system deploy/workspace-db -- mysql -N -B -u root -ppassword workspace_db -e'select info from workspace_access;'
    ```

- SonarQubeのユーザ・パスワード:  
    コマンドで表示した"SONARQUBE_USER","SONARQUBE_PASSWORD"の内容がユーザ・パスワードとなります

- IT-Automationのユーザ・パスワード:  
    コマンドで表示した"ITA_EPOCH_USER","ITA_EPOCH_PASSWORD"の内容がユーザ・パスワードとなります

- ArgoCDのユーザ・パスワード:  
    コマンドで表示した"ARGOCD_USER","ARGOCD_PASSWORD"の内容がユーザ・パスワードとなります
