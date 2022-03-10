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
    kubectl run -i --rm set-host -n epoch-system --restart=Never --image=exastro/epoch-setting:0.3_5 --pod-running-timeout=30m -- set-host [your-host]
    ```
    **注:** [your-host]には、ご自身のホストに接続するためのサーバー名またはIPアドレスを指定してください。

    **注:** EPOCHがインストール中の場合、以下のエラーとなることがあります。その際は再度コマンドを実行してください。

    ```
    error: timed out waiting for the condition
    ```

1. 初期設定実行中は、以下のような実行状況メッセージが表示されます。

    ```bash
    [INFO] Wait for Running setting tools pod
    [INFO] Call set-host command
    [INFO] START : set-host.sh
    [INFO] PARAM PRM_MY_HOST : [your-host]
    [INFO] **** STEP : 1 / 5 : Initialize Setting Parameter ...
    [INFO] **** STEP : 2 / 5 : Set Parameter To Configmap
    [INFO] CALL : kubectl patch configmap -n epoch-system host-setting-config
    configmap/host-setting-config patched
    [INFO] CALL : kubectl patch configmap -n exastro-platform-authentication-infra exastro-platform-authentication-infra-env
    configmap/exastro-platform-authentication-infra-env patched
    [INFO] CALL : kubectl patch configmap -n epoch-system epoch-service-api-config
    configmap/epoch-service-api-config patched
    [INFO] CALL : kubectl patch secret -n exastro-platform-authentication-infra exastro-platform-authentication-infra-secret
    secret/exastro-platform-authentication-infra-secret patched
    [INFO] **** STEP : 3 / 5 : restart to reflect the settings ...
    [INFO] CALL : kubectl rollout restart deploy -n epoch-system epoch-service-api2
    deployment.apps/epoch-service-api2 restarted
    [INFO] CALL : kubectl rollout restart deploy -n epoch-system epoch-control-ita-api
    deployment.apps/epoch-control-ita-api restarted
    [INFO] CALL : kubectl rollout restart deploy -n exastro-platform-authentication-infra authentication-infra-api
    deployment.apps/authentication-infra-api restarted
    [INFO] CALL : kubectl rollout restart deploy -n exastro-platform-authentication-infra keycloak
    deployment.apps/keycloak restarted
    [INFO] **** STEP : 4 / 5 : wait for restart ...
    waiting ..........
    [INFO] **** STEP : 5 / 5 : Setting api call ...
    [INFO] **** set-host.sh completed successfully ****
    [INFO] Call set-host-gitlab command
    job.batch/set-host-gitlab created
    ****  completed successfully ****
    ```

1. 以下のメッセージが表示されましたら初期設定は完了となります:

    ```bash
    ****  completed successfully ****
    ```

これでEPOCHを使用する準備が整いました。

# EPOCHの起動

- 次のURLをブラウザに入力してアクセスします:

    ```bash
    https://your-host:30443/
    ```

- サインインの画面からユーザ登録のリンク(Register)をクリックして、ユーザ登録を行ってからご使用ください。

# ツールのユーザ・パスワードの確認方法

- SonarQubeのユーザ・パスワード取得方法:

    ワークスペース作成後に、アドレスバーに表示されるworkspace_idの数値を引数として、次のコマンドを実行し、ツールのユーザ・パスワードを表示します

    コマンドで表示した"SONARQUBE_USER","SONARQUBE_PASSWORD"の内容がユーザ・パスワードとなります

    ```bash
    kubectl exec -it deployment/epoch-setting-tools -n epoch-system -- bash /scripts/get-workspace-tools-account.sh [wowkspace_id]
    ```

- Keycloakのadminパスワード取得方法

    次のコマンドを実行してadminユーザのパスワードを表示します

    ```bash
    kubectl exec -it deployment/epoch-setting-tools -n epoch-system -- bash /scripts/get-keycloak-initial-admin-password.sh
    ```

- Gitlabのrootパスワード取得方法

    次のコマンドを実行してrootユーザのパスワードを表示します

    ```bash
    kubectl exec -it deployment/epoch-setting-tools -n epoch-system -- bash /scripts/get-gitlab-initial-root-password.sh
    ```
