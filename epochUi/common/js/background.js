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

// P5.js ワークスペース用オーロラアニメーション
function backgroundAurora() {

  const ws = new webStorage();
  
  let modalData = {},
      backgroundP5, canvasWidth, canvasHeight,
      frameRate, auroraNum, auroraWidth, segmentNum, speed, resolution, opacity;
  let ry; // Y座標アニメーション用
  
  // 背景設定初期値
  const initAuroraData = function(){
    modalData['background-frame-rate'] = 8; // フレームレート
    modalData['background-aurora-number'] = 4; // オーロラ数
    modalData['background-aurora-width'] = 2; // オーロラの幅
    modalData['background-segment-number'] = 60; // 折れ線数
    modalData['background-move-speed'] = 10; // うねり速度
    modalData['background-opacity'] = 75; // 不透明度
  };
  
  const targetID = 'content-Aurora',
        canvasWrap = document.getElementById( targetID ),
        initDrawNum = 30, // 初期表示ループ数
        canvasResetEvent = new CustomEvent('canvasReset'); // リセット用カスタムイベント
  
  // WebStrageにデータがあれば読み込む
  const wsData = ws.get('epoch_aurora');
  if ( wsData !== false ) {
    modalData = wsData;
  } else {
    initAuroraData();
  }
  
  // オーロラ設定値更新
  const auroraParameter = function(){
    frameRate = Number( modalData['background-frame-rate'] );
    auroraNum = Number( modalData['background-aurora-number'] );
    auroraWidth = Number( modalData['background-aurora-width'] );
    segmentNum = Number( modalData['background-segment-number'] );
    speed = Number( modalData['background-move-speed'] );
    resolution = 0.2;
    opacity = Number( modalData['background-opacity'] );
  };
  auroraParameter();
  
  // P5.js  
  const epochBackground = function( p ){
    
    p.setup = function(){
      p.createCanvas( canvasWidth, canvasHeight );
      p.background( 0, 0, 0 );
      p.frameRate( frameRate );
      
      // 初期描画ループ
      for ( let i = 0; i < initDrawNum; i++ ) {
        drawAurora();
      }
      
    };
    p.draw = function(){
    
      //p.filter( p.BLUR, 1 );

      // モーダルが開いているときはアニメーションを停止する
      if ( document.body.classList.contains('modal-open') ) {
        p.noLoop();

        // モーダルが閉じたらアニメーションを再開する
        // bodyのclassを監視
        const observer = new MutationObserver( function(){
          if ( !document.body.classList.contains('modal-open') ) {
            p.loop();
            observer.disconnect();
          }
        });
        observer.observe( document.body, { attributes: true });
      }

      drawAurora();

    };
    
    const drawAurora = function() {
        ry += 1;
        
        // 残像用半透明枠
        p.blendMode(p.BLEND);
        p.noStroke();
        p.fill( 0, 0, 0, 3 )
        p.rect( 0, 0, p.width, p.height );
        
        // オーロラ描画
        p.noFill();
        for( let i = 1; i <= auroraNum; i++ ) {

          p.beginShape();

          const r = 255,
                g = 255,
                b = 200 / auroraNum * i,
                a = 100 / auroraNum * ( i + 1 ),
                c = Math.ceil( i / Math.ceil( auroraNum / 5 ));
                      
          p.blendMode(p.SCREEN);
          p.stroke( r, g, b, a );
          p.strokeWeight( auroraWidth );

          for ( let j = 0; j <= segmentNum * 10; j++ ) {

            const x = p.width / ( segmentNum * 10 ) * j,
                  px = j / ( 200 * c ),
                  py = i + ( ry / ( speed * 10 )),
                  r = p.noise( px, py ),
                  y = ( r * p.height * 2 ) - ( p.height / 2 );

            p.vertex( x, y );
          }

          p.endShape();
      }
    };
    
    // Windowリサイズで再描画
    const resizeCanvas = function(){
      canvasSize();
      // キャンバスリサイズ
      p.resizeCanvas( canvasWidth, canvasHeight );
      // 初期描画ループ
      for ( let i = 0; i < initDrawNum; i++ ) {
        drawAurora();
      }
    };
    
    let resizeTimer;
    const windowResized = function(){
      clearTimeout( resizeTimer );
      resizeTimer = setTimeout( function(){
        resizeCanvas();
      }, 500 );
    };
    window.onresize = windowResized;
    
    document.getElementById('side').addEventListener('transitionend', function(e){
      if ( e.target.id === 'side' ) {
        resizeCanvas();
      }
    });
  
    const canvasReset = function(){
      window.removeEventListener('canvasReset', canvasReset );
      p.remove();
      p = null;
      
      canvasWrap.innerHTML = '';
      setCanvas();
    };
    window.addEventListener('canvasReset', canvasReset );
  };
  
  const modalContent = {
    'background': {
      'title': 'ワークスペース画面設定',
      'footer': {
        'ok': {
          'text': '決定',
          'type': 'positive'
        },
        'cancel': {
          'text': 'キャンセル',
          'type': 'negative'
        },
        'reset': {
          'text': '初期値に戻す',
          'type': 'negative'
        }
      },
      'block': {
        'backgroundBody': {
          'title': 'ワークスペース背景設定',
          'item': {
            /*'backgroundType': {
              'type': 'radio',
              'title': '背景選択',
              'name': 'background-type',
              'item': {
                'aurora': 'オーロラ',
                'simnple': 'シンプル'
              },
              'note': '背景タイプを選択します。'
            },*/
            'frameRate': {
              'type': 'number',
              'min': '0',
              'max': '60',
              'title': 'アニメーションフレームレート',
              'name': 'background-frame-rate',
              'placeholder': '0',
              'note': '１秒間に描画する回数を0から60の間で入力してください。0の場合アニメーションが停止します。実際のフレームレートはスマシンペックに依存します。'
            },
            'auroraNumber': {
              'type': 'number',
              'title': 'オーロラ数',
              'min': '0',
              'max': '50',
              'name': 'background-aurora-number',
              'placeholder': '0',
              'note': 'オーロラの数を0から50で入力してください。'
            },
            'auroraWidth': {
              'type': 'number',
              'min': '1',
              'max': '20',
              'title': 'オーロラ太さ',
              'name': 'background-aurora-width',
              'placeholder': '0',
              'note': 'オーロラの太さを1から20の間で入力してください。'
            },
            'segmentNumber': {
              'type': 'number',
              'min': '1',
              'max': '200',
              'title': '折り返し調整値',
              'name': 'background-segment-number',
              'placeholder': '0',
              'note': 'オーロラの折り返し調整値を1から200の間で入力してください。数値が大きいほど折り返し数が大きくなります。'
            },
            'moveSpeed': {
              'type': 'number',
              'min': '1',
              'max': '100',
              'title': '移動距離調整値',
              'name': 'background-move-speed',
              'placeholder': '0',
              'note': 'オーロラの移動距離調整値を設定します。数値が小さいほどオーロラの移動距離が大きくなります。'
            },
            'opacity': {
              'type': 'number',
              'title': '不透明度',
              'min': '0',
              'max': '100',
              'name': 'background-opacity',
              'placeholder': '0',
              'note': 'キャンバスの不透明度を0から100（％）の間で入力してください。'
            }
          }
        }
      }
    }
  };
  const modal = new modalFunction( modalContent, modalData );
      
  const setting = function(){
    modal.open('background', {
      'ok': function(){
        modal.setParameter();
        ws.set('epoch_aurora', modalData );
        auroraParameter();
        
        modal.close();
        setTimeout( function(){
          window.dispatchEvent( canvasResetEvent );
        }, 10 );
      },
      'cancel': function(){ modal.close(); },
      'callback': function(){
        modal.$modal.find('.modal-menu-button[data-button="reset"]').on('click', function(){
          ws.remove('epoch_aurora');
          initAuroraData();
          auroraParameter();
          
          modal.close();
          setTimeout( function(){
            window.dispatchEvent( canvasResetEvent );
          }, 10 );
        });
      }
    });
  };
  
  const canvasSize = function(){
    const scale = 1 / resolution;
    canvasWrap.style.width = '100%';
    canvasWrap.style.height = '100%';
    
    canvasWidth = Math.floor( canvasWrap.clientWidth * resolution );
    canvasHeight = Math.floor( canvasWrap.clientHeight * resolution );
    
    canvasWrap.style.width = canvasWidth + 'px';
    canvasWrap.style.height = canvasHeight + 'px';
    canvasWrap.style.transform = 'scale(' + scale + ')';
  };
  
  const settingButton = document.querySelector('.workspace-setting-button');
  settingButton.addEventListener('click', function(){
    setting();
  });
  
  const setCanvas = function(){
    canvasSize();
    ry = Date.now();
    canvasWrap.style.opacity = opacity / 100;
    backgroundP5 = new p5( epochBackground, targetID );
  };
  setCanvas();
  

}