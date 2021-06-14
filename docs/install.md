# EPOCH インストール

このガイドでは、EPOCH のインストール方法について説明します。以下のトピックについて説明します:

* [前提条件](#前提条件)
* [EPOCHのインストール](#epochのインストール)


## 前提条件

1. Kubernetes クラスター バージョン 1.18 以降が必要です。

1. 使用するServiceAccountにcluster-adminロールを付与してください。


## EPOCHのインストール

次の手順の通り作業を進めてください。

1. 次のコマンドを実行して、EPOCH をインストールします:

    ```bash
    kubectl apply -f https://github.com/exastro-suite/epoch/install/install.yaml
    ```

1. すべてのコンポーネントがRunningステータスを表示するまで、次のコマンドを使用してインストールを監視します:

    ```bash
    kubectl get pods -n epoch-system --watch
    ```

    **注:** 監視を停止するには、CTRL+C を押します。

1. パイプライン設定用の永続ボリュームを設定します:

    - 以下のマニフェストを我々のGitHubから取得してください。

        ```bash
        curl -OL https://github.com/exastro-suite/epoch/install/epoch-pv.yaml
        ```

    - `# Please specify the host name of the worker node #` の部分をご自身のホスト名に変換してください。

    - 以下のコマンドでkubernetes環境へ反映してください。

        ```bash
        kubectl apply -f epoch-pv.yaml
        ```

これでEPOCHを使用する準備が整いました。

## EPOCHの起動

- 次のURLをブラウザに入力してアクセスします:

    ```bash
    http://your-host:30080/workspace.html
    ```
