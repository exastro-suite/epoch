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
function workspaceList( list ) {
    
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
          'edit': {
            'icon': 'icon-edit',
            'text': 'ワークスペース編集',
            'separate': 'on'
          },
          // 'delete': {
          //   'icon': 'icon-trash',
          //   'text': 'ワークスペース削除'
          // }
        }
      }
    ];
    
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
          list[key].lastModified,
          list[key].note,
          key
        ];
      }
    };
    updateTableBodyData();
    
    $('.content-header').find('.content-menu-button').on('click', function(){
      location.href = 'workspace.html';
    });
    
    // Table作成
    const et = new epochTable(),
          $table = et.setup('#list', tableHeader, tableBody, {'sortCol': 2, 'sortType': 'desc'} );

    if ( $table ) {
      
      // メニュー
      $table.on('click', '.et-hm-b', function(){
        const $button = $( this ),
              type = $button.attr('data-button'),
              idKey = $button.attr('data-key');

        if ( list[ idKey ] ) {
          switch( type ) {
            // 編集
            case 'edit':
              location.href = 'workspace.html?workspace_id=' + idKey;
              break;
            // 削除
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


$(function(){
    console.log("GET /api2/workspace");

    const fn = new epochCommon();

    $.ajax({
      "type": "GET",
      "url": URL_BASE + "/api2/workspace"
    }).done(function(data) {
      console.log("RESPONSE GET /api2/workspace:");
      console.log(JSON.stringify(data));

      workspaceListData = [];
      for(var i=0; i<data.rows.length; ++i) {
        workspaceListData[data.rows[i].workspace_id] = {
          id: data.rows[i].workspace_id,
          name: data.rows[i].workspace_name,
          note: data.rows[i].workspace_remarks,
          lastModified: fn.formatDate(new Date(data.rows[i].update_at), 'yyyy/MM/dd HH:mm:ss')
        };
      }
      workspaceList(workspaceListData);
    });
});