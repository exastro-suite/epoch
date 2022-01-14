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

const workspace_id = (new URLSearchParams(window.location.search)).get('workspace_id');
var role_update_at = null;

// JavaScript Document
function workspaceMemberList( memberList ) {    
    
    // ロールリスト
    var g_roleList = [
        {'role_id': 'owner', 'name': 'オーナー', 'note': '説明分1'},
        {'role_id': 'manager', 'name': '管理者', 'note': '説明分2'},
        {'role_id': 'member-mg', 'name': 'メンバー管理', 'note': '説明分3'},
        {'role_id': 'ci-setting', 'name': 'CI設定', 'note': '説明分4'},
        {'role_id': 'ci-result', 'name': 'CI確認', 'note': '説明分5'},
        {'role_id': 'cd-setting', 'name': 'CD設定', 'note': '説明分6'},
        {'role_id': 'cd-execute', 'name': 'CD実行', 'note': '説明分7'},
        {'role_id': 'cd-result', 'name': 'CD確認', 'note': '説明分8'}
    ];
    var g_roleLength = g_roleList.length;
    
    // 可能な操作
    const roleOperationList = [
        {'role_operation_id': '1', 'name': 'ワークスペース参照', 'roles': ['owner','manager','member-mg','ci-setting','ci-result','cd-setting','cd-execute','cd-result'], },
        {'role_operation_id': '2', 'name': 'ワークスペース更新（名称）', 'roles': ['owner','manager'], },
        {'role_operation_id': '3', 'name': 'ワークスペース更新（CI）', 'roles': ['owner','manager','ci-setting'], },
        {'role_operation_id': '4', 'name': 'ワークスペース更新（CD）', 'roles': ['owner','manager','cd-setting'], },
        {'role_operation_id': '5', 'name': 'ワークスペース削除', 'roles': ['owner'], },
        {'role_operation_id': '6', 'name': 'オーナーロール設定', 'roles': ['owner'], },
        {'role_operation_id': '7', 'name': 'メンバー追加', 'roles': ['owner','manager','member-mg'], },
        {'role_operation_id': '8', 'name': 'ロール変更', 'roles': ['owner','manager','member-mg'], },
        {'role_operation_id': '9', 'name': 'CIパイプライン結果確認', 'roles': ['owner','manager','ci-setting','ci-result','cd-execute'], },
        {'role_operation_id': '10', 'name': 'Manifestテンプレート・パラメータ編集', 'roles': ['owner','manager','cd-execute'], },
        {'role_operation_id': '11', 'name': 'CD実行', 'roles': ['owner','manager','cd-execute'], },
        {'role_operation_id': '12', 'name': 'CD実行結果確認', 'roles': ['owner','manager','cd-setting','cd-execute','cd-result'], }
    ];
    const roleOperationLength = roleOperationList.length;
    
    // メンバーリストをテーブル表示用に変換する
    const updateTableMemberList = function( list ){
        const mL = list.length,
              mlb = [];
        for ( let i = 0; i < mL; i++ ) {
            if(typeof(list[i].roles) == "undefined") {
              list[i].roles = [];
            }
            const row = [],
                  role = [],
                  roleLengh = list[i].roles.length;
            for ( let j = 0; j < roleLengh; j++ ) {
              role.push( list[i].roles[j].kind );
            }
            
            row.push( list[i].user_id );
            row.push( list[i].username );
            
            for ( let j = 0; j < g_roleLength; j++ ) {
              row.push(( role.indexOf( g_roleList[j].role_id ) !== -1 )? '1': '0' );
            }
            
            mlb.push( row );
        }
        return mlb;
    };
    const memberListBody = updateTableMemberList( memberList.rows );
    
    // メンバーリストヘッダー
    const memberListHeader = [
        {'title': 'ユーザID', 'id': 'row-all', 'type': 'rowCheck', 'width': '48px'},
        {'title': 'ユーザ名', 'type': 'text', 'width': 'auto', 'align': 'left', 'sort': 'on', 'filter': 'on'}
    ];
    for ( let i = 0; i < g_roleLength; i++ ) {
        memberListHeader.push({
            'title': g_roleList[i].name, 'type': 'status', 'width': '8%', 'align': 'center', 'sort': 'on', 'filter': 'on', 'list': {'1': 'ロールあり', '0': 'ロールなし'},
            'q': g_roleList[i].note
        });
    }
    
    // Table作成
    const et = new epochTable(),
          $table = et.setup('#list', memberListHeader, memberListBody, {'download': 'on'} );
    
    // メンバー削除ボタン制御
    $table.find('.et-cb-i').on('change', function(){
      if ( $( this ).val() === '') {
      $('.content-menu-button[data-button="removeMember"]').prop('disabled', true );
      } else {
      $('.content-menu-button[data-button="removeMember"]').prop('disabled', false );
      }
    });
    
    
    // モーダル
    const modalData = {
      'roleChange': {
        'id': 'role-change-modal',
        'title': 'ロールの変更',
        'class': 'layout-tab-fixed layout-padding-0',
        'footer': {
          'ok': {'text': 'ロール変更確認', 'type': 'positive'},
          'cancel': {'text': 'キャンセル', 'type': 'negative'}
        },
        'block': {
          'roleChange': {
            'item': {
              'roleChangeBody': {
                'title': '',
                'type': 'loading',
                'id': 'modalMemberTable'
              }
            }
          }
        }
      },
      'roleChangeCheck': {
        'title': '下記のメンバーのロールを変更します',
        'class': 'layout-tab-fixed layout-padding-0',
        'footer': {
          'ok': {'text': 'ロール変更', 'type': 'positive'},
          'cancel': {'text': 'ロールの選択をやり直す', 'type': 'negative'}
        },
        'block': {
          'roleChange': {
            'item': {
              'roleChangeBody': {
                'type': 'loading',
                'id': 'modalRoleChangeTable'
              }
            }
          }
        }
      },
      'roleChangeRunning': {
        'title': 'ロールを変更しています',
        'block': {
          'addMember': {
            'item': {
              'addMemberBody': {
                'type': 'loading'
              }
            }
          }
        }
      },
      'addMember': {
        'id': 'add-member-modal',
        'title': '追加するユーザ・ロールを選択してください',
        'class': 'layout-tab-fixed layout-padding-0',
        'footer': {
          'ok': {'text': '追加メンバー確認', 'type': 'positive'},
          'cancel': {'text': 'キャンセル', 'type': 'negative'}
        },
        'block': {
          'addMember': {
            'item': {
              'addMemberBody': {
                'type': 'loading',
                'id': 'modalMemberTable'
              }
            }
          }
        }
      },
      'addMemberCheck': {
        'title': '下記のメンバーを追加します',
        'class': 'layout-tab-fixed layout-padding-0',
        'footer': {
          'ok': {'text': '追加する', 'type': 'positive'},
          'cancel': {'text': 'メンバーの選択をやり直す', 'type': 'negative'}
        },
        'block': {
          'addMember': {
            'item': {
              'addMemberBody': {
                'type': 'loading',
                'id': 'modalAddMemberTable'
              }
            }
          }
        }
      },
      'addMemberRunning': {
        'title': 'メンバーを追加しています',
        'block': {
          'addMember': {
            'item': {
              'addMemberBody': {
                'type': 'loading'
              }
            }
          }
        }
      },
      'removeMember': {
        'id': 'remove-member-modal',
        'title': '下記のメンバーを削除します',
        'class': 'layout-tab-fixed layout-padding-0',
        'footer': {
          'ok': {'text': '削除', 'type': 'danger'},
          'cancel': {'text': 'キャンセル', 'type': 'negative'}
        },
        'block': {
          'addMember': {
            'item': {
              'addMemberBody': {
                'type': 'loading',
                'id': 'modalMemberTable'
              }
            }
          }
        }
      },
      'removeMemberRunning': {
        'title': 'メンバーを削除しています',
        'block': {
          'removeMember': {
            'item': {
              'removeMemberBody': {
                'type': 'loading'
              }
            }
          }
        }
      },
      'roleInfo': {
        'title': 'ロールごとの可能な操作',
        'class': 'layout-padding-0',
        'footer': {
          'ok': {'text': 'OK', 'type': 'positive'},
        },
        'block': {
          'roleInfo': {
            'item': {
              'roleInfoBody': {
                'type': 'loading',
                'id': 'roleInfoBody'
              }
            }
          }
        }
      }
    };
    const modalParameter = {};
    const modal = new modalFunction( modalData, modalParameter ),
          subModal = new modalFunction( modalData, modalParameter );

    /* -------------------------------------------------- *

        メンバー追加、ロール変更モーダル

     * -------------------------------------------------- */
    const memberModal = function( type, data ){
      
      // Table情報
      const tableHeader = [];
      
      tableHeader.push({'type': 'attr', 'attr': 'user-id'});
      if ( type === 'add') tableHeader.push({'title': '選択', 'id': 'row-all','type': 'rowCheck', 'width': '48px'});
      tableHeader.push({'title': 'ユーザ名', 'type': 'text', 'width': 'auto', 'align': 'left', 'sort': 'on', 'filter': 'on'});
      for ( let i = 0; i < g_roleLength; i++ ) {
          if(!canOwnerRoleSetting() && g_roleList[i].role_id == "owner") continue;

          if ( type === 'remove') {
              tableHeader.push({
                  'title': g_roleList[i].name, 'id': g_roleList[i].role_id, 'type': 'status', 'width': '8%', 'align': 'center', 'sort': 'on', 'filter': 'on', 'q': g_roleList[i].note
              });
          } else {
              tableHeader.push({
                'title': g_roleList[i].name, 'id': g_roleList[i].role_id, 'type': 'checkbox', 'width': '8%', 'align': 'center', 'q': g_roleList[i].note
              });
          }
      }
      tableHeader.push({'title': '', 'type': 'allCheck', 'width': '8%'});
      
      // Table表示用データ
      const modalMemberList = [],
            modalRoleList = {},
            rows = data.member.rows,
            rowsLength = rows.length,
            rolesInit = {};
      data.roleChengeList = {};
      for ( let i = 0; i < rowsLength; i++ ) {
          if ( type !== 'add') {
              
              // 選択済みのユーザID
              const selectedMemberVal = $table.find('.et-cb-i[name="' + et.tableID + '-row-all"]').val(),
                    selectedMemberID = selectedMemberVal.split(',');
              if ( selectedMemberVal !== '' && selectedMemberID.indexOf( rows[i].user_id ) === -1 ) continue;
              
              // ロール選択状態
              const memberRole = [],
                    memberRoleLength = rows[i].roles.length;

              for ( let j = 0; j < memberRoleLength; j++ ) {

                  // If you do not have the owner change authority, the owner setting is excluded.
                  // オーナー変更権限が無いときは、オーナの設定は除外する
                  if(!canOwnerRoleSetting() && rows[i].roles[j].kind == "owner") continue;

                  memberRole.push( rows[i].roles[j].kind );
              }
              rolesInit[rows[i].user_id] = memberRole.join(',');
              
              for ( let j = 0; j < g_roleLength; j++ ) {

                  // If you do not have the owner change authority, the owner setting is excluded.
                  // オーナー変更権限が無いときは、オーナの設定は除外する
                  if(!canOwnerRoleSetting() && g_roleList[j].role_id == "owner") continue;

                  const tableRoleID = data.table.tableID + '-' + g_roleList[j].role_id;
                  if ( modalRoleList[tableRoleID] === undefined ) {
                      modalRoleList[tableRoleID] = [];
                  }
                  if ( memberRole.indexOf( g_roleList[j].role_id ) !== -1 ) {
                      modalRoleList[tableRoleID].push( rows[i].user_id );
                  }
              }    
          }
          const rowsList = [];
          rowsList.push( rows[i].user_id );
          if ( type === 'add') rowsList.push( rows[i].user_id );
          rowsList.push( rows[i].username );
          for ( let j = 0; j < g_roleLength; j++ ) {

            // If you do not have the owner change authority, the owner setting is excluded.
            // オーナー変更権限が無いときは、オーナの設定は除外する
            if(!canOwnerRoleSetting() && g_roleList[j].role_id == "owner") continue;

            rowsList.push( rows[i].user_id );
          }
          rowsList.push('');
          modalMemberList.push(rowsList);
      }      
      
      // Table作成
      if ( type === 'add') {
        data.table.setup('#modalMemberTable', tableHeader, modalMemberList );
        // チェックがあるかチェック
        const tableID = data.table.tableID;
        data.table.$table.find('.et-cb-i[name="' + tableID + '-row-all"]').on('change', function(){          
            if ( $(this).val() === '' ) {
               modal.$modal.find('.epoch-button[data-button="ok"]').prop('disabled', true );
            } else {
               modal.$modal.find('.epoch-button[data-button="ok"]').prop('disabled', false );
            }
          });
      } else {
        data.table.setup('#modalMemberTable', tableHeader, modalMemberList, {'checked': modalRoleList } );
        // 変更があるかチェック
        data.table.$table.on('change', '.et-cb', function(){
          const $check = $( this ),
                userID = $check.val(),
                $tr = $check.closest('.et-r'),
                check = [];
                
          $tr.find('.et-cb:checked').each(function(){
            check.push($(this).attr('data-type'));
          });
          if ( rolesInit[userID] === check.join(',')) {
            if ( data.roleChengeList[userID] ) delete data.roleChengeList[userID]; 
          } else {
            data.roleChengeList[userID] = 1;
          }
          if ( Object.keys( data.roleChengeList ).length === 0 ) {
               modal.$modal.find('.epoch-button[data-button="ok"]').prop('disabled', true );
          } else {
               modal.$modal.find('.epoch-button[data-button="ok"]').prop('disabled', false );
          }
        });
      }
      
      // ロール詳細
      roleListButton( data.table );
      
    };
    
    /* -------------------------------------------------- *

        ロール詳細リスト

     * -------------------------------------------------- */
    
    // ロール詳細テーブル
    const roleInfoTable = new epochTable(),
          roleInfoBody = [];
          
    const roleInfoHeader = [{
      'title': '可能な操作', 'type': 'text'
    }];
    for ( let i = 0; i < g_roleLength; i++ ) {
      roleInfoHeader.push({
          'title': g_roleList[i].name, 'type': 'status', 'width': '8%', 'align': 'center', 'list': {'1': '可', '0': '不可'}
      });
    }
    for ( let i = 0; i < roleOperationLength; i++ ) {
      roleInfoBody[i] = [roleOperationList[i].name];
      for ( let j = 0; j < g_roleLength; j++ ) {
        if ( roleOperationList[i].roles.indexOf(g_roleList[j].role_id) !== -1 ) {
          roleInfoBody[i].push(1);
        } else {
          roleInfoBody[i].push(0);
        }
      }
    }
    
    const roleListButton = function( data ){
      data.$table.find('.eth').append('<div class="eth-bt"><button class="et-bt role-info-button">ロール詳細</butto></div>');
      data.$table.find('.role-info-button').on('click', function(){
        subModal.open('roleInfo',{
          'callback': function(){
            roleInfoTable.setup('#roleInfoBody', roleInfoHeader, roleInfoBody, {'filter': 'off', 'paging': 'off'});
          }
        },'none','sub');
      });           
    };
    roleListButton(et);     
     
    /* -------------------------------------------------- *

        ロール変更

     * -------------------------------------------------- */
    const roleSelectModal = function( data ){
      memberModal('role', data );
    };
    
    /* -------------------------------------------------- *

        ロール変更確認

     * -------------------------------------------------- */
    const roleSelectCheck = function( data ){
      // メンバーリストから変更済みをフィルタする
      const filterList = data.member.rows.filter(function(v){
        if ( data.roleChengeList[ v.user_id ] ) return true;
      });
      const roleChangeMembers = $.extend( true, [], filterList );
      
      if ( roleChangeMembers.length ) {
        // 選択したメンバーのロール
        const roleChangeMemberLength = roleChangeMembers.length,
              selectedRole = selectedRoleList( data );
        for ( let i = 0; i < roleChangeMemberLength; i++ ) {
          roleChangeMembers[i].roles = [];
          data.member.rows[i].new ='';
          for ( let j = 0; j < g_roleLength; j++ ) {
            if ( selectedRole[g_roleList[j].role_id] ) {
              if ( selectedRole[g_roleList[j].role_id].indexOf( roleChangeMembers[i].user_id ) !== -1 ) {
                roleChangeMembers[i].roles.push({'kind': g_roleList[j].role_id });
              }
            }
          }
        }

        if(canOwnerRoleSetting()) {
          // Check if there is at least one member who will eventually become the owner when you have the authority to set the owner
          // オーナーの設定権限があるとき、最終的にオーナーとなるメンバーが一人以上いるかチェックする

          if(roleChangeMembers.findIndex(chMember => chMember.roles.findIndex(chRole => chRole.kind == "owner") != -1 ) == -1) {
            // When the change member does not have an owner
            // 変更メンバーにオーナーがいないとき

            // If the owner authority of all registered owners is released, an error will occur.
            // 登録済みのオーナー全員のオーナー権限が解除されていたら、エラーとする
            if(g_owners.filter(
              (owner) => {
                if(roleChangeMembers.findIndex((cgMember) => {
                  return ((cgMember.user_id == owner) && (cgMember.roles.findIndex(chRole => chRole.kind == "owner") == -1));
                 } ) != -1 ) {
                  return false;
                } else {
                  return true;
                }
              }
            ) == 0 ) {
              alert(getText("EP010-0414", "最低1人以上のオーナーは必要です"));
              return;
            }              
          }
        }

        // Restores the owner's settings to the initial state when there is no owner setting authority
        // オーナー設定権限が無いとき、オーナーの設定を初期状態に復元する
        if(!canOwnerRoleSetting()) {
          roleChangeMembers.forEach((chMember) => {
            if(g_owners.indexOf(chMember.user_id) != -1 && chMember.roles.findIndex(chRole => chRole.kind == "owner") == -1) {
              chMember.roles.push({"kind":"owner"});
            }
          });
        }

        // 確認モーダル
        subModal.open('roleChangeCheck',{
          'ok': function(){
            subModal.subClose();
            subModal.open('roleChangeRunning', {
              'callback': function(){
                // ロール変更処理
                new Promise((resolve, reject) => {
                  post_data = {
                    rows: roleChangeMembers,
                    role_update_at: role_update_at,
                  }
                  console.log('[CALL] POST /workspace/{id}/member');
                  $.ajax({
                      "type": "POST",
                      "url": URL_BASE + "/api/workspace/{workspace_id}/member".replace('{workspace_id}',workspace_id),
                      "data": JSON.stringify(post_data),
                      contentType: "application/json",
                      dataType: "json",
                  }).done(function(data) {
                      console.log('[DONE] POST /workspace/{id}/member');
                      resolve();
                  }).fail((jqXHR, textStatus, errorThrown) => {
                    console.log('[FAIL] POST /workspace/{id}/member');
                    if(jqXHR.status == 401) {
                      reject(getText("EP010-0415", "ロールを変更する権限がありません"));
                    } else {
                      try {
                        reject(JSON.parse(jqXHR.responseText).errorDetail);
                      } catch(e) {
                        reject();
                      }
                    }
                  });
                }).then(() => {
                  window.location.reload();
                }).catch((message) => {
                  alert(message);
                  window.location.reload();
                });
              }
            }, 320, 'progress');
          },
          'callback': function(){
            const modalRoleChangeMemberHeader = memberListHeader.concat();
            modalRoleChangeMemberHeader[0] = {'type': 'attr', 'attr': 'user-id'};
            
            const roleChangeTable = new epochTable();
            roleChangeTable.setup('#modalRoleChangeTable', modalRoleChangeMemberHeader, updateTableMemberList( roleChangeMembers ), {'filter': 'off'} );
          }
        },'none','sub');
      } else {
        alert(getText("EP010-0416", "ロールの変更がありません。"));
      }
    };
    /* -------------------------------------------------- *

       選択済みのロールリストを作成する

     * -------------------------------------------------- */
    const selectedRoleList = function( data ){
      const tableID = data.table.tableID,
            role = {};
      for ( let i = 0; i < g_roleLength; i++ ) {
        if(!canOwnerRoleSetting() && g_roleList[i].role_id == "owner") continue;
        const roleVal = data.table.$table.find('.et-cb-i[name="' + tableID + '-' + g_roleList[i].role_id + '"]').val();
        if ( roleVal !== '' ) role[g_roleList[i].role_id] = roleVal.split(',');
      }
      return role;
    };
    
    /* -------------------------------------------------- *

        メンバー追加モーダル

     * -------------------------------------------------- */
    const addMemberModal = function( data ){
      // メンバー追加用リストの読み込みが終わったら
      setTimeout(function(){
        getMemberList('add').then((member) => {
          data['member'] = member;
          memberModal('add', data );
        })
      }, 100 );
    };
    /* -------------------------------------------------- *

        メンバー追加確認・追加処理

     * -------------------------------------------------- */
    const addMemberCheck = function( data ){
      const tableID = data.table.tableID,
            members = data.member.rows,
            selectID = data.table.$table.find('.et-cb-i[name="' + tableID + '-row-all"]').val();
      if ( selectID !== '') {
        // 選択したメンバー
        const selectIDArray = selectID.split(',');
        const addMembers = members.filter(function(v){
          if ( selectIDArray.indexOf(v.user_id) !== -1 ) return true;
        });
        const addMemberLength = addMembers.length;
        // 選択したメンバーのロール
        const selectedRole = selectedRoleList( data );
        for ( let i = 0; i < addMemberLength; i++ ) {
          if ( typeof(addMembers[i].roles) == "undefined" ) addMembers[i].roles = []
          for ( let j = 0; j < g_roleLength; j++ ) {
            if ( selectedRole[g_roleList[j].role_id] ) {
              if ( selectedRole[g_roleList[j].role_id].indexOf( addMembers[i].user_id ) !== -1 ) {
                addMembers[i].roles.push({'kind': g_roleList[j].role_id });
              }
            }
          }
        }
        // 確認モーダル
        subModal.open('addMemberCheck',{
          'ok': function(){
            subModal.subClose();
            subModal.open('addMemberRunning', {
              'callback': function(){
                // メンバー追加処理
                new Promise((resolve, reject) => {
                  post_data = {
                    rows: addMembers,
                    role_update_at: role_update_at,
                  }
                  console.log('[CALL] POST /workspace/{id}/member');
                  $.ajax({
                      "type": "POST",
                      "url": URL_BASE + "/api/workspace/{workspace_id}/member".replace('{workspace_id}',workspace_id),
                      "data": JSON.stringify(post_data),
                      contentType: "application/json",
                      dataType: "json",
                  }).done(function(data) {
                      console.log('[DONE] POST /workspace/{id}/member');
                      resolve();
                  }).fail((jqXHR, textStatus, errorThrown) => {
                    console.log('[FAIL] POST /workspace/{id}/member');
                    if(jqXHR.status == 401) {
                      reject("メンバーを追加する権限がありません");
                    } else {
                      try {
                        reject(JSON.parse(jqXHR.responseText).errorDetail);
                      } catch(e) {
                        reject();
                      }
                    }
                  });
                }).then(() => {
                  window.location.reload();
                }).catch((message) => {
                  alert(message);
                  window.location.reload();
                });
              }
            }, 320, 'progress');
          },
          'callback': function(){
            const modalAddMemberHeader = memberListHeader.concat();
            modalAddMemberHeader[0] = {'type': 'attr', 'attr': 'user-id'};
            
            const addMemberTable = new epochTable();
            addMemberTable.setup('#modalAddMemberTable', modalAddMemberHeader, updateTableMemberList( addMembers ), {'filter': 'off'} );
          }
        },'none','sub');
        
      } else {
        alert(getText("EP010-0418", "メンバーが選択されていません"));
      }
    };
        
    /* -------------------------------------------------- *

        メンバー削除モーダル

     * -------------------------------------------------- */
    const removeMemberModal = function( data ){
      // メンバー削除ヘッダー
      const modalRemoveMemberHeader = memberListHeader.concat();
      modalRemoveMemberHeader[0] = {'type': 'attr', 'attr': 'user-id'};
      // 選択済みのユーザID
      const selectedMemberVal = $table.find('.et-cb-i[name="' + et.tableID + '-row-all"]').val(),
            selectedMemberID = selectedMemberVal.split(',');
      // 選択済みのユーザをフィルタ
      data.modalRemoveMemberList = memberListBody.filter(function(v){
        if ( selectedMemberID.indexOf( v[0]) !== -1 ) return true;
      });
      // 削除するメンバーリスト
      data.removeMemberList = memberList.rows.filter(function(v){
        if ( selectedMemberID.indexOf( v.user_id ) !== -1 ) return true;
      });

      // If you do not have the owner setting authority and try to cancel the owner, an error will occur.
      // オーナーの設定権限が無くて、オーナーを解除しようとしたときはエラーにする
      if(!canOwnerRoleSetting()) {
        if( data.removeMemberList.findIndex(member => (member.roles.findIndex(role => role.kind == "owner") != -1)) != -1 ) {
          alert(getText("EP010-0417", "オーナーを解除する権限がありません"));
          modal.close();
          return;
        }
      }

      // An error will occur if all owners try to be released
      // オーナーが全員解除されてようとしたらエラーにする
      if(g_owners.filter(owner => data.removeMemberList.findIndex(rmMember => owner == rmMember.user_id) == -1 ).length == 0) {
        alert(getText("EP010-0414", "最低1人以上のオーナーは必要です"));
        modal.close();
        return;
      }

      data.table.setup('#modalMemberTable', modalRemoveMemberHeader, data.modalRemoveMemberList, {'filter': 'off'} );

    };
    /* -------------------------------------------------- *

        メンバー削除処理

     * -------------------------------------------------- */
    const removeMember = function( data ){
      subModal.open('removeMemberRunning', {
        'callback': function(){
          // メンバー削除処理
          new Promise((resolve, reject) => {
            post_data = {
              rows: data.removeMemberList.map((item) => { return { user_id: item.user_id, roles: [], username: item.username } } ),
              role_update_at: role_update_at,
            }
            console.log('[CALL] POST /workspace/{id}/member');
            $.ajax({
                "type": "POST",
                "url": URL_BASE + "/api/workspace/{workspace_id}/member".replace('{workspace_id}',workspace_id),
                "data": JSON.stringify(post_data),
                contentType: "application/json",
                dataType: "json",
            }).done(function(data) {
                console.log('[DONE] POST /workspace/{id}/member');
                resolve();
            }).fail((jqXHR, textStatus, errorThrown) => {
                console.log('[FAIL] POST /workspace/{id}/member');
                if(jqXHR.status == 401) {
                  reject("メンバーを削除する権限がありません");
                } else {
                  try {
                    reject(JSON.parse(jqXHR.responseText).errorDetail);
                  } catch(e) {
                    reject();
                  }
                }
            });
          }).then(() => {
            window.location.reload();
          }).catch((message) => {
            alert(message);
            window.location.reload();
          });
        }
      }, 320, 'progress');
    };
    

    // ヘッダーボタン操作
    $('.content-header').find('.content-menu-button').on('click', function(){
      const $headerButton = $( this ),
            headerButtonType = $headerButton.attr('data-button');
      
      switch( headerButtonType ) {
        
        // メンバー追加
        case 'addMember': {
          const memberData = {
            'table': new epochTable()
          };
          modal.open('addMember', {
            'ok': function(){
              addMemberCheck( memberData );
            },
            'callback': function(){
              modal.$modal.find('.epoch-button[data-button="ok"]').prop('disabled', true );
              addMemberModal( memberData );
            }
          }, 'none');
        } break;
        
        case 'roleChange': {
          const memberData = {
            'table': new epochTable(),
            'member': memberList
          };
          modal.open('roleChange', {
            'ok': function(){
              roleSelectCheck( memberData );
            },
            'callback': function(){
              modal.$modal.find('.epoch-button[data-button="ok"]').prop('disabled', true );
              roleSelectModal( memberData );
            }
          }, 'none');
         } break;
         
        case 'removeMember': {
          const memberData = {
            'table': new epochTable(),
            'member': memberList
          };
          modal.open('removeMember', {
            'ok': function(){
              removeMember( memberData );
            },
            'callback': function(){
              removeMemberModal( memberData );
            }
          }, 'none');
         } break;
      }
    
    });
    
    
    
    
}

