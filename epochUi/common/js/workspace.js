/*
#   Copyright 2019 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
*/
// JavaScript Document

var workspace_id = null;
var workspace_update_at = null;
var workspace_client_urls = {
  "ita" : null,
  "sonarqube": null
}

// function workspace()
// ├ initWorkspaceType: 初期タブ
// └ settingMode: ワークスペースの作成or更新（ new or update ）

function workspace( initWorkspaceType, settingMode ){

backgroundAurora();

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   JSON
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

// ワークスペースの説明
//{ type: { block: description }}
const wsDescription = {
  'setting': {
    'ws-git-service': getText('EP010-0291','１．アプリケーションコードリポジトリの情報を設定してください'),
    'ws-pipeline-tekton': getText('EP010-0292','２．CDパイプライン(TEKTON)の情報を設定してください。'),
    'ws-registry-service': getText('EP010-0293','３．レジストリサービスの情報を設定してください。'),
    'ws-pipeline-argo': getText('EP010-0294','４．環境毎のCDパイプライン(ArgoCD)の情報を設定してください。'),
    'ws-git-argo': getText('EP010-0295','５．manifestを格納するIaCリポジトリの情報を設定してください。')
  },
  'deploy': {
    'ws-git-service': getText('EP010-0600','アプリケーションコードリポジトリのCommitならびにWebHookの履歴を確認できます。'),
    'ws-pipeline-tekton': getText('EP010-0601','CIパイプライン(TEKTON)の動作結果を確認できます。'),
    'ws-registry-service': getText('EP010-0602','レジストリサービスの登録状況を確認できます。'),
    'ws-pipeline-argo': getText('EP010-0603','デプロイ実行結果(ArgoCD)の動作結果を確認できます。'),
    'ws-git-argo': getText('EP010-0604','IaCリポジトリのCommit履歴を確認できます。'),
    'ws-kubernetes-manifest-template': getText('EP010-0605','６．Kubernetes Manifestテンプレートを登録します。'),
    'ws-ita-parameter': getText('EP010-0606','７．Manifestパラメータを入力します。'),
    'ws-ita-check': getText('EP010-0607','デプロイ実行結果(IT-Automation)の実行結果を確認できます。'),
    'ws-cd-user': getText('EP010-0608','８．デプロイを実行開始します。')
  },
  'footer': {
    'create': getText('EP010-0296','ワークスペースを作成します。'),
    'update': getText('EP010-0297','ワークスペースの変更点を確認・更新を行います。'),
    'reset': getText('EP010-0298','入力値を変更する前の状態に戻します。'),
    'cdExecution': getText('EP010-0608','８．デプロイを実行開始します。')
  }
};

const wsDataJSON = {
  // 
  'parameter-info': {
  },
  'workspace': {
  },
  'environment' : {
  },
  'application-code': {
    'defaultapplicationCode': {
      'text': 'CIパイプライン',
      // TODO
      //'defaultapplicationCode-pipeline-tekton-branch': 'main, master'
      'defaultapplicationCode-pipeline-tekton-branch': ''
    }
  },
  'manifests': [],
  'git-service': {
    'git-service-select': 'epoch'
  },
  'registry-service': {
    'registry-service-select': 'dockerhub'
  },
  'git-service-argo': {
    'git-service-argo-select': 'epoch'
  },
  'cd-execution-param': {
    'operation-search-key': "",
    'environment-name': "",
    'preserve-datetime': ""
  }
};

const wsModalJSON = {
  'yamlPreview': {
    'id': 'yaml-preview',
    'title': 'プレビュー',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'yamlPreviewBody': {
        'item': {
          'templateFileListBody': {
            'id': 'yaml-preview-body',
            'type': 'loading'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Workspace作成
  \* -------------------------------------------------- */
  'createWorkspace': {
    'id': 'create-workspace',
    'title': 'ワークスペース作成確認',
    'footer': {
      'ok': {'text': '作成する', 'type': 'positive'},
      'cancel': {'text': 'キャンセル', 'type': 'negative'}
    },
    'block': {
      'compareData': {
        'item': {
          'compareDataBody': {
            'id': 'compare-list',
            'type': 'loading'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Workspace作成
  \* -------------------------------------------------- */
  'updateWorkspace': {
    'id': 'create-workspace',
    'title': 'ワークスペース更新確認',
    'footer': {
      'ok': {'text': '更新する', 'type': 'positive'},
      'cancel': {'text': 'キャンセル', 'type': 'negative'}
    },
    'block': {
      'compareData': {
        'item': {
          'compareDataBody': {
            'id': 'compare-list',
            'type': 'loading'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Workspace
  \* -------------------------------------------------- */
  'workspace': {
    'id': 'workspace-edit',
    'title': 'ワークスペース',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'templateFileList': {
        'title': 'ワークスペース基本情報',
        'item': {
          'workspaceName': {
            'type': 'input',
            'title': 'ワークスペース名',
            'name': 'workspace-name',
            'placeholder': 'ワークスペース名を入力してください'
          },
          'workspaceNote': {
            'type': 'textarea',
            'title': '備考',
            'name': 'workspace-note',
            'placeholder': '備考を入力してください'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     アプリケーションコードリポジトリ
  \* -------------------------------------------------- */
  'gitService': {
    'id': 'git-service',
    'title': 'アプリケーションコードリポジトリ',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'gitServiceSelect': {
        'title': 'Gitサービス選択',
        'item': {
          'gitServiceSelectRadio': {
            'type': 'radio',
            'name': 'git-service-select',
            'item': {
              'epoch': 'EPOCH内Gitリポジトリ',
              'github': 'GitHub'
            }
          }
        }
      },
      'gitServiceAccount': {
        'title': 'Gitアカウント指定',
        'item': {
          'gitServiceAccountUser': {
            'type': 'input',
            'title': 'ユーザ名',
            'name': 'git-service-user',
            'placeholder': 'ユーザ名を入力してください'
          },
          'gitServiceAccountToken': {
            'type': 'password',
            'title': 'トークン',
            'name': 'git-service-token',
            'placeholder': 'トークンを入力してください'
          }
        }
      },
      'gitServiceRepository': {
        'title': 'Gitリポジトリ一覧',
        'button': {
          'class': 'modal-tab-add-button',
          'value': 'CIパイプライン追加'
        },
        'tab': {
          'type': 'add',
          'target': {
            'key1': 'application-code',
            'key2': 'text'
          },
          'emptyText': 'CIパイプラインの登録がありません。CIパイプライン追加ボタンから追加してください。',
          'deletConfirmText': '登録済みのデータがあります。削除しますか？',
          'id': 'git-repository-tab',
          'defaultTitle': 'CIパイプライン',
          'item' : {
            'gitServiceRepositorySource': {
              'type': 'input',
              'title': 'Gitリポジトリ URL',
              'name': 'git-repository-url',
              'class': 'tab-name-link',
              'regexp': '^https:\/\/.+\/([^\/]+).git$',
              //'validation': '^https:\/\/.+\/([^\/]+).git$',
              'inputError': 'Gitリポジトリ URLの形式が正しくありません。',
              'placeholder': 'Gitリポジトリ URLを入力してください'
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     レジストリサービス
  \* -------------------------------------------------- */
  'registryService': {
    'id': 'registry-service',
    'title': 'レジストリサービス',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'registryServiceSelect': {
        'title': 'レジストリサービス選択',
        'item': {
          'registryServiceSelectRadio': {
            'type': 'radio',
            'name': 'registry-service-select',
            'item': {
              'epoch': 'EPOCH内レジストリ',
              'dockerhub': 'DockerHub'
            }            
          }
        }
      },
      'registryServiceAccount': {
        'title': 'レジストリ接続アカウント',
        'item': {
          'registryServiceAccountUser': {
            'type': 'input',
            'title': 'ユーザ名',
            'name': 'registry-service-account-user',
            'placeholder': 'ユーザ名を入力してください',
          },
          'registryServiceAccountPassword': {
            'type': 'password',
            'title': 'パスワード',
            'name': 'registry-service-account-password',
            'placeholder': 'パスワードを入力してください',
          }
        }
      },
      'registryServiceOutput': {
        'title': 'コンテナイメージ出力指定',
        'tab': {
          'type': 'reference',
          'target': {
            'key1': 'application-code',
            'key2': 'text'
          },
          'emptyText': 'CIパイプラインの登録がありません。Gitサービスの設定からCIパイプラインを追加してください。',
          'item': {
            'gitRepositoryURL': {
              'type': 'reference',
              'title': 'Gitリポジトリ URL',
              'target': 'git-repository-url',
              'note': 'アプリケーションコードリポジトリ設定から参照しています。'
            },
            'registryServiceOutputDestination': {
              'type': 'input',
              'title': 'イメージ出力先',
              'name': 'registry-service-output-destination',
              'placeholder': 'コンテナレジストリの出力先を入力してください'
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Tekton
  \* -------------------------------------------------- */
  'pipelineTekton': {
    'id': 'pipeline-tekton',
    'title': 'TEKTON',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'pipelineTektonParameter': {
        'title': 'ビルドパラメータ一覧',
        'tab': {
          'type': 'reference',
          'target': {
            'key1': 'application-code',
            'key2': 'text'
          },
          'emptyText': 'CIパイプラインの登録がありません。Gitサービスの設定からCIパイプラインを追加してください。',
          'item': {
            'gitRepositoryURL': {
              'type': 'reference',
              'title': 'Gitリポジトリ URL',
              'target': 'git-repository-url'
            },
            'pipelineTektonBranch': {
              'type': 'input',
              'title': 'ビルド　ブランチ',
              'name': 'pipeline-tekton-branch',
              'placeholder': 'ビルド　ブランチを入力してください（入力例：main,master）'
            },
            'pipelineTektonDockerPath': {
              'type': 'input',
              'title': 'ビルド　Dockerファイルパス',
              'name': 'pipeline-tekton-docker-path',
              'placeholder': 'ビルド Dockerファイルパスを入力してください（入力例：./Dockerfile）'
            },
            'staticAnalysis': {
              'type': 'radio',
              'title': '静的解析',
              'name': 'pipeline-tekton-static-analysis',
              'item': {
                'none': '使用しない',
                'sonarQube': 'SonarQube'
              }
            }
          }
        }
      }      
    }
  },
  /* -------------------------------------------------- *\
     Kubernetes Manifestテンプレート
  \* -------------------------------------------------- */
  'kubernetesManifestTemplate': {
    'id': 'kubernetes-manifest-template',
    'title': 'Kubernetes Manifest テンプレート',
    'footer': {
      'move': {
        'text': 'パラメータ入力画面へ',
        'type': 'positive'
      },
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      },
    },
    'block': {
      'templateFileList': {
        'title': 'テンプレートファイル一覧',
        'button': {
          'id': 'template-upload-select',
          'value': 'アップロードファイル選択'
        },
        'item': {
          'templateFileListBody': {
            'id': 'template-file-list-body',
            'type': 'loading'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Kubernetes Manifestテンプレートアップロード
  \* -------------------------------------------------- */
  'kubernetesManifestTemplateUpload': {
    'id': 'kubernetes-manifest-template-upload',
    'title': 'Kubernetes Manifest テンプレートアップロード',
    'footer': {
      'ok': {
        'text': 'アップロード',
        'type': 'positive'
      },
      'reselect': {
        'text': '再選択',
        'type': 'negative'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'templateFileUpload': {
        'title': 'テンプレートファイル選択（複数可）',
        'item': {
          'templateFileUploadBody': {
            'id': 'template-file-upload-body',
            'type': 'loading'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Kubernetes Manifestパラメータ
  \* -------------------------------------------------- */
  'manifestParametar': {
    'id': 'manifest-parameter',
    'class': 'layout-tab-fixed',
    'title': 'Manifest パラメータ',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'manifestParametarInput': {
        'tab': {
          'type': 'reference',
          'target': {
            'key1': 'manifests',
            'key2': 'file_name'
          },
          'emptyText': 'テンプレートファイルの登録がありません。Kubernetes Manifestテンプレートの設定からテンプレートファイルを追加してください。',
          'item': {
            'parameter': {
              'type': 'loading',
              'id': 'input-parameter'
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Argo CD
  \* -------------------------------------------------- */
  'pipelineArgo': {
    'id': 'pipeline-argo',
    'title': 'Argo CD',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'environmentList': {
        'title': '環境一覧',
        'button': {
          'class': 'modal-tab-add-button',
          'value': '環境追加'
        },
        'tab': {
          'id': 'environment-list-tab',
          'type': 'add',
          'target': {
            'key1': 'environment',
            'key2': 'text'
          },
          'defaultTitle': '環境',
          'emptyText': '環境の登録がありません。環境追加ボタンから追加してください。',
          'deletConfirmText': '登録済みのデータがあります。削除しますか？',
          'item': {
            'environmentName': {
              'type': 'input',
              'title': '環境名',
              'name': 'environment-name',
              'class': 'tab-name-link',
              'regexp': '^(.+)$',
              'placeholder': '環境名を入力してください'
            },
            'environmentDeployTargetRadio': {
              'type': 'radio',
              'title': 'Deploy先',
              'name': 'environment-deploy-select',
              'class': 'input-pickup-select',
              'item': {
                'internal': 'EPOCHと同じKubernetes',
                'external': '以外のKubernetes'
              },
              'note': 'Deploy先のKubernetesを選択してください'
            },  
            'environmentURL': {
              'type': 'input',
              'title': 'Kubernetes API Server URL',
              'name': 'environment-url',
              'class': 'input-pickup input-pickup-external',
              'placeholder': '実行環境のKubernetes API Server URLを入力してください（入力例：https://<外部クラスタIP>:6443）'
            },
            'environmentNamespace': {
              'type': 'input',
              'title': 'Namespace',
              'name': 'environment-namespace',
              'class': 'input-pickup input-pickup-external input-pickup-internal',
              'placeholder': '実行環境のNamespaceを入力してください',
              'validation': '^[a-z0-9]([-a-z0-9]*[a-z0-9])?$',
              'inputError': '実行環境のNamespaceの形式が正しくありません',
            },
            'environmentToken': {
              'type': 'input',
              'title': 'Authentication token',
              'name': 'environment-authentication-token',
              'class': 'input-pickup input-pickup-external',
              'placeholder': '実行環境のAuthentication tokenを入力してください'
            },
            'environmentCertificate': {
              'type': 'input',
              'title': 'Base64 encoded certificate',
              'name': 'environment-certificate',
              'class': 'input-pickup input-pickup-external',
              'placeholder': '実行環境のBase64 encoded certificateを入力してください'
            },
            'environmentDeployMember': {
              'type': 'listSelect',
              'title': 'Deploy権限',
              'name': 'environment-deploy-member',
              'button': {
                'select': 'ユーザを選択する',
                'clear': 'クリア'
              },
              'item': {
                'all': 'CD実行が可能なユーザ全員',
                'select': '下記の選択したユーザのみ'
              },
              'list': [],
              'col': 1
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Argo CD Deploy権限 メンバー選択
  \* -------------------------------------------------- */
  'pipelineArgoDeployMember': {
    'id': 'pipeline-argo-deploy-member',
    'title': 'Argo CD Deploy権限',
    'class': 'layout-tab-fixed',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'pipelineArgoDeployMemberSelect': {
        'title': 'メンバー選択',
        'item': {
          'pipelineArgoDeployMemberSelectBody': {
            'id': 'pipeline-argo-deploy-member-select',
            'type': 'loading'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     IaCリポジトリ
  \* -------------------------------------------------- */
  'gitServiceArgo': {
    'id': 'git-service-argo',
    'title': 'IaCリポジトリ',
    'footer': {
      'ok': {
        'text': '決定',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      },
    },
    'block': {
      'gitServiceArgoSelect': {
        'title': 'Gitサービス選択',
        'item': {
          'gitServiceArgoSelectRadio': {
            'type': 'radio',
            'name': 'git-service-argo-select',
            'item': {
              'epoch': 'EPOCH内Gitリポジトリ',
              'github': 'GitHub'
            }
          }
        }
      },
      'gitServiceArgoAccount': {
        'title': 'Gitアカウント指定',
        'item': {
          'gitServiceArgoAccountSelect': {
            'type': 'radio',
            'title': 'Gitアカウント選択',
            'name': 'git-service-argo-account-select',
            'class': 'input-pickup-select',
            'item': {
              'applicationCode': 'アプリケーションコードリポジトリと同一',
              'separate': '入力する'
            }
          },  
          'gitServiceArgoAccountUserApplicationCode': {
            'type': 'reference',
            'title': 'ユーザ名（アプリケーションコードリポジトリと同一）',
            'target': 'git-service-user',
            'class': 'input-pickup input-pickup-applicationCode',
            'note': 'アプリケーションコードリポジトリ設定から参照しています。'
          },
          'gitServiceArgoAccountUser': {
            'type': 'input',
            'title': 'ユーザ名',
            'name': 'git-service-argo-user',
            'class': 'input-pickup input-pickup-separate',
            'placeholder': 'ユーザ名を入力してください'
          },
          'gitServiceArgoAccountToken': {
            'type': 'password',
            'title': 'トークン',
            'name': 'git-service-argo-token',
            'class': 'input-pickup input-pickup-separate',
            'placeholder': 'トークンを入力してください'
          }
        }
      },
      'gitServiceArgoRepository': {
        'title': 'Gitリポジトリ一覧',
        'tab': {
          'type': 'reference',
          'target': {
            'key1': 'environment',
            'key2': 'text'
          },
          'emptyText': '環境の登録がありません。Argo CDの設定から環境を追加してください。',
          'item' : {
            'gitServiceArgoRepositorySource': {
              'type': 'input',
              'title': 'Gitリポジトリ URL',
              'name': 'git-service-argo-repository-url',
              'validation': '^https:\/\/.+\.git$',
              'inputError': 'Gitリポジトリ URLの形式が正しくありません。',
              'placeholder': 'Gitリポジトリ URLを入力してください'
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     CD実行指定
  \* -------------------------------------------------- */
  'cdExecution': {
    'id': 'cd-execution',
    'title': 'CD実行指定',
    'footer': {
      'ok': {
        'text': '実行',
        'type': 'positive'
      },
      'cancel': {
        'text': 'キャンセル',
        'type': 'negative'
      }
    },
    'block': {
      'cdExecutionCondition': {
        'title': '実行条件',
        'item': {
          'cdExecutionConditionBlock': {
            'type': 'loading',
            'id': 'cd-execution-condition'            
          }
        }
      },
      'cdExecutionManifestParameter': {
        'title': 'Manifestパラメータ',
        'tab': {
          'type': 'reference',
          'id': 'cd-execution-manifest-parameter',
          'target': {
            'key1': 'manifests',
            'key2': 'file_name'
          },
          'emptyText': 'テンプレートファイルの登録がありません。Kubernetes Manifestテンプレートの設定からテンプレートファイルを追加してください。',
          'item': {
            'cdExecutionManifestParameterBlock': {
              'type': 'loading'
            }
          }
        }
      },
      'cdExecutionArgo': {
        'title': 'ArgoCDパイプライン',
        'item': {
          'cdExecutionArgoBlock': {
            'type': 'loading',
            'id': 'cd-execution-argo'            
          }
        }
      }
    }
  }
};
const modal = new modalFunction( wsModalJSON, wsDataJSON );

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   初期設定
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

// 共通Function
const fn = new epochCommon();

// jQueryオブジェクトのキャッシュ
const $content = $('#content'),
      $workspace = $('#workspace'),
      $workspaceBody = $workspace.find('.workspace-body'),
      $workspaceFooter = $workspace.find('.workspace-footer'),
      $workspaceImage = $workspace.find('.workspace-setting-image'),
      $workspaceLine = $('#workspace-line'),
      $workspaceEpoch = $('#workspace-epoch');

// common
const workspace = {
        'w': Number( $workspaceImage.css('width').replace('px','') ),
        'h': Number( $workspaceImage.css('height').replace('px','') ),
      },
      xmlns = 'http://www.w3.org/2000/svg';

// EPOCH枠座標用
let ep;

// SVGのviewBoxをセット
$workspaceLine.get(0).setAttribute('viewBox', '0 0 ' + workspace.w + ' ' + workspace.h );
$workspaceEpoch.get(0).setAttribute('viewBox', '0 0 ' + workspace.w + ' ' + workspace.h );

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   結線用SVG
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

const newSVG = function( type ) {

    if ( type === undefined ) type = 'line';

    // パスを作成
    const $svgLine = $( document.createElementNS( xmlns, type ) ),
          $svgLineBack = $( document.createElementNS( xmlns, type ) );
    $svgLine.attr('class', 'svg-' + type );
    $svgLineBack.attr('class', 'svg-' + type + '-back');

    // SVGエリアに追加
    $workspaceLine.prepend( $svgLineBack ).append( $svgLine );
      
    return $svgLine.add( $svgLineBack );
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ワークスペース配置
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

const getSize = function( $t ) {
  const w = Math.round( $t.outerWidth() ),
        h = Math.round( $t.outerHeight() ),
        l = Math.round( $t.offset().left - $workspaceLine.offset().left ),
        t = Math.round( $t.offset().top - $workspaceLine.offset().top ),
        xc = Math.round( l + w / 2 ),
        yc = Math.round( t + h / 2 );
  return {'w': w, 'h': h, 'l': l, 't': t, 'xc': xc, 'yc': yc };
};

const order = function() {
  const length = arguments.length,
        order = new Array();
  for ( let i = 0; i < length; i++ ) {
    order.push(arguments[i]);
  }
  return order.join(' ');
};

// 各ブロックの配置と結線を行う
const setWorkspacePosition = function(){

    const blockWidth = 256, // ブロックサイズ
          blockMargin = 16, // 間隔
          epockPadding = 8,
          positioning = 20, // 上下位置調整
          a = 8; // 矢印のサイズ

    const $appArea = $('#ws-ci-area'),
          $epoch = $('#ws-epoch-setting'),
          $tekton = $('#ws-pipeline-tekton'),
          $argo = $('#ws-pipeline-argo'),
          $docker = $('#ws-registry-service'),
          $ita  = $('#ws-ita'),
          $git = $('#ws-git-service'),
          $gitArgo = $('#ws-git-argo'),
          $startCI = $('#ws-ci-user'),
          $startCD = $('#ws-cd-user'),
          $end = $('#ws-system'),
          $ac = $('#ws-application-code'),
          $km = $('#ws-kubernetes-manifest'),
          $kmT = $('#ws-kubernetes-manifest-template'),
          $mp = $('#ws-ita-parameter'),
          $itaF = $('#ws-ita-frow'),
          epoch = {}, tekton = {}, argo = {}, docker = {},
          ita = {}, git = {}, gitArgo = {},
          startCI = {}, startCD = {}, end = {}, appArea = {};

    git.w = blockWidth;
    git.h = $git.outerHeight();
    
    tekton.w = blockWidth;
    tekton.h = $tekton.outerHeight();
    tekton.l = workspace.w / 2 - tekton.w / 2;
    
    git.l = tekton.l - blockMargin * 4 - git.w;
    git.t = positioning + blockMargin * 2;
    
    tekton.t = git.t + git.h - tekton.h;
    tekton.xc = tekton.l + tekton.w / 2;
    tekton.yc = tekton.t + tekton.h / 2;
    
    $git.css({'width': git.w, 'left': git.l, 'top' : git.t });
    $tekton.css({'width': tekton.w, 'left': tekton.l, 'top' : tekton.t });

    argo.w = blockWidth * 2 + blockMargin * 4;
    argo.h = $argo.outerHeight();
    argo.l = tekton.l;
    argo.t = tekton.t + tekton.h + blockMargin * 3;
    argo.yc = argo.t + argo.h / 2;
    $argo.css({'width': argo.w, 'left': argo.l, 'top' : argo.t });

    docker.w = blockWidth;
    docker.h = $docker.outerHeight();
    docker.l = tekton.l + tekton.w + blockMargin * 4;
    docker.t = tekton.t;
    docker.xc = docker.l + docker.w / 2;
    $docker.css({'width': docker.w, 'left': docker.l, 'top' : docker.t });

    ita.w = blockWidth;
    ita.h = $ita.outerHeight();
    ita.l = tekton.l - blockMargin * 4 - ita.w;
    ita.t = argo.t;
    $ita.css({'width': ita.w, 'left': ita.l, 'top' : ita.t });

    gitArgo.w = blockWidth;
    gitArgo.h = $gitArgo.outerHeight();
    gitArgo.l = tekton.l;
    gitArgo.t = ita.t + ita.h - gitArgo.h;
    gitArgo.xc = gitArgo.l + gitArgo.w / 2;
    gitArgo.yc = gitArgo.t + gitArgo.h / 2;
    $gitArgo.css({'width': gitArgo.w, 'left': gitArgo.l, 'top' : gitArgo.t });

    startCI.w = $startCI.outerWidth();
    startCI.h = $startCI.outerHeight();
    startCI.l = 0;
    startCI.t = tekton.t + tekton.h / 2 - startCI.h / 2;
    startCI.xc = startCI.l + startCI.w / 2;
    startCI.yc = startCI.t + startCI.h / 2;
    $startCI.css({'left': startCI.l, 'top' : startCI.t });

    end.w = $end.outerWidth();
    end.h = $end.outerHeight();
    end.l = workspace.w - end.w;
    end.t = argo.t + argo.h / 2 - end.h / 2;
    $end.css({'left': end.l, 'top' : end.t });

    const ac = getSize( $ac ),
          km = getSize( $km ),
          kmT = getSize( $kmT ),
          mp = getSize( $mp ),
          itaF = getSize( $itaF );

    startCD.w = $startCD.outerWidth();
    startCD.h = $startCD.outerHeight();
    startCD.l = 0;
    startCD.t = itaF.t + itaF.h / 2 - startCD.h / 2;
    startCD.xc = startCD.l + startCD.w / 2;
    startCD.yc = startCD.t + startCD.h / 2;
    $startCD.css({'left': startCD.l, 'top' : startCD.t });

    epoch.w = blockWidth;
    epoch.h = $epoch.outerHeight();
    epoch.l = docker.l + docker.w - epoch.w;
    epoch.t = argo.t + argo.h + blockMargin * 2;
    $epoch.css({'width': epoch.w, 'left': epoch.l, 'top' : epoch.t });
    
    appArea.l = git.l - blockMargin * 1.5;
    appArea.t = git.t - blockMargin;
    appArea.w = docker.l + docker.w - git.l + blockMargin * 3;
    appArea.h = tekton.t + tekton.h - git.t + blockMargin * 2;
    $appArea.css({'width': appArea.w, 'height': appArea.h, 'left': appArea.l, 'top' : appArea.t });
    
    // 横直線
    const connectH = function( t1, t2, type ){
        const $line = newSVG('path');
        $line.attr({
            'd': order( 'M',t1.l+t1.w,t1.yc,'L',t2.l+4,t1.yc,'l',-a,-a,a,a,-a,a,a,-a ),
            'data-type': type
        });
    };

    connectH( startCI, ac, 'ci');
    connectH( ac, tekton, 'ci');
    connectH( tekton, docker, 'ci');

    connectH( startCD, itaF, 'cd');
    connectH( argo, end, 'cd');

    // Argo CD --> Git
    const $line1 = newSVG('path');
    $line1.attr({
    'd': order('M',gitArgo.xc-12,argo.t+argo.h,gitArgo.xc-12,gitArgo.t-12,'c',0,24,24,24,24,0,'L',gitArgo.xc+12,argo.t+argo.h-4,'l',-a,a,a,-a,a,a,-a,-a),
    'data-type': 'cd'});

    // Argo CD --> DockerHub
    const $line2 = newSVG('path');
    $line2.attr({
    'd': order('M',docker.xc-12,argo.t,docker.xc-12,docker.t+docker.h+12,'c',0,-24,24,-24,24,0,'L',docker.xc+12,argo.t+4,'l',-a,-a,a,a,a,-a,-a,a ),
    'data-type': 'cd'});

    // ITA Frow --> Kubernetes Manifest 
    const $line3 = newSVG('path');
    $line3.attr({
    'd': order('M',itaF.xc,itaF.t+itaF.h,itaF.xc,itaF.t+itaF.h+blockMargin*2,km.xc,itaF.t+itaF.h+blockMargin*2,km.xc,km.t+km.h-4,'l',-a,a,a,-a,a,a,-a,-a ),
    'data-type': 'cd'});

    // CI --> Kubernetes Manifestテンプレート
    const $line4 = newSVG('path');
    $line4.attr({
    'd': order('M',startCI.xc,startCI.t+startCI.h,startCI.xc,kmT.yc,kmT.l,kmT.yc,'l',-a,a,a,-a,-a,-a,a,a),
    'data-type': 'ci'});

    // CD --> Manifestパラメータ
    const $line5 = newSVG('path');
    $line5.attr({
    'd': order('M',startCD.xc,startCD.t, startCD.xc,mp.yc, mp.l,mp.yc,'l',-a,a,a,-a,-a,-a,a,a),
    'data-type': 'cd'});

    // EPOCH枠の座標
    ep = {
        'y1': 0,
        'y2': git.t - epockPadding,
        'y3': tekton.t - epockPadding,
        'y4': argo.t - epockPadding,
        'y5': argo.t + argo.h + epockPadding,
        'y6': epoch.t + epoch.h + epockPadding,
        'y7': ita.t + ita.h + epockPadding,
        'x1': ita.l - epockPadding,
        'x2': git.l + git.w + epockPadding,
        'x3': argo.l - epockPadding,
        'x4': tekton.l + tekton.w + epockPadding,
        'x5': epoch.l - epockPadding,
        'x6': epoch.l + epoch.w + epockPadding
    }
    
    workspace.h = ep.y7 + positioning * 1.5;
    $workspaceImage.css('height', workspace.h );
    
    setEpochFrame();
    sizeAdjustment();
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   EPOCH枠
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

const setEpochFrame = function(){
  const gitServiceType = $('#ws-git-service').attr('data-service'),
        registryServiceType = $('#ws-registry-service').attr('data-service'),
        gitServiceArgoType = $('#ws-git-argo').attr('data-service'),
        points = new Array();
  
  if ( gitServiceType !== 'epoch') {
    points.push(ep.x1,ep.y4,ep.x2,ep.y4,ep.x3,ep.y3);
  } else {
    points.push(ep.x1,ep.y2,ep.x2,ep.y2,ep.x3,ep.y3);
  }
  
  if ( registryServiceType !== 'epoch') {
    points.push(ep.x4,ep.y3,ep.x5,ep.y4,ep.x6,ep.y4);
  } else {
    points.push(ep.x4,ep.y3,ep.x6,ep.y3);
  }
  
  if ( gitServiceArgoType !== 'epoch') {
    points.push(ep.x6,ep.y6,ep.x5,ep.y6,ep.x4,ep.y5,ep.x3,ep.y5,ep.x2,ep.y7);
  } else {
    points.push(ep.x6,ep.y6,ep.x5,ep.y6,ep.x4,ep.y7);
  }
  
  points.push(ep.x1,ep.y7);
  
  $workspaceEpoch.find('polygon').attr('points', points.join(' ') );
};

const workspaceReload = function(){
    $workspaceLine.empty();
    $workspaceImage.removeAttr('style');
    setWorkspacePosition();
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ワークスペースのサイズを画面に合わせる
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

const sizeAdjustment = function(){
    const w = $workspaceBody.outerWidth(),
          h = $workspaceBody.outerHeight();

    const maxScaling = 99,
          scalingVertical = Math.floor( ( w - 48 ) / workspace.w * 1000 ) / 1000,
          scalingHorizontal = Math.floor( ( h - 16 ) / workspace.h * 1000 ) / 1000;
          
    let scaling = ( scalingVertical < scalingHorizontal ) ? scalingVertical : scalingHorizontal;
    if ( scaling > maxScaling ) scaling = maxScaling;
    
    const top = ( h - workspace.h * scaling ) / 2,
          left = ( w - workspace.w * scaling ) / 2;

    $workspaceImage.css({
      'transform': 'scale(' + scaling + ')',
      'top': top,
      'left': left
    }).addClass('ready');  
};
setWorkspacePosition();

let resizeTimer;
$( window ).on('resize.workspaceSize', function(){
  if ( resizeTimer ) return;

	resizeTimer = setTimeout(function(){
		resizeTimer = 0 ;
    sizeAdjustment();
	}, 300 ) ;
});

// サイドメニューのアニメーションが終了した際にもリサイズ
$('#side').on('transitionend', function(e){
  if ( e.originalEvent.target.id === 'side' ) {
    sizeAdjustment();
  }
});

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ワークスペースフッターボタンセット
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

// ボタンをセット
const footerButton = [
  {'type': 'setting', 'mode': ['new'], 'text': 'ワークスペース作成', 'buttonType': 'create', 'buttonCategory': 'positive', 'disabled': true, 'separate': true },
  {'type': 'setting', 'mode': ['update'], 'text': 'ワークスペース更新', 'buttonType': 'update', 'buttonCategory': 'positive', 'disabled': true, 'separate': true },
  {'type': 'setting', 'mode': ['new', 'update'], 'text': 'リセット', 'buttonType': 'reset', 'buttonCategory': 'negative', 'disabled': true, 'separate': false },
  {'type': 'deploy', 'mode': [], 'text': 'デプロイ', 'buttonType': 'cdExecution', 'buttonCategory': 'modal-open positive', 'disabled': false, 'separate': false },
];
const buttonLength = footerButton.length;

const setFotter = function( workspaceType ) {
  let footerHTML = '<ul class="workspace-footer-menu-list">';
  for ( let i = 0; i < buttonLength; i++ ) {
    if ( footerButton[i].type !== workspaceType ) continue;
    if ( workspaceType === 'setting' && footerButton[i].mode.indexOf( settingMode ) === -1 ) continue;
    const text = footerButton[i].text,
          button = footerButton[i].buttonType,
          type = footerButton[i].buttonCategory,
          disabled = ( footerButton[i].disabled )? ' disabled': '',
          separate = ( footerButton[i].separate )? ' separate': '',
          description = wsDescription.footer[button];
    // ROLE制御
    let display = "display:none";
    const ws_id = (new URLSearchParams(window.location.search)).get('workspace_id');
    switch(footerButton[i].buttonType) {
        case "update":
        case "reset":
          if(currentUser != null && currentUser.data ) {
            if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-name-update".replace('{ws_id}',ws_id)) != -1
            || currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-ci-update".replace('{ws_id}',ws_id)) != -1
            || currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-cd-update".replace('{ws_id}',ws_id)) != -1) {
              display="";
            }
          }
          break;
        case "cdExecution":
          if(currentUser != null && currentUser.data ) {
            if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute".replace('{ws_id}',ws_id)) != -1) {
              display="";
            }
          }
          break;
        default:
          display="";
    }

    footerHTML += '<li class="workspace-footer-menu-item' + separate + '">'
    + '<button class="epoch-button epoch-popup workspace-footer-menu-button ' + type + '" data-button="' + button + '"' + disabled + ' title="' + description + '" + style="' + display + '">' + text + '</button>';
  }
  footerHTML += '</ul>';

  $workspaceFooter.html( footerHTML );
}

// ボタンイベント
$workspaceFooter.on('click', '.workspace-footer-menu-button', function(){
  const $button = $( this ),
        type = $button.attr('data-button');

  switch ( type ) {
    case 'create': {
      modal.open('createWorkspace', {
        'callback': function(){
          const compareData = wsDataCompare(),
                html = [];
          for ( const key in compareData.html ) {
            html.push( compareData.html[key] );
          }
          modal.$modal.find('#compare-list').html( html.join('') );
        },
        'ok': function(){
          // 作成処理
          // alert('作成しました。');
          modal.close();
          apply_workspace();
        }
      }, '1200');
    } break;
    case 'update': {
      modal.open('updateWorkspace', {
        'callback': function(){
          const compareData = wsDataCompare(),
                html = [];
          for ( const key in compareData.html ) {
            html.push( compareData.html[key] );
          }
          // 更新が無いときの表示
          if(html.join('') === "") {
            modal.$modal.find('#compare-list').html('変更した項目はありません');
          } else {
            modal.$modal.find('#compare-list').html( html.join('') );
          }
        },
        'ok': function(){
          // 更新処理
          console.log( compareFlag ); // 変更箇所
          // alert('更新しました。');
          modal.close();
          apply_workspace();
        }
      }, '1200');
    } break;
    case 'reset':
      // リセット
      // alert('リセットしました。');
      // 確認メッセージ
      if (confirm("入力値をリセットしてもよろしいですか？"))
        if(workspace_id == null) {
          // 新規のときは画面リロード
          top.location.reload();        
        } else {
          // ワークスペース情報の読み込み
          getWorksapce();
        }
    break;
    case 'cdExecution':
      modal.open('cdExecution',{
          'callback': cdExecution,
          'ok' : () => {
            cdRunning();
          }
      });
  }
});

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   モーダル入力内容
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

// モーダル内の入力データを wsDataJSON に入れる
const setInputData = function( tabTarget, commonTarget ){
  const inputTarget = 'input[type="text"], input[type="password"], input[type="radio"]:checked, textarea, input[type="hidden"]';
  
  // タブリストの作成
  modal.$modal.find('.modal-tab-item').each( function(){
    const $tab = $( this ),
          tabID = $tab.attr('data-id'),
          tabText = $tab.text();
    if ( wsDataJSON[ tabTarget ] === undefined ) wsDataJSON[ tabTarget ] = {};
    if ( wsDataJSON[ tabTarget ][ tabID ] === undefined ) wsDataJSON[ tabTarget ][ tabID ] = {};
    wsDataJSON[ tabTarget ][ tabID ]['text'] = tabText;
  });
  modal.$modal.find( inputTarget ).each( function(){
    const $input = $( this ),
          name = $input.attr('name');
    // タブの中か調べる
    const $tabBlock = $input.closest('.modal-tab-body-block');
    if ( $tabBlock.length ) {
      const tabID = $tabBlock.attr('id');
      if ( wsDataJSON[ tabTarget ] === undefined ) wsDataJSON[ tabTarget ] = {};
      if ( wsDataJSON[ tabTarget ][ tabID ] === undefined ) wsDataJSON[ tabTarget ][ tabID ] = {};
      if ( $input.is(':disabled') ) {
        wsDataJSON[ tabTarget ][ tabID ][ name ] = null
      } else {
        wsDataJSON[ tabTarget ][ tabID ][ name ] = $input.val();
      }
    } else {
      if ( wsDataJSON[ commonTarget ] === undefined ) wsDataJSON[ commonTarget ] = {};
      if ( $input.is(':disabled') ) {
        wsDataJSON[ commonTarget ][ name ] = null
      } else {
        wsDataJSON[ commonTarget ][ name ] = $input.val();
      }
    }
  });
};

// 削除されたタブに合わせてデータも削除する
const deleteTabData = function( target ){
  const deleteData = modal.$modal.attr('data-tab-delete');
  if ( deleteData !== undefined ) {
    const deleteArray = deleteData.split(','),
          deleteLength = deleteArray.length;
    for ( let i = 0; i < deleteLength; i++ ) {
      if ( wsDataJSON[target][deleteArray[i]] !== undefined ) {
        delete wsDataJSON[target][deleteArray[i]];
      } else {
        alert( deleteArray[i] + ' error.');
      }
    }
  }  
};

// 入力されたパラメータを wsDataJSON に入れる
const setParameterData = function(){
  const inputTarget = 'input[type="text"], input[type="password"], input[type="radio"]:checked, textarea, input[type="hidden"]';
  
  modal.$modal.find( inputTarget ).each( function(){
    const $input = $( this ),
          fileID = $input.attr('data-file'),
          enviromentID =  $input.attr('data-enviroment'),
          name = $input.attr('name'),
          value = $input.val();
    if ( enviromentID !== '__parameterItemInfo__') {
      if ( wsDataJSON['environment'] === undefined )  wsDataJSON['environment'] = {};
      if ( wsDataJSON['environment'][ enviromentID ] !== undefined ) {
        if ( wsDataJSON['environment'][ enviromentID ]['parameter'] === undefined ) {
          wsDataJSON['environment'][ enviromentID ]['parameter'] = {};
        }
        if ( wsDataJSON['environment'][ enviromentID ]['parameter'][ fileID ] === undefined ) {
          wsDataJSON['environment'][ enviromentID ]['parameter'][ fileID ] = {};
        }
        wsDataJSON['environment'][ enviromentID ]['parameter'][ fileID ][ name ] = value;
      }
    } else {
      // パラメータ説明
      if ( wsDataJSON['parameter-info'] === undefined )  wsDataJSON['parameter-info'] = {};
      if ( wsDataJSON['parameter-info'][ fileID ] === undefined ) {
        wsDataJSON['parameter-info'][ fileID ] = {};
      }
      wsDataJSON['parameter-info'][ fileID ][ name ] = value;
    }
  });
  
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   レジストリサービス
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

// ユーザ名の入力に合わせてイメージ出力先に値をセットする
const setRegistryServiceInput = function(){
  const $modal = $('#registry-service'),
        inputArray = [];
  $modal.find('.registry-service-account-user').on({
    // フォーカスが当たった時にURLと未入力チェック
    'focus': function(){
      $modal.find('.modal-tab-body-block').each(function(i){
        const $tab = $( this ),
              repositoryURL = $tab.find('.item-reference').text(),
              imageTarget = $tab.find('.registry-service-output-destination').val();
        inputArray[i] = [];
        if ( repositoryURL !== '' && repositoryURL !== undefined ) {
          inputArray[i].push( repositoryURL.replace(/^.+\/([^\/]+)\.git$/, '$1') );
        } else {
          inputArray[i].push('');
        }
        if ( imageTarget === '') {
          inputArray[i].push( null );
        } else {
          inputArray[i].push( imageTarget );
        }
      });
    },
    'input': function(){
      const value = $( this ).val();
      $modal.find('.modal-tab-body-block').each(function(i){
        const $imageTarget = $( this ).find('.registry-service-output-destination');
        if ( inputArray[i][1] === null ) {
          $imageTarget.val( value + '/' + inputArray[i][0].toLowerCase() ).trigger('input');
        }
      });
    }
  });

};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   テンプレートファイルリスト
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const templateFileList = function(){
  const $modal = $('#kubernetes-manifest-template'),
        $fileList = $('#template-file-list-body'),
        $moveButton = $modal.find('.epoch-button[data-button="move"]'),
        fileList = wsDataJSON['manifests'],
        fileLength = fileList.length;
  
  const moveButton = function( disabled ){
    $moveButton.prop('disabled', disabled );
  };
  if ( fileLength < 1 ) {
    moveButton( true );
  }
  let listHtml = '<table class="c-table c-table-fixed">'
  + '<thead>'
    + '<tr class="c-table-row">'
      + '<th class="template-name c-table-col"><div class="c-table-ci">名前</div></th>'
      + '<th class="template-date c-table-col"><div class="c-table-ci">最終更新日時</div></th>'
      + '<th class="template-user c-table-col"><div class="c-table-ci">最終更新者</div></th>'
      + '<th class="template-note c-table-col"><div class="c-table-ci">備考</div></th>'
    + '</tr>'
  + '</thead>'
  + '<tbody>';
  
  if ( fileLength > 0 ) {
    for ( let i = 0; i < fileLength; i++ ) {
      // var update_at = (new Date(fn.textEntities(fileList[i]["update_at"]))).toLocaleString('ja-JP');
      var update_at = "";

      listHtml += ''
      + '<tr class="c-table-row">'
      + '<td class="template-name c-table-col"><div class="c-table-ci">' + fn.textEntities(fileList[i]["file_name"]) + '</div></td>'
      + '<td class="template-date c-table-col"><div class="c-table-ci">' + update_at + '</td>'
      + '<td class="template-user c-table-col"><div class="c-table-ci"></div></td>'
      //+ '<td class="template-note c-table-col"><div class="c-table-ci">' + fn.textEntities(fileList[i]["file_text"]) + '</div></td>'
      + '<td class="template-note c-table-col"><div class="c-table-ci"></div></td>'
      + '<td class="template-menu c-table-col"><div class="c-table-ci">'
          + '<ul class="c-table-menu-list">'
            // + '<li class="c-table-menu-item">'
            //   + '<button class="c-table-menu-button epoch-popup-m" title="プレビュー" data-key="' + i + '" data-button="preview">'
            //     + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-preview" /></svg></button></li>'
            // + '<li class="c-table-menu-item">'
            //   + '<button class="c-table-menu-button epoch-popup-m" title="ダウンロード" data-key="' + i + '" data-button="download">'
            //     + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-download" /></svg></button></li>'
            // + '<li class="c-table-menu-item">'
            //   + '<button class="c-table-menu-button epoch-popup-m" title="備考" data-key="' + i + '" data-button="note">'
            //     + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-edit" /></svg></button></li>'
            // + '<li class="c-table-menu-item">'
            //   + '<button class="c-table-menu-button epoch-popup-m" title="更新" data-key="' + i + '" data-button="update">'
            //     + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-update" /></svg></button></li>'
            + '<li class="c-table-menu-item">'
              + '<button class="c-table-menu-button epoch-popup-m" title="削除" data-key="' + i + '" data-button="delete">'
                + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-trash" /></svg></button></li>'
          + '</ul>'
        + '</div></td>'
      + '</tr>';
    }
    listHtml += '</tbody></table>';
  } else {
    listHtml += '<div class="empty-block"></div>';
  }
  
  $fileList.html( listHtml );
  
  $fileList.find('.c-table-menu-button').on('click', function(){
    const $button = $( this ),
          key = $button.attr('data-key'),
          type = $( this ).attr('data-button');
    switch( type ) {
      case 'preview':
        alert( wsDataJSON['manifests'][key] + 'プレビュー');
        break;
      case 'download':
        alert('Download');
        break;
      case 'memo':
        alert('ファイルを更新しますか？');
        break;
      case 'update':
        alert('ファイルを更新しますか？');
        break;
      case 'delete':
        if (confirm(wsDataJSON['manifests'][key]['file_name'] + 'を削除しますか？')) {
          templateFileDelete(key, wsDataJSON['manifests'][key]['file_id']);

          $button.mouseleave().closest('.c-table-row').remove();
          $button.closest('.c-table-row').remove();

          // data-key再設定
          $fileList.find('.c-table-menu-button').each((index, elm) => {
            $(elm).attr('data-key',index);       
          });

          // 件数によって入力画面ボタンを制御
          if ( $modal.find('tbody .c-table-row').length < 1 ) {
            moveButton( true );
          } else {
            moveButton( false );
          }
        }
        break;      
    }
  });
  
  $moveButton.on('click', function(){
    modal.change('manifestParametar', {
      'ok': function(){
        setParameterData();
        apply_manifest();
        modal.close();
      },
      'callback': inputParameter
    }, 1160 );
  });

  // ファイル選択モーダルを開く
  $('#template-upload-select').on('click', function(){
    modal.change('kubernetesManifestTemplateUpload', {
      'cancel': function(){
        modal.change('kubernetesManifestTemplate', {
          'callback': templateFileList
        },
        1160 )
      },
      'callback': templateFileSelect
    });
  });
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   テンプレートファイル選択
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const templateFileSelect = function( type ){
  if ( type === undefined ) type = ' multiple';

  const $modal = $('#kubernetes-manifest-template-upload'),
        $file = $modal.find('#template-file-upload-body'),
        $upload = $modal.find('.modal-menu-button[data-button="ok"]'),
        $reSelect = $modal.find('.modal-menu-button[data-button="reselect"]');
  
  $upload.add( $reSelect ).prop('disabled', true );
  
  let uploadHtml = ''
  + '<div class="item-file-block">'
    + '<form id="template-files" method="post" enctype="multipart/form-data">'
      + '<input type="file" name="manifest_files" class="item-file"' + type + '>'
    + '</form>'
    + '<div class="item-file-list">'
      + '<table class="c-table c-table-fixed">'
        + '<thead>'
          + '<tr class="c-table-row">'
            + '<th class="template-name c-table-col"><div class="c-table-ci">名前</div></th>'
            + '<th class="template-type c-table-col"><div class="c-table-ci">種類</div></th>'
            + '<th class="template-size c-table-col"><div class="c-table-ci">サイズ</div></th>'
            + '<th class="template-date c-table-col"><div class="c-table-ci">更新日時</div></th>'
          + '</tr>'
        + '</thead>'
      + '</table>'
    + '</div>'
    + '<div class="item-file-droparea">'
      + '<p class="item-file-droparea-text">ここにファイルをドロップ または クリック</p>'
    + '</div>'
  + '</div>';
  $file.html( uploadHtml );

  // ファイル選択リストを表示する
  $file.find('.item-file').on('change', function(){
    const $inputFile = $( this );
    if ( $inputFile.val() !== '') {
      const files = $inputFile.prop('files'),
            fileLength = files.length;
      
      let $fileTable = $('<tbody/>'),
          fileCount = 0,
          errorCount = 0;
      
      const createTable = function() {
        fileCount++;
        // すべての処理が終わったら
        if ( fileCount >= fileLength ) {
          if ( errorCount === 0 ) {
            // ファイルリストを表示
            $file.find('.item-file-list').show().find('table').append( $fileTable );
            $file.find('.item-file-droparea').hide();

            // Uploadボタン押下時にはformが無くなっているのでここに移動
            const formData = new FormData( $('#template-files').get(0) );
            
            // アップロード、再選択ボタン
            $upload.add( $reSelect ).prop('disabled', false ).on('click', function(){
              const $button = $( this ),
                    type = $button.attr('data-button');
              switch( type ) {
                case 'ok': {         
                $button.prop('disabled', true );
                // フォームデータ取得
                // Uploadボタン押下時にはformが無くなっているので上に移動
                //const formData = new FormData( $('#template-files').get(0) );
                console.log('CALL : マニフェストテンプレートアップロード');
                // 送信
                $.ajax({
                  'url': workspace_api_conf.api.manifestTemplate.post.replace('{workspace_id}', workspace_id),
                  'type': 'post',
                  'data': formData,
                  'processData': false,
                  'contentType': false,
                  'cache': false,
                }).done(function( data, textStatus ){
                  if ( textStatus === 'success') {
                    console.log("manifest post response:" + JSON.stringify(data));
                    wsDataJSON['manifests'] = [];
                    for(var fileidx = 0; fileidx < data['rows'].length; fileidx++ ) {
                      wsDataJSON['manifests'][wsDataJSON['manifests'].length] = {
                        'file_id':  data['rows'][fileidx]['id'],
                        'file_name':  data['rows'][fileidx]['file_name'],
                        'file_text':  data['rows'][fileidx]['file_text'],
                        'update_at':  data['rows'][fileidx]['update_at'],
                      };
                    }
                    // アップロードが完了したら
                    workspaceImageUpdate();

                    // 選択が終わったらテンプレート一覧を表示
                    modal.change('kubernetesManifestTemplate', {
                      'callback': templateFileList
                    },
                    1160 );
                  }
                }).fail(function( jqXHR, textStatus, errorThrown ){
                  // エラー
                });
                } break;
                case 'reselect': {
                  $inputFile.val('');
                  $upload.add( $reSelect ).prop('disabled', true );
                  $file.find('.item-file-list').hide().find('tbody').remove();
                  $file.find('.item-file-droparea').show();
                } break;
              }
            });
          } else {
            alert('yamlファイル以外が選択されました。');
          }
        }
      }
      
      // ファイル数分FileReaderで処理する
      for ( let i = 0; i < fileLength; i++ ) {
        //if ( files[i].type === 'text/plain') {
        if ( files[i].name.match(/\.yaml$/) ) {
            const reader = new FileReader();
          $( reader ).on('load', function( data ){
            
            const filename = fn.textEntities(files[i].name),
                  date = new Date( files[i].lastModifiedDate ),
                  formatDate = fn.formatDate( date, 'yyyy/MM/dd HH:mm:ss');
            
            const $row = $(''
            + '<tr class="c-table-row">'
              + '<td class="template-name c-table-col"><div class="c-table-ci">' + filename + '</div></td>'
              + '<td class="template-type c-table-col"><div class="c-table-ci">' + files[i].type + '</div></td>'
              + '<td class="template-size c-table-col"><div class="c-table-ci">' + files[i].size + '</div></td>'
              + '<td class="template-date c-table-col"><div class="c-table-ci">' + formatDate + '</div></td>'
              + '<td class="template-menu c-table-col"><div class="c-table-ci">'
                + '<ul class="c-table-menu-list">'
                  + '<li class="c-table-menu-item">'
                    + '<button class="c-table-menu-button epoch-popup-m" title="プレビュー" data-button="preview">'
                      + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-preview" /></svg></button></li>'
                + '</ul>'
              + '</div></td>'
            + '</tr>');
            
            // ファイルプレビュー
            $row.find('.c-table-menu-button').on('click', function(){
              modal.open('yamlPreview',{
                'callback': function(){
                  $('#yaml-preview').find('.modal-title').text( filename );
                  $('#yaml-preview-body').html(''
                  + '<pre class="item-parameter-pre prettyprint linenums lang-yaml">'
                    + data.target.result.replace(/({{\s.*?\s}})/g, '<span class="preview-parameter">$1</span>')
                  + '</pre>');
                  // コードハイライト
                  if ( PR !== undefined ) {
                    PR.prettyPrint();
                  }
                }
              }, 960, 'sub');
            });
            
            $fileTable.append( $row );
            
            createTable();
          });
          reader.readAsText(files[i]);
        } else {
          errorCount++;
          createTable();
        }
      }
    }
  });
  
  // ファイルドロップ
  $file.find('.item-file-droparea').on({
    'click': function(){
      $file.find('.item-file').click();
    },
    'dragover': function(e){
      e.preventDefault();
    },
    'dragenter': function(){
      $(this).addClass('enter');
    },
    'dragleave': function(){
      $(this).removeClass('enter');
    },
    'drop': function(e){
      e.preventDefault();
      $(this).removeClass('enter');
      // ドロップしたファイルをinputにセット
      $file.find('.item-file').get(0).files = e.originalEvent.dataTransfer.files;
      // changeトリガー
      $file.find('.item-file').change();
    }
  });
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Manifestテンプレートファイル削除実行
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function templateFileDelete(key, file_id){
  
  // API呼び出し
  new Promise(function(resolve, reject) {
    //
    // Manifestテンプレート削除APIの呼び出し
    //

    console.log("CALL : Manifestテンプレート削除 : key:" + key + ", id:" + file_id);
    api_param = {
      "type": "DELETE",
      "url": workspace_api_conf.api.manifestTemplate.delete.replace('{workspace_id}', workspace_id).replace('{file_id}', file_id),
    }

    $.ajax(api_param).done(function(data) {
      console.log("DONE : Manifestテンプレート削除");
      console.log("manifest delete response:" + JSON.stringify(data));

      wsDataJSON['manifests'] = [];
      for(var fileidx = 0; fileidx < data['rows'].length; fileidx++ ) {
        wsDataJSON['manifests'][wsDataJSON['manifests'].length] = {
          'file_id':  data['rows'][fileidx]['id'],
          'file_name':  data['rows'][fileidx]['file_name'],
          'file_text':  data['rows'][fileidx]['file_text'],
          'update_at':  data['rows'][fileidx]['update_at'],
        };
      }

      // 該当行のManifestパラメータ削除
      console.log("environment:-------------------------");
      for(var env in wsDataJSON['environment']) {
        delete wsDataJSON.environment[env].parameter[file_id];
        // newPara = {};
        // var i = 0;
        // for(var fileKey in wsDataJSON['environment'][env]["parameter"]) {
        //   // 選択されている行を除いて移行
        //   if (fileKey != key){
        //     i = i + 1;
        //     fildID = 'file'+("000"+i).slice(-3);
        //     newPara[fildID] = {};
        //     // パラメータごとにキー値があるので置き換え
        //     for(var para in wsDataJSON['environment'][env]["parameter"][fileKey])
        //     {
        //       paraID = para.substr((key + '-' + env + '-').length);
        //       newPara[fildID][fildID + "-" + env + "-" + paraID] = wsDataJSON['environment'][env]["parameter"][fileKey][para];
        //     }
        //   }
        // }
        // // 編集後の値を設定
        // wsDataJSON['environment'][env]["parameter"] = newPara;
        // console.log(wsDataJSON['environment'][env]['parameter']);
      }

      workspaceImageUpdate();

      apply_manifest();

      // 成功
      resolve();
    }).fail(function() {
      console.log("FAIL : Manifestテンプレート削除");
      // 失敗
      reject();
    });

  }).then(() => {
    console.log('Complete !!');
  }).catch(() => {
    // 実行中ダイアログ表示
    console.log('Fail !!');
  });
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   パラメータ入力
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const inputParameter = function(){  
  
  // タブごとに処理
  $('#manifest-parameter').find('.modal-tab-body-block').each(function(i){
  
    // yamlファイルを読み込む
    const dummyYaml = wsDataJSON['manifests'][i]['file_text'];

    // 読み込みが完了したら
    const $tabBlock = $( this ),
          tabID = $tabBlock.attr('id'),
          parameterSpan = '<span class="item-parameter" data-value="$2">$1</span>';
          
    let $parameter = $(''
    + '<div class="item-parameter-block">'
      + '<div class="item-parameter-input-area">'
      + '</div>'
      + '<div class="item-parameter-move">'
      + '</div>'
      + '<div class="item-parameter-code">'
        + '<pre class="item-parameter-pre prettyprint linenums lang-yaml">'
          + dummyYaml.replace(/({{\s(.*?)\s}})/g, parameterSpan )
        + '</pre>'
      + '</div>'
    + '</div>');
    
    // パラメータリストの作成
    const parameterList = {};
    $parameter.find('.item-parameter').each(function(){
      const parameterID = $( this ).attr('data-value');
      // 重複チェック
      if ( parameterList[ parameterID ] === undefined ) {
        parameterList[ parameterID ] = $( this ).text()
      }
    });
    
    let parameterArea = '';

    // 予約項目説明
    const itemFixedInfo = {
      'image': 'イメージ',
      'image_tag': 'イメージタグ名'
    };
    
    // 環境が登録済みか？
    if ( Object.keys( wsDataJSON.environment ).length ) {
      parameterArea += ''
      + '<table class="item-parameter-table">'
        + '<thead>'
          + '<tr class="item-parameter-row">'
            + '<th class="item-parameter-cell"><div class="item-parameter-cell-i">パラメータ</div></th>';
      // thead 環境名
      for ( const key in wsDataJSON.environment ) {          
        parameterArea += ''
        + '<th class="item-parameter-cell">'
          + '<div class="item-parameter-cell-i">'
            + wsDataJSON.environment[key].text
          + '</div>'
        + '</th>';
      }
      parameterArea += ''
            + '<th class="item-parameter-cell item-parameter-info">'
              + '<div class="item-parameter-cell-i">項目説明</div>'
            + '</th>'
          + '</tr>'
        + '</thead>'
      + '<tbody>';
      for ( const parameterID in parameterList ) {
        const parameterName = parameterList[parameterID].replace(/^{{\s(.+)\s}}$/,'$1');
        parameterArea += '<tr class="item-parameter-row"><th class="item-parameter-cell"><div class="item-parameter-cell-i">' + parameterName + '</div></th>';
        for ( let key in wsDataJSON.environment ) {
          const name = key + '-' + tabID + '-' + parameterID,
                environmentName = wsDataJSON.environment[key].text;
          let value = modal.searchValue( wsDataJSON.environment[key], name );
          if ( value === undefined ) value = '';
          parameterArea += '<td class="item-parameter-cell">'
          + '<div class="item-parameter-input-w">'
            + '<input type="text" '
              + 'value="' + value + '" '
              + 'class="item-text" '
              + 'placeholder="' + environmentName + ' : ' + parameterName + '" '
              + 'name="' + name + '" '
              + 'data-file="' + tabID + '" '
              + 'data-enviroment="' + key + '" '
              + 'data-parameter="' + parameterID + '">'
            + '</div>'
          + '</td>';
        }
        // 項目説明
        parameterArea += '<td class="item-parameter-cell item-parameter-info"><div class="item-parameter-input-w">';
        if ( itemFixedInfo[parameterName] === undefined ) {
          const name = '__parameterItemInfo__-' + tabID + '-' + parameterID;
          let value = modal.searchValue( wsDataJSON['parameter-info'][tabID], name );
          if ( value === undefined ) value = '';
          parameterArea += ''
          + '<input type="text" '
            + 'value="' + value + '" '
            + 'class="item-text" '
            + 'placeholder="項目説明 : ' + parameterName + '" '
            + 'name="' + name + '" '
            + 'data-file="' + tabID + '" '
            + 'data-enviroment="__parameterItemInfo__" '
            + 'data-parameter="' + parameterID + '">';
        } else {
          parameterArea += '<span class="item-parameter-fixed-info">' + itemFixedInfo[parameterName] + '</span>';
        }        
        parameterArea += '</div></td></tr>';
      }
      parameterArea += '</tbody>'
      + '</table>';
    } else {
      parameterArea += '<div class="item-parameter-empty-block"><div class="modal-empty-block">環境の登録がありません。</div></div>'
    }
    $parameter.find('.item-parameter-input-area').html( parameterArea );
    
    $tabBlock.html( $parameter );
    
    $parameter.find('.item-text').on({
      // フォーカスでコードを指定位置にスクロール
      'focus': function(){
        const $input = $( this ),
              p = $input.attr('data-parameter'),
              $p = $parameter.find('.item-parameter[data-value="' + p + '"]').eq(0),
              $l = $p.closest('li'),
              $code = $parameter.find('.item-parameter-code');
        $code.find('.select').removeClass('select');
        $p.addClass('select');
        $code.stop( 0,0 ).animate({ scrollTop: $l.position().top + $code.scrollTop() }, 300, 'swing');
      }  
    });

    $parameter.find('.item-parameter-move').on({
      'mousedown': function( md ){
        const $move = $( this ),
              $window = $( window ),
              $parent = $move.closest('.item-parameter-block'),
              $blockA = $move.prev('.item-parameter-input-area'),
              $blockB = $move.next('.item-parameter-code'),
              moveSize = $move.outerHeight() / 2,
              parentSize = $parent.innerHeight(),
              mdY = md.pageY,
              aSize = $blockA.outerHeight(),
              bSize = $blockB.outerHeight(),
              minHeight = 80,
              maxHeight = parentSize - minHeight - ( moveSize * 2 );
        
        let   aSetSize, bSetSize,
              moveY = 0;
        
        getSelection().removeAllRanges();
        
        const sizeSet = function( a, b ){
          $blockA.css('height', a );
          $blockB.css('height', b );
        };
        sizeSet( aSize, bSize );
        
        $parent.addClass('active');
        $window.on({
          'mousemove.parameterSlide': function( mm ){
            moveY = mdY - mm.pageY;
            aSetSize = aSize - moveY;
            bSetSize = bSize + moveY;
            if ( aSetSize < minHeight ) {
              aSetSize = minHeight;
              bSetSize = maxHeight;
            }
            if ( bSetSize < minHeight ) {
              bSetSize = minHeight;
              aSetSize = maxHeight;
            }
            sizeSet( aSetSize, bSetSize );
          },
          'mouseup.parameterSlide': function(){
            $window.off('mousemove.parameterSlide mouseup.parameterSlide');
            $parent.removeClass('active');
            aSetSize = ( aSetSize + moveSize ) / parentSize * 100;
            bSetSize = 100 - aSetSize;
            sizeSet('calc(' + aSetSize + '% - ' + moveSize + 'px)', 'calc(' + bSetSize + '% - ' + moveSize + 'px)');
          }
        });
      }
    });

    // コードハイライト
    if ( PR !== undefined ) {
      PR.prettyPrint();
    }
    
  });
  
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   CD実行
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const cdExecution = function(){
  const envList = wsDataJSON['environment'],
        $modal = $('#modal-container'),
        $exeSetting = $('#cd-execution-condition'), // 実行条件
        $manifest = $('#cd-execution-manifest-parameter'), // Manifestパラメータ
        $argo = $('#cd-execution-argo'), // ArgoCDパイプライン
        $okButton = $modal.find('.modal-menu-button[data-button="ok"]');
        
  $okButton.prop('disabled', true );

  // CD execution environment information processing - CD実行環境情報処理
  new Promise((resolve, reject) =>{
    var workspace_id = (new URLSearchParams(window.location.search)).get('workspace_id');
      $.ajax({
          "type": "GET",
          "url": URL_BASE + "/api/workspace/{workspace_id}/cd/environment".replace('{workspace_id}',workspace_id)
      }).done(function(data) {
          console.log('[DONE] /workspace/{id}/member/environment');

          resolve(data['environments']);
      }).fail((jqXHR, textStatus, errorThrown) => {
          console.log('[FAIL] /workspace/{id}/cd/environment');
          reject();
      });
  }).then((getEnvList) => {
    console.log(getText('EP010-0301', '[DONE] 環境取得'));
    console.log(getEnvList);

    // 実行条件
    let exeSettingOptionHTML = '<option value="none" selected>CD実行する環境を選択してください。</option>';
    // for ( const key in envList ) {
    for ( const idx in getEnvList ) {
      // exeSettingOptionHTML += '<option value="' + key + '">' + envList[key].text + '</option>'
      exeSettingOptionHTML += '<option value="' + getEnvList[idx]["id"] + '">' + getEnvList[idx]["name"] + '</option>'
    }
    exeSettingOptionHTML += '</select>';

    const today = fn.formatDate( new Date(), 'yyyy/MM/dd HH:mm');

    const exeSettingHTML = ''
    + '<table id="cd-execution-condition-table" class="c-table">'
      + '<tr class="c-table-row">'
        + '<th class="c-table-col c-table-col-header"><div class="c-table-ci">CD実行日時</div></th>'
        + '<td class="c-table-col"><div class="c-table-ci">'
          + '<ul class="execution-date-select item-radio-list">'
            + '<li class="item-radio-item">'
              + '<input class="item-radio" type="radio" id="execution-date-immediate" value="immediate" name="execution-date" checked>'
              + '<label class="item-radio-label" for="execution-date-immediate">即実行</label>'
            + '</li>'
            + '<li class="item-radio-item">'
              + '<input class="item-radio" type="radio" id="execution-date-set" value="dateset" name="execution-date">'
              + '<label class="item-radio-label" for="execution-date-set">予約日時指定</label>'
            + '</li>'
          + '</ul>'
          + '<div class="execution-date"><input type="text" class="execution-date-input item-text" placeholder="' + today + '" value="' + today + '" disabled></div>'
        + '</div></td>'
      + '</tr>'
        + '<tr class="c-table-row">'
          + '<th class="c-table-col c-table-col-header"><div class="c-table-ci">環境</div></th>'
          + '<td class="c-table-col"><div class="c-table-ci">'
            + '<div class="item-select-area">'
              + '<select id="cd-execution-environment-select" class="item-select">'
                + exeSettingOptionHTML
              + '</select>'
            + '</div>'
          + '</div></td>'
        + '</tr>'
      + '</table>';
      
      $exeSetting.html( exeSettingHTML );
    

      const $executionDateInput = $modal.find('.execution-date-input');
      $executionDateInput.datePicker({'s': 'none'});
      
      $modal.find('.item-radio[name="execution-date"]').on('change', function(){
        const value = $( this ).val();
        if ( value === 'dateset') {
          $executionDateInput.prop('disabled', false ).focus();
        } else {
          $executionDateInput.prop('disabled', true );
        }
      });
      
      // 選択されていません。
      const notSelected = function(){
        return '<div class="modal-empty-block">環境が選択されていません。</div>';
      };
      
      // Manifestパラメータ
      $manifest.find('.modal-tab-body-block').html( notSelected() );
      
      // テーブルHTML
      const tableHTML = function( table ){
        let html = '<table class="c-table">';
        for ( const key in table ) {
          html += ''
          + '<tr class="c-table-row">'
            + '<th class="c-table-col c-table-col-header"><div class="c-table-ci">' + key + '</div></th>'
            + '<td class="c-table-col"><div class="c-table-ci">' + fn.textEntities( table[key] ) + '</div></td>'
          + '</tr>';
        }
        html += '</table>';
        return html;
      };
      $argo.html( notSelected() );
      
      // 環境選択
      $modal.find('#cd-execution-environment-select').on('change', function(){
        const envID = $( this ).val(),
              deploy = envList[envID],
              rKey = envID + '-git-service-argo-repository-url',
              nKey = envID + '-environment-namespace',
              sKey = envID + '-environment-deploy-select',
              uKey = envID + '-environment-url',
              uDefault = 'https://Kubernetes.default.svc';
        
        console.log('cd-execution-environment-select change');
        if ( envID !== 'none') {
        
          // パラメーター
          $manifest.find('.modal-tab-body-block').each(function(){
            const $parameter = $( this ),
                  fileID = $parameter.attr('id');
            if ( deploy['parameter'] !== undefined && deploy['parameter'][fileID] !== undefined ) {
              const envPara = deploy['parameter'][fileID],
                    paraList = {};
              for ( const key in envPara ) {
                const paraReg = new RegExp('^' + envID + '-' + fileID + '-');
                paraList[ key.replace( paraReg, '') ] = envPara[key];
              }          
              $parameter.html( tableHTML( paraList ) );
            } else {
              $parameter.html('<div class="modal-empty-block">Manifestパラメータの登録がありません。</div>')
            }
          });  
        
          // Deploy環境
          const name = deploy['text'],
                repository = ( deploy[rKey] !== undefined )? deploy[rKey]: '',
                namespace  = ( deploy[nKey] !== undefined )? deploy[nKey]: '';
          let url;
          if ( deploy[sKey] === 'internal') {
            // 内部
            url = uDefault;
          } else if ( deploy[sKey] === 'external') {
            // 外部
            url = ( deploy[uKey] !== undefined )? deploy[uKey]: '';
          } else {
            url = '';
          }
          wsDataJSON['cd-execution-param']['operation-search-key'] = repository;
          wsDataJSON['cd-execution-param']['environment-name'] = name;
          $argo.html('<p>以下の内容でDeployします。よろしいですか？</p>'
          + tableHTML({
            '環境名': name,
            'Manifestリポジトリ': repository,
            'Kubernetes API Server URL': url,
            'Namespace': namespace
          }) );
          $okButton.prop('disabled', false );
        } else {
          $argo.add(  $manifest.find('.modal-tab-body-block') ).html( notSelected() );
          wsDataJSON['cd-execution-param']['operation-search-key'] = '';
          wsDataJSON['cd-execution-param']['environment-name'] = '';
          $okButton.prop('disabled', true );
        }
      });
  
    }).catch(() => {
      console.log(getText('EP010-0302', '[FAIL] 環境取得'));
  });

};


// CD実行可能メンバーの取得 - Get a CD executable member
const deployMembers = wsModalJSON.pipelineArgo.block.environmentList.tab.item.environmentDeployMember;

const get_cdexec_member = function() {
  var workspace_id = (new URLSearchParams(window.location.search)).get('workspace_id');
  if(workspace_id == null) {
    return;
  }
  $.ajax({
    "type": "GET",
    "url": URL_BASE + "/api/workspace/{workspace_id}/member/cdexec".replace('{workspace_id}',workspace_id)
  }).done(function(data) {
    console.log('[DONE] /workspace/{id}/member/cdexec');

    deployMembers.list = []
    
    // Set the acquired member list - 取得したメンバーリストを設定
    for(var useridx = 0; useridx < data['rows'].length; useridx++ ) {
      deployMembers.list.push([
        data['rows'][useridx]['user_id'],
        data['rows'][useridx]['username']
      ]);
    }
  });
}

$(document).ready(() => { get_cdexec_member(); });

const argoCdAddDeployMembersModal = function(){
  const $argoModal = $('#pipeline-argo');

  // ArgoCDモーダル - Deploy権限項目の「ユーザ選択」ボタン押下時のイベント処理
  // ArgoCD modal - Event processing when the "Select User" button with Deploy permission item is pressed
  $argoModal.on('click', '.item-list-select-button', function(){
    const $button = $( this ),
          type = $button.attr('data-button'),
          $select = $button.closest('.item-block'),
          value = $select.find('.item-list-select-id').val(),
          ids = ( value === '')? []: value.split(','),
          subModal = new modalFunction( wsModalJSON, wsDataJSON );

    switch( type ) {
      case 'select': {
        subModal.open('pipelineArgoDeployMember', {
          'ok': function(){
            const id = subModal.$modal.find('.et-cb-i').val();
            subModal.createListSelectSetList( $select, id, deployMembers.list, deployMembers.col );
            subModal.close();
          },
          'callback': function(){
            const et = new epochTable(),
                  checked = {};
            checked[et.tableID + '-row-all'] = ids;
            et.setup('#pipeline-argo-deploy-member-select', [
              {'title': '選択', 'id': 'row-all','type': 'rowCheck', 'width': '48px'},
              {'title': 'ユーザ名', 'type': 'text', 'width': 'auto', 'sort': 'on', 'filter': 'on'}
            ], deployMembers.list, {'checked': checked });
          }
        }, 720,'sub');
      } break;
      case 'clear':
        $select.find('.item-list-select-id').val('');
        subModal.createListSelectSetList( $select, '', [], 0 );
    }
  });
};


////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   CD実行
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const cdRunning = function(){
  
  // API呼び出し
  new Promise(function(resolve, reject) {
    // 実行中ダイアログ表示
    $('#modal-progress-container').css('display','flex');
    $('#progress-message-ok').css("display","none");
    $('#progress-message-ok-cdexec').css("display","inline");
    $('#progress-message-ok-cdexec').prop("disabled", true);
    //
    // CD実行APIの呼び出し
    //
    $('#progress_message').html('CD実行開始');

    // API Body生成
    reqbody = {};
    reqbody['operationSearchKey'] = wsDataJSON['cd-execution-param']['operation-search-key'];
    reqbody['environmentName'] = wsDataJSON['cd-execution-param']['environment-name'];
    //reqbody['preserveDatetime'] = wsDataJSON['cd-execution-param']['preserve-datetime'];
    if ( modal.$modal.find('.item-radio[name="execution-date"]:checked').val() === 'dateset') {
      reqbody['preserveDatetime'] = modal.$modal.find('.execution-date-input').val();
    } else {
      reqbody['preserveDatetime'] = "";
    }

    console.log("EXEC wsDataJSON:" + JSON.stringify(wsDataJSON));

    console.log("CALL : CD実行開始");
    api_param = {
      "type": "POST",
      "url": workspace_api_conf.api.cdExecDesignation.post.replace('{workspace_id}', workspace_id),
      "data": JSON.stringify(reqbody),
      contentType: "application/json",
      dataType: "json",
    }

    $.ajax(api_param).done(function(data) {
      console.log("DONE : CD実行");
      console.log("--- data ----");
      console.log(JSON.stringify(data));
      // 成功
      resolve();
    }).fail(function() {
      console.log("FAIL : CD実行");
      // 失敗
      reject();
    });

  }).then(() => {
    $('#progress_message').html('CD実行開始しました');
    console.log('Complete !!');
    $('#progress-message-ok-cdexec').prop("disabled", false);
  }).catch(() => {
    // 実行中ダイアログ表示
    $('#progress_message').html('CD実行失敗しました');
    $('#progress-message-ok-cdexec').prop("disabled", false);
    console.log('Fail !!');
  });
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   モーダルオープン
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
$('#content').find('.modal-open').on('click', function(e){
  e.stopPropagation();
  const $button = $( this ),
        target = $button.attr('data-button'),
        funcs = {};

  let width = 800;

  console.log('modal open:' + target);

  switch( target ) {
    // Workspace
    case 'workspace': {
      funcs.ok = function(){
        setInputData('', 'workspace');
        wsDataCompare();
        workspaceImageUpdate();
        modal.close();
      };   
      } break;
    // Gitサービス
    case 'gitService': {
      funcs.ok = function(){
        setInputData('application-code', 'git-service');
        deleteTabData('application-code');
        wsDataCompare();
        workspaceImageUpdate();
        modal.close();
      };   
      } break;
    // レジストリサービス
    case 'registryService': {
      funcs.ok = function(){
        setInputData('application-code', 'registry-service');
        wsDataCompare();
        workspaceImageUpdate();
        modal.close();
      };      
      funcs.callback = setRegistryServiceInput;
    } break;
    // Argo CD
    case 'pipelineArgo': {
      funcs.ok = function(){
        setInputData('environment', '');
        deleteTabData('environment');
        wsDataCompare();
        workspaceImageUpdate();
        modal.close();
      };
      funcs.callback = argoCdAddDeployMembersModal;
      } break;
    // Tekton
    case 'pipelineTekton': {
      funcs.ok = function(){
        setInputData('application-code', '');
        wsDataCompare();
        workspaceImageUpdate();
        modal.close();
      };      
      } break;
    // Argo CD Gitサービス
    case 'gitServiceArgo': {
      funcs.ok = function(){
        setInputData('environment', 'git-service-argo');
        wsDataCompare();
        workspaceImageUpdate();
        modal.close();
      };
    } break;
    
    // Kubernetes Manifest テンプレート
    case 'kubernetesManifestTemplate': {
      funcs.callback = templateFileList;
      funcs.move = function(){}
      width = 1160;
    } break;
    // Manifestパラメータ
    case 'manifestParametar': {
      funcs.ok = function(){
        setParameterData();
        workspaceImageUpdate();
        apply_manifest();
        modal.close();
      };
      funcs.callback = inputParameter;
      width = 1160;
    } break;
  }

  modal.open( target, funcs, width );
});

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   各種サービス結果確認
//   > workspace_result.js
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
$workspace.find('.modal-check').on('click', function(e){
  e.stopPropagation();
  
  const $b = $( this ),
        type = $b.attr('data-button');
  
  switch( type ) {
      // アプリケーションコードリポジトリ
      case 'gitServiceCheck':
          wsAppCodeRepoCheck( wsDataJSON['git-service'] );
      break;
      case 'pipelineTektonCheck':
          wsTektonCheck();
      break;
      // マニフェストリポジトリ
      case 'gitServiceArgoCheck':
          wsManiRepoCheck( wsDataJSON['environment'] );
      break;
      // レジストリサービス
      case 'registryServiceCheck':
          wsRegiSerCheck();
      break;
      // ArgoCD
      case 'arogCdResultCheck':
          wsArgocdCheck();
      break;
      // IT Automation
      case 'exastroItAutomationResultCheck':
          wsItaCheck();
      break;
  }
  
});

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   文字がはみ出てる場合調整する
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const workspaceTextAdjust = function( ) {
  $workspace.find('.adjust-text').each(function(){
    const $text = $( this ),
          sWidth = $text.get(0).scrollWidth,
          cWidth = $text.closest('div').get(0).offsetWidth;
    if ( cWidth < sWidth ) {
      $text.css('transform', 'scaleX(' + ( cWidth / sWidth ) + ')')
    } else {
      $text.removeAttr('style');
    }
  });
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ワークスペース情報の更新
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
// 変更フラグ
const compareFlag = {
  'workspace': false,
  'gitService': false,
  'pipelineTekton': false,
  'registryService': false,
  'pipelineArgo': false,
  'gitServiceArgo': false
};

// 枠をクリックした際にボタンをクリック
$workspace.on('click', '.button-box-area, .button-document-area', function(){
  $( this ).find('button:visible').trigger('click');
});

const workspaceImageUpdate = function( ) {
  
  // ワークスペースタイプ
  const type = $content.attr('data-workspace-type');
  
  // ワークスペース名
  const $workspaceName = $content.find('.content-title-heading'),
        $workspaceNote = $content.find('.content-note-inner'),
        workspaceName = ( fn.isset( wsDataJSON['workspace']['workspace-name'] ) )?
                          wsDataJSON['workspace']['workspace-name']:
                          '名称未設定',
        workspaceNote = ( fn.isset( wsDataJSON['workspace']['workspace-note'] ) )?
                          wsDataJSON['workspace']['workspace-note']:
                          '';
  $workspaceName.text( workspaceName );
  $workspaceNote.text( workspaceNote );

  // ボタンの親チェックと説明の追加
  $workspace.find('.button-box-area, .button-document-area')
    .removeClass('button-box-area button-document-area epoch-popup')
    .removeAttr('title');
  $workspace.find('.workspace-button:visible').each(function(){
    const $block = $( this ).closest('.workspace-block, .workspace-point'),
          id = $block.attr('id');
    $block.addClass('button-box-area epoch-popup').attr('title', wsDescription[type][id] );
  });
  $workspace.find('.workspace-document-button:visible').each(function(){
    const $block = $( this ).closest('.workspace-document-wrap'),
          id = $block.attr('id');
    $block.addClass('button-document-area epoch-popup').attr('title', wsDescription[type][id] );
  });

  // ワークスペースステータス
  const $status = $workspace.find('.workspace-status-list');

  // Gitサービス
  const $gitService = $('#ws-git-service'),
        gitServiceID = wsDataJSON['git-service']['git-service-select'],
        gitServiceText = wsModalJSON.gitService.block.gitServiceSelect.item.gitServiceSelectRadio.item[gitServiceID];
  $gitService.find('.workspace-block-name-inner').text( gitServiceText );
  $gitService.attr('data-service', gitServiceID );
  
  // レジストリサービス
  const $registryService = $('#ws-registry-service'),
        registryServiceID = wsDataJSON['registry-service']['registry-service-select'],
        registryServiceText = wsModalJSON.registryService.block.registryServiceSelect.item.registryServiceSelectRadio.item[registryServiceID];
  $registryService.find('.workspace-block-name-inner').text( registryServiceText );
  $registryService.attr('data-service', registryServiceID );
  
  // Argo CD Gitサービス
  const $gitServiceArgo = $('#ws-git-argo'),
        gitServiceArgoID = wsDataJSON['git-service-argo']['git-service-argo-select'],
        gitServiceArgoText = wsModalJSON.gitServiceArgo.block.gitServiceArgoSelect.item.gitServiceArgoSelectRadio.item[gitServiceArgoID];
  $gitServiceArgo.find('.workspace-block-name-inner').text( gitServiceArgoText );
  $gitServiceArgo.attr('data-service', gitServiceArgoID );
  
  // 重なり共通
  const multipleMax = 5;
  const cloneBlock = function( number ){
    if ( number - 1 > 0 ) {
      return '<div></div>' + cloneBlock( number - 1 );
    }
    return '';
  };
  
  // 環境数
  const $envTarget = $('#ws-ita-parameter, #ws-git-epoch, #ws-system, #ws-kubernetes-manifest'),
        envNumber = Object.keys( wsDataJSON['environment'] ).length,
        limitEnvNumber = ( multipleMax >= envNumber )? envNumber: multipleMax,
        divEnvClone = cloneBlock( limitEnvNumber );
  $envTarget.attr('data-multiple', limitEnvNumber );
  $envTarget.find('.multiple-number').text( envNumber );
  $envTarget.find('.multiple-block').html( divEnvClone );
  $status.find('.environment').text( envNumber );
  
  // アプリケーションコード数
  const $appTarget = $('#ws-ci-area'),
        appNumber = Object.keys( wsDataJSON['application-code'] ).length,
        limitAppNumber = ( multipleMax >= appNumber )? appNumber: multipleMax,
        divAppClone = cloneBlock( limitAppNumber );
  $appTarget.attr('data-multiple', limitAppNumber );
  $appTarget.find('.multiple-number').text( appNumber );
  $appTarget.find('.multiple-block').html( divAppClone );
  $status.find('.application').text( appNumber );
  
  // Kubernetes Manifestテンプレート数
  const $tempTarget = $('#ws-kubernetes-manifest-template'),
        tempNumber = Object.keys( wsDataJSON['manifests'] ).length,
        limitTempNumber = ( multipleMax >= tempNumber )? tempNumber: multipleMax,
        divTempClone = cloneBlock( limitTempNumber );
        
  $status.find('.template').text( tempNumber ); 
  $tempTarget.attr('data-multiple', limitTempNumber );
  $tempTarget.find('.multiple-number').text( tempNumber );
  $tempTarget.find('.multiple-block').html( divTempClone );
  
  const done = 'done',
        unentered = 'unentered';

        // 入力チェック
  if ( type === 'setting') {
    
    let inputF = false,
        compareF = false;
    
    // 共通
    const checkList = {
      'gitService': {'num': appNumber, 'block': 'ws-git-service'},
      'pipelineTekton': {'num': appNumber, 'block': 'ws-pipeline-tekton'},
      'registryService': {'num': appNumber, 'block': 'ws-registry-service'},
      'pipelineArgo': {'num': envNumber, 'block': 'ws-pipeline-argo'},
      'gitServiceArgo': {'num': envNumber, 'block': 'ws-git-argo'}
    };
    for ( const key in checkList ) {
        // 枠
        $content.find('#' + checkList[key].block )
          .attr('data-modified', compareFlag[ key ] );
        // ボタン
        const inputChack = ( checkList[key].num && modal.inputCheck( key ) )? done: unentered;
        if ( inputF === false && inputChack === 'unentered') inputF = true;
        $content.find('.workspace-button[data-button="' + key + '"]')
          .attr('data-status', inputChack );
    }
        
    // ワークスペース名
    const workspaceInput = ( modal.inputCheck('workspace') )? done: unentered;
    $content.find('.content-header .workspace-button').attr('data-status', workspaceInput );
    if ( inputF === false && workspaceInput === 'unentered') inputF = true;
    
    // 変更チェック
    for ( const key in compareFlag ) {
      if ( compareFlag[key] ) compareF = true;
    }
    
    // 作成・更新ボタン
    const createF = ( inputF === false && compareF === true )? false: true;
    // 現段階では常に押下可能に
    //$workspaceFooter.find('.workspace-footer-menu-button[data-button="create"], .workspace-footer-menu-button[data-button="update"]').prop('disabled', createF );
    $workspaceFooter.find('.workspace-footer-menu-button[data-button="create"], .workspace-footer-menu-button[data-button="update"]').prop('disabled', false );
    
    // リセットボタン
    const resetF = ( compareF === true )? false: true;
    // 現段階では常に押下可能に
    // $workspaceFooter.find('.workspace-footer-menu-button[data-button="reset"]').prop('disabled', resetF );
    $workspaceFooter.find('.workspace-footer-menu-button[data-button="reset"]').prop('disabled', false );
    
  } else if ( type === 'deploy') {
    const manifestTemp = ( tempNumber > 0 )? done: unentered;
    $content.find('.workspace-document-button[data-button="kubernetesManifestTemplate"]').attr('data-status', manifestTemp );
  }
  
  workspaceReload();
  workspaceTextAdjust();
  setEpochFrame();
  
  console.log(wsDataJSON);
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ワークスペースの切り替え
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const $tabList = $workspace.find('.workspace-tab-list');

const workspaceChange = function( workspaceType ){
  $tabList.find('.current').removeClass('current');
  $tabList.find('.workspace-tab-link[href="#' + workspaceType + '"]').addClass('current');
  
  $content.attr('data-workspace-type', workspaceType );
  
  setFotter( workspaceType );
  workspaceImageUpdate();
  workspaceReload();
  workspaceTextAdjust();
};
workspaceChange( initWorkspaceType );

$tabList.find('.workspace-tab-link[href^="#"]').on('click', function(e){
  e.preventDefault();
  const $tab = $( this ),
        target = $tab.attr('href').replace(/^#/,'');
  
  if ( !$tab.is('.current') ) {
    workspaceChange( target );    
  }

});

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   変更チェック
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

// 変更ステータス
const compareStatus = {
  'add': 'Add',
  'equal': 'Equal',
  'change': 'Change',
  'remove': 'Remove'
};

// 変更前
let beforeWsData = $.extend( true, {}, wsDataJSON );

// 比較データ作成（ beforeWsData <> wsDataJSON ）
const wsDataCompare = function(){
    
    const tempBeforeData = $.extend( true, {}, beforeWsData ),
          tempAfterData =  $.extend( true, {}, wsDataJSON );
    
    // 比較
    const compare = function( a, b ){
        if ( b === undefined ) {
            if ( a === undefined ) {
              return [ compareStatus.equal, b, a ];
            } else {
              return [ compareStatus.add, b, a ];
            }
        } else if ( b === null || b === '') {
          if ( a === null || a === '' ) {
            return [ compareStatus.equal, b, a ];
          } else {
            return [ compareStatus.add, b, a ];
          }
        } else if ( a === b ) {
            return [ compareStatus.equal, b, a ];
        } else {
            return [ compareStatus.change, b, a ];
        }
    };
    
    const result = {
      'compare': {},
      'html': {}
    };
    
    // 変更・追加チェック
    const changeCheck = function( a, b, r ){
        const type = modal.typeJudgment( a );
        switch ( type ) {
            case 'object':
                for ( const k in a ) {
                    const t = modal.typeJudgment( a[k] );
                    switch ( t ) {
                        case 'object':
                            if ( !b[k] ) b[k] = {};
                            if ( !r[k] ) r[k] = {};
                        break;
                        case 'string':
                            r[k] = compare( a[k], b[k] );     
                    }
                    changeCheck( a[k], b[k], r[k] );
                }
            break;
        }
    };    
    changeCheck( tempAfterData, tempBeforeData, result.compare );
    
    // 削除チェック
    const deleteCheck = function( b, a, r ) {
        const type = modal.typeJudgment( b );
        switch ( type ) {
            case 'object':
                for ( const k in b ) {
                    const t = modal.typeJudgment( b[k] );
                    switch ( t ) {
                        case 'object':
                            if ( !r[k] ) r[k] = {};
                            if ( a[k] === undefined ) {
                                for ( const key in b[k] ) {
                                  if ( b[k][key] !== null ) {
                                    r[k][key] = [ compareStatus.remove, b[k][key], undefined ];
                                  }
                                }
                            } else {
                                deleteCheck( b[k], a[k], r[k] );
                            }
                        break;
                        case 'string':
                            if ( a[k] === null || a[k] === undefined ) {
                                r[k] = [ compareStatus.remove, b[k], undefined ];
                            }
                    }
                }
            break;
        }
    };
    deleteCheck( tempBeforeData, tempAfterData, result.compare );    
    
    // モーダルごとにチェック
    for ( const key in compareFlag ) {
      const info = compareInfo( key, result.compare );
      compareFlag[key] = info.flag;
      result.html[key] = info.html;
    }    

    return result;
};
  
// 比較データから比較内容を表示する
const compareInfo = function( modalID, compareData ){

    const m = wsModalJSON[modalID];
    let h = '',
        flag = false;
    
    const title = m['title'],
          block = m['block'];
    
    const compareRow = function( title, status, before, after ) {
      let rowHTML = '<tr class="compareRow" data-status="' + status + '">';
      if ( title !== '') rowHTML += '<th class="compareTh compareItemTitle"><span>' + title + '</span></th>';
      rowHTML += '<td class="compareTd compareStatus"><span class="' + status + '">' + status + '</span></td>'
        + '<td class="compareTd compareBefore"><span>' + before + '</span></td>'
        + '<td class="compareTd compareAfter"><span>' + after + '</span></td>'
      + '</tr>';
      return rowHTML;
    }
    
    const itemBlock = function( item, searchData, tabID ){
      let ih = '';
      for ( const itemKey in item ) {
        const block = item[itemKey],
              id = ( tabID )? tabID + '-': '';
              
        let t = ( block['title'] )? block['title']: '',
            p = block['type'];

        if ( p !== 'reference' ) {
          const n = id + block['name'];
          
          const typeCheck = function( v ){
            switch( p ) {
              case 'radio':
              case 'listSelect':
                return block['item'][v];
              case 'listSelectID': {
                const n = block['list'].filter( function(f) {
                  if ( v.split(',').indexOf( String( f[0] )) !== -1 ) return f;
                });
                
                const nL = n.length,
                      l = [];
                for ( let i = 0; i < nL; i++ ) {
                  l.push( modal.fn.textEntities( n[i][1] ));
                }
                return '<em>' + l.join('</em><em>') + '</em>';
              }
              case 'password':
                return '********';
              default:
                return v;
            }
          };
          
          const addRow = function( targetID ){
            const search = modal.searchValue( searchData, targetID );
            if ( search ) {
              const c = ( search )? search: [''],
                    s = c[0],
                    b = ( c[1] )? typeCheck(c[1]): '',
                    a = ( c[2] )? typeCheck(c[2]): '';
              if ( s !== compareStatus.equal ) {
                ih += compareRow( t, s, b, a );
                flag = true;
              }
            }
          };
          addRow( n );

          // listSelect 用
          if ( p === 'listSelect') {
            t += '(Select)';
            p = 'listSelectID'
            addRow( n + '-id');
          }        
                    
        }
      }
      if ( ih === '') {
        return '';
      } else {
        return '<div class="comparaItemBody"><table class="compareTable"><tbody>' + ih + '</tbody></table></div>';
      }
    };
    
    const tabBlock = function( tab ){
      let th = '';
      const p = tab['type'];
      if ( p === 'add' || p === 'reference') {
        const t = tab['target'];
        for ( const tabKey in compareData[t['key1']] ) {
          // tab名
          const r = compareData[t['key1']][tabKey][t['key2']],
                n = ( r[2] )? r[2]: r[1];
          if ( r[0] === compareStatus.add ) flag = true;
          
          const kh = itemBlock( tab['item'], compareData[t['key1']][tabKey], tabKey );
          if ( kh !== '') {
            th += '<div class="compareTabBlock">'
              + '<div class="compareTabTitle">' + n + '</div>'
              + '<div class="comparaTabBody">' + kh + '</div>'
            + '</div>';
          }
        }
      }  
      return th;
    };
    
    for ( const key in block ) {
      const b = block[key];
      let r = '';
      if ( b['item'] ) {
        r = itemBlock( b['item'], compareData );
      } else if ( b['tab'] ) {
        r = tabBlock( b['tab'] );
      }
      if ( r !== '') {
        const blockTitle = ( b['title'] )? b['title']: '';
        h += '<div class="compareBlockTitle">' + blockTitle + '</div>'
        + '<div class="compareBlockBody">' + r + '</div>';
      }
    }
    
    if ( h !== '') {
      h = '<div class="compare">'
          + '<div class="compareTitle">' + title + '</div>'
          + '<div class="compareBody">' + h + '</div>'
        + '</div>';
    }

    return {
      'html': h,
      'flag': flag
    };

};

  //-----------------------------------------------------------------------
  // API呼び出し関連
  //-----------------------------------------------------------------------

  // window onloadイベント
  $(document).ready(function(){ getWorksapce(); });

  // ワークスペース情報の読み込み
  function getWorksapce(){

    workspace_id = (new URLSearchParams(window.location.search)).get('workspace_id');
    if(workspace_id == null) {
      // No need to get data when new - 新規の時はデータの取得は不要
      return;
    }

    new Promise((resolve, reject) => {

      console.log("[CALL] GET " + workspace_api_conf.api.resource.get);
 
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.resource.get.replace('{workspace_id}', workspace_id),
      }).done(function(data) {
        console.log("[DONE] GET " + workspace_api_conf.api.resource.get + " response\n" + JSON.stringify(data));
  
        workspace_id = data['rows'][0]['workspace_id'];
  
        data_workspace = data['rows'][0];

        if(data_workspace['parameter-info']) {
          wsDataJSON['parameter-info'] = data_workspace['parameter-info']
        }
        
        if(data_workspace['common']) {
          wsDataJSON['workspace'] = {
            'workspace-name' :                    data_workspace['common']['name'],
            'workspace-note' :                    data_workspace['common']['note'],
          };
        }
        wsDataJSON['git-service'] = {
          'git-service-select' :                data_workspace['ci_config']['pipelines_common']['git_repositry']['housing'] == 'inner'? 'epoch': data_workspace['ci_config']['pipelines_common']['git_repositry']['interface'],
          'git-service-user' :                  data_workspace['ci_config']['pipelines_common']['git_repositry']['user'],
          'git-service-token' :                 data_workspace['ci_config']['pipelines_common']['git_repositry']['token'],
        };
        wsDataJSON['registry-service'] = {
          'registry-service-select' :           data_workspace['ci_config']['pipelines_common']['container_registry']['housing'] == 'inner'? 'epoch': data_workspace['ci_config']['pipelines_common']['container_registry']['interface'],
          'registry-service-account-user' :     data_workspace['ci_config']['pipelines_common']['container_registry']['user'],
          'registry-service-account-password' : data_workspace['ci_config']['pipelines_common']['container_registry']['password'],
        };
  
        wsDataJSON['application-code'] = {};
        data_pipelines = data_workspace['ci_config']['pipelines'];
        for(var i in data_pipelines) {
          var item = data_pipelines[i]['pipeline_id'];
          wsDataJSON['application-code'][item] = {};
          wsDataJSON['application-code'][item]['text'] = data_pipelines[i]['git_repositry']['url'].replace(/^.*\//,'').replace(/\.git$/,'');
          wsDataJSON['application-code'][item][item + '-git-repository-url']                  = data_pipelines[i]['git_repositry']['url'];
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-branch']              = data_pipelines[i]['build']['branch'].join(',');
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-docker-path']         = data_pipelines[i]['build']['dockerfile_path'];
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-static-analysis']     = data_pipelines[i]['static_analysis']['interface'];
          wsDataJSON['application-code'][item][item + '-registry-service-output-destination'] = data_pipelines[i]['container_registry']['image'];
        }
  
        wsDataJSON['environment'] = {};
        data_environments = data_workspace['cd_config']['environments'];
        for(var i in data_environments) {
          var item = data_environments[i]['environment_id'];
          wsDataJSON['environment'][item] = {};
          wsDataJSON['environment'][item]['text']                         = data_environments[i]['name'];
          wsDataJSON['environment'][item][item + '-environment-name']     = data_environments[i]['name'];
          wsDataJSON['environment'][item][item + '-environment-deploy-select'] = data_environments[i]['deploy_destination']['cluster_kind'];
          //wsDataJSON['environment'][item][item + '-environment-url']      = data_environments[i]['deploy_destination']['cluster_url'];
          wsDataJSON['environment'][item][item + '-environment-namespace']= data_environments[i]['deploy_destination']['namespace'];
          if(data_environments[i]['deploy_destination']['cluster_kind'] == "external") {
            wsDataJSON['environment'][item][item + '-environment-url']      = data_environments[i]['deploy_destination']['cluster_url'];
            wsDataJSON['environment'][item][item + '-environment-authentication-token']= data_environments[i]['deploy_destination']['authentication_token'];
            wsDataJSON['environment'][item][item + '-environment-certificate']= data_environments[i]['deploy_destination']['base64_encoded_certificate'];
          } else {
            wsDataJSON['environment'][item][item + '-environment-url']      = null;
            wsDataJSON['environment'][item][item + '-environment-authentication-token']= null;
            wsDataJSON['environment'][item][item + '-environment-certificate']= null;
          }
          if(data_environments[i]['cd_exec_users']){
            wsDataJSON['environment'][item][item + '-environment-deploy-member']= data_environments[i]['cd_exec_users']['user_select'];
            wsDataJSON['environment'][item][item + '-environment-deploy-member-id']= data_environments[i]['cd_exec_users']['user_id'];
          }

          // マニフェストgitリポジトリ情報の設定
          wsDataJSON['environment'][item][item + '-git-service-argo-repository-url']= data_environments[i]['git_repositry']['url'];

          // マニフェストパラメータの設定
          wsDataJSON['environment'][item]['parameter'] =  {};
          for(var fl in data_workspace['ci_config']['environments'][i]['manifests']) {
            var flid = data_workspace['ci_config']['environments'][i]['manifests'][fl]['file_id'];
            wsDataJSON['environment'][item]['parameter'][flid] = {};
            for(var prm in data_workspace['ci_config']['environments'][i]['manifests'][fl]['parameters']) {
              wsDataJSON['environment'][item]['parameter'][flid][item + "-" + flid + '-' + prm] = data_workspace['ci_config']['environments'][i]['manifests'][fl]['parameters'][prm];
            }
          }
        }

        // data_workspaceからwsDataJSONのマニフェストgitリポジトリ情報へ書き出す
        wsDataJSON['git-service-argo'] = {
          'git-service-argo-account-select' : data_workspace['cd_config']['environments_common']['git_repositry']['account_select'],
          'git-service-argo-user' : data_workspace['cd_config']['environments_common']['git_repositry']['account_select'] == "applicationCode"? null : data_workspace['cd_config']['environments_common']['git_repositry']['user'],
          'git-service-argo-token' : data_workspace['cd_config']['environments_common']['git_repositry']['account_select'] == "applicationCode"? null :data_workspace['cd_config']['environments_common']['git_repositry']['token'],
          'git-service-argo-select' : data_workspace['cd_config']['environments_common']['git_repositry']['housing'] == 'inner'? 'epoch': data_workspace['cd_config']['environments_common']['git_repositry']['interface'],
        };

        // Save the update date and time for exclusive control - 排他制御のため更新日時を保存する
        workspace_update_at = data_workspace['update_at'];
        resolve();

      }).fail(function(jqXHR, textStatus, errorThrown) {
        console.log("FAIL : ワークスペース情報取得 jqXHR.status:"+jqXHR.status);
        if(jqXHR.status == 401) {
          reject({"reason": "http-code-401"});
        } else {
          reject();
        }
      });        

    }).then(() => {return new Promise((resolve, reject) => {

      console.log("[CALL] GET " + workspace_api_conf.api.manifestTemplate.get);

      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.manifestTemplate.get.replace('{workspace_id}', workspace_id),
      }).done(function(data) {
        console.log("[DONE] GET " + workspace_api_conf.api.manifestTemplate.get);

        wsDataJSON['manifests'] = [];
        for(var fileidx = 0; fileidx < data['rows'].length; fileidx++ ) {
          wsDataJSON['manifests'][wsDataJSON['manifests'].length] = {
            'file_id':  data['rows'][fileidx]['id'],
            'file_name': data['rows'][fileidx]['file_name'],
            'file_text': data['rows'][fileidx]['file_text'],
            'update_at':  data['rows'][fileidx]['update_at'],
          };
        }

        resolve();

      }).fail(function() {
        console.log("FAIL : テンプレート情報取得");
        // 失敗
        reject();
      });        
    })}).then(() => {
      // Reset the information before the change - 変更前の情報を再設定
      beforeWsData = $.extend( true, {}, wsDataJSON );

      workspaceImageUpdate();
      getClient();

      // CI/CD実行タブを表示
      $('#cicd-tab-item').css('visibility','visible');
      // alert("ワークスペース情報を読み込みました");
      console.log('[DONE] getWorksapce');

    }).catch((info) => {
        // CI/CD実行タブを表示
      $('#cicd-tab-item').css('visibility','hidden');
      // alert("ワークスペース情報を読み込みに失敗しました");
      console.log("catch(info):" + JSON.stringify(info));
      if(info != null) {
        switch(info.reason) {
          case "http-code-401":
            alert("ワークスペースを表示する権限がありません");
            break;
          default:
            alert("ワークスペースを表示できません");
            break;
        }
        window.location = URL_BASE;
      }
      console.log('[FAIL] getWorksapce');
    });
  }

  // TODO:Sprint79 DELETE
  // $('#apply-workspace-button').on('click',apply_workspace);
  function apply_workspace() {
  
    console.log('CALL apply_workspace()');
    console.log('---- wsDataJSON ----');
    console.log(JSON.stringify(wsDataJSON));
  
    // API Body生成
    reqbody = create_api_body();
  
    console.log('---- reqbody ----');
    console.log(JSON.stringify(reqbody));
  
    created_workspace_id = null;
  
    // API呼び出し
    new Promise(function(resolve, reject) {
      // 実行中ダイアログ表示
      $('#modal-progress-container').css('display','flex');
      $('#progress-message-ok').css("display","inline");
      $('#progress-message-ok-cdexec').css("display","none");
      $('#progress-message-ok').prop("disabled", true);
      //
      // ワークスペース情報登録API
      //
      $('#progress_message').html('STEP 1/3 : ワークスペース情報を登録しています');
      $('#error_statement').html('');
      $('#error_detail').html('');
      $('#progress-complete').val('');

      update_mode = "";
      console.log("CALL : ワークスペース情報登録");
      if (workspace_id == null) {
        api_param = {
          "type": "POST",
          "url": workspace_api_conf.api.resource.post,
          "data": JSON.stringify(reqbody),
          contentType: "application/json",
          dataType: "json",
        }
        update_mode = "作成"; 
      } else {
        api_param = {
          "type": "PUT",
          "url": workspace_api_conf.api.resource.put.replace('{workspace_id}', workspace_id),
          "data": JSON.stringify(reqbody),
          contentType: "application/json",
          dataType: "json",
        }
        update_mode = "更新"; 
      }
  
      $.ajax(api_param).done(function(data) {
        console.log("DONE : ワークスペース情報登録");
        console.log("--- data ----");
        console.log(JSON.stringify(data));
        if(workspace_id == null) {
          created_workspace_id = data['rows'][0]['workspace_id'];
          workspace_id = created_workspace_id;
        } else {
          created_workspace_id = workspace_id;
        }
        // 成功
        resolve();
      }).fail((jqXHR, textStatus, errorThrown) => {
        console.log("FAIL : ワークスペース情報登録");
        console.log("RESPONSE:" + jqXHR.responseText);
        // 失敗
        try { reject({"error_statement" : jqXHR.responseJSON.result.errorStatement, "error_detail": jqXHR.responseJSON.result.errorDetail}); } catch { reject(); }
      });
    }).then(() => {
      //
      // ロール最新化のためセッションをリフレッシュ
      //
      return refresh_session();
    }).then(() => { return new Promise((resolve, reject) => {
      //
      //  ワークスペース作成API
      //
      $('#progress_message').html('STEP 2/3 : ワークスペースを' + update_mode + 'しています');
      console.log("CALL : ワークスペース作成");
  
      $.ajax({
        type:"POST",
        url: workspace_api_conf.api.workspace.post.replace('{workspace_id}', workspace_id),
        // data:JSON.stringify(reqbody),
        contentType: "application/json",
        dataType: "json",
      }).done((data) => {
        console.log("DONE : ワークスペース作成");
        console.log("--- data ----");
        console.log(JSON.stringify(data));
  
        if(data.result == '200') {
          // 成功
          // TEKTON起動まで待つため、WAIT
          setTimeout(function() { resolve(); }, workspace_api_conf.api.workspace.wait);
        } else {
          // 失敗
          reject();
        }
      }).fail((jqXHR, textStatus, errorThrown) => {
        console.log("FAIL : ワークスペース作成");
        console.log("RESPONSE:" + jqXHR.responseText);
        // 失敗
        try { reject({"error_statement" : jqXHR.responseJSON.result.errorStatement, "error_detail": jqXHR.responseJSON.result.errorDetail}); } catch { reject(); }
      });
    })}).then(() => {
      $('#progress_message').html('STEP 3/3 :   パイプラインを' + update_mode + 'しています');
      return Promise.all([
        new Promise((resolve, reject) => {
          // CI pipeline 
          if((new URLSearchParams(window.location.search)).get('workspace_id') != null
          && currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-ci-update".replace('{ws_id}',workspace_id)) == -1) {
            // If you do not have permission to update the CI pipeline, proceed to the next without calling the API
            // CIパイプラインの更新権限が無いときはAPIを呼ばずに次に進む
            resolve();
            return;
          }
          //
          // パイプライン作成API
          //
          console.log("CALL : CIパイプライン設定");
          $.ajax({
            type:"POST",
            url: workspace_api_conf.api.ci_pipeline.post.replace('{workspace_id}', workspace_id),
            // data:JSON.stringify(reqbody),
            contentType: "application/json",
            dataType: "json",
          }).done(function(data) {
            console.log("DONE : CIパイプライン設定");
            console.log("--- data ----");
            console.log(JSON.stringify(data));
      
            if(data.result == '200') {
              // 成功
              resolve();
            } else {
              // 失敗
              reject();
            }
          }).fail((jqXHR, textStatus, errorThrown) => {
            console.log("FAIL : CIパイプライン設定");
            console.log("RESPONSE:" + jqXHR.responseText);
            // 失敗
            try { reject({"error_statement" : jqXHR.responseJSON.errorStatement, "error_detail": jqXHR.responseJSON.errorDetail}); } catch { reject(); }
          });
        }),
        new Promise((resolve, reject) => {
          // CD pipeline
          if((new URLSearchParams(window.location.search)).get('workspace_id') != null
          && currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-cd-update".replace('{ws_id}',workspace_id)) == -1) {
            // If you do not have permission to update the CD pipeline, proceed to the next without calling the API
            // CDパイプラインの更新権限が無いときはAPIを呼ばずに次に進む
            resolve();
            return;
          }
          //
          // CDパイプライン設定API
          //
          console.log("CALL : CDパイプライン設定");
          $.ajax({
            type:"POST",
            url: workspace_api_conf.api.cd_pipeline.post.replace('{workspace_id}', workspace_id),
            // data:JSON.stringify(reqbody),
            contentType: "application/json",
            dataType: "json",
          }).done(function(data) {
            console.log("DONE : CDパイプライン設定");
            console.log("--- data ----");
            console.log(JSON.stringify(data));
            if(data.result == '200') {
              // 成功
              resolve();
            } else {
              // 失敗
              try { reject({"error_statement" : data.errorStatement, "error_detail": data.errorDetail}); } catch { reject(); }
            }
          }).fail((jqXHR, textStatus, errorThrown) => {
            console.log("FAIL : CDパイプライン設定");
            console.log("RESPONSE:" + jqXHR.responseText);
            // 失敗
            try { reject({"error_statement" : jqXHR.responseJSON.errorStatement, "error_detail": jqXHR.responseJSON.errorDetail}); } catch { reject(); }
          });
        }),
      ])
    }).then(() => {
      // 実行中ダイアログ表示
      $('#progress-complete').val('1');
      $('#progress_message').html('【COMPLETE】 ワークスペースを' + update_mode + 'しました（ワークスペースID:'+created_workspace_id+'）');
      $('#progress-message-ok').prop("disabled", false);
      // CI/CD実行タブを表示
      $('#cicd-tab-item').css('visibility','visible');
      $('#apply-workspace-button').html('ワークスペース更新');
      getClient();
      console.log('[DONE] apply_workspace');
    }).catch((errorinfo) => {
      // 実行中ダイアログ表示
      $('#progress-complete').val('-1');

      if(workspace_id == null) {
        $('#progress_message').html('【ERROR】 ワークスペースの' + update_mode + 'に失敗しました');
      } else {
        $('#progress_message').html('【ERROR】 ワークスペースの' + update_mode + 'に失敗しました（ワークスペースID:'+created_workspace_id+'）');
      }
      try {
        if(errorinfo.error_statement) {
          $('#error_statement').html('<br><hr>ERROR情報<br>　' + errorinfo.error_statement);
        } else {
          $('#error_statement').html('');
        }
      } catch {
        $('#error_statement').html('');
      }
      try {
        if(errorinfo.error_detail) {
          $('#error_detail').html('　' + errorinfo.error_detail);
        } else {
          $('#error_detail').html('　上記の処理でエラーが発生しました');
        }
      } catch {
        $('#error_detail').html('');
      }

      $('#progress-message-ok').prop("disabled", false);
      console.log('[FAIL] apply_workspace');
    });
  }

  function getClient() {
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.client.get.replace('{client_id}', workspace_api_conf.api.client.client_id.ita.replace("{workspace_id}",workspace_id))
      }).done(function(data) {
        workspace_client_urls.ita = workspace_api_conf.links.ita.replace("{baseurl}", data["baseUrl"]);
        console.log("Done:getClient ita");
      }).fail(function() {
        console.log("FAIL:getClient ita");
      });

      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.client.get.replace('{client_id}', workspace_api_conf.api.client.client_id.sonarqube.replace("{workspace_id}",workspace_id))
      }).done(function(data) {
        workspace_client_urls.sonarqube = workspace_api_conf.links.sonarqube.replace("{baseurl}", data["baseUrl"]);
        console.log("Done:getClient sonarqube");
      }).fail(function() {
        console.log("FAIL:getClient sonarqube");
      });
  }

  function create_api_body() {
    var date = new Date();

    reqbody = {
      'update_at':   workspace_update_at
    };
  
    // 新IFの設定

    // manifestパラメータの項目名
    reqbody['parameter-info'] = wsDataJSON['parameter-info'];

    // パラメータ設定 -  共通
    reqbody['common'] = {
      "name"  :   (wsDataJSON['workspace']['workspace-name']? wsDataJSON['workspace']['workspace-name'] : ""),
      "note"  :   (wsDataJSON['workspace']['workspace-note']? wsDataJSON['workspace']['workspace-note'] : ""),
      "organization_id"  : 1,
      "owners"  :  [],
    };
  
    // パラメータ設定 - CI環境設定
    reqbody['ci_config'] = {};
  
    reqbody['ci_config']['pipelines_common'] = {};
    reqbody['ci_config']['pipelines_common']['git_repositry'] = {
      'housing' :   (wsDataJSON['git-service']['git-service-select']=='epoch'? 'inner': 'outer'),
      'interface' : (wsDataJSON['git-service']['git-service-select']=='epoch'? 'gitlab': wsDataJSON['git-service']['git-service-select']),
      'user' :      (wsDataJSON['git-service']['git-service-user']? wsDataJSON['git-service']['git-service-user']: ""),
      'password' :  (wsDataJSON['git-service']['git-service-token']? wsDataJSON['git-service']['git-service-token']: ""),
      'token' :     (wsDataJSON['git-service']['git-service-token']? wsDataJSON['git-service']['git-service-token']: ""),
    };
    reqbody['ci_config']['pipelines_common']['container_registry'] = {
      'housing' :   (wsDataJSON['registry-service']['registry-service-select']=='epoch'? 'inner': 'outer'),
      'interface' : (wsDataJSON['registry-service']['registry-service-select']=='epoch'? 'docker-registry': wsDataJSON['registry-service']['registry-service-select']),
      'user' :      (wsDataJSON['registry-service']['registry-service-account-user']? wsDataJSON['registry-service']['registry-service-account-user']: ""),
      'password' :  (wsDataJSON['registry-service']['registry-service-account-password']? wsDataJSON['registry-service']['registry-service-account-password']: ""),
    };
  
    reqbody['ci_config']['pipelines'] = [];
    for(var i in wsDataJSON['application-code']) {
      // TEST-CODE
      let unit_test_params = null;
      switch((wsDataJSON['application-code'][i][i+'-git-repository-url']).replace(/^.*\//,"")) {
        case "pytest-sample01.git":
          unit_test_params = {
            "enable" : "true",
            'image' :        "python:3",
            'command' :      "./unittest.epoch.sh",
            'directory' :    "/app",
            'params' : {
              'DB_HOST' :  "pytest-postgres.default.svc",
              'DB_PORT' :  "5432",
              'DB_NAME' :  "pytest",
              'DB_USER' :  "testuser",
              'DB_PASSWORD' :  "test"
            }
          };
          break;
        case "carts.git":
          unit_test_params = {
            "enable" : "true",
            'image' :  "maven:3.6-jdk-8",
            'command' : "./unittest.epoch.sh",
            'directory' : "/usr/src/mymaven",
            'params' : { }
          };
          break;
        default:
          unit_test_params = {
            "enable" : "false"
          };
      }
      // TEST-CODE

      reqbody['ci_config']['pipelines'][reqbody['ci_config']['pipelines'].length] = {
        'pipeline_id'   :  i,
        'git_repositry' :  {
          'url' :             (wsDataJSON['application-code'][i][i+'-git-repository-url']? wsDataJSON['application-code'][i][i+'-git-repository-url'] : ""),
        },
        'webhooks_url'   :  "https://" + location.hostname,
        'build' : {
          'branch' :          (wsDataJSON['application-code'][i][i+'-pipeline-tekton-branch']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-branch'].split(','): []),
          'dockerfile_path' : (wsDataJSON['application-code'][i][i+'-pipeline-tekton-docker-path']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-docker-path'] : ""),
        },
        'container_registry' : {
          'image' :           (wsDataJSON['application-code'][i][i+'-registry-service-output-destination']? wsDataJSON['application-code'][i][i+'-registry-service-output-destination'] : ""),
        },
        'static_analysis' : {
          'interface' :       (wsDataJSON['application-code'][i][i+'-pipeline-tekton-static-analysis']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-static-analysis'] : ""),
        },
        'unit_test' : unit_test_params
      }
    }

    // パラメータ設定 - マニフェスト
    reqbody['ci_config']['environments'] = [];
    var envidx = 0;
    for(var env in wsDataJSON['environment']) {
      var prmenv = {
        'environment_id'    : env,
        'manifests'         : [],
      }
      for(var flidx in wsDataJSON['manifests']) {
        flid = ("" + wsDataJSON['manifests'][flidx]['file_id']);
        var prmmani = {
          'file_id'         : flid,
          'file'            : wsDataJSON['manifests'][flidx]['file_name'],
          'parameters'      : {},
        };
        if(wsDataJSON['environment'][env]['parameter']) {
          // マニフェストパラメータの指定をしている時、パラメータを設定する
          // 環境を追加してパラメータ指定を行わない時は上記if文でスキップする
          for(var prm in wsDataJSON['environment'][env]['parameter'][flid]) {
            var prmname = prm.replace(new RegExp('^'+env+'-'+flid+'-'),'');
            prmmani['parameters'][prmname] = wsDataJSON['environment'][env]['parameter'][flid][prm];
          }
        }
        prmenv['manifests'][prmenv['manifests'].length] = prmmani;
      }
      // file_id順に並び変える
      prmenv['manifests'].sort( function( a, b ){
        var r = 0;
        if( Number(a.file_id) < Number(b.file_id) ){ r = -1; }
        else if( Number(a.file_id) > Number(b.file_id) ){ r = 1; }
    
        return r;
      } );

      reqbody['ci_config']['environments'][reqbody['ci_config']['environments'].length] = prmenv;
      envidx++;
    }

    // パラメータ設定 - CD環境設定
    reqbody['cd_config'] = {
      'system_config' : 'one-namespace',
      'environments_common' : {
          'git_repositry' : {
            'account_select' : wsDataJSON['git-service-argo']['git-service-argo-account-select'],
            'housing':    (wsDataJSON['git-service-argo']['git-service-argo-select']=='epoch'? 'inner': 'outer'),
            'interface':  (wsDataJSON['git-service-argo']['git-service-argo-select']=='epoch'? 'gitlab': wsDataJSON['git-service-argo']['git-service-argo-select']),
          }
      },
      'environments' : [],
    }
    if(wsDataJSON['git-service-argo']['git-service-argo-account-select'] == "applicationCode") {
      reqbody['cd_config'].environments_common.git_repositry.user = wsDataJSON['git-service']['git-service-user'];
      reqbody['cd_config'].environments_common.git_repositry.password = wsDataJSON['git-service']['git-service-token'];
      reqbody['cd_config'].environments_common.git_repositry.token = wsDataJSON['git-service']['git-service-token'];
    } else {
      reqbody['cd_config'].environments_common.git_repositry.user = wsDataJSON['git-service-argo']['git-service-argo-user'];
      reqbody['cd_config'].environments_common.git_repositry.password = wsDataJSON['git-service-argo']['git-service-argo-token'];
      reqbody['cd_config'].environments_common.git_repositry.token = wsDataJSON['git-service-argo']['git-service-argo-token'];
    }

    for(var i in wsDataJSON['environment']) {
      var envitem = {
        'environment_id'  :     i,
        'name' :                (wsDataJSON['environment'][i][i + '-environment-name']? wsDataJSON['environment'][i][i + '-environment-name']: "" ),
        'git_repositry' : {
          'url'           : wsDataJSON['environment'][i][i + '-git-service-argo-repository-url'],
        },
        'deploy_destination' : {
          'cluster_kind' : (wsDataJSON['environment'][i][i + '-environment-deploy-select']? wsDataJSON['environment'][i][i + '-environment-deploy-select']: "internal" ),
          'namespace' :             (wsDataJSON['environment'][i][i + '-environment-namespace']? wsDataJSON['environment'][i][i + '-environment-namespace']: "" ),
          'authentication_token' :  (wsDataJSON['environment'][i][i + '-environment-authentication-token']? wsDataJSON['environment'][i][i + '-environment-authentication-token']: "" ),
          'base64_encoded_certificate' :  (wsDataJSON['environment'][i][i + '-environment-certificate']? wsDataJSON['environment'][i][i + '-environment-certificate']: "" ),
        },
        'cd_exec_users' : {
          'user_select' : wsDataJSON['environment'][i][i + '-environment-deploy-member'],
          'user_id' : wsDataJSON['environment'][i][i + '-environment-deploy-member-id']
        }
      }
      if( envitem['deploy_destination']['cluster_kind'] == "internal" ) {
        // 内部Clusterの場合
        envitem['deploy_destination']['cluster_url'] = "https://kubernetes.default.svc";
      } else {
        // 外部Clusterの場合
        envitem['deploy_destination']['cluster_url'] = (wsDataJSON['environment'][i][i + '-environment-url']? wsDataJSON['environment'][i][i + '-environment-url']: "" );
      }

      reqbody['cd_config']['environments'][reqbody['cd_config']['environments'].length] = envitem;
    }
    return reqbody;
  }

  function apply_manifest() {
    var date = new Date();
  
    console.log('CALL apply_manifest()');
    console.log('---- wsDataJSON ----');
    console.log(JSON.stringify(wsDataJSON));
  
    // API Body生成
    reqbody = create_api_body();
  
    console.log('---- reqbody ----');
    console.log(JSON.stringify(reqbody));
  
    // API呼び出し
    new Promise(function(resolve, reject) {
      // 実行中ダイアログ表示
      // $('#modal-progress-container').css('display','flex');
      $('#progress-message-ok').css("display","inline");
      $('#progress-message-ok-cdexec').css("display","none");
      $('#progress-message-ok').prop("disabled", true);

      //
      // マニフェストパラメータ設定API
      //
      console.log("CALL : マニフェストパラメータ設定");

      $.ajax({
        type:"POST",
        url: workspace_api_conf.api.manifestParameter.post.replace('{workspace_id}', workspace_id),
        data:JSON.stringify(reqbody),
        contentType: "application/json",
        dataType: "json",
      }).done(function(data) {
        console.log("DONE : マニフェストパラメータ設定");
        console.log("--- data ----");
        console.log(JSON.stringify(data));
        if(data.result == '200') {
          // 成功
          resolve();
        } else {
          // 失敗
          reject();
        }
      }).fail(function() {
        console.log("FAIL : マニフェストパラメータ設定");
        // 失敗
        reject();
      });

    }).then(() => {

      console.log('Complete !!');

    }).catch(() => {
      // 実行中ダイアログ表示
      $('#modal-progress-container').css('display','flex');
      $('#progress_message').html('ERROR :  マニフェストパラメータの設定に失敗しました');
  
      $('#progress-message-ok').prop("disabled", false);
      console.log('Fail !!');
    });
  }

  //
  // 処理中メッセージBOXのOKボタン
  //
  $('#progress-message-ok').on('click',() => {
    $('#modal-progress-container').css('display','none');
    if((new URLSearchParams(window.location.search)).get('workspace_id') == null && workspace_id != null) {
      // 新規で登録後は、locationにworkspace_idを付与するため、workspace_idを付けて再描画
      window.location = window.location + "?workspace_id=" + workspace_id;
    } else if((new URLSearchParams(window.location.search)).get('workspace_id') != null) {
      // Reload to update the update date and time - 更新日時をアップデートするため再読込する
      window.location.reload();      
    }
  });
  //
  // 処理中メッセージBOXのOKボタン(CD実行用)
  //
  $('#progress-message-ok-cdexec').on('click',() => {
    $('#modal-progress-container').css('display','none');
    modal.close();
  });

  /* ---------------- *\
  |  ci result polling
  \* ---------------- */
  const ci_result_polling = function() {

    let ci_result_call = false;
    try {
      if(workspace_id != null
      && currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ci-pipeline-result".replace('{ws_id}',workspace_id)) != -1 ) {
        ci_result_call = true;
      }
    } catch(e) { }

    if(!ci_result_call) {
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.ciResult.nop.get
      }).always(function(result) {
        setTimeout(ci_result_polling, ci_result_polling_span);
      });
    } else {
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.ciResult.pipelinerun.get.replace('{workspace_id}', workspace_id),
        "data": {'latest': "True"}
      }).done(function(response) {
        var current_pipelineruns = response.rows;
        var visibility = "hidden";
        for(let i = 0; i < current_pipelineruns.length; i++) {
          if(['Pending', 'Running'].includes(current_pipelineruns[i].status)) {
            visibility = "visible";
            break;
          }
        }
        $('#pipelineTektonCheckArea').css("visibility", visibility);
      }).fail(function(error) {
        console.log("FAIL : get pipelinerun");

      }).always(function(result) {

        setTimeout(ci_result_polling, ci_result_polling_span);
      });
    }
  }

  /* ---------------- *\
  |  it-automation result polling
  \* ---------------- */
  const ita_result_polling = function() {

    let ita_result_call = false;
    try {
      if(workspace_id != null
      && currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute-result".replace('{ws_id}',workspace_id)) != -1 ) {
        ita_result_call = true;
      }
    } catch(e) { }

    if(!ita_result_call) {
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.cd_pipeline.nop.get
      }).always(function(result) {
        setTimeout(ita_result_polling, ita_result_polling_span);
      });
    } else {
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.cd_pipeline.ita.get.replace('{workspace_id}', workspace_id),
        "data": {'processing': "True"}
      }).done(function(response) {
        var cdresult = response.rows;
        console.log("DONE : cdresult");
        console.log("--- data ----");
        console.log(JSON.stringify(cdresult));
        var visibility = "hidden";
        for(let i = 0; i < cdresult.length; i++) {
          if(['ITA-Execute'].includes(cdresult[i].cd_status)) {
            visibility = "visible"
            break;
          }
        }
        $('#exastroItAutomationResultCheckArea').css("visibility", visibility);
      }).fail(function(error) {
        console.log("FAIL : get ita result");

      }).always(function(result) {
        setTimeout(ita_result_polling, ita_result_polling_span);
      });
    }
  }

  /* ---------------- *\
  |  argocd result polling
  \* ---------------- */
  const argocd_result_polling = function() {

    let argocd_result_call = false;
    try {
      if(workspace_id != null
      && currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute-result".replace('{ws_id}',workspace_id)) != -1 ) {
        argocd_result_call = true;
      }
    } catch(e) { }

    if(!argocd_result_call) {
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.cd_pipeline.nop.get
      }).always(function(result) {
        setTimeout(argocd_result_polling, argocd_result_polling_span);
      });
    } else {
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.cd_pipeline.argocd.get.replace('{workspace_id}', workspace_id),
        "data": {'processing': "True"}
      }).done(function(response) {
        var cdresult = response.rows;
        console.log("DONE : cdresult");
        console.log("--- data ----");
        console.log(JSON.stringify(cdresult));
        var visibility = "hidden";
        for(let i = 0; i < cdresult.length; i++) {
          if(['ArgoCD-Sync', 'ArgoCD-Processing'].includes(cdresult[i].cd_status)) {
            visibility = "visible"
            break;
          }
        }
        $('#arogCdResultCheckArea').css("visibility", visibility);
      }).fail(function(error) {
        console.log("FAIL : get argocd result");

      }).always(function(result) {

        setTimeout(argocd_result_polling, argocd_result_polling_span);
      });
    }
  }

  // window onloadイベント
  $(document).ready(function(){ ci_result_polling();argocd_result_polling(); ita_result_polling();});

  // Button control by role - ロールによるボタン制御
  function show_buttons_by_role() {

    let ws_id = (new URLSearchParams(window.location.search)).get('workspace_id');
    if(ws_id == null) {
      //
      // When in a new workspace - 新規ワークスペースのとき
      //

      // Show all buttons - 全てのボタンを表示する
      $('.workspace-footer-menu-button[data-button="update"]').css("display","");
      $('.workspace-footer-menu-button[data-button="reset"]').css("display","");
      $('.workspace-footer-menu-button[data-button="cdExecution"]').css("display","");

      $('#gitServiceCheckButton').css("display","");
      $('#pipelineTektonCheckButton').css("display","");
      // $('#pipelineTektonCheckArea').css("visibility","hidden");
      $('#registryServiceCheckButton').css("display","");
      $('#cdExecutionButtonArea').css("display","");
      $('#exastroItAutomationResultCheckButton').css("display","");
      $('#gitServiceArgoCheckButton').css("display","");
      $('#arogCdResultCheckButton').css("display","");

    } else {
      //
      // For existing workspaces - 既存のワークスペースのとき
      //

      // Waiting for API data acquisition - APIのデータ取得待ち
      if(currentUser == null) { setTimeout(show_buttons_by_role, 100); return; }
      if(!currentUser.data)   { setTimeout(show_buttons_by_role, 100); return; }

      // Set the footer button - フッタのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-name-update".replace('{ws_id}',ws_id)) != -1
      || currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-ci-update".replace('{ws_id}',ws_id)) != -1
      || currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-cd-update".replace('{ws_id}',ws_id)) != -1) {
        $('.workspace-footer-menu-button[data-button="update"]').css("display","");
        $('.workspace-footer-menu-button[data-button="reset"]').css("display","");
      }
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute".replace('{ws_id}',ws_id)) != -1) {
        $('.workspace-footer-menu-button[data-button="cdExecution"]').css("display","");
      }

      // Set the buttons for the workspace name modal dialog - ワークスペース名モーダルダイアログのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-name-update".replace('{ws_id}',ws_id)) == -1) {
        delete wsModalJSON.workspace.footer.ok;
      }

      // Set buttons for application code repository modal dialog - アプリケーションコードリポジトリモーダルダイアログのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-ci-update".replace('{ws_id}',ws_id)) == -1) {
        delete wsModalJSON.gitService.footer.ok;
      }

      // Set buttons for TEKTON modal dialog - TEKTONモーダルダイアログのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-ci-update".replace('{ws_id}',ws_id)) == -1) {
        delete wsModalJSON.pipelineTekton.footer.ok;
      }
      
      // Set buttons for registry service modal dialog - レジストリサービスモーダルダイアログのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-ci-update".replace('{ws_id}',ws_id)) == -1) {
        delete wsModalJSON.registryService.footer.ok;
      }

      // Set buttons for ArgoCD modal dialog - ArgoCDモーダルダイアログのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-cd-update".replace('{ws_id}',ws_id)) == -1) {
        delete wsModalJSON.pipelineArgo.footer.ok;
      }

      // Set the Deploy permission item for the ArgoCD modal dialog - ArgoCDモーダルダイアログのDeploy権限項目を設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-cd-update".replace('{ws_id}',ws_id)) == -1
      || currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-member-role-update".replace('{ws_id}',ws_id)) == -1) {
        // Hide the "Deploy permission" item for permissions other than role update + workspace cd update
        // ロール変更＋ワークスペース更新 (CD)以外の権限では「Deploy権限」項目を非表示にする
        delete wsModalJSON.pipelineArgo.block.environmentList.tab.item.environmentDeployMember;
      }
      
      // Set buttons for IaC repository modal dialog - IaCリポジトリモーダルダイアログのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ws-cd-update".replace('{ws_id}',ws_id)) == -1) {
        delete wsModalJSON.gitServiceArgo.footer.ok;
      }

      // Set the execution confirmation button of the application repository
      // アプリケーションリポジトリの実行確認のボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ci-pipeline-result".replace('{ws_id}',ws_id)) != -1) {
        $('#gitServiceCheckButton').css("display","");
      }

      // Set the TEKTON execution confirmation button
      // TEKTONの実行確認のボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ci-pipeline-result".replace('{ws_id}',ws_id)) != -1) {
        $('#pipelineTektonCheckButton').css("display","");
        // $('#pipelineTektonCheckArea').css("visibility","visible");
      }

      // Set the registry service execution confirmation button
      // レジストリサービスの実行確認のボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-ci-pipeline-result".replace('{ws_id}',ws_id)) != -1) {
        $('#registryServiceCheckButton').css("display","");
      }

      // Set the button to run the CD - CD実行のボタンを設定する
      // if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute".replace('{ws_id}',ws_id)) != -1) {
      //   $('#cdExecutionButtonArea').css("display","");
      // }
      
      // Set the manifest upload button - マニフェストアップロードのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-manifest-upload".replace('{ws_id}',ws_id)) != -1) {
        $('#ManifestTemplateButtonArea').css("display","");
      }

      // Set the manifest parameter button - マニフェストパラメータのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-manifest-setting".replace('{ws_id}',ws_id)) == -1) {
        delete wsModalJSON.manifestParametar.footer.ok;
      }

      // Set the IT-Automation button - IT-Automationのボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute-result".replace('{ws_id}',ws_id)) != -1) {
        $('#exastroItAutomationResultCheckButton').css("display","");
      }

      // Set the IaC repository confirmation button - IaCリポジトリ確認のボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute-result".replace('{ws_id}',ws_id)) != -1) {
        $('#gitServiceArgoCheckButton').css("display","");
      }

      // Set the Argo CD confirmation button - ArgoCD確認のボタンを設定する
      if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-cd-execute-result".replace('{ws_id}',ws_id)) != -1) {
        $('#arogCdResultCheckButton').css("display","");
      }
    }
  }
  $(document).ready(function(){ show_buttons_by_role(); });
}

$(function(){
  if((new URLSearchParams(window.location.search)).get('workspace_id')==null) {
    // Display when new workspace - 新規ワークスペースの時の表示
    workspace('setting', 'new');
    $(".topic-path-current").text("新規");
    $('#cicd-tab-item').css('visibility','hidden');
  } else {
    // Display when registered workspace - 登録済みワークスペースの時の表示
    workspace('setting', 'update');
    $(".topic-path-current").text("詳細");
  }
});
