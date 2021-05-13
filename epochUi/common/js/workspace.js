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
    'environment' : {
    },
    'application-code': {
    },
    'template-file': {
      'file001': {
        'file-name': 'text.yaml'
      }
    },
    'git-service': {
      'git-service-select': 'epoch'
    },
    'static-analysis': {
      'static-analysis-select': 'sonarqube'
    },
    'registry-service': {
      'registry-service-select': 'epoch'
    }
  };
  
  const wsModalJSON = {
    /* -------------------------------------------------- *\
       Gitサービス
    \* -------------------------------------------------- */
    'gitService': {
      'id': 'git-service',
      'title': 'Gitサービス',
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
      'title': 'Tekton',
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
      'block': [
        {
          'id': 'template-file-list',
          'title': 'テンプレートファイル一覧',
          'button': {
            'id': 'template-upload-select',
            'value': 'アップロードファイル選択'
          },
          'item': [
              {
                'type': 'table',
                'value': {
                  'data':[
                    [{'type':'link','text':'aaaaa.yaml','href':'#'},{'type':'button','text':'更新'},{'type':'button','text':'削除'}],
                    [{'type':'link','text':'bbbbb.yaml','href':'#'},{'type':'button','text':'更新'},{'type':'button','text':'削除'}],
                    [{'type':'link','text':'ccccc.yaml','href':'#'},{'type':'button','text':'更新'},{'type':'button','text':'削除'}]
                  ]
                }
              }
          ]
        }
      ]
    },
    /* -------------------------------------------------- *\
       Kubernetes Manifestテンプレートアップロード
    \* -------------------------------------------------- */
    'kubernetesManifestTemplateUpload': {
      'id': 'kubernetes-manifest-template',
      'title': 'Kubernetes Manifest テンプレートアップロード',
      'block': [
        {
          'title': 'テンプレートアップロード',
          'item': [
              {
                'type': 'file'
              }
          ]
        }
      ]
    },
    /* -------------------------------------------------- *\
       Kubernetes Manifestパラメータ
    \* -------------------------------------------------- */
    'manifestParametar': {
      'title': 'Manifest パラメータ',
      'block': {
        'registryServiceOutput': {
          'title': 'パラメータ入力',
          'tab': {
            'type': 'reference',
            'target': {
              'key1': 'template-file',
              'key2': 'file-name'
            },
            'emptyText': 'テンプレートファイルの登録がありません。Kubernetes Manifestテンプレートの設定からテンプレートファイルを追加してください。',
            'deletConfirmText': '',
            'item': {
              'gitRepositoryURL': {
                'type': 'parameter'
              }
            }
          }
        }
      }
    },
    /* -------------------------------------------------- *\
       静的解析
    \* -------------------------------------------------- */
    'staticAnalysis': {
      'title': '静的解析',
      'block': {
        'staticAnalysisSelect': {
          'title': '静的解析サービス選択',
          'item': {
            'staticAnalysisSelectRadio': {
              'type': 'radio',
              'name': 'static-analysis-select',
              'value': '',
              'item': {
                'sonarqube': 'SonarQube',
                'none': '使用しない'
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
                //'type': 'password',
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
    }
  };
  const modal = new modalFunction( wsModalJSON, wsDataJSON );
  
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  //
  //   初期設定
  // 
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  
  // jQueryオブジェクトのキャッシュ
  const $workspace = $('#workspace'),
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
            $gitE = $('#ws-git-epoch'),
            $startCI = $('#ws-ci-user'),
            $startCD = $('#ws-cd-user'),
            $end = $('#ws-system'),
            $ac = $('#ws-application-code'),
            $km = $('#ws-kubernetes-manifest'),
            $kmT = $('#ws-kubernetes-manifest-template'),
            $mp = $('#ws-ita-parameter'),
            $itaF = $('#ws-ita-frow'),
            epoch = {}, tekton = {}, argo = {}, docker = {},
            ita = {}, git = {}, gitE = {}, sonar = {},
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
  
      gitE.w = blockWidth * 1.1;
      gitE.h = $gitE.outerHeight();
      gitE.l = tekton.l;
      gitE.t = argo.t + argo.h + blockMargin * 4;
      $gitE.css({'width': gitE.w, 'left': gitE.l, 'top' : gitE.t });
  
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
  
      epoch.w = blockWidth * 0.8;
      epoch.h = $epoch.outerHeight();
      epoch.l = docker.l + docker.w - epoch.w;
      epoch.t = itaF.t + itaF.h + blockMargin * 2 - epoch.h;
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
  
      // Argo CD --> Kubernetes Manifest 
      const $line1 = newSVG('path');
      $line1.attr({
      'd': order('M',km.xc-12,argo.t+argo.h,km.xc-12,km.t-12,'c',0,24,24,24,24,0,'L',km.xc+12,argo.t+argo.h-4,'l',-a,a,a,-a,a,a,-a,-a),
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
          'y5': epoch.t + epoch.h + epockPadding,
          'x1': ita.l - epockPadding,
          'x2': git.l + git.w + epockPadding,
          'x3': argo.l - epockPadding,
          'x4': tekton.l + tekton.w + epockPadding,
          'x5': epoch.l + epoch.w + epockPadding
      }
  
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
          points = new Array();
    
    if ( gitServiceType !== 'epoch') {
      points.push(ep.x1,ep.y4,ep.x3,ep.y4,ep.x3,ep.y3);
    } else {
      points.push(ep.x1,ep.y2,ep.x2,ep.y2,ep.x2,ep.y3);
    }
    
    if ( registryServiceType !== 'epoch') {
      points.push(ep.x4,ep.y3,ep.x4,ep.y4,ep.x5,ep.y4);
    } else {
      points.push(ep.x4,ep.y3,ep.x5,ep.y3);
    }
    
    points.push(ep.x5,ep.y5,ep.x1,ep.y5);
    
    $workspaceEpoch.find('polygon').attr('points', points.join(' ') );
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
  
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  //
  //   モーダル
  // 
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  
  // モーダル内の入力データを wsDataJSON に入れる
  const setInputData = function( $modal, tabTarget, commonTarget ) {
    const inputTarget = 'input[type="text"], input[type="password"], input[type="radio"]:checked, textarea';
    const inputValue = function( $input ){
      return $input.val();
    };
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
        wsDataJSON[ tabTarget ][ tabID ][ name ] = inputValue( $input );
      } else {
        if ( wsDataJSON[ commonTarget ] === undefined ) wsDataJSON[ commonTarget ] = new Object();
        wsDataJSON[ commonTarget ][ name ] = inputValue( $input );
      }
    });
  }
  
  // 削除されたタブに合わせてデータも削除する
  const deleteTabData = function( $modal, target ) {
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
    
  $workspace.find('.modal-open').on('click', function(){
    const target = $( this ).attr('data-button');
    
    let okFunction, cancelFunction, callback;
  
    switch( target ) {
      // Gitサービス
      case 'gitService': {
        okFunction = function( $modal ){
          setInputData( $modal, 'application-code', 'git-service');
          deleteTabData( $modal, 'application-code');
          workspaceImageUpdate();
        };   
        } break;
      // 静的解析
      case 'staticAnalysis': {
        okFunction = function( $modal ){
          setInputData( $modal, '', 'static-analysis');
          workspaceImageUpdate();
        };      
        } break;
      // レジストリサービス
      case 'registryService': {
        okFunction = function( $modal ){
          setInputData( $modal, 'application-code', 'registry-service');
          workspaceImageUpdate();
        };      
        } break;
      // Argo CD
      case 'pipelineArgo': {
        okFunction = function( $modal ){
          setInputData( $modal, 'environment', '');
          deleteTabData( $modal, 'environment');
          workspaceImageUpdate();
        };      
        } break;
      // Tekton
      case 'pipelineTekton': {
        okFunction = function( $modal ){
          setInputData( $modal, 'application-code', '');
          workspaceImageUpdate();
        };      
        } break;
    }
    
    
    modal.open( target, okFunction, cancelFunction, callback );
    templateFileList();
    
  });
  
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  //
  //   テンプレートファイルリスト
  // 
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  const dummyFileList = [
    {
      'path': 'test1.yaml',
      'note': 'test 1'
    },
    {
      'path': 'test2.yaml',
      'note': 'test 2'
    },
      {
      'path': 'test2.yaml',
      'note': 'test 2'
    }
  ];
  
  
  const templateFileList = function() {
  
   
  };
  
  
  
  
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  //
  //   ワークスペース情報の更新
  // 
  ////////////////////////////////////////////////////////////////////////////////////////////////////
  
  const workspaceImageUpdate = function( ) {
    // Gitサービス
    const $gitService = $('#ws-git-service'),
          gitServiceID = wsDataJSON['git-service']['git-service-select'],
          gitServiceText = wsModalJSON.gitService.block.gitServiceSelect.item.gitServiceSelectRadio.item[gitServiceID];
    $gitService.find('.workspace-block-name').text( gitServiceText );
    $gitService.attr('data-service', gitServiceID );
    
    // 静的解析
    const $staticAnalysis = $('#ws-static-analysis'),
          $staticLine = $('[data-id="static-analysis-line"]'),
          staticAnalysisID = wsDataJSON['static-analysis']['static-analysis-select'],
          staticAnalysisText = wsModalJSON.staticAnalysis.block.staticAnalysisSelect.item.staticAnalysisSelectRadio.item[staticAnalysisID];
    $staticAnalysis.find('.workspace-block-name').text( staticAnalysisText );
    $staticAnalysis.attr('data-service', staticAnalysisID );
    if ( staticAnalysisID === 'none') {
      $staticLine.attr('style','display:none');
    } else {
      $staticLine.removeAttr('style');
    }
    
    // レジストリサービス
    const $registryService = $('#ws-registry-service'),
          registryServiceID = wsDataJSON['registry-service']['registry-service-select'],
          registryServiceText = wsModalJSON.registryService.block.registryServiceSelect.item.registryServiceSelectRadio.item[registryServiceID];
    $registryService.find('.workspace-block-name').text( registryServiceText );
    $registryService.attr('data-service', registryServiceID );
    
    // 重なり共通
    const multipleMax = 5;
    const cloneBlock = function( number ){
      if ( number - 1 > 0 ) {
        return '<div></div>' + cloneBlock( number - 1 );
      }
      return '';
    };
    
    // 環境数
    const $envTarget = $('#ws-ita-parameter, #ws-git-epoch, #ws-system'),
          envNumber = Object.keys( wsDataJSON['environment'] ).length,
          limitEnvNumber = ( multipleMax >= envNumber )? envNumber: multipleMax,
          divEnvClone = cloneBlock( limitEnvNumber );
    $envTarget.attr('data-multiple', limitEnvNumber );
    $envTarget.find('.multiple-number').text( envNumber );
    $envTarget.find('.multiple-block').html( divEnvClone );
    
    // アプリケーションコード数
    const $appTarget = $('#ws-ci-area'),
          appNumber = Object.keys( wsDataJSON["application-code"] ).length,
          limitAppNumber = ( multipleMax >= appNumber )? appNumber: multipleMax,
          divAppClone = cloneBlock( limitAppNumber );
    $appTarget.attr('data-multiple', limitAppNumber );
    $appTarget.find('.multiple-number').text( appNumber );
    $appTarget.find('.multiple-block').html( divAppClone );
    setEpochFrame();
  }
  workspaceImageUpdate();
  
  
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
        wsDataJSON['git-service'] = {
          'git-service-select' :                data_workspace['ci_config']['pipelines_common']['git_repositry']['housing'] == 'inner'? 'epoch': data_workspace['ci_config']['pipelines_common']['git_repositry']['interface'],
          'git-service-user' :                  data_workspace['ci_config']['pipelines_common']['git_repositry']['user'],
          'git-service-password' :              data_workspace['ci_config']['pipelines_common']['git_repositry']['password'],
          'git-service-token' :                 data_workspace['ci_config']['pipelines_common']['git_repositry']['token'],
        };
        wsDataJSON['static-analysis'] = {
          'static-analysis-select' :            data_workspace['ci_config']['pipelines_common']['static_analysis']['analysis'],
        };
        wsDataJSON['registry-service'] = {
          'registry-service-select' :           data_workspace['ci_config']['pipelines_common']['container_registry']['housing'] == 'inner'? 'epoch': data_workspace['ci_config']['pipelines_common']['container_registry']['interface'],
          'registry-service-account-user' :     data_workspace['ci_config']['pipelines_common']['container_registry']['user'],
          'registry-service-account-password' : data_workspace['ci_config']['pipelines_common']['container_registry']['password'],
        };
  
        wsDataJSON['application-code'] = {};
        data_pipelines = data_workspace['ci_config']['pipelines'];
        for(var i in data_pipelines) {
          item = 't'+i;
          wsDataJSON['application-code'][item] = {};
          wsDataJSON['application-code'][item]['text'] = data_pipelines[i]['git_repositry']['url'].replace(/^.*\//,'').replace(/\.git$/,'');
          wsDataJSON['application-code'][item][item + '-git-repository-url']                  = data_pipelines[i]['git_repositry']['url'];
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-branch']              = data_pipelines[i]['build']['branch'].join(',');
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-context-path']        = data_pipelines[i]['build']['context_path'];
          wsDataJSON['application-code'][item][item + '-pipeline-tekton-docker-path']         = data_pipelines[i]['build']['dockerfile_path'];
          wsDataJSON['application-code'][item][item + '-registry-service-output-destination'] = data_pipelines[i]['contaier_registry']['image'];
        }
  
        wsDataJSON['environment'] = {};
        data_environments = data_workspace['cd_config']['environments'];
        for(var i in data_environments) {
          item = 't'+i;
          wsDataJSON['environment'][item] = {};
          wsDataJSON['environment'][item]['text']                         = data_environments[i]['name'];
          wsDataJSON['environment'][item][item + '-environment-name']     = data_environments[i]['name'];
          wsDataJSON['environment'][item][item + '-environment-url']      = data_environments[i]['deploy_destination']['cluster_url'];
          wsDataJSON['environment'][item][item + '-environment-namespace']= data_environments[i]['deploy_destination']['namespace'];
          wsDataJSON['environment'][item][item + '-environment-authentication-token']= data_environments[i]['deploy_destination']['authentication_token'];
          wsDataJSON['environment'][item][item + '-environment-certificate']= data_environments[i]['deploy_destination']['base64_encoded_certificate'];
        }
        workspaceImageUpdate();
        resolve();
      }).fail(function() {
        console.log("FAIL : ワークスペース情報取得");
        workspace_id = null;
        // 失敗
        reject();
      }).then(() => {
        console.log('Complite !!');
      }).catch(() => {
        console.log('Fail !!');
      });
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
      "name"  :   "ワークスペース名",
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
    reqbody['ci_config']['pipelines_common']['static_analysis'] = {
      'analysis' :  wsDataJSON['static-analysis']['static-analysis-select'],
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
        'git_repositry' :  {
          'url' :             (wsDataJSON['application-code'][i][i+'-git-repository-url']? wsDataJSON['application-code'][i][i+'-git-repository-url'] : ""),
        },
        'build' : {
          'branch' :          (wsDataJSON['application-code'][i][i+'-pipeline-tekton-branch']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-branch'].split(','): []),
          'context_path' :    (wsDataJSON['application-code'][i][i+'-pipeline-tekton-context-path']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-context-path'] : ""),
          'dockerfile_path' : (wsDataJSON['application-code'][i][i+'-pipeline-tekton-docker-path']? wsDataJSON['application-code'][i][i+'-pipeline-tekton-docker-path'] : ""),
        },
        'contaier_registry' : {
          'image' :           (wsDataJSON['application-code'][i][i+'-registry-service-output-destination']? wsDataJSON['application-code'][i][i+'-registry-service-output-destination'] : ""),
        },
      }
    }
  
    // パラメータ設定 - CD環境設定
    reqbody['cd_config'] = {};
    reqbody['cd_config']['system_config'] = "one-namespace";
    reqbody['cd_config']['environments'] = [];
    for(var i in wsDataJSON['environment']) {
      reqbody['cd_config']['environments'][reqbody['cd_config']['environments'].length] = {
          'environment_id'  :     (reqbody['cd_config']['environments'].length + 1),
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
    reqbody['clusterInfo'] = workspace_api_conf['parameter']['clusterInfo'];
    reqbody['workspace'] = {};
    reqbody['workspace']['registry'] = {
        "username": (wsDataJSON['registry-service']['registry-service-account-user']? wsDataJSON['registry-service']['registry-service-account-user']: ""),
        "password": (wsDataJSON['registry-service']['registry-service-account-password']? wsDataJSON['registry-service']['registry-service-account-password']: ""),
    };
    reqbody['workspace']['manifest'] = workspace_api_conf['parameter']['manifest'];
    reqbody['workspace']['manifest-ita'] = workspace_api_conf['parameter']['manifest-ita'];
  
    reqbody['build'] = {
      'git': {
        "username": (wsDataJSON['git-service']['git-service-user']? wsDataJSON['git-service']['git-service-user']: ""),
        "password": (wsDataJSON['git-service']['git-service-password']? wsDataJSON['git-service']['git-service-password']: ""),
        "url":  reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['git_repositry']['url']: "",
        "branch": reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['build']['branch'].join(','): "",
        "repos" : reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['git_repositry']['url'].replace("https://github.com/","").replace(".git",""): "",
        "WebHooksUrl": "http://example.com/",
        "token": (wsDataJSON['git-service']['git-service-token']? wsDataJSON['git-service']['git-service-token']: ""),
      },
      "pathToContext": reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['build']['context_path']: "",
      "pathToDockerfile": reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['build']['dockerfile_path']: "",
      "registry" : {
        "url" : reqbody['ci_config']['pipelines'][0]? reqbody['ci_config']['pipelines'][0]['contaier_registry']['image']: "",
        "imageTag" : date.getFullYear() + ('0' + (date.getMonth() + 1)).slice(-2) + ('0' + date.getDate()).slice(-2) + '.' + ('0' + date.getHours()).slice(-2) + ('0' + date.getMinutes()).slice(-2) + ('0' + date.getSeconds()).slice(-2),
      }
    };
   
    reqbody['deploy'] = workspace_api_conf['parameter']['deploy'];
    reqbody['deploy']['enviroments']['test']['namespace'] = (reqbody['cd_config']['environments'][0]? reqbody['cd_config']['environments'][0]['deploy_destination']['namespace']: "");
  
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
      $('#progress_message').html('STEP 1/4 : ワークスペース情報を登録しています');
  
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
        $('#progress_message').html('STEP 2/4 : ワークスペースを作成しています');
      } else {
        $('#progress_message').html('STEP 2/4 : ワークスペースを更新しています');
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
        $('#progress_message').html('STEP 3/4 :   パイプラインを作成しています');
      } else {
        $('#progress_message').html('STEP 3/4 :   パイプラインを更新しています');
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
      $('#progress_message').html('STEP 4/4 :   パイプラインを設定しています');
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
    })}).then(() => {
      // 実行中ダイアログ表示
      if(workspace_id == null) {
        $('#progress_message').html('COMPLITE :  ワークスペースを作成しました（ワークスペースID:'+created_workspace_id+'）');
        workspace_id = created_workspace_id;
      } else {
        $('#progress_message').html('COMPLITE :  ワークスペースを更新しました（ワークスペースID:'+workspace_id+'）');
      }
      $('#progress-message-ok').prop("disabled", false);
      console.log('Complite !!');
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