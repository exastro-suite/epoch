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

1. 次のコマンドを実行して、EPOCHの初期設定を行います:

    ```bash
    kubectl run -i --rm set-host -n epoch-system --restart=Never --image=exastro/epoch-setting:0.3_3 --pod-running-timeout=30m -- set-host [your-host]
    ```
    **注:** [your-host]には、ご自身のホストに接続するためのサーバー名またはIPアドレスを指定してください。

    **注:** EPOCHがインストール中の場合、以下のエラーとなることがあります。その際は再度コマンドを実行してください。

    ```
    error: timed out waiting for the condition
    ```

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
