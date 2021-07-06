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
      modalData['background-frame-rate'] = 0; // フレームレート
      modalData['background-aurora-number'] = 4; // オーロラ数
      modalData['background-aurora-width'] = 2; // オーロラの幅
      modalData['background-segment-number'] = 600; // 折れ線数
      modalData['background-move-speed'] = 200; // うねり速度
      modalData['background-resolution'] = 0.2; // 解像度
      modalData['background-opacity'] = 1; // 不透明度
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
      frameRate = Number( modalData['background-frame-rate'] ),
      auroraNum = Number( modalData['background-aurora-number'] ),
      auroraWidth = Number( modalData['background-aurora-width'] ),
      segmentNum = Number( modalData['background-segment-number'] ),
      speed = Number( modalData['background-move-speed'] );
      resolution = Number( modalData['background-resolution'] );
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

            for ( let j = 0; j <= segmentNum; j++ ) {

              const x = p.width / segmentNum * j,
                    px = j / ( 200 * c ),
                    py = i + ( ry / speed ),
                    r = p.noise( px, py ),
                    y = ( r * p.height * 2 ) - ( p.height / 2 );

              p.vertex( x, y );
            }

            p.endShape();
        }
      };
      
      // Windowリサイズで再描画
      let resizeTimer;
      const windowResized = function(){
        
        clearTimeout( resizeTimer );
        resizeTimer = setTimeout( function(){
          canvasSize();
          // キャンバスリサイズ
          p.resizeCanvas( canvasWidth, canvasHeight );
          // 初期描画ループ
          for ( let i = 0; i < initDrawNum; i++ ) {
            drawAurora();
          }
        }, 500 );
      };
      window.onresize = windowResized;
    
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
        'title': 'ワークスペース背景設定',
        'footer': {
          'ok': {
            'text': '決定',
            'type': 'positive'
          },
          'cancel': {
            'text': '閉じる',
            'type': 'negative'
          },
          'reset': {
            'text': '初期値に戻す',
            'type': 'negative'
          }
        },
        'block': {
          'backgroundBody': {
            'item': {
              'frameRate': {
                'type': 'input',
                'title': 'フレームレート',
                'name': 'background-frame-rate',
                'placeholder': 'フレームレートを入力してください',
                'note': '１秒間に描画する回数を0から60の間で入力してください。0の場合アニメーションが停止します。実際のフレームレートはスマシンペックに依存します。'
              },
              'auroraNumber': {
                'type': 'input',
                'title': 'オーロラ数',
                'name': 'background-aurora-number',
                'placeholder': 'オーロラ数を入力してください',
                'note': 'オーロラの数を1から50で入力してください。'
              },
              'auroraWidth': {
                'type': 'input',
                'title': 'オーロラ幅',
                'name': 'background-aurora-width',
                'placeholder': 'オーロラの幅を入力してください',
                'note': 'オーロラの太さを1から20の間で入力してください。'
              },
              'segmentNumber': {
                'type': 'input',
                'title': '分割数',
                'name': 'background-segment-number',
                'placeholder': 'オーロラの分割数を入力してください',
                'note': 'オーロラの分割数を設定します。'
              },
              'moveSpeed': {
                'type': 'input',
                'title': '移動距離調整値',
                'name': 'background-move-speed',
                'placeholder': '移動距離調整値を入力してください。',
                'note': 'オーロラの移動距離調整値を設定します。数値が小さいほどオーロラの移動距離が大きくなります。'
              },
              'moveResolution': {
                'type': 'input',
                'title': '解像度',
                'name': 'background-resolution',
                'placeholder': '解像度を入力してください。',
                'note': 'オーロラの解像度を設定します。'
              },
              'opacity': {
                'type': 'input',
                'title': '不透明度',
                'name': 'background-opacity',
                'placeholder': '不透明度入力してください。',
                'note': 'オーロラの不透明度を設定します。'
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
    
    const settingButton = document.querySelector('.header-menu-link');
    settingButton.addEventListener('click', function(){
      setting();
    });
    
    const setCanvas = function(){
      canvasSize();
      ry = Date.now();
      canvasWrap.style.opacity = opacity;
      backgroundP5 = new p5( epochBackground, targetID );
    };
    setCanvas();
    

}