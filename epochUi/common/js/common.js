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
          })
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
          if ( t <= 0 ) t = tT + tH + m;
          if ( wW < l + pW ) l = wW - pW - m;
          if ( l <= 0 ) l = m;
          
          $popup.css({
            'width': pW,
            'height': pH,
            'left': l,
            'top': t
          });

          $target.on({
            'mouseleave.popup': function(){
              const $popup = $body.find('.epoch-popup-block, .epoch-popup-m-block'),
                    title = $popup.text();
              $popup.remove();

              // titleを戻す
              $target.off('mouseleave.popup').attr('title', title );        
            }
          });          
        }
      }
    }, '.epoch-popup, .epoch-popup-m');

}

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