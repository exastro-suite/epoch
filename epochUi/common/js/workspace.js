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

$(function(){

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   JSON
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const wsDataJSON = {
  'workspace': {
  },
  'environment' : {
  },
  'application-code': {
  },
  /*
  'template-file': {
    'file001': {
      'name': 'text1text1text1text1text1text1text1text1.yaml',
      'path': 'exsample/text1.yaml',
      'date': '2021/05/12 09:00:00',
      'user': 'administratoradministratoradministratoradministrator',
      'note': '<a>test1</a>'
    },
    'file002': {
      'name': 'text2.yaml',
      'path': 'exsample/text2.yaml',
      'date': '2021/05/12 09:00:00',
      'user': 'administrator',
      'note': '<a>test2</a>memomemomemomemomemomemomemomemomemomemomemomemomemomemomemo'
    }
  },
  */
  /*
  'template-file': {
    'file001': {
      'name': 'front-end.yaml',
      'path': 'exsample/front-end.yaml',
      'date': '2021/05/12 09:00:00',
      'user': 'administratoradministratoradministratoradministrator',
      'note': '<a>test1</a>'
    },
    'file002': {
      'name': 'catalogue.yaml',
      'path': 'exsample/catalogue.yaml',
      'date': '2021/05/12 09:00:00',
      'user': 'administrator',
      'note': '<a>test2</a>memomemomemomemomemomemomemomemomemomemomemomemomemomemomemo'
    }
  },
  */
  'template-file': {},
  'git-service': {
    'git-service-select': 'epoch'
  },
  'registry-service': {
    'registry-service-select': 'epoch'
  },
  'git-service-argo': {
    'git-service-argo-select': 'epoch'
  },
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
     Gitサービス
  \* -------------------------------------------------- */
  'gitService': {
    'id': 'git-service',
    'title': 'Gitサービス',
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
            'title': 'Gitリポジトリ(ソース)　ユーザ名',
            'name': 'git-service-user',
            'placeholder': 'Gitリポジトリ(ソース)　ユーザ名を入力してください'
          },
          'gitServiceAccountPassword': {
            'type': 'password',
            'title': 'Gitリポジトリ(ソース)　パスワード',
            'name': 'git-service-password',
            'placeholder': 'Gitリポジトリ(ソース)　パスワードを入力してください'
          },
          'gitServiceAccountToken': {
            'type': 'password',
            'title': 'Gitリポジトリ(ソース)　トークン',
            'name': 'git-service-token',
            'placeholder': 'Gitリポジトリ(ソース)　トークンを入力してください'
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
              'title': 'Gitリポジトリ(ソース)　URL',
              'name': 'git-repository-url',
              'class': 'tab-name-link',
              'regexp': '^https:\/\/github.com\/[^\/]+\/([^\/]+).git$',
              'placeholder': 'Gitリポジトリ(ソース)　URLを入力してください'
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
              'title': 'Gitリポジトリ(ソース)　URL',
              'target': 'git-repository-url'
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
              'title': 'Gitリポジトリ(ソース)　URL',
              'target': 'git-repository-url'
            },
            'pipelineTektonBranch': {
              'type': 'input',
              'title': 'ビルド　ブランチ',
              'name': 'pipeline-tekton-branch',
              'placeholder': 'ビルド　ブランチを入力してください'
            },
            'pipelineTektonContextPath': {
              'type': 'input',
              'title': 'ビルド　コンテキストパス',
              'name': 'pipeline-tekton-context-path',
              'placeholder': 'ビルド　コンテキストパスを入力してください'
            },
            'pipelineTektonDockerPath': {
              'type': 'input',
              'title': 'ビルド　Dockerファイルパス',
              'name': 'pipeline-tekton-docker-path',
              'placeholder': 'ビルド　Dockerファイルパスを入力してください'
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
      'registryServiceOutput': {
        'title': 'パラメータ入力',
        'tab': {
          'type': 'reference',
          'target': {
            'key1': 'template-file',
            'key2': 'name'
          },
          'emptyText': 'テンプレートファイルの登録がありません。Kubernetes Manifestテンプレートの設定からテンプレートファイルを追加してください。',
          'deletConfirmText': '',
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
          'item': {
            'environmentName': {
              'type': 'input',
              'title': '環境名',
              'name': 'environment-name',
              'class': 'tab-name-link',
              'regexp': '^(.+)$',
              'placeholder': '環境名を入力してください'
            },
            'environmentURL': {
              'type': 'input',
              'title': 'Kubernetes API Serer URL',
              'name': 'environment-url',
              'placeholder': '実行環境のKubernetes API Serer URLを入力してください'
            },
            'environmentNamespace': {
              'type': 'input',
              'title': 'Namespace',
              'name': 'environment-namespace',
              'placeholder': '実行環境のNamespaceを入力してください'
            },
            'environmentToken': {
              'type': 'input',
              'title': 'Authentication token',
              'name': 'environment-authentication-token',
              'placeholder': '実行環境のAuthentication tokenを入力してください'
            },
            'environmentCertificate': {
              'type': 'input',
              'title': 'Base64 encoded certificate',
              'name': 'environment-certificate',
              'placeholder': '実行環境のBase64 encoded certificateを入力してください'
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Argo CD Gitサービス
  \* -------------------------------------------------- */
  'gitServiceArgo': {
    'id': 'git-service-argo',
    'title': 'Argo CD Gitサービス',
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
          'gitServiceArgoAccountUser': {
            'type': 'input',
            'title': 'Gitリポジトリ(ソース)　ユーザ名',
            'name': 'git-service-argo-user',
            'placeholder': 'Gitリポジトリ(ソース)　ユーザ名を入力してください'
          },
          'gitServiceArgoAccountPassword': {
            'type': 'password',
            'title': 'Gitリポジトリ(ソース)　パスワード',
            'name': 'git-service-argo-password',
            'placeholder': 'Gitリポジトリ(ソース)　パスワードを入力してください'
          },
          'gitServiceArgoAccountToken': {
            'type': 'password',
            'title': 'Gitリポジトリ(ソース)　トークン',
            'name': 'git-service-argo-token',
            'placeholder': 'Gitリポジトリ(ソース)　トークンを入力してください'
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
          'deletConfirmText': '',
          'item' : {
            'gitServiceArgoRepositorySource': {
              'type': 'input',
              'title': 'Gitリポジトリ(ソース)　URL',
              'name': 'git-service-argo-repository-url',
              'class': 'tab-name-link',
              'regexp': '^https:\/\/github.com\/[^\/]+\/([^\/]+).git$',
              'placeholder': 'Gitリポジトリ(ソース)　URLを入力してください'
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     CD実行指定
  \* -------------------------------------------------- */
  'cdRunning': {
    'id': 'cd-running',
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
      'executionCondition': {
        'title': '実行条件',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'execution-condition'            
          }
        }
      },
      'manifestParameter': {
        'title': 'Manifestパラメータ',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'manifest-parameter'            
          }
        }
      },
      'argoCdPipeline': {
        'title': 'ArgoCDパイプライン',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'argo-cd-pipeline'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     TEKTON Gitサービス確認
  \* -------------------------------------------------- */
  'gitServiceCheck': {
    'id': 'git-service-check',
    'title': 'Gitサービス',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'commitList': {
        'title': 'Commit一覧',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'commit-list'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     TEKTON確認
  \* -------------------------------------------------- */
  'pipelineTektonCheck': {
    'id': 'pipeline-tekton-check',
    'title': 'TEKTON',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'imageList': {
        'title': '実行状況',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'image-list'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     レジストリサービス確認
  \* -------------------------------------------------- */
  'registryServiceCheck': {
    'id': 'registry-service-check',
    'title': 'レジストリサービス',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'imageList': {
        'title': 'イメージ一覧',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'image-list'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Exastro IT Automation 実行結果一覧
  \* -------------------------------------------------- */
  'exastroItAutomationResultCheck': {
    'id': 'exastro-it-automation-result-check',
    'title': 'Exastro IT Automation 実行結果一覧',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'resultList': {
        'title': '実行結果一覧',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'result-list'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Exastro IT Automation 実行状況確認
  \* -------------------------------------------------- */
  'exastroItAutomationStatusCheck': {
    'id': 'exastro-it-automation-status-check',
    'title': 'Exastro IT Automation 実行状況確認',
    'footer': {
      'cancel': {
        'text': '実行結果一覧に戻る',
        'type': 'negative'
      }
    },
    'block': {
      'statusList': {
        'title': '実行状況確認',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'status-list'            
          }
        }
      },
      'manifestParameter': {
        'title': 'Manifestパラメータ',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'manifest-parameter'            
          }
        }
      },
      'progressLog': {
        'title': '進行状況ログ',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'progress-log'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Kubernetes Manifest
  \* -------------------------------------------------- */
  'kubernetesManifestCheck': {
    'id': 'kubernetes-manifest-check',
    'title': 'Manifestリポジトリ',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'commitList': {
        'title': 'Commit一覧',
        'tab': {
          'type': 'reference',
          'target': {
            'key1': 'environment',
            'key2': 'text'
          },
          'emptyText': '環境の設定がありません。',
          'item': {
            'commitListBody': {
              'type': 'loading',
              'id': 'commit-list-body'
            }
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     IaC リポジトリ確認
  \* -------------------------------------------------- */
  'gitServiceArgoCheck': {
    'id': 'git-service-argo-check',
    'title': 'IaC リポジトリ',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'commitList': {
        'title': 'リポジトリ一覧',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'commit-list'
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Argo CD 実行結果一覧
  \* -------------------------------------------------- */
  'arogCdResultCheck': {
    'id': 'pipeline-argo-cd-check',
    'title': 'Argo CD',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'resultList': {
        'title': '実行結果一覧',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'result-list'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     Argo CD 実行状況確認
  \* -------------------------------------------------- */
  'arogCdStatusCheck': {
    'id': 'pipeline-argo-cd-check',
    'title': 'Argo CD',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'resultList': {
        'title': '実行状況確認',
        'item': {
          'comitList': {
            'type': 'loading',
            'id': 'status-list'            
          }
        }
      }
    }
  },
  /* -------------------------------------------------- *\
     システム
  \* -------------------------------------------------- */
  'systemCheck': {
    'id': 'system-check',
    'title': 'システム',
    'footer': {
      'cancel': {
        'text': '閉じる',
        'type': 'negative'
      }
    },
    'block': {
      'systemOperationStatus': {
        'title': '稼働状況',
        'tab': {
          'type': 'reference',
          'target': {
            'key1': 'environment',
            'key2': 'text'
          },
          'emptyText': '環境の設定がありません。',
          'item': {
            'systemOperationStatusBody': {
              'type': 'loading',
              'id': 'system-operation-status-body'
            }
          }
        }
      }
    }
  },
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
    const $line5 = newSVG('path');
    $line5.attr({
    'd': order('M',startCI.xc,startCI.t+startCI.h,startCI.xc,mp.yc,mp.l,mp.yc,'l',-a,a,a,-a,-a,-a,a,a),
    'data-type': 'ci'});
    
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

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   モーダル入力内容
// 
////////////////////////////////////////////////////////////////////////////////////////////////////

// モーダル内の入力データを wsDataJSON に入れる
const setInputData = function( $modal, tabTarget, commonTarget ){
  const inputTarget = 'input[type="text"], input[type="password"], input[type="radio"]:checked, textarea';
  
  // タブリストの作成
  $modal.find('.modal-tab-item').each( function(){
    const $tab = $( this ),
          tabID = $tab.attr('data-id'),
          tabText = $tab.text();
    if ( wsDataJSON[ tabTarget ] === undefined ) wsDataJSON[ tabTarget ] = new Object();
    if ( wsDataJSON[ tabTarget ][ tabID ] === undefined ) wsDataJSON[ tabTarget ][ tabID ] = new Object();
    wsDataJSON[ tabTarget ][ tabID ]['text'] = tabText;
  });
  $modal.find( inputTarget ).each( function(){
    const $input = $( this ),
          name = $input.attr('name');
    // タブの中か調べる
    const $tabBlock = $input.closest('.modal-tab-body-block');
    if ( $tabBlock.length ) {
      const tabID = $tabBlock.attr('id');
      if ( wsDataJSON[ tabTarget ] === undefined ) wsDataJSON[ tabTarget ] = new Object();
      if ( wsDataJSON[ tabTarget ][ tabID ] === undefined ) wsDataJSON[ tabTarget ][ tabID ] = new Object();
      wsDataJSON[ tabTarget ][ tabID ][ name ] = $input.val();
    } else {
      if ( wsDataJSON[ commonTarget ] === undefined ) wsDataJSON[ commonTarget ] = new Object();
      wsDataJSON[ commonTarget ][ name ] = $input.val();
    }
  });
};

// 削除されたタブに合わせてデータも削除する
const deleteTabData = function( $modal, target ){
  const deleteData = $modal.attr('data-tab-delete');
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
const setParameterData = function( $modal ){
  const inputTarget = 'input[type="text"], input[type="password"], input[type="radio"]:checked, textarea';
  
  $modal.find( inputTarget ).each( function(){
    const $input = $( this ),
          fileID = $input.attr('data-file'),
          enviromentID =  $input.attr('data-enviroment'),
          name = $input.attr('name'),
          value = $input.val();
    if ( wsDataJSON['environment'] !== undefined ) {
      if ( wsDataJSON['environment'][ enviromentID ] !== undefined ) {
        if ( wsDataJSON['environment'][ enviromentID ]['parameter'] === undefined ) {
          wsDataJSON['environment'][ enviromentID ]['parameter'] = new Object();
        }
        if ( wsDataJSON['environment'][ enviromentID ]['parameter'][ fileID ] === undefined ) {
          wsDataJSON['environment'][ enviromentID ]['parameter'][ fileID ] = new Object();
        }
        wsDataJSON['environment'][ enviromentID ]['parameter'][ fileID ][ name ] = value;
        } else {
        window.console.error( enviromentID + ' not found.');
      }
    }
  });
  
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   テンプレートファイルリスト
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const templateFileList = function(){
  const $fileList = $('#template-file-list-body'),
        fileList = wsDataJSON['template-file'],
        fileLength = Object.keys( fileList ).length;
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
    for ( let key in fileList ) {
      listHtml += ''
      + '<tr class="c-table-row">'
        + '<td class="template-name c-table-col"><div class="c-table-ci">' + fn.textEntities(fileList[key]["name"]) + '</div></td>'
        + '<td class="template-date c-table-col"><div class="c-table-ci">' + fn.textEntities(fileList[key]["date"]) + '</div></td>'
        + '<td class="template-user c-table-col"><div class="c-table-ci">' + fn.textEntities(fileList[key]["user"]) + '</div></td>'
        + '<td class="template-note c-table-col"><div class="c-table-ci">' + fn.textEntities(fileList[key]["note"]) + '</div></td>'
        + '<td class="template-menu c-table-col"><div class="c-table-ci">'
          + '<ul class="c-table-menu-list">'
            + '<li class="c-table-menu-item">'
              + '<button class="c-table-menu-button epoch-popup-m" title="プレビュー" data-key="' + key + '" data-button="preview">'
                + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-preview" /></svg></button></li>'
            + '<li class="c-table-menu-item">'
              + '<button class="c-table-menu-button epoch-popup-m" title="ダウンロード" data-key="' + key + '" data-button="download">'
                + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-download" /></svg></button></li>'
            + '<li class="c-table-menu-item">'
              + '<button class="c-table-menu-button epoch-popup-m" title="備考" data-key="' + key + '" data-button="note">'
                + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-edit" /></svg></button></li>'
            + '<li class="c-table-menu-item">'
              + '<button class="c-table-menu-button epoch-popup-m" title="更新" data-key="' + key + '" data-button="update">'
                + '<svg viewBox="0 0 64 64" class="c-table-menu-svg"><use xlink:href="#icon-update" /></svg></button></li>'
            + '<li class="c-table-menu-item">'
              + '<button class="c-table-menu-button epoch-popup-m" title="削除" data-key="' + key + '" data-button="delete">'
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
        alert( wsDataJSON['template-file'][key]['path'] + 'プレビュー');
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
        alert('削除しますか？');
        break;      
    }
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
            
            // アップロード、再選択ボタン
            $upload.add( $reSelect ).prop('disabled', false ).on('click', function(){
              const $button = $( this ),
                    type = $button.attr('data-button');
              switch( type ) {
                case 'ok': {         
                $button.prop('disabled', true );
                // フォームデータ取得
                const formData = new FormData( $('#template-files').get(0) );
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

                    // 暫定実装 -----
                    wsDataJSON['template-file'] = {};
                    var disp = "";

                    console.log("manifest post response:" + JSON.stringify(data));
                    for(var fileidx = 0; fileidx < data['rows'].length; fileidx++ ) {
                      disp += data['rows'][fileidx]['file_name'] + '\n';
                      wsDataJSON['template-file']['file'+("000"+(fileidx+1)).slice(-3)] = {
                        'name' : data['rows'][fileidx]['file_name'],
                        'path' : 'exsample/' + data['rows'][fileidx]['file_name'],
                        'date' : '2021/05/12 09:00:00',
                        'user' : 'epoch-user',
                        'note' : '<a>' + data['rows'][fileidx]['file_name'] + '</a>',
                        "text" : data['rows'][fileidx]['file_text'],
                      }
                    }
                    // 暫定実装 -----

                    // アップロードが完了したら
                    $file.find('.item-file-list').html('<pre>' + disp + '</pre>');

                    workspaceImageUpdate();
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
//   パラメータ入力
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const inputParameter = function(){  
  
  // タブごとに処理
  $('#manifest-parameter').find('.modal-tab-body-block').each(function(i){
  
    // yamlファイルを読み込む
    //
    // 
    
    // モック用ダミーyamlデータ
/*
    const dummyYaml = '# epoch-template => No.' + i + '\n'
    + 'apiVersion: apps/v1\n'
    + 'kind: Deployment\n'
    + 'metadata:\n'
    + '  name: catalogue\n'
    + '  labels:\n'
    + '    name: catalogue\n'
    + 'spec:\n'
    + '  replicas: {{ replicas_' + i + ' }}\n'
    + '  selector:\n'
    + '    matchLabels:\n'
    + '      name: catalogue\n'
    + '  template:\n'
    + '    metadata:\n'
    + '      labels:\n'
    + '        name: catalogue\n'
    + '    spec:\n'
    + '      containers:\n'
    + '      - name: catalogue\n'
    + '        image: {{ image_' + i + ' }} : {{ image_tag_' + i + ' }}\n'
    + '        ports:\n'
    + '        - containerPort: 8000\n'
    + '      nodeSelector:\n'
    + '        beta.kubernetes.io/os: linux\n'
    + 'spec2:\n'
    + '  replicas: {{ replicas_' + i + ' }}\n'
    + '  selector:\n'
    + '    matchLabels:\n'
    + '      name: catalogue\n'
    + '  template:\n'
    + '    metadata:\n'
    + '      labels:\n'
    + '        name: catalogue\n'
    + '    spec:\n'
    + '      containers:\n'
    + '      - name: catalogue\n'
    + '        image: {{ image_' + i + ' }} : {{ image_tag_' + i + ' }}\n'
    + '        ports:\n'
    + '        - containerPort: 8000\n'
    + '      nodeSelector:\n'
    + '        beta.kubernetes.io/os: linux\n'
    + '---\n'
    + 'apiVersion: v1\n'
    + 'kind: Service\n'
    + 'metadata:\n'
    + '  name: catalogue\n'
    + '  labels:\n'
    + '    name: catalogue\n'
    + 'spec:\n'
    + '  ports:\n'
    + '    # the port that this service should serve on\n'
    + '  - port: 80\n'
    + '    targetPort: 8000\n'
    + '  selector:\n'
    + '    name: catalogue\n';
*/
/*
const dummyYaml = '# epoch-template => No.' + i + '\n'
+ 'apiVersion: apps/v1\n'
+ 'kind: Deployment\n'
+ 'metadata:\n'
+ '  name: front-end\n'
+ '  labels:\n'
+ '    name: front-end\n'
+ 'spec:\n'
+ '  replicas: {{ replicas }}\n'
+ '  selector:\n'
+ '    matchLabels:\n'
+ '      name: front-end\n'
+ '  template:\n'
+ '    metadata:\n'
+ '      labels:\n'
+ '        name: front-end\n'
+ '    spec:\n'
+ '      containers:\n'
+ '      - name: front-end\n'
+ '        image: {{ image }} : {{ image_tag }}\n'
+ '        ports:\n'
+ '        - containerPort: 8000\n'
+ '      nodeSelector:\n'
+ '        beta.kubernetes.io/os: linux\n'
+ '---\n'
+ 'apiVersion: v1\n'
+ 'kind: Service\n'
+ 'metadata:\n'
+ '  name: front-end\n'
+ '  labels:\n'
+ '    name: front-end\n'
+ 'spec:\n'
+ '  ports:\n'
+ '    # the port that this service should serve on\n'
+ '  - port: 80\n'
+ '    targetPort: 8000\n'
+ '  selector:\n'
+ '    name: front-end\n';
*/
    // 暫定実装 -----
    const dummyYaml = wsDataJSON['template-file']['file'+("000"+(i+1)).slice(-3)]['text'];
    // 暫定実装 -----

    // 読み込みが完了したら
    const $tabBlock = $( this ),
          tabID = $tabBlock.attr('id'),
          parameterSpan = '<span class="item-parameter" data-status="unentered" data-value="$2">$1</span>',
          envNumber = Object.keys( wsDataJSON['environment'] ).length;
          
    let $parameter = $(''
    + '<div class="item-parameter-block">'
      + '<div class="item-parameter-code">'
        + '<pre class="item-parameter-pre prettyprint linenums lang-yaml">'
          + dummyYaml.replace(/({{\s(.*?)\s}})/g, parameterSpan )
        + '</pre>'
      + '</div>'
      + '<div class="item-parameter-select">'
      + '</div>'
    + '</div>');
    
    // パラメータリストの作成
    const parameterList = new Object();
    $parameter.find('.item-parameter').each(function(){
      const parameterID = $( this ).attr('data-value');
      // 重複チェック
      if ( parameterList[ parameterID ] === undefined ) {
        parameterList[ parameterID ] = $( this ).text()
      }
    });
    
    let parameterArea = '';
    for ( let key in parameterList ) {
      const parameterID = key,
            $p = $parameter.find('.item-parameter[data-value="' + key + '"]');
      let emptyCount = 0;
      parameterArea += '<div id="' + tabID + '-' + parameterID + '" class="item-parameter-area">'
      + '<div class="item-parameter-name">'
        + parameterList[key]
      + '</div>'
      + '<div class="item-parameter-input-area">';
      
      if ( Object.keys(wsDataJSON.environment).length ) {
        for ( let key in wsDataJSON.environment ) {
          const envName = wsDataJSON.environment[key].text;
          const $input = modal.createInput({
            'title': envName,
            'name': key + '-' + parameterID,
            'placeholder': envName + '用のパラメータを入力してください。'
          }, tabID );
          $input.find('input').attr({
            'data-file': tabID,
            'data-enviroment': key,
            'data-parameter': parameterID
          });
          emptyCount += ( $input.find('.item-text').val() === '')? 1: 0;
          parameterArea += $input.get(0).outerHTML;
        }
      } else {
        parameterArea += '<div class="modal-empty-block">環境の登録がありません。</div>'
      }
    
      parameterArea += '</div></div>';
      
      if ( emptyCount === 0 && envNumber !== 0 ) {
        $p.attr('data-status', 'done');
      } else {
        $p.attr('data-status', 'unentered');
      }
    }
    $parameter.find('.item-parameter-select').html( parameterArea );
    
    // パラメータ切り替え
    $parameter.find('.item-parameter').on('click', function(){
      const $clickParameter = $( this ),
            $parameterArea = $clickParameter.closest('.item-parameter-block'),
            $targetBlock = $('#' + tabID + '-' + $clickParameter.attr('data-value') );
      $parameterArea.find('.parameter-open').removeClass('parameter-open');
      $clickParameter.add( $targetBlock ).addClass('parameter-open');
    });
    
    // 最初のパラメータオープン
    $parameter.find('.item-parameter').eq(0).addClass('parameter-open');
    $parameter.find('.item-parameter-area').eq(0).addClass('parameter-open');
    
    $tabBlock.html( $parameter );
    
    // 入力チェック
    $parameter.find('.item-text').on('blur', function(){
      const $input = $( this ),
            p = $input.attr('data-parameter'),
            $inputArea = $parameter.find('#' + $input.attr('data-file') + '-' + p ),
            $p = $parameter.find('.item-parameter[data-value="' + p + '"]');
      // 未入力の数
      const emptyLength = $inputArea.find('.item-text').filter(function(){
        return ( $( this ).val() === '')
      }).length;
      if ( emptyLength === 0 && envNumber !== 0) {
        $p.attr('data-status', 'done');
      } else {
        $p.attr('data-status', 'unentered');
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
//   IT Automation実行結果一覧
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const itaResultList = function(){
  const $resultList = $('#result-list');
  
  $resultList.html('<button class="running-status">実行状況</button>')
  
  const cancel = function(){
    //const callback = itaResultList;
    modal.change('exastroItAutomationResultCheck', {
      'callback': itaResultList
    });
  };
  
  $resultList.find('.running-status').on('click', function(){
    modal.change('exastroItAutomationStatusCheck', {
      'cancel': cancel,
      'callback': itaStatusList
    });
  });

};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   IT Automation実行状況確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const itaStatusList = function(){
  const $statusList = $('#status-list');
  
  // Conductor画面
  const $itaConductor = $(''
  + '<div class="conductor-area">'
    + '<div class="node conductor-start"><div class="node-main"><div class="node-cap node-in"></div><div class="node-body"><div class="node-circle"><span class="node-gem"><span class="node-gem-inner node-gem-length-1">S</span></span><span class="node-running"></span><span class="node-result" data-result-text="" data-href="#"></span></div><div class="node-type"><span>Conductor</span></div><div class="node-name"><span>Start</span></div></div><div id="terminal-1" class="node-terminal node-out connect-a connected"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div></div><div class="node-note"><div class="node-note-inner"><p></p></div></div></div>'
    + '<div class="node conductor-end"><div class="node-main"><div id="terminal-2" class="node-terminal node-in connected connect-a"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div><div class="node-body"><div class="node-circle"><span class="node-gem"><span class="node-gem-inner node-gem-length-1">E</span></span><span class="node-running"></span><span class="node-result" data-result-text="" data-href="#"></span></div><div class="node-type"><span>Conductor</span></div><div class="node-name"><span>End</span></div></div><div class="node-cap node-out"></div></div><div class="node-note"><div class="node-note-inner"><p></p></div></div></div>'
    + '<div class="node conductor-epoch"><div class="node-main"><div id="terminal-3" class="node-terminal node-in connected connect-a"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div><div class="node-body"><div class="node-circle"><span class="node-gem"><span class="node-gem-inner node-gem-length-1"></span></span><span class="node-running"></span><span class="node-result" data-result-text="" data-href="#"></span></div><div class="node-type"><span>Movement</span></div><div class="node-name"><span>Parameter set</span></div></div><div id="terminal-4" class="node-terminal node-out connect-a connected"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div></div><div class="node-note"><div class="node-note-inner"><p></p></div></div><div class="node-skip"><input class="node-skip-checkbox" tabindex="-1" type="checkbox"><label class="node-skip-label">Skip</label></div><div class="node-operation"><dl class="node-operation-body"><dt class="node-operation-name">OP</dt><dd class="node-operation-data"></dd></dl><div class="node-operation-border"></div></div></div>'
    + '<div class="conductor-line"></div>'
  + '</div>');
  
  setTimeout( function(){ $itaConductor.find('.conductor-start').addClass('running'); }, 1000 );
  setTimeout( function(){ $itaConductor.find('.conductor-epoch').addClass('running'); }, 3000 );
  setTimeout( function(){ $itaConductor.find('.conductor-end').addClass('running'); }, 5000 );
  setTimeout( function(){
    $itaConductor.find('.node').addClass('complete').attr('data-result', '9').find('.node-result').attr('data-result-text', 'DONE');
  }, 7000 );
  
  $statusList.html( $itaConductor )
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Argo CD 実行結果一覧
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const arogCdResultList = function(){
  const $resultList = $('#result-list');
  
  var link = "";
  for(var env in wsDataJSON['environment']) {
    link = wsDataJSON['environment'][env][env + '-git-service-argo-repository-url'];
    break;
  };

  // EPOCH_LINK
  $resultList.html('<a href="' + link + '" target="_blank" text="aaa">' + link + '</a>')
//  $resultList.html('<button class="running-status">実行状況</button>')
  
  $resultList.find('.running-status').on('click', function(){
    modal.change('arogCdStatusCheck', {
      'cancel': function(){
        modal.change('arogCdResultCheck', {
          'callback': arogCdResultList
        });
      },
      'callback': arogCdStatusList
    });
  });

};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Argo CD 実行状況確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const arogCdStatusList = function(){
  const $resultList = $('#result-list');
  
  $resultList.html('<button class="running-status">実行状況</button>')

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
      $('#progress-message-ok').prop("disabled", true);
      //
      // CD実行APIの呼び出し
      //
      $('#progress_message').html('CD実行開始');
            
      // API Body生成
      reqbody = {};

      // 旧形式の付与
      // reqbody['clusterInfo'] = workspace_api_conf['parameter']['clusterInfo'];
      reqbody['operationId'] = workspace_api_conf['parameter']['operationId'];
      reqbody['conductorClassNo'] = workspace_api_conf['parameter']['conductorClassNo'];
      reqbody['preserveDatetime'] = workspace_api_conf['parameter']['preserveDatetime'];
      reqbody['itaInfo'] = workspace_api_conf['parameter']['itaInfo'];

      console.log("CALL : CD実行開始");
      api_param = {
        "type": "POST",
        "url": workspace_api_conf.api.cdExecDesignation.post,
        "data": JSON.stringify(reqbody),
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
      $('#progress-message-ok').prop("disabled", false);
    }).catch(() => {
      // 実行中ダイアログ表示
      $('#progress_message').html('CD実行失敗しました');
      $('#progress-message-ok').prop("disabled", false);
      console.log('Fail !!');
    });
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   モーダルオープン
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
$content.find('.modal-open, .workspace-status-item').on('click', function(){
  const $button = $( this ),
        target = $button.attr('data-button');
  
  let ok, cancel, callback, width = 800;

  // TODO
  console.log('modal target:' + target);

  switch( target ) {
    // Workspace
    case 'workspace': {
      ok = function( $modal ){
        setInputData( $modal, '', 'workspace');
        workspaceImageUpdate();
      };   
      } break;
    // Gitサービス
    case 'gitService': {
      ok = function( $modal ){
        setInputData( $modal, 'application-code', 'git-service');
        deleteTabData( $modal, 'application-code');
        workspaceImageUpdate();
      };   
      } break;
    // レジストリサービス
    case 'registryService': {
      ok = function( $modal ){
        setInputData( $modal, 'application-code', 'registry-service');
        workspaceImageUpdate();
      };      
      } break;
    // Argo CD
    case 'pipelineArgo': {
      ok = function( $modal ){
        setInputData( $modal, 'environment', '');
        deleteTabData( $modal, 'environment');
        workspaceImageUpdate();
      };      
      } break;
    // Tekton
    case 'pipelineTekton': {
      ok = function( $modal ){
        setInputData( $modal, 'application-code', '');
        workspaceImageUpdate();
      };      
      } break;
    // Argo CD Gitサービス
    case 'gitServiceArgo': {
      ok = function( $modal ){
        setInputData( $modal, 'environment', 'git-service-argo');
        workspaceImageUpdate();
      };
    } break;
    // Kubernetes Manifest テンプレート
    case 'kubernetesManifestTemplate': {
      callback = templateFileList;
      width = 1160;
    } break;
    // Manifestパラメータ
    case 'manifestParametar': {
      ok = function( $modal ){
        setParameterData( $modal );
      };
      callback = inputParameter;
      width = 1160;
    } break;
    // Exastro IT Automation 実行結果一覧
    case 'exastroItAutomationResultCheck': {
      callback = itaResultList;
    } break;
    // Argo CD 実行結果一覧
    case 'arogCdResultCheck': {
      callback = arogCdResultList;
    } break;
    // CD実行
    case 'cdRunning': {
      ok = function( ){
        cdRunning( );
      };
    } break;
  }

  modal.open( target, {
    'ok': ok,
    'cancel': cancel,
    'callback': callback
  }, width );
  
  console.log($('.modal-block-main'));
  switch(target) {
    case 'gitServiceCheck':
      var link_append = "";
      data_pipelines = data_workspace['ci_config']['pipelines'];
      for(var i in data_pipelines) {
        var item = data_pipelines[i]['pipeline_id'];

        var link = wsDataJSON['application-code'][item][item + '-git-repository-url'];
        link = link.replace(".git","") + "/commits";
        link_append += '<a href="' + link + '" target="_blank">' + link + '</a><br />';
      };
      $('.modal-block-main').html(link_append);
      break;
    case 'gitServiceArgoCheck':
      var link = "";
      const $commitList = $('#commit-list');
      $commitList.html('');
      for(var env in wsDataJSON['environment']) {
        link = wsDataJSON['environment'][env][env + '-git-service-argo-repository-url'];
        link = link.replace(".git","") + "/commits";

        // EPOCH_LINK
        $commitList.append('<a href="' + link + '" target="_blank">' + link + '</a><br />')
      };
      break;
    case 'pipelineTektonCheck':
      $('.modal-block-main').html('<a href="' + workspace_api_conf.links.tekton + '" target="_blank">確認</a>');
      break;
    case 'registryServiceCheck':
      $('.modal-block-main').html('<a href="' + workspace_api_conf.links.registry + '" target="_blank">確認</a>');
      break;
    case 'arogCdResultCheck':
      $('.modal-block-main').html('<a href="' + workspace_api_conf.links.argo + '" target="_blank">確認</a>');
      break;
    case 'exastroItAutomationResultCheck':
      $('.modal-block-main').html('<a href="' + workspace_api_conf.links.ita + '" target="_blank">確認</a>');
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

const workspaceImageUpdate = function( ) {
  
  // ワークスペースモード
  const mode = $content.attr('data-mode');
  
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
        gitServiceArgoText = wsModalJSON.gitServiceArgo.block.gitServiceArgoSelect.item.gitServiceArgoSelectRadio.item[gitServiceArgoID];console.log(gitServiceArgoID)
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
  const $envTarget = $('#ws-ita-parameter, #ws-git-epoch, #ws-system, #ws-git-argo'),
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
        tempNumber = Object.keys( wsDataJSON['template-file'] ).length,
        limitTempNumber = ( multipleMax >= tempNumber )? tempNumber: multipleMax,
        divTempClone = cloneBlock( limitTempNumber );
        
  $status.find('.template').text( tempNumber ); 
  $tempTarget.attr('data-multiple', limitTempNumber );
  $tempTarget.find('.multiple-number').text( tempNumber );
  $tempTarget.find('.multiple-block').html( divTempClone );
  
  // 入力チェック
  if ( mode === 'setting') {
    const done = 'done',
          unentered = 'unentered';
    // ワークスペース名
    const workspaceInput = ( modal.inputCheck('workspace') )? done: unentered;
    $content.find('.content-header .workspace-button').attr('data-status', workspaceInput );
    // Gitサービス
    const gitServiceInput = ( appNumber && modal.inputCheck('gitService') )? done: unentered;
    $gitService.find('.workspace-button[data-button="gitService"]').attr('data-status', gitServiceInput );
    // TEKTON
    const tektonInput = ( appNumber && modal.inputCheck('pipelineTekton') )? done: unentered;
    $('#ws-pipeline-tekton').find('.workspace-button[data-button="pipelineTekton"]').attr('data-status', tektonInput );
    // レジストリサービス
    const registryServiceInput = ( appNumber && modal.inputCheck('registryService') )? done: unentered;
    $registryService.find('.workspace-button[data-button="registryService"]').attr('data-status', registryServiceInput );
    // Argo CD
    const argoCdInput = ( envNumber && modal.inputCheck('pipelineArgo') )? done: unentered;
    $('#ws-pipeline-argo').find('.workspace-button[data-button="pipelineArgo"]').attr('data-status', argoCdInput );
    // Argo CD Gitサービス
    const gitServiceArgoInput = ( envNumber && modal.inputCheck('gitServiceArgo') )? done: unentered;
    $gitServiceArgo.find('.workspace-button[data-button="gitServiceArgo"]').attr('data-status', gitServiceArgoInput );
    // テンプレートファイル
    const $wsIta = $('#ws-ita'),
          templateInput = ( tempNumber !== 0 )? done: unentered;
    $wsIta.find('.workspace-document-button[data-button="kubernetesManifestTemplate"]').attr('data-status', templateInput );
  }
  
  workspaceReload();
  workspaceTextAdjust();
  setEpochFrame();
  
  
  console.log(wsDataJSON);
}
workspaceImageUpdate();

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ワークスペースの切り替え
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
const $tabList = $workspace.find('.workspace-tab-list');
$tabList.find('.workspace-tab-link[href^="#"]').on('click', function(e){
  e.preventDefault();
  const $tab = $( this ),
        target = $tab.attr('href').replace(/^#/,'');
  
  if ( !$tab.is('.current') ) {
    $tabList.find('.current').removeClass('current');
    $tab.addClass('current');
    $content.attr('data-mode', target );
    
    workspaceReload();
    workspaceTextAdjust();
  }

});

  //-----------------------------------------------------------------------
  // API呼び出し関連
  //-----------------------------------------------------------------------
  var workspace_id = null;
  
  //$(document).ready(function(){
  $('#load-workspace-button').on('click', function(){
  
    // 試験用実装
    {
      workspace_id = parseInt(window.prompt('読み込むワークスペースIDを指定してください', workspace_api_conf.test.default_workspace_id));
    }
  
    new Promise((resolve, reject) => {
  
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.resource.get.replace('{workspace_id}', workspace_id),
      }).done(function(data) {
        console.log("DONE : ワークスペース情報取得");
        console.log(typeof(data));
        console.log(JSON.stringify(data));
  
        workspace_id = data['result']['output'][0]['workspace_id'];
  
        data_workspace = data['result']['output'][0];

        if(data_workspace['common']) {
          wsDataJSON['workspace'] = {
            'workspace-name' :                    data_workspace['common']['name'],
            'workspace-note' :                    data_workspace['common']['note'],
          };
        }
        wsDataJSON['git-service'] = {
          'git-service-select' :                data_workspace['ci_config']['pipelines_common']['git_repositry']['housing'] == 'inner'? 'epoch': data_workspace['ci_config']['pipelines_common']['git_repositry']['interface'],
          'git-service-user' :                  data_workspace['ci_config']['pipelines_common']['git_repositry']['user'],
          'git-service-password' :              data_workspace['ci_config']['pipelines_common']['git_repositry']['password'],
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
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-context-path']        = data_pipelines[i]['build']['context_path'];
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-docker-path']         = data_pipelines[i]['build']['dockerfile_path'];
          wsDataJSON['application-code'][item]['pipeline-tekton-static-analysis']             = data_pipelines[i]['static_analysis']['interface'];
          wsDataJSON['application-code'][item][item + '-registry-service-output-destination'] = data_pipelines[i]['contaier_registry']['image'];
        }
  
        wsDataJSON['environment'] = {};
        data_environments = data_workspace['cd_config']['environments'];
        for(var i in data_environments) {
          var item = data_environments[i]['environment_id'];
          wsDataJSON['environment'][item] = {};
          wsDataJSON['environment'][item]['text']                         = data_environments[i]['name'];
          wsDataJSON['environment'][item][item + '-environment-name']     = data_environments[i]['name'];
          wsDataJSON['environment'][item][item + '-environment-url']      = data_environments[i]['deploy_destination']['cluster_url'];
          wsDataJSON['environment'][item][item + '-environment-namespace']= data_environments[i]['deploy_destination']['namespace'];
          wsDataJSON['environment'][item][item + '-environment-authentication-token']= data_environments[i]['deploy_destination']['authentication_token'];
          wsDataJSON['environment'][item][item + '-environment-certificate']= data_environments[i]['deploy_destination']['base64_encoded_certificate'];

          // マニフェストgitリポジトリ情報の設定
          wsDataJSON['environment'][item][item + '-git-service-argo-repository-url']= data_workspace['ci_config']['environments'][i]['git_url'];

          // マニフェストパラメータの設定
          wsDataJSON['environment'][item]['parameter'] =  {};
          for(var fl in data_workspace['ci_config']['environments'][i]['manifests']) {
            var flid = data_workspace['ci_config']['environments'][i]['manifests'][fl]['file_id'];
            wsDataJSON['environment'][item]['parameter'][flid] = {};
            for(var prm in data_workspace['ci_config']['environments'][i]['manifests'][fl]['parameters']) {
              wsDataJSON['environment'][item]['parameter'][flid][flid + '-' + item + '-' + prm] = data_workspace['ci_config']['environments'][i]['manifests'][fl]['parameters'][prm];
            }
          }
        }

        // data_workspaceからwsDataJSONのマニフェストgitリポジトリ情報へ書き出す
        wsDataJSON['git-service-argo'] = {};
        if(data_workspace['ci_config']['environments'][0]) {
          wsDataJSON['git-service-argo']['git-service-argo-user'] = data_workspace['ci_config']['environments'][0]['git_user'];
          wsDataJSON['git-service-argo']['git-service-argo-password'] = data_workspace['ci_config']['environments'][0]['git_password'];
          wsDataJSON['git-service-argo']['git-service-argo-token'] = data_workspace['ci_config']['environments'][0]['git_token'];
        }

        resolve();
      }).fail(function() {
        console.log("FAIL : ワークスペース情報取得");
        workspace_id = null;
        // 失敗
        reject();
      });        

    }).then(() => {return new Promise((resolve, reject) => {

      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.manifestTemplate.get.replace('{workspace_id}', workspace_id),
      }).done(function(data) {
        // 暫定実装 -----
        wsDataJSON['template-file'] = {};
        var disp = "";

        console.log("manifest get data:" + JSON.stringify(data));
        for(var fileidx = 0; fileidx < data['rows'].length; fileidx++ ) {
          disp += data['rows'][fileidx]['file_name'] + '\n';
          wsDataJSON['template-file']['file'+("000"+(fileidx+1)).slice(-3)] = {
            'name' : data['rows'][fileidx]['file_name'],
            'path' : 'exsample/' + data['rows'][fileidx]['file_name'],
            'date' : '2021/05/12 09:00:00',
            'user' : 'epoch-user',
            'note' : '<a>' + data['rows'][fileidx]['file_name'] + '</a>',
            "text" : data['rows'][fileidx]['file_text'],
          }
        }
        // 暫定実装 -----

        resolve();

      }).fail(function() {
        console.log("FAIL : テンプレート情報取得");
        // 失敗
        reject();
      });        

    })}).then(() => {
      // ボタン名変更
      $('#apply-workspace-button').html('ワークスペース更新');
      workspaceImageUpdate();
      alert("ワークスペース情報を読み込みました");
      console.log('Complete !!');
    }).catch(() => {
      alert("ワークスペース情報を読み込みに失敗しました");
      console.log('Fail !!');
    });
  });
  
  $('#apply-workspace-button').on('click',apply_workspace);
  function apply_workspace() {
    var date = new Date();
  
    console.log('CALL apply_workspace()');
    console.log('---- wsDataJSON ----');
    console.log(JSON.stringify(wsDataJSON));
  
    // API Body生成
    reqbody = {};
  
    // 新IFの設定
    // パラメータ設定 -  共通
    reqbody['common'] = {
      "name"  :   (wsDataJSON['workspace']['workspace-name']? wsDataJSON['workspace']['workspace-name'] : ""),
      "note"  :   (wsDataJSON['workspace']['workspace-note']? wsDataJSON['workspace']['workspace-note'] : ""),
      "organization"  : "0001",
      "owners"  :  [],
    };
  
    // パラメータ設定 - CI環境設定
    reqbody['ci_config'] = {};
  
    reqbody['ci_config']['pipelines_common'] = {};
    reqbody['ci_config']['pipelines_common']['git_repositry'] = {
      'housing' :   (wsDataJSON['git-service']['git-service-select']=='epoch'? 'inner': 'outer'),
      'interface' : (wsDataJSON['git-service']['git-service-select']=='epoch'? 'gitlab': wsDataJSON['git-service']['git-service-select']),
      'user' :      (wsDataJSON['git-service']['git-service-user']? wsDataJSON['git-service']['git-service-user']: ""),
      'password' :  (wsDataJSON['git-service']['git-service-password']? wsDataJSON['git-service']['git-service-password']: ""),
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
      reqbody['ci_config']['pipelines'][reqbody['ci_config']['pipelines'].length] = {
        'pipeline_id'   :  i,
        'git_repositry' :  {
          'url' :             (wsDataJSON['application-code'][i][i+'-git-repository-url']? wsDataJSON['application-code'][i][i+'-git-repository-url'] : ""),
        },
        'webhooks_url'   :  location.protocol + "//" + location.hostname,
        'build' : {
          'branch' :          (wsDataJSON['application-code'][i][i+'-pipeline-tekton-branch']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-branch'].split(','): []),
          'context_path' :    (wsDataJSON['application-code'][i][i+'-pipeline-tekton-context-path']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-context-path'] : ""),
          'dockerfile_path' : (wsDataJSON['application-code'][i][i+'-pipeline-tekton-docker-path']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-docker-path'] : ""),
        },
        'contaier_registry' : {
          'image' :           (wsDataJSON['application-code'][i][i+'-registry-service-output-destination']? wsDataJSON['application-code'][i][i+'-registry-service-output-destination'] : ""),
        },
        'static_analysis' : {
          'interface' :       (wsDataJSON['application-code'][i]['pipeline-tekton-static-analysis']? wsDataJSON['application-code'][i]['pipeline-tekton-static-analysis'] : ""),
        }
      }
    }

    // パラメータ設定 - マニフェスト
    reqbody['ci_config']['environments'] = [];
    var envidx = 0;
    for(var env in wsDataJSON['environment']) {
      var prmenv = {
        'environment_id'    : env,
        'git_url'           : wsDataJSON['environment'][env][env + '-git-service-argo-repository-url'],
        'git_user'          : wsDataJSON['git-service-argo']['git-service-argo-user'],
        'git_password'      : wsDataJSON['git-service-argo']['git-service-argo-password'],
        'git_token'         : wsDataJSON['git-service-argo']['git-service-argo-token'],
        'manifests'         : [],
      }
      for(var flid in wsDataJSON['template-file']) {
        var prmmani = {
          'file_id'         : flid,
          'file'            : wsDataJSON['template-file'][flid]['name'],
          'parameters'      : {},
        };
        console.log('env:'+env);
        if(wsDataJSON['environment'][env]['parameter']) {
          // マニフェストパラメータの指定をしている時、パラメータを設定する
          // 環境を追加してパラメータ指定を行わない時は上記if文でスキップする
          for(var prm in wsDataJSON['environment'][env]['parameter'][flid]) {
            var prmname = prm.replace(new RegExp('^'+flid+'-'+env+'-'),'');
            prmmani['parameters'][prmname] = wsDataJSON['environment'][env]['parameter'][flid][prm];
          }
        }
        prmenv['manifests'][prmenv['manifests'].length] = prmmani;
      }
      reqbody['ci_config']['environments'][reqbody['ci_config']['environments'].length] = prmenv;
      envidx++;
    }

    // パラメータ設定 - CD環境設定
    reqbody['cd_config'] = {};
    reqbody['cd_config']['system_config'] = "one-namespace";
    reqbody['cd_config']['environments'] = [];
    for(var i in wsDataJSON['environment']) {
      reqbody['cd_config']['environments'][reqbody['cd_config']['environments'].length] = {
          //'environment_id'  :     (reqbody['cd_config']['environments'].length + 1),
          'environment_id'  :     i,
          'name' :                (wsDataJSON['environment'][i][i + '-environment-name']? wsDataJSON['environment'][i][i + '-environment-name']: "" ),
          'deploy_destination' : {
            'cluster_url' :           (wsDataJSON['environment'][i][i + '-environment-url']? wsDataJSON['environment'][i][i + '-environment-url']: "" ),
            'namespace' :             (wsDataJSON['environment'][i][i + '-environment-namespace']? wsDataJSON['environment'][i][i + '-environment-namespace']: "" ),
            'authentication_token' :  (wsDataJSON['environment'][i][i + '-environment-authentication-token']? wsDataJSON['environment'][i][i + '-environment-authentication-token']: "" ),
            'base64_encoded_certificate' :  (wsDataJSON['environment'][i][i + '-environment-certificate']? wsDataJSON['environment'][i][i + '-environment-certificate']: "" ),
          },
      }
    }
  
    // パラメータ設定 - マニフェスト
    //  ※現時点では保留※
  
    // 旧形式の付与
    // reqbody['clusterInfo'] = workspace_api_conf['parameter']['clusterInfo'];
    reqbody['workspace'] = {};
    reqbody['workspace']['registry'] = {
        "username": (wsDataJSON['registry-service']['registry-service-account-user']? wsDataJSON['registry-service']['registry-service-account-user']: ""),
        "password": (wsDataJSON['registry-service']['registry-service-account-password']? wsDataJSON['registry-service']['registry-service-account-password']: ""),
    };
    // reqbody['workspace']['manifest'] = workspace_api_conf['parameter']['manifest'];


    reqbody['workspace']['manifest-ita'] = [];
    for(var env in wsDataJSON['environment']) {
      var prmenv = {
        'git_url'           : wsDataJSON['environment'][env][env + '-git-service-argo-repository-url'],
        'git_user'          : wsDataJSON['git-service-argo']['git-service-argo-user'],
        'git_password'      : wsDataJSON['git-service-argo']['git-service-argo-password'],
      }
      reqbody['workspace']['manifest-ita'][reqbody['workspace']['manifest-ita'].length] = prmenv;
    }
    

    // reqbody['build'] = {
    //   'git': {
    //     "username": (wsDataJSON['git-service']['git-service-user']? wsDataJSON['git-service']['git-service-user']: ""),
    //     "password": (wsDataJSON['git-service']['git-service-password']? wsDataJSON['git-service']['git-service-password']: ""),
    //     "url":  reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['git_repositry']['url']: "",
    //     "branch": reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['build']['branch'].join(','): "",
    //     "repos" : reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['git_repositry']['url'].replace("https://github.com/","").replace(".git",""): "",
    //     "WebHooksUrl": "http://example.com/",
    //     "token": (wsDataJSON['git-service']['git-service-token']? wsDataJSON['git-service']['git-service-token']: ""),
    //   },
    //   "pathToContext": reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['build']['context_path']: "",
    //   "pathToDockerfile": reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['build']['dockerfile_path']: "",
    //   "registry" : {
    //     "url" : reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['contaier_registry']['image']: "",
    //     "imageTag" : date.getFullYear() + ('0' + (date.getMonth() + 1)).slice(-2) + ('0' + date.getDate()).slice(-2) + '.' + ('0' + date.getHours()).slice(-2) + ('0' + date.getMinutes()).slice(-2) + ('0' + date.getSeconds()).slice(-2),
    //   }
    // };
   
    // reqbody['deploy'] = {
    //   "enviroments" : {}
    // };
    // for(var env in wsDataJSON['environment']) {
    //   var env_name = wsDataJSON['environment'][env][env + '-environment-name'];
    //   var prmenv = {
    //     "git": {
    //       "url" : wsDataJSON['environment'][env][env + '-git-service-argo-repository-url'],
    //     },
    //     "cluster" : wsDataJSON['environment'][env][env + '-environment-url'],
    //     "namespace" : wsDataJSON['environment'][env][env + '-environment-namespace'],
    //   }
    //   reqbody['deploy']['enviroments'][env_name] = prmenv;
    // }
  
    console.log('---- reqbody ----');
    console.log(JSON.stringify(reqbody));
  
    created_workspace_id = null;
  
    // API呼び出し
    new Promise(function(resolve, reject) {
      // 実行中ダイアログ表示
      $('#modal-progress-container').css('display','flex');
      $('#progress-message-ok').prop("disabled", true);
      //
      // ワークスペース情報登録API
      //
      $('#progress_message').html('STEP 1/5 : ワークスペース情報を登録しています');
  
      console.log("CALL : ワークスペース情報登録");
      if (workspace_id == null) {
        api_param = {
          "type": "POST",
          "url": workspace_api_conf.api.resource.post,
          "data": JSON.stringify(reqbody),
          dataType: "json",
        }
      } else {
        api_param = {
          "type": "PUT",
          "url": workspace_api_conf.api.resource.put.replace('{workspace_id}', workspace_id),
          "data": JSON.stringify(reqbody),
          dataType: "json",
        }
      }
  
      $.ajax(api_param).done(function(data) {
        console.log("DONE : ワークスペース情報登録");
        console.log("--- data ----");
        console.log(JSON.stringify(data));
        created_workspace_id = data['rows'][0]['workspace_id'];
        // 成功
        resolve();
      }).fail(function() {
        console.log("FAIL : ワークスペース情報登録");
        // 失敗
        reject();
      });
    }).then(() => { return new Promise((resolve, reject) => {
      //
      //  ワークスペース作成API
      //
      if(workspace_id == null) {
        $('#progress_message').html('STEP 2/5 : ワークスペースを作成しています');
      } else {
        $('#progress_message').html('STEP 2/5 : ワークスペースを更新しています');
      }
      console.log("CALL : ワークスペース作成");
  
      $.ajax({
        type:"POST",
        url: workspace_api_conf.api.workspace.post,
        data:JSON.stringify(reqbody),
        dataType: "json",
  
      }).done((data) => {
        console.log("DONE : ワークスペース作成");
        console.log("--- data ----");
        console.log(JSON.stringify(data));
  
        if(data.result.code == '200') {
          // 成功
          // TEKTON起動まで待つため、WAIT
          setTimeout(function() { resolve(); }, workspace_api_conf.api.workspace.wait);
        } else {
          // 失敗
          reject();
        }
      }).fail(() => {
        console.log("FAIL : ワークスペース作成");
        // 失敗
        reject();
      });
  
    })}).then(() => { return new Promise((resolve, reject) => {
      //
      // パイプライン作成API
      //
      if(workspace_id == null) {
        $('#progress_message').html('STEP 3/5 :   パイプラインを作成しています');
      } else {
        $('#progress_message').html('STEP 3/5 :   パイプラインを更新しています');
      }
      console.log("CALL : パイプライン作成");
  
      $.ajax({
        type:"POST",
        url: workspace_api_conf.api.pipeline.post,
        data:JSON.stringify(reqbody),
        dataType: "json",
      }).done(function(data) {
        console.log("DONE : パイプライン作成");
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
        console.log("FAIL : パイプライン作成");
        // 失敗
        reject();
      });
  
    })}).then(() => { return new Promise((resolve, reject) => {
      //
      // パイプラインパラメータ設定API
      //
      $('#progress_message').html('STEP 4/5 :   パイプラインを設定しています');
      console.log("CALL : パイプラインパラメータ設定");
  
      $.ajax({
        type:"POST",
        url: workspace_api_conf.api.pipelineParameter.post,
        data:JSON.stringify(reqbody),
        dataType: "json",
      }).done(function(data) {
        console.log("DONE : パイプラインパラメータ設定");
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
        console.log("FAIL : パイプラインパラメータ設定");
        // 失敗
        reject();
      });

    })}).then(() => { return new Promise((resolve, reject) => {
      //
      // マニフェストパラメータ設定API
      //
      $('#progress_message').html('STEP 5/5 :   マニフェストパラメータを設定しています');
      console.log("CALL : マニフェストパラメータ設定");

      $.ajax({
        type:"POST",
        url: workspace_api_conf.api.manifestParameter.post,
        data:JSON.stringify(reqbody),
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

    })}).then(() => {
      // 実行中ダイアログ表示
      if(workspace_id == null) {
        $('#progress_message').html('COMPLETE :  ワークスペースを作成しました（ワークスペースID:'+created_workspace_id+'）');
        workspace_id = created_workspace_id;
      } else {
        $('#progress_message').html('COMPLETE :  ワークスペースを更新しました（ワークスペースID:'+workspace_id+'）');
      }
      $('#progress-message-ok').prop("disabled", false);
      console.log('Complete !!');
    }).catch(() => {
      // 実行中ダイアログ表示
      
      if(created_workspace_id != null) {
        $('#progress_message').html('ERROR :  ワークスペースの作成に失敗しました（ワークスペースID:'+created_workspace_id+'）');
        workspace_id = created_workspace_id;
      } else if(workspace_id == null) {
        $('#progress_message').html('ERROR :  ワークスペースの作成に失敗しました');
      } else {
        $('#progress_message').html('ERROR :  ワークスペースの更新に失敗しました（ワークスペースID:'+workspace_id+'）');
      }
  
      $('#progress-message-ok').prop("disabled", false);
      console.log('Fail !!');
    });
  }
  
  //
  // 処理中メッセージBOXのOKボタン
  //
  $('#progress-message-ok').on('click',() => {
    $('#modal-progress-container').css('display','none');
  });

});