/*
  Get workspace - ワークスペース情報の取得
*/
$(function() {
  $.ajax({
    "type": "GET",
    "url": URL_BASE + "/api/workspace/{workspace_id}".replace('{workspace_id}',workspace_id)
  }).done(function(data) {
      console.log('[DONE] /workspace/{id}');
      role_update_at = data.rows[0].role_update_at;

      $("#member-list-title").text(data.rows[0].common.name + "のメンバー一覧");
      $(".content-note-inner").text(data.rows[0].common.name + "のメンバー一覧です。");
  }).fail((jqXHR, textStatus, errorThrown) => {
    console.log('[FAIL] /workspace/{id}');
    alert(getText("EP010-0001", "この画面を表示する権限がありません"));
    window.location = "/";
  });
})

var g_memberList = {"rows":[]};
var g_owners = [];

function getMemberList(type) {
  return new Promise((resolve, reject) => {
    if ( type === 'add') {
      // Get all users to be added - 追加の対象となる全てのユーザを取得する
      console.log('[CALL] /api/member');
      $.ajax({
          "type": "GET",
          "url": URL_BASE + "/api/member"
      }).done(function(data) {
        console.log('[DONE] /api/member');

        // Omit users who are already members of the workspace - 既にワークスペースのメンバーとなっているユーザは省く
        member = data.rows.filter((user) => {
          return g_memberList.rows.filter(member => {return (member.user_id == user.user_id)}).length == 0;
        });
        resolve({"rows":member});
      }).fail((jqXHR, textStatus, errorThrown) => {
          console.log('[FAIL] /api/member');
          reject();
      });
    } else {
      // Get a member of the workspace - ワークスペースのメンバーを取得する
      console.log('[CALL] /workspace/{id}/member');
      $.ajax({
        "type": "GET",
        "url": URL_BASE + "/api/workspace/{workspace_id}/member".replace('{workspace_id}',workspace_id)
      }).done(function(data) {
          console.log('[DONE] /workspace/{id}/member');
          g_memberList = data;
          g_owners = g_memberList.rows.filter((member) => member.roles.findIndex(role => (role.kind == "owner")) != -1).map(member => member.user_id);
          console.log(g_owners);
          resolve(g_memberList);
      }).fail((jqXHR, textStatus, errorThrown) => {
          console.log('[FAIL] /workspace/{id}/member');
          reject();
      });
    }
  });
}

