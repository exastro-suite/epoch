# EPOCH インストール

このガイドでは、EPOCH のインストール方法について説明します。以下のトピックについて説明します:

* [前提条件](#前提条件)
* [EPOCHのインストール](#epochのインストール)
* [EPOCHの起動](#epochの起動)
* [管理コンソールの起動](#管理コンソールの起動)
* [ツールのユーザ・パスワードの確認方法](#ツールのユーザ・パスワードの確認方法)

## 前提条件

1. Kubernetes クラスター バージョン 1.18 ～ 1.21が必要です。

1. 使用するServiceAccountにcluster-adminロールを付与してください。

1. Kubernetes環境から外部のインターネットに接続できる必要があります。

1. Persistent Volumeは、シングルノードのみ対応してます。

1. ソフトウェアの最小要件は以下の通りとなります。

    |Master Node| |
    | -: | :-: |
    |CPU|2 Core (3.0 GHz)|
    |Memory|8GB|
    |Disc space|10GB|

    |Worker node| |
    | -: | :-: |
    |CPU|2 Core (3.0 GHz)|
    |Memory|8GB|
    |Disc space|40GB|

    ※ Worker nodeは、1ワークスペースあたりの要件となります。  
    ※ 要件にはインストールで含まれるEcoSystemの使用要件も含まれております。

1. Kubernetes環境では、次のポート番号を使用できる必要があります。

    |ポート番号|使用用途|
    | -: | :- |
    | 30443 | epochシステム |
    | 31182 | 認証システム |
    | 31183 | GitLab |

1. EPOCHでは、SonarQubeを使用するため、Worker nodeのLinuxの設定について、次の条件を満たしている必要があります。

    | kernelパラメータ | 条件 |
    | :- | :- |
    | vm.max_map_count | 524288 以上 |
    | fs.file-max | 131072 以上 |


    | ユーザーリソース | 条件 |
    | :- | :- |
    | 同時にオープンできるファイル数 | 131072 以上 |
    | 実行可能なユーザープロセスの最大数 | 8192 以上 |

    ※SonarQubeのホスト要件については以下のサイトで確認できます。  
    [https://hub.docker.com/_/sonarqube](https://hub.docker.com/_/sonarqube)

## EPOCHのインストール

次の手順の通り作業を進めてください。

1. 次のコマンドを実行して、EPOCH をインストールします:

    ```
    kubectl apply -f https://github.com/exastro-suite/epoch/releases/latest/download/epoch-install.yaml
    ```

1. 次のコマンドを実行して、EPOCHの初期設定を行います:

    ```
    kubectl run -i --rm set-host -n epoch-system --restart=Never --image=exastro/epoch-setting:0.3_5 --pod-running-timeout=30m -- set-host [your-host]
    ```
    **注:** [your-host]には、ご自身のホストに接続するためのサーバー名またはIPアドレスを指定してください。

    **注:** EPOCHがインストール中の場合、以下のエラーとなることがあります。その際は再度コマンドを実行してください。

    ```
    error: timed out waiting for the condition
    ```

1. 初期設定実行中は、以下のような実行状況メッセージが表示されます。

    ```
    If you don't see a command prompt, try pressing enter.
    [INFO] Call set-host command
    [INFO] START : set-host.sh
    [INFO] PARAM PRM_MY_HOST : [your-host]
    [INFO] **** STEP : 1 / 7 : Initialize Setting Parameter ...
    [INFO] **** STEP : 2 / 7 : wait for keycloak pod ...
    waiting ...............
    [INFO] **** STEP : 3 / 7 : Set Parameter To Configmap
    [INFO] CALL : kubectl patch configmap -n epoch-system host-setting-config
    configmap/host-setting-config patched
    [INFO] CALL : kubectl patch configmap -n exastro-platform-authentication-infra exastro-platform-authentication-infra-env
    configmap/exastro-platform-authentication-infra-env patched
    [INFO] CALL : kubectl patch configmap -n epoch-system epoch-service-api-config
    configmap/epoch-service-api-config patched
    [INFO] CALL : kubectl patch secret -n exastro-platform-authentication-infra exastro-platform-authentication-infra-secret
    secret/exastro-platform-authentication-infra-secret patched
    [INFO] **** STEP : 4 / 7 : restart to reflect the settings ...
    [INFO] CALL : kubectl rollout restart deploy -n epoch-system epoch-service-api2
    deployment.apps/epoch-service-api2 restarted
    [INFO] CALL : kubectl rollout restart deploy -n epoch-system epoch-control-argocd-api
    deployment.apps/epoch-control-argocd-api restarted
    [INFO] CALL : kubectl rollout restart deploy -n epoch-system epoch-control-ita-api
    deployment.apps/epoch-control-ita-api restarted
    [INFO] CALL : kubectl rollout restart deploy -n exastro-platform-authentication-infra authentication-infra-api
    deployment.apps/authentication-infra-api restarted
    [INFO] **** STEP : 5 / 7 : wait for restart ...
    waiting ....
    [INFO] **** STEP : 6 / 7 : Initialize setting keycloak call ...
    [INFO] CALL : keycloak get admin user id
    [INFO] CALL : keycloak put admin new password
    [INFO] **** STEP : 7 / 7 : Setting api call ...
    [INFO] **** set-host.sh completed successfully ****
    [INFO] Call set-host-gitlab command
    job.batch/set-host-gitlab created
    ****  completed successfully ****
    pod "set-host" deleted
    ```

1. 以下のメッセージが表示されましたら初期設定は完了となります:

    ```
    ****  completed successfully ****
    ```

    これでEPOCHを使用する準備が整いました。

---

# EPOCHの起動

- 次のURLをブラウザに入力してアクセスします:

    ```
    https://your-host:30443/
    ```

- サインインの画面からユーザー名に"epoch-admin"(管理者ユーザー)、パスワードに"password"を入力して、情報更新を行ってからご使用ください。

- 新規登録したユーザーでワークスペースを作成する際は、管理コンソールより管理者ユーザーでサインインを来ない、新規登録ユーザーのグループを付与することで利用可能となります。

---

# 管理コンソールの起動

- 管理コンソールへのログインは次のURLをブラウザに入力してアクセスします:

    ```
    https://your-host:31182/auth/admin/exastroplatform/console/
    ```

---

# ツールのユーザ・パスワードの確認方法

- SonarQubeのユーザ・パスワード取得方法:

    ワークスペース作成後に、アドレスバーに表示されるworkspace_idの数値を引数として、次のコマンドを実行し、ツールのユーザ・パスワードを表示します

    コマンドで表示した"SONARQUBE_USER","SONARQUBE_PASSWORD"の内容がユーザ・パスワードとなります

    ```
    kubectl exec -it deployment/epoch-setting-tools -n epoch-system -- bash /scripts/get-workspace-tools-account.sh [wowkspace_id]
    ```

- IT-Automationのユーザ・パスワード取得方法:

    ワークスペース作成後に、アドレスバーに表示されるworkspace_idの数値を引数として、次のコマンドを実行し、ツールのユーザ・パスワードを表示します

    コマンドで表示した"ITA_USER","ITA_PASSWORD"の内容がユーザ・パスワードとなります

    ```
    kubectl exec -it deployment/epoch-setting-tools -n epoch-system -- bash /scripts/get-workspace-tools-account.sh [wowkspace_id]
    ```

- Keycloakのadminパスワード取得方法

    次のコマンドを実行してadminユーザのパスワードを表示します

    ```
    kubectl exec -it deployment/epoch-setting-tools -n epoch-system -- bash /scripts/get-keycloak-initial-admin-password.sh
    ```

- Gitlabのrootパスワード取得方法

    次のコマンドを実行してrootユーザのパスワードを表示します

    ```
    kubectl exec -it deployment/epoch-setting-tools -n epoch-system -- bash /scripts/get-gitlab-initial-root-password.sh
    ```
