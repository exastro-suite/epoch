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

// テーブルヘッダー
const tableHeader = [
  {
    'title': 'ワークスペース名',
    'type': 'text',
    'width': '25%',
    'align': 'left',
    'sort': 'on',
    'filter': 'on',
  },
  {
    'title': 'ロール',
    'type': 'itemList',
    'width': '25%',
    'align': 'left',
    'filter': 'on',
    'sort': 'on',
    'item': [
      ['owner','オーナー'],
      ['manager','管理者'],
      ['member-mg','メンバー管理'],
      ['ci-setting','CI設定'],
      ['ci-result','CI確認'],
      ['cd-setting','CD設定'],
      ['cd-execute','CD実行'],
      ['cd-result','CD確認'],
    ]
  },
  {
    'title': 'メンバー数',
    'type': 'number',
    'width': '100px',
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
    'title': '',
    'menu': {
      'member': {
        'icon': 'icon-menu-account',
        'text': 'メンバー一覧',
      },
      'edit': {
        'icon': 'icon-edit',
        'text': 'ワークスペース編集',
        'separate': 'on'
      },
      'leave': {
        'icon': 'icon-trash',
        'text': 'ワークスペース退去'
      },
      // 'delete': {
      //   'icon': 'icon-trash',
      //   'text': 'ワークスペース削除'
      // }
    }
  }
];

function workspaceList( list ) {    
    // テーブルボディ
    const tableBody = [];

    // Table表示用のデータを作成する
    const updateTableBodyData = function(){
      // 配列全削除
      tableBody.splice(0);

      let i = 0;
      for ( const key in list ) {
        tableBody[i++] = [
          list[key].name,
          list[key].roles,
          list[key].members,
          list[key].lastModified,
          list[key].note,
          key
        ];
      }
    };
    updateTableBodyData();
    
    const modalData = {
      'delete': {
        'id': 'delete',
        'title': 'ワークスペース退去確認',
        'footer': {
          'ok': {
            'text': '退去',
            'type': 'danger'
          },
          'cancel': {
            'text': 'キャンセル',
            'type': 'negative'
          }
        },
        'block': {
          'delete': {
            'item': {
              'newPasswordEnterBlock': {
                'type': 'message',
                'text': ''            
              }
            }
          }
        }
      }
    };

    const modal = new modalFunction( modalData ),
          deleteBlock = modalData.delete.block.delete.item.newPasswordEnterBlock;
    
    // ワークスペース新規作成
    $('.content-header').find('.content-menu-button').on('click', function(){
      location.href = 'workspace.html';
    });
    
    // Create table - Table作成
    const et = new epochTable(),
          $table = et.setup('#list', tableHeader, tableBody, {'sortCol': 3, 'sortType': 'desc', 'download': 'on'} );

    if ( $table ) {
      
      // menu - メニュー
      $table.on('click', '.et-hm-b', function(){
        const $button = $( this ),
              type = $button.attr('data-button'),
              idKey = $button.attr('data-key');

        if ( list[ idKey ] ) {
          const name = list[ idKey ].name;
          switch( type ) {
            // member list - メンバー一覧
            case 'member':
              location.href = 'workspace_member_list.html?workspace_id=' + idKey;
              break;
            // edit - 編集
            case 'edit':
              location.href = 'workspace.html?workspace_id=' + idKey;
              break;
            // leave - 退去
            case 'leave':
              // leave confirmation modal display - 退去確認モーダル表示
              deleteBlock.text = name + 'を退去しますか？';
                modal.open('delete',{
                  'ok': function(){
                    // leave process - 退去処理
                    isLeave = leave_workspace(idKey);
                    if(!isLeave) {
                      // Delete the list if you move out - 退去した場合はリストを削除する
                      $button.mouseleave();
                      delete list[ idKey ];
                      updateTableBodyData();
                      et.update( tableBody );
                    } 
                    modal.close();
                },
              },'400');
              break;
            // delete - 削除
            case 'delete':
              if ( confirm('削除しますか？') ) {
                $button.mouseleave();
                delete list[ idKey ];
                updateTableBodyData();
                et.update( tableBody );
                }
              break;
          }
        } else {
          window.console.warn('Specified workspace(ID:' + idKey + ') does not exist.');
        }
      });
    }
}

// 退去 leave
function leave_workspace(workspace_id) {
  console.log("[CALL] leave_workspace()");
  new Promise((resolve, reject) =>{
    console.log('[CALL] DELETE /workspace/{id}/member/current');
    $.ajax({
        "type": "DELETE",
        "url": URL_BASE + "/api/workspace/{workspace_id}/member/current".replace('{workspace_id}',workspace_id),
    }).done(function(data) {
        console.log('[DONE] DELETE /workspace/{id}/member/current');
        resolve();
    }).fail((jqXHR, textStatus, errorThrown) => {
        console.log('[FAIL] DELETE /workspace/{id}/member/current');
        if(jqXHR.status == 400) {
          reject(JSON.parse(jqXHR.responseText).reason);
        } else {
          reject();
        }
    });
  }).then(() => {
      console.log(getText("EP010-0108", "[DONE] 退去"));
      alert(getText("EP010-0107", "ワークスペースから退去しました"));
      window.location.reload();
  }).catch((reason) => {
      console.log(getText("EP010-0109", "[FAIL] 退去"));
      alert(reason);
      window.location.reload();
  });
}

$(function(){
    console.log("GET /api/workspace");

    const fn = new epochCommon();

    $.ajax({
      "type": "GET",
      "url": URL_BASE + "/api/workspace"
    }).done(function(data) {
      console.log("RESPONSE GET /api/workspace:");
      console.log(JSON.stringify(data));

      workspaceListData = [];
      
      for(var i=0; i<data.rows.length; ++i) {
        // Workspace for each row - ワークスペース各行ごとの処理
        roleIdList = [];
        
        for(var roleIdx=0; roleIdx < data.rows[i].roles.length; roleIdx++) {
          for(var itemIdx=0; itemIdx < tableHeader[1].item.length; itemIdx++) {

            // ログインユーザのロール(kind)と、表示するロール項目のインデックス値で一致するものがあるか判定
            // Determine if there is a match between the login user's role(kind) and the index value of the role item to be displayed
            if(data.rows[i].roles[roleIdx].kind == tableHeader[1].item[itemIdx][0]) {

              // 一致した場合、表示するロール項目のインデックス値を配列にセット
              // If there is a match, set the index value of the role item to be displayed in the array
              roleIdList.push(tableHeader[1].item[itemIdx][0])
            }
          }
        }

        workspaceListData[data.rows[i].workspace_id] = {
          id: data.rows[i].workspace_id,
          name: data.rows[i].workspace_name,
          roles: roleIdList,
          members: data.rows[i].members,
          note: data.rows[i].workspace_remarks,
          lastModified: fn.formatDate(new Date(data.rows[i].update_at), 'yyyy/MM/dd HH:mm:ss')
        };
      }
      workspaceList(workspaceListData);
    });
});

