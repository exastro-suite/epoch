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
      'mouseenter': function(){
        const $target = $( this ),
              title = $target.attr('title');
        if ( title !== undefined ) {
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
          
        }
      },
      'mouseleave': function(){
        const $target = $( this ),
              $popup = $body.find('.epoch-popup-block, .epoch-popup-m-block'),
              title = $popup.text();
        $popup.remove();
        
        // titleを戻す
        $target.attr('title', title );        
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
    if ( text !== undefined ) {
      for ( var i = 0; i < entities.length; i++ ) {
        text = text.replace( new RegExp( entities[i][0], 'g'), '&' + entities[i][1] + ';' );
      }
    }
    return text;
  }
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
(function(){
  $.fn.yaml = function(){
    const $text = $( this ),
          text = $text.text();
    $text.html( text );
  };
})();


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