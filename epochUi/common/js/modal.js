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
//   モーダル
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function modalFunction( modalJSON, valueJSON ){
    this.modalJSON = modalJSON;
    this.valueJSON = valueJSON;
    
    this.focusElements = 'input, button, textarea, a';
    /* -------------------------------------------------- *\
       モーダル用div
    \* -------------------------------------------------- */
    $('body').append(
      $('<div/>', {'id': 'modal-container'}),
      $('<div/>', {'id': 'sub-modal-container'})
    );
}
modalFunction.prototype = {
    /* -------------------------------------------------- *\
       ユニークなIDを返す
    \* -------------------------------------------------- */
    'getUniqueID': function() {
      const newUniqueID = function() {
        const strong = 9999,
              uniqueID = 't' + new Date().getTime().toString(16) + Math.floor( strong * Math.random()).toString(16);
        return uniqueID;
      }
      return newUniqueID();
    },
    /* -------------------------------------------------- *\
       型を返す
    \* -------------------------------------------------- */
    'typeJudgment': function( value ) {
      return Object.prototype.toString.call(value).slice(8, -1).toLowerCase();
    },
    /* -------------------------------------------------- *\
       keyが存在するか確認する
    \* -------------------------------------------------- */
    'searchKey': function( values, targetKey ) {
      let result = undefined;
      for ( const key in values ) {
        if ( key === targetKey ) {
          return true;
        }
        const type = this.typeJudgment(values[key]);
        if ( type === 'object') {
          result = this.searchKey( values[key], targetKey );
          if ( result !== undefined ) {
            return result;
          }
        }
      }
      return result;
    },
    /* -------------------------------------------------- *\
       最初に一致したkeyからvalueを返す
    \* -------------------------------------------------- */
    'searchValue': function( values, targetKey ) {
      let result = undefined;
      for ( const key in values ) {
        const type = this.typeJudgment(values[key]);
        if ( type === 'object') {
          result = this.searchValue( values[key], targetKey );
          if ( result !== undefined ) return result;
        } else if ( type === 'string' || type === 'number' || type === 'null') {
          if ( targetKey === key ) {
            return values[key];
          }
        }
      }
      return result;
    },
    /* -------------------------------------------------- *\
       モーダルを開く
    \* -------------------------------------------------- */
    'open': function( target, funcs, width, type ){
        const modal = this,
              $modal = modal.createMain( modal.modalJSON[target], width );
        modal.$modal = $modal;
  
        if ( type === undefined ) type = 'main';
        
        if ( type === 'main') {
          $('body').addClass('modal-open');
          $('#modal-container').html( $modal ).css('display','flex');
          
          // ボタン
          $modal.find('.modal-menu-button, .modal-close-button').on('click', function(){
            const type = $( this ).attr('data-button');
            switch( type ) {
              case 'cancel':
                if ( funcs.cancel !== undefined ) {
                  funcs.cancel();
                } else {
                  modal.close();
                }
                break;
              case 'ok':
                if ( funcs.ok !== undefined ) {
                  funcs.ok( $modal );
                  modal.close();
                }
                break;
            }
          });

          // タブ
          if ( $modal.find('.modal-tab-block').length ) {
            $modal.find('.modal-tab-block').each(function(){
              const $tabBlock = $( this );

              // タブ切り替え、幅調整
              $tabBlock.on({
                'keydown': function(e){
                  if ( e.keyCode === 13 ) {
                    modal.openTab( $(this) );
                  }
                },
                'click': function(){
                  modal.openTab( $(this) );
                },
                'mouseenter': function(){
                  modal.tabSize( $(this) );
                },
                'mouseleave': function(){
                  const $item = $( this );
                  if ( !$item.is('.open') ) {
                    $( this ).css('width', 'auto');
                  }
                }
              }, '.modal-tab-item');
            });
          }          

          // 入力欄Radioセレクト
          if ( $modal.find('.input-pickup-select').length ) {
            $modal.find('.input-pickup-select:checked').each( function(){
              modal.pikupInput( $(this) );
            });            
            $modal.find('.input-pickup-select').on('change', function(){
              modal.pikupInput( $(this) );
            });
          }
          
          // 数値入力とフェーダー
          $modal.find('.item-number-range').each(function(){
            const $fader = $( this ),
                  $input = $fader.prev();
            let   val = $input.val(),
                  min = $input.attr('data-min'),
                  max = $input.attr('data-max');
            if ( min !== 'none' && max !== 'none') {
              min = Number( min );
              max = Number( max );
              if ( val === '' || val === undefined ) val = min;
              
              const inputRange = max - min,
                    $knob = $fader.find('.item-number-range-knob');
              let   width = $fader.width(),
                    ratio = val / inputRange,
                    positionX = Math.round( width * ratio );
                    
              $knob.css('left', Math.round( ratio * 100 ) + '%');
              
              $fader.on('mousedown', function( mde ){
                // 選択を解除する
                getSelection().removeAllRanges();
                
                $fader.addClass('active');
                const clickX = mde.pageX - $fader.offset().left;
                
                val = $input.val();
                width = $fader.width();
                ratio = clickX / width;
                positionX = Math.round( width * ratio );
                
                $knob.css('left', Math.round( ratio * 100 ) + '%' );
                $input.val( Math.round( inputRange * ratio ) + min );

                const $window = $( window );
                
                $window.on({
                  'mouseup.faderKnob': function(){
                    $fader.removeClass('active');
                    $window.off('mouseup.faderKnob mousemove.faderKnob');
                    positionX = Math.round( width * ratio );
                  },
                  'mousemove.faderKnob': function( mme ){
                    const moveX = mme.pageX - mde.pageX;
                    
                    ratio = ( positionX + moveX ) / width;
                    if ( ratio <= 0 ) ratio = 0;
                    if ( ratio >= 1 ) ratio = 1;                    
                    
                    $knob.css('left', Math.round( ratio * 100 ) + '%' );
                    $input.val( Math.round( inputRange * ratio ) + min );
                  }
                });
              
              });
              
              $input.on('input', function(){
                val = $input.val();
                if ( val < min || val === '') {
                  $input.val( min );
                  val = min;
                }
                if ( val > max ) {
                  $input.val( max );
                  val = max;
                }
                
                width = $fader.width();
                ratio = val / inputRange;
                positionX = Math.round( width * ratio );
                
                $knob.css('left', Math.round( ratio * 100 ) + '%' );
              });
              
              
              
              
            } else {
              $fader.remove();
            }
          });
          
          modal.focusOn('#modal-container', '#container');
          
        } else if ( type === 'sub') {
          $('#container').off('focusin.modal');
          $('body').addClass('sub-modal-open');
          $('#sub-modal-container').html( $modal ).css('display','flex');
          
          modal.focusOn('#sub-modal-container', '#container, #modal-container');
          
          $modal.find('.modal-menu-button, .modal-close-button').on('click', function(){
            modal.focusOff('#container, #modal-container');
            modal.focusOn('#modal-container', '#container');
            $('#sub-modal-container').empty().css('display','none');
            $('body').removeClass('sub-modal-open');
          });
        }
               
        if ( funcs.callback !== undefined ) {
          funcs.callback();
        }
        
        // モーダルを開いた際、.modal-bodyの最初の要素をフォーカスする
        const $modalBodyInput = $modal.find('.modal-body').find( modal.focusElements );
        if ( $modalBodyInput.length ) {
          $modalBodyInput.eq(0).focus();
        } else {
          $modal.find('.modal-footer').find( modal.focusElements ).eq(0).focus();
        }

    },
    'pikupInput': function( $check ){
      const $itemBlock = $check.closest('.modal-item'),
            target = $check.val();
      $itemBlock.find('.input-pickup').prop('disabled', true );
      $itemBlock.find('.input-pickup').closest('.item-block').hide();

      $itemBlock.find('.input-pickup-' + target ).prop('disabled', false );
      $itemBlock.find('.input-pickup-' + target ).closest('.item-block').show();
    },
    /* -------------------------------------------------- *\
       モーダル外にフォーカスが移動したら ON
    \* -------------------------------------------------- */
    'focusOn': function( focusTarget, outTarget ){
      const modal = this;
      $( outTarget ).on('focusin.modal', function(){
        $( focusTarget ).find( modal.focusElements ).eq(0).focus();
      });
    },
    /* -------------------------------------------------- *\
       モーダル外にフォーカスが移動したら OFF
    \* -------------------------------------------------- */
    'focusOff': function( outTarget ){
      $( outTarget ).off('focusin.modal');
    },
    /* -------------------------------------------------- *\
       モーダルを閉じる
    \* -------------------------------------------------- */
    'close': function(){
      this.focusOff('#container');
      $('#modal-container').empty().css('display','none');
      $('body').removeClass('modal-open');
    },
    /* -------------------------------------------------- *\
       モーダルを切り替える
    \* -------------------------------------------------- */
    'change': function( type, funcs, width ){
      this.focusOff('#container');
      $('#modal-container').empty();
      this.open( type, funcs, width );
    },
    /* -------------------------------------------------- *\
       入力値をvalueJSONに入れる
    \* -------------------------------------------------- */
    'setParameter': function( parentKey ){
      const modal = this,
            inputTarget = 'input[type="text"], input[type="number"], input[type="password"], input[type="radio"]:checked, textarea';
  
      modal.$modal.find( inputTarget ).each( function(){
        const $input = $( this ),
              name = $input.attr('name'),
              value = $input.val();
        if ( parentKey === undefined ) {
          modal.valueJSON[ name ] = value;
        } else {
          if ( modal.valueJSON[ parentKey ] === undefined ) modal.valueJSON[ parentKey ] = {};
          modal.valueJSON[ parentKey ][ name ] = value;
        }
      });
    },
    /* -------------------------------------------------- *\
       main
    \* -------------------------------------------------- */
    'createMain': function createModal( main, width ){
      if ( width === undefined ) width = 800;
      if ( main.class === undefined ) main.class = '';
      const $modal = $('<div/>', {
        'id': main.id,
        'class': 'modal ' + main.class,
        'style': 'max-width:' + width + 'px'
      });
      $modal.append(
        $('<div/>', {'class': 'modal-header'}).append(
          $('<div/>', {'class': 'modal-title', 'text': main.title }),
          $('<div/>', {'class': 'modal-close'}).append(
            $('<button/>', {
              'class': 'modal-close-button',
              'type': 'button',
              'data-button': 'cancel'
            })
          )
        ),
        $('<div/>', {'class': 'modal-main'}).append( this.createBody( main.block ) ),
        $('<div/>', {'class': 'modal-footer'}).append( this.createFooter( main.footer ) )
      );
      return $modal;
    },
    /* -------------------------------------------------- *\
       footer
    \* -------------------------------------------------- */
    'createFooter': function createModal( footer ){
      const $footer = $('<ul/>', {'class': 'modal-menu-list'});
      for ( const key in footer ) {
        $footer.append(
          $('<li/>', {'class': 'modal-menu-item'}).append(
            $('<button/>', {
              'class': 'epoch-button modal-menu-button ' + footer[key].type ,
              'text': footer[key].text,
              'data-button': key
            })
          )
        );
      }
      return $footer;
    },
    /* -------------------------------------------------- *\
       body
    \* -------------------------------------------------- */
    'createBody': function createModalBlock( block ) {
      if ( block !== undefined ) {
        const modal = this ,
              $modalBody = $('<div/>', {'class': 'modal-body'});
        for ( const key in block ) {
          const buttonCheck = function( blockI ){
            if ( blockI.button !== undefined ) {
              const buttonClass = ( blockI.button.class !== undefined )? ' ' + blockI.button.class: '';
              return $('<button/>', {
                        'id': blockI.button.id,
                        'class': 'epoch-button modal-block-button' + buttonClass,
                        'type': 'button',
                        'text': blockI.button.value
                      });
            } else {
              return false;
            }
          };
          const $button = buttonCheck( block[key] );
          $modalBody.append(
            $('<div/>', {'class': 'modal-block'}).append(
              ( block[key].title !== undefined )?
              $('<div/>', {'class': 'modal-block-header'}).append(
                $('<div/>', {'class': 'modal-block-title', 'text': block[key].title }),
                ( $button !== false )? $button: ''
              ): '',
              $('<div/>', {'class': 'modal-block-main'}).append(
                ( block[key].tab !== undefined )?
                  modal.createTabBody( block[key].tab ):
                  modal.createItem( block[key].item )
              )
            )
          );
          // タブ追加イベント
          if ( $modalBody.find('.modal-tab-add-button').length ) {
            $modalBody.find('.modal-tab-add-button').on('click', function(){
              if ( $modalBody.find('.modal-tab-empty').length ) {
                $modalBody.find('.modal-tab-empty').removeClass('modal-tab-empty');
                $modalBody.find('.modal-empty-block').remove();
              }
              const tabID = modal.getUniqueID();
              
              const $item = $('<li/>', {
                'class': 'modal-tab-item',
                'data-id': tabID,
                'tabindex': 0,
                'data-default': block[key].tab.defaultTitle
              }).append(
                $('<div/>', {'class': 'modal-tab-name'}).append(
                  $('<span/>', {'class': 'modal-tab-text', 'text': block[key].tab.defaultTitle }),
                  $('<span/>', {'class': 'modal-tab-delete'})
                )
              );
              $modalBody.find('.modal-tab-list').append( $item );
                
              $modalBody.find('.modal-tab-body').append(
                $('<div/>', {
                  'id': tabID,
                  'class': 'modal-tab-body-block'
                }).append(
                  modal.createItem( block[key].tab.item, tabID )
                )
              );
              
              // 追加されたタブに入力選択処理
              const $addTab = $modalBody.find('#' + tabID );
              if ( $addTab.find('.input-pickup-select').length ) {
                $addTab.find('.input-pickup-select:checked').each( function(){
                  modal.pikupInput( $(this) );
                });            
                $addTab.find('.input-pickup-select').on('change', function(){
                  modal.pikupInput( $(this) );
                });
              }
              
              modal.openTab( $item );
            });            
          }
        }
        return $modalBody;
      }
    },
    /* -------------------------------------------------- *\
       Tab
    \* -------------------------------------------------- */
    'createTabBody': function( tab ){
      const modal = this,
            type = tab.type,
            modalClass = ( type === 'add')? 'modal-tab-block modal-tab-add-block': 'modal-tab-block',
            $tab = $('<div/>', {'id': tab.id, 'class': modalClass }),
            $tabMenu = $('<div/>', {'class': 'modal-tab-menu'}),
            $tabBody = $('<div/>', {'class': 'modal-tab-body'}),
            $tabList = $('<ul/>', {'class': 'modal-tab-list'});
      // Tabが空の場合
      const emptyTab = function(){
        $tab.addClass('modal-tab-empty');
        $tabBody.html(
          $('<div/>', {
            'class': 'modal-empty-block',
            'text': tab.emptyText
          })
        );
      };
      if ( type === 'add' || type === 'reference') {
        const target = modal.valueJSON[ tab.target.key1 ],
              type = modal.typeJudgment( target );
        let length = 0;
        if ( type === 'object') {
          length = Object.keys( target ).length;
        } else if ( type === 'array') {
          length = target.length;
        }
        if ( length > 0 ) {
          const $html = function( key, id ){
            $tabList.append(
              $('<li/>', {
                'class': 'modal-tab-item',
                'data-id': id,
                'tabindex': 0,
                'data-default': target[key][tab.target.key2]
              }).append(
                $('<div/>', {'class': 'modal-tab-name'}).append(
                  $('<span/>', {'class': 'modal-tab-text', 'text': target[key][tab.target.key2] }),
                  ( type === 'add')? $('<span/>', {'class': 'modal-tab-delete'}): ''
                )
              )
            );
            $tabBody.append(
              $('<div/>', {
                'id': id,
                'class': 'modal-tab-body-block'
              }).append(
                modal.createItem( tab.item, key )
              )
            );
          };
          if ( type === 'object') {
            for ( const key in target ) {
              $html( key, key );
            }
          } else if ( type === 'array') {
            for ( let i = 0; i < length; i++ ) {
              // マニュフェストならfile_idをidとする
              const key = ( target[i]['file_id'] !== undefined )? target[i].file_id: i;
              $html( i, key );
            }
          }
        } else {
          emptyTab();
        }
      } else if ( type === 'common') {
        if ( tab.tabs !== undefined ) {
          for ( const key in tab.tabs ) {
            $tabList.append(
              $('<li/>', {
                'class': 'modal-tab-item',
                'data-id': key,
                'tabindex': 0
              }).append(
                $('<div/>', {'class': 'modal-tab-name'}).append(
                  $('<span/>', {'class': 'modal-tab-text', 'text': tab.tabs[key]['title'] })
                )
              )
            );
            $tabBody.append(
              $('<div/>', {
                'id': key,
                'class': 'modal-tab-body-block'
              }).append(
                modal.createItem( tab.tabs[key].item, key )
              )
            );
          }
        }      
      }
      $tabMenu.append( $tabList );
      $tabList.find('.modal-tab-item:first-child').addClass('open');
      $tabBody.find('.modal-tab-body-block:first-child').addClass('open');
      $tab.append( $tabMenu, $tabBody );
      
      // タブ削除イベント
      if ( type === 'add') {
        $tab.on('click', '.modal-tab-delete', function(){
          const $tabItem = $( this ).closest('.modal-tab-item'),
                tabID = $tabItem.attr('data-id');
          // データがすでに登録されているか確認する
          if ( modal.searchKey( modal.valueJSON, tabID ) === true ) {
            if ( !confirm( tab.deletConfirmText ) ) return false;
            // 消したタブIDをプールする
            const $modal = $tabItem.closest('.modal'),
                  tabDelete = ( $modal.attr('data-tab-delete') === undefined )?
                              new Array(): $modal.attr('data-tab-delete').split(',');
            tabDelete.push( tabID );
            $modal.attr('data-tab-delete', tabDelete.join(',') );
          }
          $tabItem.add( $('#' + tabID ) ).remove();        
          
          if ( !$tabList.find('.modal-tab-item').length ) {
            emptyTab();
          } else {
            modal.openTab( $tabMenu.find('.modal-tab-item').eq(0) );
          }
          
        });
      }
      
      return $tab;
    },
    /* -------------------------------------------------- *\
       タブを開く
    \* -------------------------------------------------- */
    'openTab': function( $tab ){
      const $tabBlock = $tab.closest('.modal-tab-block'),
            tabNumber = $tabBlock.find('.modal-tab-item').index( $tab.get(0) );
      $tabBlock.find('.open').removeClass('open');
      $tabBlock.find('.modal-tab-item').css('width', 'auto').attr('tabindex', 0 );
      
      $tab.addClass('open').attr('tabindex', -1 );
      $tabBlock.find('.modal-tab-body-block').eq( tabNumber ).addClass('open').find( this.focusElements ).eq(0).focus();
      this.tabSize( $tab );
    },
    /* -------------------------------------------------- *\
       タブのサイズを調整する
    \* -------------------------------------------------- */
    'tabSize': function( $tab ){
      const padding = 32,
            offsetWidth = $tab.find('.modal-tab-text').get(0).offsetWidth,
            scrollWidth = $tab.find('.modal-tab-text').get(0).scrollWidth;
      if ( offsetWidth < scrollWidth ) {
        $tab.css('width', scrollWidth + padding );
      }
    },
    /* -------------------------------------------------- *\
       item
    \* -------------------------------------------------- */
    'createItem': function( item, tabNumber ){
      if ( item !== undefined ) {
        const modal = this,
              $item = $('<div/>', {'class': 'modal-item'});
        for ( const key in item ) {
          const itemType = function( data ){
            switch( data.type ) {
              case 'input': return modal.createInput( data, tabNumber );
              case 'number': return modal.createNumber( data, tabNumber );
              case 'textarea': return modal.createTextarea( data, tabNumber );
              case 'password': return modal.createPassword( data, tabNumber );
              case 'radio': return modal.createRadio( data, tabNumber );
              case 'loading': return modal.createLoadingBlock( data, tabNumber );
              case 'reference': return modal.createReference( data, tabNumber );
              case 'freeitem': return modal.createFreeItem( data, tabNumber );
              case 'message': return modal.createMessage( data );
            }
          };
          $item.append( itemType( item[key] ) );
        }
        return $item;
      }
    },
    /* -------------------------------------------------- *\
       loading
    \* -------------------------------------------------- */
    'createLoadingBlock': function( loading, tabNumber ){
      if ( loading !== undefined ) {
        const $loading = $('<div/>', {
          'id': ( tabNumber !== undefined )? tabNumber + '-' + loading.id: loading.id
        }).append(
          $('<div/>', {'class': 'modal-loading-inner'})
        );
        return $loading;
      }
    },
    /* -------------------------------------------------- *\
       input TEXT
    \* -------------------------------------------------- */
    'createInput': function( text, tabNumber ){
      const modal = this,
            $input = $('<dl/>', {'class': 'item-text-block item-block'}),
            name = ( tabNumber !== undefined )? tabNumber + '-' + text.name: text.name,
            value = this.searchValue( this.valueJSON, name ),
            className = ( text.class !== undefined )? ' ' + text.class: '';
      if ( text.max === undefined ) text.max = 0;
      $input.append(
        $('<dt/>', {'class': 'item-text-title item-title', 'text': text.title }),
        ( text.max > 0 )? $('<dd/>', {'class': 'item-text-length', 'text': '000/000' }): '',
        $('<dd/>', {'class': 'item-text-area'}).append(
          $('<input>', {
            'type': 'text',
            'name': name,
            'data-name': text.name,
            'class': 'item-text ' + text.name + className,
            'placeholder' : text.placeholder,
            'value': value        
          })
        ),
        ( text.note !== undefined )? $('<dd/>', {'class': 'item-note item-text-note', 'text':  text.note }): ''
      );
      // 入力チェック
      if ( text.validation !== undefined ) {
        $input.append( $('<dd/>', {'class': 'item-text-error', 'text': text.inputError }) );
        
        const reg = new RegExp( text.validation ),
              $error = $input.find('.item-text-error');
        
        const errorCheck = function( val ){
          if ( val !== undefined ) {
            if ( !val.match( reg ) && val !== '') {
              $error.addClass('input-error');
            } else {
              $error.removeClass('input-error');
            }
          } else {
            $error.removeClass('input-error');
          }
        };
        errorCheck( value );
        if ( modal.$modal !== undefined ) modal.errorCheck();

        $input.find('.item-text').on('blur', function(){
          const $this = $( this ),
                val = $this.val();
          errorCheck( val );
          if ( modal.$modal !== undefined ) modal.errorCheck();
        });
      }
      // タブ名と入力を合わせる
      const $tabNameInput = $input.find('.tab-name-link');
      if ( $tabNameInput.length ) {
        $tabNameInput.on({
          'input': function(){
            const $this = $( this ),
                  $tab = $this.closest('.modal-tab-block'),
                  defaultTitle = $tab.find('.odal-tab-item').attr('data-default-title'),
                  id = $this.closest('.modal-tab-body-block').attr('id'),
                  val = $this.val(),
                  reg = new RegExp( text.regexp );
            let repositoryName;
            if ( val.match( reg ) ) {
              repositoryName = val.replace( reg, '$1');    
            } else {
              repositoryName = defaultTitle;
            }
            $tab.find('[data-id="' + id + '"]').find('.modal-tab-text').text(repositoryName);
          }
        });
      }
      return $input;
    },
    /* -------------------------------------------------- *\
       Number
    \* -------------------------------------------------- */
    'createNumber': function( number, tabNumber ){
      const $number = $('<dl/>', {'class': 'item-number-block item-block'}),
            name = ( tabNumber !== undefined )? tabNumber + '-' + number.name: number.name,
            value = this.searchValue( this.valueJSON, name ),
            className = ( number.class !== undefined )? ' ' + number.class: '',
            min = ( number.min !== undefined )? Number( number.min ): 'none',
            max = ( number.max !== undefined )? Number( number.max ): 'none';
      $number.append(
        $('<dt/>', {'class': 'item-number-title item-title', 'text': number.title }),
        $('<dd/>', {'class': 'item-number-area'}).append(
          $('<input>', {
            'type': 'number',
            'name': name,
            'data-name': number.name,
            'data-min': min,
            'data-max': max,
            'autocomplete': 'off',
            'class': 'item-number ' + number.name + className,
            'placeholder' : number.placeholder,
            'value': value        
          }),
          $('<div/>', {'class':'item-number-range'}).append($('<div/>', {'class': 'item-number-range-knob'}))
        ),
        ( number.note !== undefined )? $('<dd/>', {'class': 'item-note item-number-note', 'text':  number.note }): ''
      );
      
      return $number;
    },
    /* -------------------------------------------------- *\
       Textarea
    \* -------------------------------------------------- */
    'createTextarea': function( textarea, tabNumber ){
      const $textarea = $('<dl/>', {'class': 'item-textarea-block item-block'}),
            name = ( tabNumber !== undefined )? tabNumber + '-' + textarea.name: textarea.name,
            value = this.searchValue( this.valueJSON, name ),
            className = ( textarea.class !== undefined )? ' ' + textarea.class: '';
      $textarea.append(
        $('<dt/>', {'class': 'item-textarea-title item-title', 'text': textarea.title }),
        $('<dd/>', {'class': 'item-textarea-area'}).append(
          $('<textarea/>', {
            'name': name,
            'data-name': textarea.name,
            'class': 'item-textarea ' + textarea.name + className,
            'placeholder' : textarea.placeholder,
            'text': value        
          }),
          ( textarea.note !== undefined )? $('<dd/>', {'class': 'item-note item-textarea-note', 'text':  textarea.note }): ''
        )
      );
      return $textarea;
    },
    /* -------------------------------------------------- *\
       Reference
    \* -------------------------------------------------- */
    'createReference': function( reference, tabNumber ){
      const $input = $('<dl/>', {'class': 'item-reference-block item-block'}),
            value = ( tabNumber !== undefined )? this.searchValue( this.valueJSON, tabNumber + '-' + reference.target ) : this.searchValue( this.valueJSON, reference.target ),
            className = ( reference.class !== undefined )? ' ' + reference.class: '';
      $input.append(
        $('<dt/>', {'class': 'item-reference-title item-title', 'text': reference.title }),
        $('<dd/>', {'class': 'item-reference-area'}).append(
          $('<span/>', {
            'text': value,
            'class': 'item-reference' + className
          }),
          ( reference.note !== undefined )? $('<dd/>', {'class': 'item-note item-reference-note', 'text':  reference.note }): ''
        )
      );
      return $input;
    },
    /* -------------------------------------------------- *\
       input PASSWORD
    \* -------------------------------------------------- */
    'createPassword': function( password, tabNumber ){
      const $input = $('<dl/>', {'class': 'item-password-block item-block'}),
            name = ( tabNumber !== undefined )? tabNumber + '-' + password.name: password.name,
            value = this.searchValue( this.valueJSON, name ),
            className = ( password.class !== undefined )? ' ' + password.class: '';
      $input.append(
        $('<dt/>', {'class': 'item-password-title item-title', 'text': password.title }),
        $('<dd/>', {'class': 'item-password-area'}).append(
          $('<input>', {
            'type': 'password',
            'name': name,
            'class': 'item-password ' + password.name + className,
            'placeholder' : password.placeholder,
            'value': value
          }),
          $('<span/>', {
            'class': 'item-password-eye'
          }).append('<svg viewBox="0 0 64 64" class="workspace-button-svg"><use href="#icon-eye-close" /></svg>')
        ),
        ( password.note !== undefined )? $('<dd/>', {'class': 'item-note item-password-note', 'text':  password.note }): ''
      );
      // パスワード入力マスク解除
      $input.find('.item-password-eye').on({
        'mousedown' : function(){
          var $eye = $( this ),
              $input = $eye.prev('input');

          $eye.find('use').attr('href', '#icon-eye-open');
          $input.blur().attr('type', 'text');

          $( window ).on({
            'mouseup.passwordEye' : function(){
              $( this ).off('mouseup.passwordEye');
              $input.attr('type', 'password').focus();
              $eye.find('use').attr('href', '#icon-eye-close');
            }
          });
        }
      });
      return $input;
    },
    /* -------------------------------------------------- *\
       input RADIO
    \* -------------------------------------------------- */
    'createRadio': function( radio, tabNumber ){
      const $radio = $('<dl/>', {'class': 'item-radio-block item-block'}).prepend(
              ( radio.title !== undefined )? $('<dt/>', {'class': 'item-radio-title item-title', 'text': radio.title }): '',
              $('<dd/>', {'class': 'item-radio-area'}).append(
                $('<ul/>', {'class': 'item-radio-list'})
              ),
              ( radio.note !== undefined )? $('<dd/>', {'class': 'item-note item-radio-note', 'text':  radio.note }): ''
            ),
            name = ( tabNumber !== undefined )? tabNumber + '-' + radio.name: radio.name,
            checkedValue = this.searchValue( this.valueJSON, name ),
            checked = ( checkedValue !== undefined )? name + '-' + checkedValue: undefined,
            className = ( radio.class !== undefined )? ' ' + radio.class: '';
      for ( const key in radio.item ) {
        $radio.find('.item-radio-list').append(
          $('<li/>', {'class': 'item-radio-item'}).append(
            $('<input>', {
              'class': 'item-radio' + className,
              'type': 'radio',
              'id': name + '-' + key,
              'value': key,
              'name': name
            }),
            $('<label/>', {
              'class': 'item-radio-label',
              'for': name + '-' + key,
              'text': radio.item[key]
            })
          )
        );
      }
      if ( checked !== undefined ) {
        $radio.find('#' + checked ).prop('checked', true );
      } else {
        $radio.find('.item-radio').eq(0).prop('checked', true );
      }
      return $radio;
    },
    /* -------------------------------------------------- *\
       自由
    \* -------------------------------------------------- */
    'createFreeItem': function( free, tabNumber ){
      const $free = $('<dl/>', {'class': 'item-freeitem-block item-block'}),
            name = ( tabNumber !== undefined )? tabNumber + '-' + free.name: free.name,
            value = this.searchValue( this.valueJSON, name ),
            list = ( value === undefined )? {'':''}: value,
            listLength = Object.keys( list ).length,
            className = ( free.class !== undefined )? ' ' + free.class: '';
      
      const addLine = function( key, value ){
        return ''
        + '<li class="item-freeitem-item">'
          + '<div class="item-freeitem-item-move"></div>'
          + '<div class="item-freeitem-item-name"><input class="item-freeitem-input item-text" type="text" value="' + key + '" placeholder="項目名を入力してください。"></div>'
          + '<div class="item-freeitem-item-content"><input class="item-freeitem-input item-text" type="text" value="' + value + '" placeholder="項目内容を入力してください。"></div>'
          + '<div class="item-freeitem-item-delete"></div>'
        + '</li>';
      };
      
      let inputHTML = '<ul class="item-freeitem-list">';
      for ( let i = 0; i < listLength; i++ ) {
        for ( const key in list ) {
          inputHTML += addLine( key, list[key] );
        }
      }
      inputHTML += '</ul>'
      + '<ul class="item-freeitem-menu-list">'
        + '<li class="item-freeitem-menu-item"><button class="epoch-button item-freeitem-add-button add" type="button">項目を追加する</button></li>'
      + '</ul>';
      
      $free.append(
        $('<dt/>', {'class': 'item-freeitem-title item-title', 'text': free.title }),
        $('<dd/>', {'class': 'item-freeitem-area'}).append(
          $('<div/>', {
            'name': name,
            'data-name': free.name,
            'class': 'item-freeitem ' + free.name + className,
            'html': inputHTML
          })
        )
      );
      
      $free.find('.item-freeitem-add').on('click', function(){
        $free.find('.item-freeitem-list').append( addLine('','') );
      });
      return $free;
    },
    /* -------------------------------------------------- *\
       メッセージ
    \* -------------------------------------------------- */
    'createMessage': function( message ){
      const $free = $('<dl/>', {'class': 'item-message-block item-block'}),
            className = ( message.class !== undefined )? ' ' + message.class: '';
      $free.append(
        $('<dt/>', {'class': 'item-message-title item-title', 'text': message.title }),
        $('<dd/>', {'class': 'item-message-area'}).append(
          $('<div/>', {
            'class': 'item-message ' + className,
            'text': message.text
          })
        )
      );
      return $free;
    },
    /* -------------------------------------------------- *\
       入力内にエラーがあればOKボタンを無効化する
    \* -------------------------------------------------- */
    'errorCheck': function(){
      const modal = this;
      if ( modal.$modal !== undefined ) {
        const $okButton = modal.$modal.find('.modal-menu-button[data-button="ok"]');
        if ( modal.$modal.find('.input-error').length ) {
          $okButton.prop('disabled', true );
        } else {
          $okButton.prop('disabled', false );
        }
      }
    },
    /* -------------------------------------------------- *\
       対象のモーダル内のinputがすべて入力されているか
    \* -------------------------------------------------- */
    'inputCheck': function( jTarget ){
      let emptyNumber = 0;
      const modal = this,
            block = this.modalJSON[jTarget].block;
      
      const inputF = function( text, tabNumber ){
        const name = ( tabNumber !== undefined )? tabNumber + '-' + text.name: text.name,
              value = modal.searchValue( modal.valueJSON, name );
        // undefinedまたは空白の場合は未入力とする nullは無視
        if ( value === undefined || value === '' ) emptyNumber++;      
      };
      const tabF = function( tab ){
        const  type = tab.type;
        if ( type === 'add' || type === 'reference') {
          const target = modal.valueJSON[ tab.target.key1 ];
          if ( Object.keys( target ).length > 0 ) {
            for ( const key in target ) {
              itemF( tab.item, key );
            }
          }
        }
      };
      const itemF = function( item, tabNumber ){
        if ( item !== undefined ) {
          for ( const key in item ) {
            switch( item[key].type ) {
              case 'input':
              case 'password': inputF( item[key], tabNumber ); break;
            }
          }
        }
      };
      
      for ( const key in block ) {
        if ( block[key].tab !== undefined ) {
          tabF( block[key].tab );
        } else {
          itemF( block[key].item );
        }
      }
      
      return ( emptyNumber === 0 )? true: false;
    }
};