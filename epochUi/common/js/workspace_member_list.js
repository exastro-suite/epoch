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
$(document).ready(() => {
    var workspace_id = (new URLSearchParams(window.location.search)).get('workspace_id');
    var epoch_member = null;
    var workspace_member = null;
    var role_update_at = null;

    // 画面表示
    function document_ready() {
        new Promise((resolve, reject) => {
            // メンバー全員の取得
            console.log('[CALL] /api/member');
            $.ajax({
                "type": "GET",
                "url": URL_BASE + "/api/member"
            }).done(function(data) {
                console.log('[DONE] /api/member');
                epoch_members = data;
                resolve();
            }).fail((jqXHR, textStatus, errorThrown) => {
                console.log('[FAIL] /api/member');
                reject();
            });

        }).then(() => { return new Promise((resolve, reject) =>  {
            console.log('[CALL] /workspace/{id}/member');
            $.ajax({
                "type": "GET",
                "url": URL_BASE + "/api/workspace/{workspace_id}/member".replace('{workspace_id}',workspace_id)
            }).done(function(data) {
                console.log('[DONE] /workspace/{id}/member');
                workspace_members = data;
                resolve();
            }).fail((jqXHR, textStatus, errorThrown) => {
                console.log('[FAIL] /workspace/{id}/member');
                reject();
            });

        })}).then(() => { return new Promise((resolve, reject) =>  {
            console.log('[CALL] /workspace/{id}');
            $.ajax({
                "type": "GET",
                "url": URL_BASE + "/api/workspace/{workspace_id}".replace('{workspace_id}',workspace_id)
            }).done(function(data) {
                console.log('[DONE] /workspace/{id}');
                role_update_at = data.rows[0].update_at;
                resolve();
            }).fail((jqXHR, textStatus, errorThrown) => {
                console.log('[FAIL] /workspace/{id}');
                reject();
            });
        })}).then(() => {
            console.log('[DONE] API CALLS');
            // API結果に表示
            $("#epoch_members").val(JSON.stringify(epoch_members, null, "  "));
            $("#workspace_members").val(JSON.stringify(workspace_members, null, "  "));

            //画面表示
            html_text =     '<table style="width:100%;"><caption>メンバー一覧</caption>'
                        +   '<tr><th align="left">管理者</th></tr>';
            for(var i in epoch_members.rows) {
                html_text += '<tr><td><label><input type="checkbox" value="{user_id}" class="check_manager" {checked}>{username}</label></td></tr>'
                    .replace('{username}',epoch_members.rows[i].username)
                    .replace('{user_id}',epoch_members.rows[i].user_id)
                    .replace('{checked}',have_role(epoch_members.rows[i].user_id, 'manager')? 'checked': '')
            }
            html_text += '</table>';
            $("#member_list_table").html(html_text);
        }).catch(() => {
            console.log('[FAIL] document_ready');
        });
    }
    document_ready();

    // 戻るボタン
    $("#button_return").click(() => {
        window.location = URL_BASE;
    })

    // 登録ボタン
    $("#button_register").click(() => {
        console.log("[CALL] #button_register.click");
        data_json = {
            rows : [],
            "role_update_at": role_update_at,
        }

        $(".check_manager").each((i, obj) => {
            roles = [];
            if(have_role(obj.value, "owner")) {
                roles.push({"kind":"owner"});
            }
            if(obj.checked) {
                roles.push({"kind":"manager"});
            }
            data_json.rows.push(
                {
                    "user_id" : obj.value,
                    "username": username(obj.value),
                    "roles" : roles
                }
            );
        });

        $("#post_data").val(JSON.stringify(data_json,null, "  "));

        // メンバー更新
        new Promise((resolve, reject) =>{
            console.log('[CALL] POST /workspace/{id}/member');
            $.ajax({
                "type": "POST",
                "url": URL_BASE + "/api/workspace/{workspace_id}/member".replace('{workspace_id}',workspace_id),
                "data": JSON.stringify(data_json),
                contentType: "application/json",
                dataType: "json",
            }).done(function(data) {
                console.log('[DONE] POST /workspace/{id}/member');
                resolve();
            }).fail((jqXHR, textStatus, errorThrown) => {
                console.log('[FAIL] POST /workspace/{id}/member');
                reject();
            });
        }).then(() => {
            console.log('[DONE] メンバー更新');
            alert("メンバーを更新しました");
        }).catch(() => {
            console.log('[FAIL] メンバー更新');
            alert("メンバーの更新に失敗しました");
        });
    })

    // ロール有無の確認
    function have_role(user_id, kind) {
        for(var i in workspace_members.rows) {
            if(workspace_members.rows[i].user_id == user_id) {
                for(var j in workspace_members.rows[i].roles) {
                    if(workspace_members.rows[i].roles[j].kind == kind) {
                        return true;
                    }
                }
                return false;
            }
        }
        return false;
    }

    // ユーザ名取得
    function username(user_id) {
        for(var i in epoch_members.rows) {
            if(epoch_members.rows[i].user_id == user_id) {
                return epoch_members.rows[i].username;
            }
        }
        return null;
    }
})