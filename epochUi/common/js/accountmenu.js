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
// アカウントメニュー処理
$(function(){

  //-----------------------------------------------------------------------
  // ログイン情報取得
  //-----------------------------------------------------------------------
  function getCurrentUser() {
    console.log("[START] function getCurrentUser");

    $.ajax({
      "type": "GET",
      "url": api_url_base + "/user/current",
    }).done(function(data) {
      console.log("[TRACE] function getCurrentUser response:" + JSON.stringify(data));

      $('.login-user-name').text(data["info"]["firstName"] + " " + data["info"]["lastName"]);
      $('#username').text(data["info"]["username"]);
      $('#account_email').text(data["info"]["email"]);

    }).fail((jqXHR, textStatus, errorThrown) => {
      console.log("[TRACE] function getCurrentUser $.ajax.fail");
    });
  }
  $(document).ready(function(){ getCurrentUser(); });

  //-----------------------------------------------------------------------
  // アカウントメニュー押下
  //-----------------------------------------------------------------------
  $('.header-menu-account').on('click',() => {
    $('#modal-account-container').css('display','flex');
  });
  $('#modal-account-close').on('click',() => {
    $('#modal-account-container').css('display','none');
  });
  //-----------------------------------------------------------------------
  // パスワード変更
  //-----------------------------------------------------------------------
  $('#password-update').on('click',() => {
    console.log("[START] password-update");

    if ( $('#password-now').val() == "" ) {
      alert("現パスワードを入力してください");
      return;
    }
    if ( $('#password-new').val() == "" ) {
      alert("新パスワードを入力してください");
      return;
    }
    if ( $('#password-new-confirm').val() == "" ) {
      alert("新パスワード（確認）を入力してください");
      return;
    }
    if ( $('#password-new').val() != $('#password-new-confirm').val() ) {
      alert("新パスワードと新パスワード（確認）が一致していません\n入力内容を確認してください");
      return;
    }

    $.ajax({
      type: "PUT",
      url: api_url_base + "/user/current/password",
      data: JSON.stringify({
        "current_password" : $('#password-now').val(),
        "password" : $('#password-new').val()
      }),
      contentType: "application/json",
      dataType: "json"
    }).done(function(data) {
      alert("パスワードを更新しました");
      $('#password-now').val("");
      $('#password-new').val("");
      $('#password-new-confirm').val("");

    }).fail((jqXHR, textStatus, errorThrown) => {
      if(jqXHR.status == "401") {
        alert("現パスワードが違います。パスワードを修正して再度実施してください");
      } else {
        alert("パスワードの更新に失敗しました。しばらくたってからもう一度実施してください");
      }
    });
  });
  //-----------------------------------------------------------------------
  // ログアウトリンク押下
  //-----------------------------------------------------------------------
  $('#logout-link').on('click',() => {
    window.location= "/oidc-redirect/?logout=" + encodeURIComponent(window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + "/");
  });
});