function show_buttons_by_role() {
  // Waiting for API data acquisition - APIのデータ取得待ち
  if(currentUser == null) { setTimeout(show_buttons_by_role, 100); return; }
  if(!currentUser.data)   { setTimeout(show_buttons_by_role, 100); return; }

  styleElement = document.createElement('style');
  document.head.appendChild(styleElement);

  if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-member-add".replace('{ws_id}',workspace_id)) != -1) {
    $('#button_add_member').css("display","");
  }
  if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-member-role-update".replace('{ws_id}',workspace_id)) != -1) {
    $('#button_role_change').css("display","");
  }
  if(currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-member-add".replace('{ws_id}',workspace_id)) != -1) {
    $('#button_remove_member').css("display","");
  } else {
    // Hide the checkbox to select a member if you do not have permission to add a member
    // メンバーの追加権限が無いときはメンバーを選択するチェックボックスを非表示にする
    styleElement.sheet.insertRule("div.et-cbw { visibility: hidden; }");
  }

  // List display after setting the role - ロールの設定が終わってからリスト表示
  getMemberList().then((memberList) => {
    workspaceMemberList(memberList);
  })
}
$(function () {show_buttons_by_role()})

// Does the login person have owner setting authority?
// ログイン者がオーナー設定権限を持っているか
function canOwnerRoleSetting() {
  return (currentUser.data.composite_roles.indexOf("ws-{ws_id}-role-owner-role-setting".replace('{ws_id}',workspace_id)) != -1);
}
