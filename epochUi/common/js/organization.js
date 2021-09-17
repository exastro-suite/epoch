/*
#   Copyright 2021 NEC Corporation
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

function organization( list ) {

    // テーブルヘッダー
    const tableHeader = [
      {
        'title': 'オーガナイゼーション名',
        'type': 'text',
        'width': '20%',
        'align': 'left',
        'sort': 'on',
        'filter': 'on',
      },
      {
        'title': 'オーナー',
        'type': 'list',
        'width': '15%',
        'align': 'left',
        'sort': 'on',
        'filter': 'on',
      },
      {
        'title': 'アカウント数',
        'type': 'text',
        'width': '120px',
        'align': 'center',
        'sort': 'on',
        'filter': 'on',
      },
      {
        'title': '最終更新日時',
        'type': 'date',
        'width': '160px',
        'align': 'center',
        'sort': 'on',
        'filter': 'on',
      },
      {
        'title': '備考',
        'type': 'text',
        'width': 'auto',
        'align': 'left',
        'sort': 'on',
        'filter': 'on'
      },
      {
        'type': 'hoverMenu',
        'menu': {
          'workspace': {
            'icon': 'icon-menu-workspace',
            'text': 'ワークスペース一覧'
          },
          'edit': {
            'icon': 'icon-edit',
            'text': '編集'
          },
          'account': {
            'icon': 'icon-menu-account',
            'text': 'アカウント一覧',
            'separate': 'on'
          },
          'delete': {
            'icon': 'icon-trash',
            'text': '退去'
          }
        }
      }
    ];

    // テーブルボディ
    const tableBody = [];

    // organizationListからTable表示用のデータを作成する
    const updateTableBodyData = function(){
      // 配列全削除
      tableBody.splice(0);

      let i = 0;
      for ( const key in list ) {
        tableBody[i++] = [
          list[key].name,
          list[key].owner,
          list[key].account,
          list[key].lastModified,
          list[key].note,
          key
        ];
      }
    };
    updateTableBodyData();

    // モーダル内に表示するデータを入れる
    const modalOrganization = {};

    // モーダル
    const modalJSON = {
      'newOrganization': {
        'id': 'new-organization',
        'title': 'オーガナイゼーション作成',
        'footer': {
          'ok': {
            'text': '作成する',
            'type': 'positive'
          },
          'cancel': {
            'text': 'キャンセル',
            'type': 'negative'
          }
        },
        'block': {
          'organization': {
            'item': {
              'name': {
                'type': 'input',
                'title': 'オーガナイゼーション名',
                'name': 'name',
                'placeholder': 'オーガナイゼーション名を入力してください',
                'required': 'on',
                'min': 1,
                'max': 32
              },
              'free': {
                'type': 'freeitem',
                'title': '付加情報',
                'name': 'info'
              },
              'note': {
                'type': 'textarea',
                'title': '備考',
                'name': 'note',
                'placeholder': '備考を入力してください'
              }
            }
          }
        }
      },
      'editOrganization': {
        'id': 'edit-organization',
        'title': 'オーガナイゼーション編集',
        'footer': {
          'ok': {
            'text': '更新する',
            'type': 'positive'
          },
          'cancel': {
            'text': 'キャンセル',
            'type': 'negative'
          }
        },
        'block': {
          'organization': {
            'item': {
              'name': {
                'type': 'input',
                'title': 'オーガナイゼーション名',
                'name': 'name',
                'placeholder': 'オーガナイゼーション名を入力してください'
              },
              'free': {
                'type': 'freeitem',
                'title': '付加情報',
                'name': 'info'
              },
              'note': {
                'type': 'textarea',
                'title': '備考',
                'name': 'note',
                'placeholder': '備考を入力してください'
              }
            }
          }
        }
      },
      'deleteOrganization': {
        'id': 'delete-organization',
        'title': 'オーガナイゼーション削除',
        'footer': {
          'ok': {
            'text': 'オーガナイゼーション削除',
            'type': 'danger'
          },
          'cancel': {
            'text': 'キャンセル',
            'type': 'negative'
          }
        },
        'block': {
          'organization': {
            'title': '下記のオーガナイゼーションを削除します',
            'item': {
              'name': {
                'type': 'reference',
                'title': 'オーガナイゼーション名',
                'target': 'name'
              },
              'owner': {
                'type': 'reference',
                'title': 'オーナー',
                'target': 'owner'
              },
              'message': {
                'type': 'message',
                'title': '注意',
                'text': 'オーガナイゼーションを削除すると紐づくワークスペースも削除されます。'
              }
            }
          }
        }
      }
    };
    
    // オーガナイゼーションテーブルの表示
    const et = new epochTable(),
          modal = new modalFunction( modalJSON, modalOrganization ),
          $table = et.setup('#list', tableHeader, tableBody, {'sortCol': 3, 'sortType': 'desc', 'filter': 'off'} );

    if ( $table ) {

      // オーガナイゼーションメニューボタン
      $table.on('click', '.et-hm-b', function(){
        const $button = $( this ),
              type = $button.attr('data-button'),
              idKey = $button.attr('data-key'); // 操作するオーガナイゼーションのID

        if ( list[ idKey ] ) {
          // モーダルに表示するデータを取得
          modalOrganization['data'] = list[ idKey ];

          switch( type ) {
            // 編集
            case 'edit':
              modal.open('editOrganization',{
                'ok': function(){
                  // 入力値の取得
                  modal.setParameter('data');
                  
                  // 更新
                  list[ idKey ].name = modalOrganization['data'] .name;
                  list[ idKey ].info = modalOrganization['data'] .info;
                  list[ idKey ].note = modalOrganization['data'] .note;
                  list[ idKey ].owner = '';
                  list[ idKey ].lastModified = '';
                  
                  // テーブル再表示
                  updateTableBodyData();
                  et.update( tableBody, {'sortCol': 3, 'sortType': 'desc'} );
          
                  modal.close();
                }
              });
              break;
            // 削除
            case 'delete':
              modal.open('deleteOrganization',{
                'ok': function(){
                  delete list[ idKey ];
                  updateTableBodyData();
                  et.update( tableBody );
                  modal.close();
                }
              });
              break;
            // workspace
            case 'workspace':
              window.location.href = "workspace.html";
              break;
          }
        } else {
          window.console.warn('Specified organization(ID:' + idKey + ') does not exist.');
        }
      });
    }
    
    // オーガナイゼーション追加
    const $content = $('#content');
    $content.find('.modal-open').on('click', function(){
      modalOrganization['data'] = {};
      modal.open('newOrganization',{
        'ok': function(){
          // 入力値の取得
          modal.setParameter('data');

          var param = {
            'organization_name': modalOrganization['data'].name,
            'additional_information': modalOrganization['data'].info
          }
          console.log(JSON.stringify(param));
        
          $.ajax({
            "type": "POST",
            "url": organization_api_conf.api.resource.post,
            "data": JSON.stringify(param),
            dataType: "json",
          }).done(function(data) {
            console.log("DONE : オーガナイゼーション登録");
            console.log(typeof(data));
            console.log(JSON.stringify(data));

            reload();

            // modal.close();

          }).fail(function() {
            // 失敗
            console.log("FAIL : オーガナイゼーション登録");

          });
        }
      });
    });

}

function reload() {

  console.log('generate_organization_elements');

  const organizationList = [];

  $.ajax({
    "type": "GET",
    "url": organization_api_conf.api.resource.get_all
  }).done(function(response_body) {
    console.log("DONE : オーガナイゼーション一覧取得");
    // console.log(typeof(response_body));
    console.log(JSON.stringify(response_body));

    const fn = new epochCommon();
    response_body.output.forEach(function(data) {
      var row = {
        'name': data.organization_name,
        'info': data.additional_information,
        'note': '--',
        'owner': '--',
        'lastModified': fn.formatDate(new Date(parseInt(data.update_at_int + '000')), 'yyyy/MM/dd HH:mm:ss'),
        'account': '--'
      };
      organizationList.push(row);
    });

    organization( organizationList );

    console.log("一覧表示 完了");

  }).fail(function() {
    // 失敗
    console.log("FAIL : オーガナイゼーション一覧取得");

  });

}

$(function(){
  reload();
});
