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

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   画面共通
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
var URL_BASE=window.location.protocol + "//" + window.location.hostname + ":" + window.location.port

function initialScreen() {

    const $window = $( window ),
          $body = $('body'),
          $container =$('#container'),
          $header = $('#header'),
          $side = $('#side');

    const storage = new webStorage();
    
    /* -------------------------------------------------- *\
       ページ表示後一定時間アニメーションさせない
    \* -------------------------------------------------- */
    const notDuration = function( $target, notDurationTime ) {
        const notDurationClass = 'not-duration';
        $target.addClass( notDurationClass );
        setTimeout( function(){
            $target.removeClass( notDurationClass );
        }, notDurationTime );
    };
    
    /* -------------------------------------------------- *\
       サイドメニュー開閉処理
    \* -------------------------------------------------- */
    const sideMenuStorageKey = 'epoch_side_menu_status',
          sideMenuCloseClass = 'close',
          sideMenuStatus = storage.get( sideMenuStorageKey );

    if ( sideMenuStatus !== false && sideMenuStatus === sideMenuCloseClass ) {
        notDuration( $side, 300 );
        $side.addClass( sideMenuCloseClass );
    }
    $header.find('.main-menu-switch').on('click', function(){
        if ( $side.is('.' + sideMenuCloseClass ) ) {
            storage.remove( sideMenuStorageKey );
            $side.removeClass( sideMenuCloseClass );
        } else {
            storage.set( sideMenuStorageKey, sideMenuCloseClass );
            $side.addClass( sideMenuCloseClass );
        }
    });
    
    /* -------------------------------------------------- *\
       title属性ポップアップ
    \* -------------------------------------------------- */
    $body.on({
      'mouseenter.popup': function(){
        const $target = $( this ),
              title = $target.attr('title');
        if ( title !== undefined ) {
          // buttonかつdisabledの場合
          if ( $target.is('button') && $target.prop('disabled') === true ) return false;        
          // デフォルトtitileを無効にするためいったん削除
          $target.removeAttr('title');
          
          // Popup追加
          const popupClass = ( $target.is('.epoch-popup-m') )? 'epoch-popup-m-block': 'epoch-popup-block';
          const $popup = $('<div/>', {
            'class': popupClass,
            'text': title
          }).append('<div class="epoch-popup-arrow"><span></span></div>')
          const $arrow = $popup.find('.epoch-popup-arrow');
          $body.append( $popup );
          
          let s = 1; // scale
          
          // 対象がワークスペースイメージ内の場合scaleを取得
          const $wsImage = $target.closest('.workspace-setting-image');
          if ( $wsImage.length && $wsImage.css('transform') !== undefined ) {
            const matrix = $wsImage.css('transform').replace(/^matrix\((.+)\)/, '$1');
            s = matrix.split(',')[0];
          }
          
          // 位置
          const m = 8,
                wW = $window.width(),
                tW = $target.outerWidth() * s,
                tH = $target.outerHeight() * s,
                tL = $target.offset().left,
                tT = $target.offset().top,
                pW = $popup.outerWidth(),
                pH = $popup.outerHeight();

          let l = ( tL + tW / 2 ) - ( pW / 2 ),
              t = tT - pH - m;
          
          // Windowサイズを超える場合は調整
          if ( t <= 0 )  {
            $popup.addClass('epoch-popup-bottom');
            t = tT + tH + m;
          } else {
            $popup.addClass('epoch-popup-top');
          }
          if ( wW < l + pW ) l = wW - pW - m;
          if ( l <= 0 ) l = m;
          
          $popup.css({
            'width': pW,
            'height': pH,
            'left': l,
            'top': t
          });

              // 矢印の位置
              const aL = ( tL + ( tW / 2 )) - l;
              $arrow.css('left', aL );

          $target.on({
            'mouseleave.popup ': function(){
              const $popup = $body.find('.epoch-popup-block, .epoch-popup-m-block'),
                    title = $popup.text();
              $popup.remove();

              // titleを戻す
              $target.off('mouseleave.popup').attr('title', title );        
            }
          });
          
          // 対象が存在するか一定間隔でチェックし、消えていた場合ポップアップを削除する
          const targetCheck = function(){
            if ( $target.is(':visible') ) {
              if ( $popup.is(':visible') ) {
                setTimeout( targetCheck, 200 );
              }
            } else {
              $popup.remove();
            }              
          };
          targetCheck();
        }
      }
    }, '.epoch-popup, .epoch-popup-m');
        
    const user = new userInfo();
    user.init('user-info');
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ユーザ情報
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function userInfo(){}
userInfo.prototype = {
  // ユーザ情報読み込み
  'init': function( id ){
    const u = this;
    
    u.$info = $('#' + id );
    u.infoData = {'password':{}};
    u.modal = new modalFunction( u.modalData, u.infoData );
    u.common = new epochCommon();
    
    setTimeout(function(){
      // ユーザ情報を読み込み
      console.log("[START] get user info");

      $.ajax({
        "type": "GET",
        "url": URL_BASE + "/api/user/current",
      }).done(function(data) {
        console.log("[TRACE] get user info response:" + JSON.stringify(data));

        u.data = {
          "id": data["info"]["id"],
          "username": data["info"]["username"],
          "enabled": data["info"]["enabled"],
          "firstName": data["info"]["firstName"],
          "lastName": data["info"]["lastName"],
          "email": data["info"]["email"]
        };

        // ロールリスト（仮）
        try {
          u.role = JSON.parse('{"ECサイトA":["オーナー"],"ECサイトB":["更新","CD実行"],"カタログ運営サイト開発":["オーナー"],"販売管理サイト開発A":["CI結果参照"],"販売管理サイト開発B":["CD実行","CD結果"],"販売管理サイト開発C":["CD実行","CD結果"],"販売管理サイト開発D":["CD実行","CD結果"]}');
        } catch(e) {
          alert(e);
        }
      
        u.set();

      }).fail((jqXHR, textStatus, errorThrown) => {
        console.log("[TRACE] get user info $.ajax.fail");
      });      
    }, 100 );
  },
  // ユーザメニューをセット
  'set': function(){
    const u = this;
    
    u.userInfoHTML();
    
    // パスワード変更
    const changePassword = function(){
      u.modal.setParameter('password');
      
      if ( u.infoData.password['new-password-enter'] === u.infoData.password['new-password-re-enter'] ) {        
        const password = {
          'oldPassword': u.infoData.password['password-enter'],
          'newPassword': u.infoData.password['new-password-enter']
        };
        
        // クリア
        u.infoData.password = {};
        
        // パスワード更新処理
        setTimeout( function(){
          console.log("[START] password-update");

          $.ajax({
            type: "PUT",
            url: URL_BASE + "/api/user/current/password",
            data: JSON.stringify({
              "current_password" : password['oldPassword'],
              "password" : password['newPassword']
            }),
            contentType: "application/json",
            dataType: "json"
          }).done(function(data) {
            alert("パスワードを更新しました");
          }).fail((jqXHR, textStatus, errorThrown) => {
            if(jqXHR.status == "401") {
              alert("現パスワードが違います。パスワードを修正して再度実施してください");
            } else {
              alert("パスワードの更新に失敗しました。しばらくたってからもう一度実施してください");
            }
          });
          u.modal.close();
        }, 100 );
      }     
    };
    
    // ログアウト
    const logout = function(){
      // ログアウト処理
      const logoutUrl = '/oidc-redirect/?logout=' + encodeURIComponent(window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/');
      window.location.href = logoutUrl;
    };
    
    // 閉じる
    const $userIcon = u.$info.find('.login-user-info-button');
    let userInfoButtonTitle = $userIcon.attr('title');
    const userInfoClose = function(){
      u.$info.find('.user-info-detail').removeClass('open');
      $( window ).off('mousedown.useInfoClose');
      $userIcon.addClass('epoch-popup-m').removeClass('open').attr('title', userInfoButtonTitle );
    };
    
    // ボタン
    u.$info.find('.login-user-info-button, .user-info-button').on('click', function(){
      const $button = $( this ),
            type = $button.attr('data-type');
      switch( type ) {
        case 'open':
          if ( !$button.is('.open') ) {
            $button.addClass('open').mouseleave().removeClass('epoch-popup-m');
            $button.removeAttr('title');
            u.$info.find('.user-info-detail').addClass('open');
            $( window ).on('mousedown.useInfoClose', function( e ){
              if ( !$( e.target ).closest('#modal-container, .user-info-detail, .login-user-info-button').length ) {
                userInfoClose();
              }
            });
          } else {
            userInfoClose();
            $button.mouseenter();
          }
          break;
        case 'close':
          userInfoClose();
          break;
        case 'role':
          u.modal.open('roleList',{
            'ok': logout,
            'callback': function(){
              u.modal.$modal.find('#role-list-body').html( u.roleList(0) );
            }
          });
          break;
        case 'password':
          u.modal.open('changePassword',{
            'ok': changePassword
          });
          break;
        case 'logout':
          u.modal.open('logout',{
            'ok': logout,
          },'400');
          break;
      }
    });
    
  },
  'userInfoHTML': function(){
    const u = this,
          firstName = ( u.data['firstName'] !== undefined )? u.data['firstName']: 'EPOCH',
          lastName = ( u.data['lastName'] !== undefined )? u.data['lastName']: 'USER',
          name = firstName + ' ' + lastName,
          // 全角文字が含まれている場合は苗字1文字にする
          iconName = ( name.match(/[^\x20-\x7e]/) )?
            lastName.slice(0,1):
            ( firstName.slice(0,1) + lastName.slice(0,1) ).toUpperCase();
    
    u.$info.find('.login-user-name').text( name );
    
    const $userIcon = $('<span/>', {
      'class': 'login-user-icon',
      'text': iconName
    });
    u.$info.find('.login-user-info-button').append( $userIcon );
    
    const $userInfoIcon = $('<div/>', {
      'class': 'user-info-icon'
    }).append( $('<div/>', {
        'class': 'user-info-icon-image',
        'text': iconName
      })
    );
    u.$info.find('.user-info-status').append( $userInfoIcon );
    
    const $userInfoStatusText = $('<div/>', {
      'class': 'user-info-status-text'
    }).append( $('<div/>', {
        'class': 'user-info-id',
        'text': u.data['username']
      })
    ).append( $('<div/>', {
        'class': 'user-info-name',
        'text': name
      })
    );
    if ( u.data['email'] !== undefined ) {
      $userInfoStatusText.append( $('<div/>', {
          'class': 'user-info-mail',
          'text': u.data['email']
        })
      );
    }
    u.$info.find('.user-info-status').append( $userInfoStatusText );
    
    u.$info.find('.user-info-role-number').text( Object.keys( u.role ).length );
    u.$info.find('.user-info-role-wrap').append( u.roleList(5) );
  },
  'roleList': function( num ) {
    if ( num === undefined || num < 0 ) num = 0;
    const u = this;
    let html = '<ul class="user-info-role-list">',
        count = 0;
    for ( const key in u.role ) {
      if ( num !== 0 && num <= count ) break;
      html += ''
      + '<li class="user-info-role-item">'
        + '<dl class="user-info-role-card">'
          + '<dt class="user-info-role-name">'
            + '<svg viewBox="0 0 64 64" class="user-info-role-icon">'
              + '<use href="#icon-menu-workspace"></use>'
            + '</svg>'
            + u.common.textEntities( key )
          + '</dt>'
          + '<dd class="user-info-role-operation">'
            + '<ul class="user-info-role-operation-list">';
      const operationLength = u.role[key].length;
      for ( let i = 0; i < operationLength; i++ ) {
        html += '<li class="user-info-role-operation-item">' + u.role[key][i] + '</li>';
      }              
      html += ''
            + '</ul>'
          + '</dd>'
        + '</dl>'
      + '</li>';
      count++;
    }
    html += '</ul>';
    
    return html;
  },
  // モーダルデータ
  'modalData': {
    'changePassword': {
      'id': 'change-password',
      'title': 'パスワード変更',
      'footer': {
        'ok': {
          'text': '決定',
          'type': 'positive'
        },
        'cancel': {
          'text': 'キャンセル',
          'type': 'negative'
        }
      },
      'block': {
        'password': {
          'title': '現在のパスワード',
          'item': {
            'passwordEnterBlock': {
              'title': '現在のパスワード',
              'type': 'password',
              'required': 'on',
              'name': 'password-enter'            
            }
          }
        },
        'newPassword': {
          'title': '新しいパスワード',
          'item': {
            'newPasswordEnterBlock': {
              'title': '新しいパスワード',
              'type': 'password',
              'required': 'on',
              // 入力規則は一旦非表示
              // 'min': 8,
              // 'max': 32,
              // 'validation': '^(?=.*[0-9])^(?=.*[A-Z])(?=.*[a-z])(?=.*[.?/-])[a-zA-Z0-9.?/-]+$',
              // 'inputError': 'パスワードの形式が正しくありません。',
              // 'note': '数字、アルファベット大文字、アルファベット小文字、記号（. ? / -）のそれぞれ1文字以上を含めてください。',
              'name': 'new-password-enter'            
            },
            'newPasswordReEnterBlock': {
              'title': '新しいパスワード再入力',
              'type': 'password',
              'required': 'on',
              'matchTargetName': 'new-password-enter',
              'mismatchErrorMessage': 'パスワードが一致しません。',
              'name': 'new-password-re-enter'            
            }
          }
        }
      }
    },
    'roleList': {
      'id': 'role-list',
      'title': 'Role一覧',
      'footer': {
        'cancel': {
          'text': '閉じる',
          'type': 'negative'
        }
      },
      'block': {
        'role-list': {
          'item': {
            'roleListBlock': {
              'id': 'role-list-body',
              'type': 'loading',
            }
          }
        }
      }
    },
    'logout': {
      'id': 'logout',
      'title': 'ログアウト確認',
      'footer': {
        'ok': {
          'text': 'ログアウト',
          'type': 'positive'
        },
        'cancel': {
          'text': 'キャンセル',
          'type': 'negative'
        }
      },
      'block': {
        'password': {
          'item': {
            'newPasswordEnterBlock': {
              'type': 'message',
              'text': 'ログアウトしますか？'            
            }
          }
        }
      }
    }
  }
};

//-----------------------------------------------------------------------
// ログイン情報取得
//-----------------------------------------------------------------------
// function getCurrentUser() {
//   console.log("[START] function getCurrentUser");

//   $.ajax({
//     "type": "GET",
//     "url": api_url_base + "/user/current",
//   }).done(function(data) {
//     console.log("[TRACE] function getCurrentUser response:" + JSON.stringify(data));

//       $('.login-user-name').text(data["info"]["firstName"] + " " + data["info"]["lastName"]);
//       $('#username').text(data["info"]["username"]);
//       $('#account_email').text(data["info"]["email"]);

//   }).fail((jqXHR, textStatus, errorThrown) => {
//     console.log("[TRACE] function getCurrentUser $.ajax.fail");
//   });
// }

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   共通
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function epochCommon(){}
epochCommon.prototype = {
  // テキストの無害化
  'textEntities': function( text ) {
    const entities = [
      ['&', 'amp'],
      ['\"', 'quot'],
      ['\'', 'apos'],
      ['<', 'lt'],
      ['>', 'gt'],
    ];
    if ( text !== undefined && text !== null && typeof text === 'string') {
      for ( var i = 0; i < entities.length; i++ ) {
        text = text.replace( new RegExp( entities[i][0], 'g'), '&' + entities[i][1] + ';' );
      }
    }
    return text;
  },
  // 日時フォーマット
  'formatDate': function( date, format ) {
    format = format.replace(/yyyy/g, date.getFullYear());
    format = format.replace(/MM/g, ('0' + (date.getMonth() + 1)).slice(-2));
    format = format.replace(/dd/g, ('0' + date.getDate()).slice(-2));
    format = format.replace(/HH/g, ('0' + date.getHours()).slice(-2));
    format = format.replace(/mm/g, ('0' + date.getMinutes()).slice(-2));
    format = format.replace(/ss/g, ('0' + date.getSeconds()).slice(-2));
    format = format.replace(/SSS/g, ('00' + date.getMilliseconds()).slice(-3));
    return format;
  },
  // isset
  'isset': function( data ) {
    return ( data === undefined || data === null || data === '')? false: true;
  }
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Web Storage
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function webStorage(){}
webStorage.prototype = {
    'check': function( type ){
        const storage = ( type === 'local')? localStorage:
                        ( type === 'session')? sessionStorage:
                        undefined;
        try {
            const storage = window[type],
            x = '__storage_test__';
            storage.setItem( x, x );
            storage.removeItem( x );
            return true;
        }
        catch( e ) {
            return e instanceof DOMException && (
            // everything except Firefox
            e.code === 22 ||
            // Firefox
            e.code === 1014 ||
            // test name field too, because code might not be present
            // everything except Firefox
            e.name === 'QuotaExceededError' ||
            // Firefox
            e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
            // acknowledge QuotaExceededError only if there's something already stored
            storage.length !== 0;
        }
    },
    'set': function( key, value, type ){
        if ( type === undefined ) type = 'local';
        const storage = ( type === 'local')? localStorage: ( type === 'session')? sessionStorage: undefined;
        if ( storage !== undefined ) {
            try {
                storage.setItem( key, JSON.stringify( value ) );
            } catch( e ) {
                window.console.error('Web storage error: setItem( ' + key + ' ) / ' + e.message );
                storage.removeItem( key );
            }
        } else {
            return false;
        }
    },
    'get': function( key, type ){
        if ( type === undefined ) type = 'local';
        const storage = ( type === 'local')? localStorage: ( type === 'session')? sessionStorage: undefined;
        if ( storage !== undefined ) {
            if ( storage.getItem( key ) !== null  ) {
                return JSON.parse( storage.getItem( key ) );
            } else {
                return false;
            }
        } else {
            return false;
        }
    },
    'remove': function( key, type ){
        if ( type === undefined ) type = 'local';
        const storage = ( type === 'local')? localStorage: ( type === 'session')? sessionStorage: undefined;
        if ( storage !== undefined ) {
            storage.removeItem( key )
        } else {
            return false;
        }
    }
};