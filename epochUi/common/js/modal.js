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
    
    this.fn = new epochCommon();

    this.focusElements = 'input, button, textarea, a';
    /* -------------------------------------------------- *\
       モーダル用div
    \* -------------------------------------------------- */
    if ( !$('#modal-container').length ) {
      $('body').append(
          $('<div/>', {'id': 'modal-container'}),
          $('<div/>', {'id': 'sub-modal-container'})
      );
  }
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
        const modal = this;
        
        if ( type === undefined ) type = 'main';
        modal.type = type;
        
        const $modal = modal.createMain( modal.modalJSON[target], width );
        if ( modal.$modal !== undefined ) {
            alert('modal error');
            return;
        }
        modal.$modal = $modal;
        
        if ( type === 'main') {

          $('body').addClass('modal-open');
          $('#modal-container').html( $modal ).css('display','flex');
          
          // ボタン
          $modal.find('.modal-menu-button, .modal-close-button').on('click', function(){
            const buttonType = $( this ).attr('data-button');
            if ( funcs[buttonType] !== undefined && modal.typeJudgment(funcs[buttonType]) === 'function') {
              funcs[buttonType]();            
            } else {
              modal.close();
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
                    const $tab = $(this);
                    if ( !$tab.is('.open') ) {
                      modal.openTab( $tab );
                    }
                  }
                },
                'click': function(){
                  const $tab = $(this);
                  if ( !$tab.is('.open') ) {
                    modal.openTab( $tab );
                  }
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
              modal.inputErrorCheck();
            });
          }
          
          modal.focusOn('#modal-container', '#container');
          
        } else if ( type === 'sub' || type == 'progress') {
          $('#container').off('focusin.modal');
          $('body').addClass('sub-modal-open');
          $('#sub-modal-container').html( $modal ).css('display','flex');
          
          modal.focusOn('#sub-modal-container', '#container, #modal-container');
          
          $modal.find('.modal-menu-button, .modal-close-button').on('click', function(){
            const buttonType = $( this ).attr('data-button');
            if ( funcs[buttonType] !== undefined && modal.typeJudgment(funcs[buttonType]) === 'function') {
              funcs[buttonType]();
            } else {
              modal.subClose();
            }
          });
        }
        // 入力チェック
        modal.inputErrorCheck();
        
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
      this.$modal = undefined;
      $('#modal-container').empty().css('display','none');
      $('body').removeClass('modal-open');
    },
    /* -------------------------------------------------- *\
       サブモーダルを閉じる
    \* -------------------------------------------------- */
    'subClose': function(){
      const modal = this;
      modal.focusOff('#container, #modal-container');
      modal.focusOn('#modal-container', '#container');
      $('#sub-modal-container').empty().css('display','none');
      $('body').removeClass('sub-modal-open');
      modal.$modal = undefined;
    },
    /* -------------------------------------------------- *\
       モーダルを切り替える
    \* -------------------------------------------------- */
    'change': function( type, funcs, width ){
      this.focusOff('#container');
      this.$modal = undefined;
      $('#modal-container').empty();
      this.open( type, funcs, width );
    },
    /* -------------------------------------------------- *\
       入力値をvalueJSONに入れる
    \* -------------------------------------------------- */
    'setParameter': function( parentKey ){
      const modal = this,
            inputTarget = 'input[type="text"], input[type="number"], input[type="password"], input[type="radio"]:checked, textarea, input[type="hidden"]';
      
      const setValue = function( key, value ){
        if ( parentKey === undefined ) {
          modal.valueJSON[ key ] = value;
        } else {
          if ( modal.valueJSON[ parentKey ] === undefined ) modal.valueJSON[ parentKey ] = {};
          modal.valueJSON[ parentKey ][ key ] = value;
        }      
      };
      modal.$modal.find( inputTarget ).each( function(){
        const $input = $( this ),
              key = $input.attr('name'),
              value = $input.val();
        // 自由項目は除く
        if ( !$input.is('.item-freeitem-input') ) {
          setValue( key, value );
        }
      });
      
      // 自由項目
      modal.$modal.find('.item-freeitem').each( function(){
        const $free = $( this ),
              key = $free.attr('name'),
              free = {};
        $free.find('.item-freeitem-item').each( function(){
          const $item = $( this ),
                key = $item.find('.item-freeitem-input.name').val(),
                value = $item.find('.item-freeitem-input.content').val();
          free[key] = value;
        });
        setValue( key, JSON.stringify( free ));        
      });
    },
    /* -------------------------------------------------- *\
       main
    \* -------------------------------------------------- */
    'createMain': function createModal( main, width ){
      const modal = this;
      if ( width === undefined ) width = 800;
      if ( main.class === undefined ) main.class = '';
      if ( !main.footer ) main.class += ' no-footer'
      const $modal = $('<div/>', {
        'id': main.id,
        'data-modal': 'modal-' + modal.getUniqueID(),
        'data-type': modal.type,
        'class': 'modal ' + main.class,
        'style': ( width === 'none')? 'max-width: none': 'max-width:' + width + 'px'
      });
      
      $modal.append(
        $('<div/>', {'class': 'modal-header'}).append(
          $('<div/>', {'class': 'modal-title', 'text': main.title })
        ),
        $('<div/>', {'class': 'modal-main'}).append( modal.createBody( main.block ) )
      );
      if ( modal.type !== 'progress') {
        $modal.find('.modal-header').append(
          $('<div/>', {'class': 'modal-close'}).append(
            $('<button/>', {
              'class': 'modal-close-button',
              'type': 'button',
              'data-button': 'cancel'
            })
          )
        )
      }
      if ( main.footer ) {
        $modal.append(
          $('<div/>', {'class': 'modal-footer'}).append( modal.createFooter( main.footer ) )
        );
      }
      
      return $modal;
    },
    /* -------------------------------------------------- *\
       footer
    \* -------------------------------------------------- */
    'createFooter': function createModal( footer ){
      const modal = this,
            $footer = $('<ul/>', {'class': 'modal-menu-list'});
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
      
      // 未入力とエラー数表示
      $footer.append(''
        + '<li class="modal-menu-item modal-error-item">'
          + '<div class="modal-error-info modal-required-count">必須項目残り<span class="modal-required-count-num"></span>件</div>'
          + '<div class="modal-error-info modal-error-count">エラー件数<span class="modal-error-count-num"></span>件</div>'
        + '</li>'
      );
      
      // 未入力、エラー項目にスクロール
      $footer.find('.modal-error-info').on('click', function(){
        const $modal = modal.$modal,
              $main = $modal.find('.modal-main'),
              $target = ( $( this ).is('.modal-required-count') )? $modal.find('.required-error').eq(0): $modal.find('.input-error, .count-error').eq(0);
              
        // 対象がタブ内の場合
        const $tabBlock = $target.closest('.modal-tab-body-block');
        if ( $tabBlock.length ) {
          const tabID = $tabBlock.attr('id');
          modal.openTab( $main.find('.modal-tab-item[data-id="' + tabID + '"]'), false );
        }

        const mainScroll = $main.scrollTop(),
              $itemBlock = $target.closest('.item-block'),
              targetScrollTop = $itemBlock.position().top + mainScroll - 8;
        $modal.find('.modal-main').animate({'scrollTop': targetScrollTop }, 300, 'swing', function(){
          // スクロールが終わったらフォーカス
          $target.focus();
          
          // 強調表示
          const emClassName = 'select-emphasis';
          if ( !$itemBlock.is('.' + emClassName ) ) {
            $itemBlock.addClass( emClassName );
            setTimeout( function(){
              $itemBlock.removeClass( emClassName );
            }, 1000 );
          }          
        });
      });
            
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
          
          const $modalBlock = $('<div/>', {'class': 'modal-block'}).append(
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
          );
          $modalBody.append( $modalBlock );
          // タブ追加イベント
          if ( $modalBlock.find('.modal-tab-add-button').length ) {
            $modalBlock.find('.modal-tab-add-button').on('click', function(){
              if ( $modalBlock.find('.modal-tab-empty').length ) {
                $modalBlock.find('.modal-tab-empty').removeClass('modal-tab-empty');
                $modalBlock.find('.modal-empty-block').remove();
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
              $modalBlock.find('.modal-tab-list').append( $item );
                
              $modalBlock.find('.modal-tab-body').append(
                $('<div/>', {
                  'id': tabID,
                  'class': 'modal-tab-body-block'
                }).append(
                  modal.createItem( block[key].tab.item, tabID )
                )
              );
              
              // 追加されたタブに入力選択処理
              const $addTab = $modalBlock.find('#' + tabID );
              if ( $addTab.find('.input-pickup-select').length ) {
                $addTab.find('.input-pickup-select:checked').each( function(){
                  modal.pikupInput( $(this) );
                });            
                $addTab.find('.input-pickup-select').on('change', function(){
                  modal.pikupInput( $(this) );
                });
              }
              modal.openTab( $item );
              modal.inputErrorCheck();
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
            tabType = tab.type,
            modalClass = ( tabType === 'add')? 'modal-tab-block modal-tab-add-block': 'modal-tab-block',
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
      if ( tabType === 'add' || tabType === 'reference') {
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
                'data-default': tab.defaultTitle
              }).append(
                $('<div/>', {'class': 'modal-tab-name'}).append(
                  $('<span/>', {'class': 'modal-tab-text', 'text': target[key][tab.target.key2] }),
                  ( tabType === 'add')? $('<span/>', {'class': 'modal-tab-delete'}): ''
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
            if ( tab.target.key1 === 'manifests') {
              // マニュフェストはfile_nameでソートする
              const sortKey = 'file_name';
              target.sort(function( a, b ){
                const as = a[sortKey].toLowerCase(),
                      bs = b[sortKey].toLowerCase();
                if ( as < bs ) {
                    return -1;
                } else if ( as > bs ) {
                    return 1;
                } else {
                  return 0;
                }
              });
              for ( let i = 0; i < length; i++ ) {
                $html( i, target[i].file_id );
              }
            } else {
              for ( let i = 0; i < length; i++ ) {
                $html( i, i );
              }
            }
          }

        } else {
          emptyTab();
        }
      } else if ( tabType === 'common') {
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
      if ( tabType === 'add') {
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
          $tabItem.mouseleave().add( $('#' + tabID ) ).remove();
          
          if ( !$tabList.find('.modal-tab-item').length ) {
            emptyTab();
          } else {
            modal.openTab( $tabMenu.find('.modal-tab-item').eq(0) );
          }
          
          modal.inputErrorCheck();
          
        });
      }
      
      return $tab;
    },
    /* -------------------------------------------------- *\
       タブを開く
    \* -------------------------------------------------- */
    'openTab': function( $tab, focusFlag ){
      if ( focusFlag === undefined ) focusFlag = true;
      
      const $tabBlock = $tab.closest('.modal-tab-block'),
            tabNumber = $tabBlock.find('.modal-tab-item').index( $tab.get(0) );
      $tabBlock.find('.open').removeClass('open');
      $tabBlock.find('.modal-tab-item').css('width', 'auto').attr('tabindex', 0 );
      
      $tab.addClass('open').attr('tabindex', -1 );
      $tabBlock.find('.modal-tab-body-block').eq( tabNumber ).addClass('open');
      
      
      // 開いた最初の入力要素にフォーカス
      if ( focusFlag !== false ) {      
        $tabBlock.find('.modal-tab-body-block.open').find( this.focusElements ).eq(0).focus();
      }
      this.tabSize( $tab );
    },
    /* -------------------------------------------------- *\
       タブのサイズを調整する
    \* -------------------------------------------------- */
    'tabSize': function( $tab ){
      const offsetWidth = $tab.find('.modal-tab-text').get(0).offsetWidth,
            scrollWidth = $tab.find('.modal-tab-text').get(0).scrollWidth,
            text = $tab.text();
      
      if ( offsetWidth < scrollWidth ) {
        if ( $tab.is('.epoch-popup') ) {
          if ( $tab.attr('title') !== undefined ) {
            $tab.attr('title', text );
          }
        } else {
          $tab.attr('title', text ).addClass('epoch-popup');
        }
      } else {
        $tab.removeAttr('title').removeClass('epoch-popup');
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
              case 'listSelect': return modal.createListSelect( data, tabNumber );
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
          ( loading.text !== undefined )? $('<div/>', {'class': 'modal-progress-message', 'text': loading.text }): '',
          $('<div/>', {'class': 'modal-loading-inner'})
        );
        return $loading;
      }
    },
    /* -------------------------------------------------- *\
       Item common
    \* -------------------------------------------------- */
    'createCommonItem': function( type, data, tab ){
      const modal = this,
            $dl = $('<dl/>', {'class': 'item-' + type + '-block item-block'}),
            title = ( data.title === undefined )? '': data.title;
      
      // Title
      if ( title !== '') {
        const $dt = $('<dt/>', {'class': 'item-' + type + '-header item-header'}).append(
          $('<span/>', {'class': 'item-header-cell item-title'}).append(
            $('<span/>', {'class': 'item-title-text', 'text': title })
          )
        );
        // テキストとテキストエリアは入力文字数を表示する
        if ( ['text','textarea','password','number'].indexOf( type ) !== -1 ) {
          let wordCountHTML = ''
          + '<span class="item-header-cell item-word-count">'
            + '<span class="item-word-count-inner">';

          if ( type !== 'number') {
            wordCountHTML += '<span class="item-word-number">0</span>';
          }

          // 最小最大文字数
          if ( data.min !== undefined && data.max !== undefined ) {
            const min = data.min,
                  max = data.max;
            wordCountHTML += '<span class="item-word-min-max">' + min + ' - ' + max + '</span>';
          }

          wordCountHTML += '</span></span>';
          $dt.append( wordCountHTML );
        }
        // 必須マーク
        if ( data.required !== undefined ) {
          $dt.append('<span class="item-header-cell item-required"><span class="item-required-mark">必須</span></span>');
        }
        
        $dl.append( $dt );
      }
      
      // Body
      const $inputDD = $('<dd/>', {'class': 'item-' + type + '-area'});
      switch( type ) {
        case 'text':
        case 'textarea':
          $inputDD.append( modal.createCommonInput( type, data, tab ) );
          break;
        case 'password':
          $inputDD.append(
            modal.createCommonInput( type, data, tab ),
            $('<span/>', {'class': 'item-password-eye'}).append(
              '<svg viewBox="0 0 64 64" class="workspace-button-svg"><use href="#icon-eye-close" /></svg>'
            )
          );
          break;
        case 'number':
          $inputDD.append(
            modal.createCommonInput( type, data, tab ),
            '<div class="item-number-range">'
              + '<div class="item-number-range-knob"></div>'
              + '<div class="item-number-range-lower"></div>'
              + '<div class="item-number-range-tooltip"></div>'
            + '</div>'
          );
          break;
        case 'radio':
          $inputDD.append('<ul class="item-radio-list"></ul');
          break;
        default:
      }
      $dl.append( $inputDD );
      
      // Note
      if ( data.note !== undefined ) {
        // テキストを無害化し改行（\n）を置換
        const text = $('<div/>', {'text': data.note }).html().replace(/\n/g, '<br>');
        $dl.append( $('<dd/>', {'class': 'item-note item-' + type + '-note', 'html': text }) );
      }
      
      // Event
      if ( type === 'number') {
        modal.faderEvent( $dl );
      }
      
      // 入力チェック
      if ( ['text', 'textarea', 'password'].indexOf( type) !== -1 ) {
        
        const $input = $dl.find('input, textarea'),
              $count = $dl.find('.item-word-number'),
              min = $input.attr('data-min'),
              max = $input.attr('data-max'),
              value = $input.val(),
              length = value.length;
        
        // 必須チェック
        modal.requiredCheck( $input );
        
        // 入力範囲内かチェック
        const numCheck = function(){
          const num = $input.val().length;
          if ( num > 0 ) {
            if ( min !== undefined && max !== undefined ) {
              if ( num >= min && num <= max ) {
                $input.add( $count ).removeClass('count-error');
              } else {
                $input.add( $count ).addClass('count-error count-input-event');
              }
            }
          } else {
            $input.add( $count ).removeClass('count-error');
          }
        };
        numCheck();
        $count.text( length );
        
        // 正規表現チェック
        const errorCheck = function(){
          if ( data.validation !== undefined ) {
            const reg = new RegExp( data.validation ),
                  $target = $input.add( $dl.find('.item-error') ),
                  val = $input.val();
            if ( val !== undefined ) {
              if ( !reg.test( val ) && val !== '') {
                $target.addClass('input-error regex-input-event');
              } else {
                $target.removeClass('input-error');
              }
            } else {
              $target.removeClass('input-error');
            }
          }
        };
        errorCheck();
        if ( data.validation !== undefined ) {
          const $inputError = $('<div/>', {
            'class': 'item-error item-' + type + '-error',
            'text': ( data.inputError !== undefined )? data.inputError: 'Error'
          });
          $dl.find('.item-' + type + '-area').append( $inputError );
        }
        
        // 再入力一致チェック
        const misatchErrorCheck = function(){
          if ( data.matchTargetName !== undefined ) {
            const $matchTaget = modal.$modal.find('[name="' + data.matchTargetName + '"]'),
                  matchTargetVal = $matchTaget.val(),
                  $target = $input.add( $dl.find('.item-mismatch-error') ),
                  val = $input.val();
            if ( val !== matchTargetVal && val !== '' && matchTargetVal !== '') {
              $target.addClass('input-mismatch-error mismatch-input-event');
            } else {
              $target.removeClass('input-mismatch-error');
            }
          }
        };
        if ( data.matchTargetName !== undefined ) {
          const $mismatchError = $('<div/>', {
            'class': 'item-mismatch-error item-' + type + '-mismatch-error',
            'text': ( data.mismatchErrorMessage !== undefined )? data.mismatchErrorMessage: 'Error'
          });
          $dl.find('.item-' + type + '-area').append( $mismatchError );
          
          // フォーカスした時に対象にイベントを付ける
          $input.one('focus', function(){
            const $matchTaget = modal.$modal.find('[name="' + data.matchTargetName + '"]');
            $matchTaget.on({
              'input': function(){
                if ( $input.is('.mismatch-input-event') ) misatchErrorCheck();
              },
              'blur': function(){
                misatchErrorCheck();
              }
            });
          });
        }
        
        // イベント
        $input.on({
          'input': function(){
            modal.requiredCheck( $input );
            $count.text( $input.val().length );
            if ( $input.is('.count-input-event') ) numCheck();
            if ( $input.is('.regex-input-event') ) errorCheck();
            if ( $input.is('.mismatch-input-event') ) misatchErrorCheck();            
          },
          'blur': function(){
            $input.removeClass('count-input-event regex-input-event mismatch-input-event');
            numCheck();
            errorCheck();
            misatchErrorCheck();
          }
        });
        
        // イベントを実行順で登録する
        $input.one({
          'focus': function(){
            if ( data.matchTargetName !== undefined ) {
              const $matchTaget = modal.$modal.find('[name="' + data.matchTargetName + '"]');
              $matchTaget.on({
                'input': function(){
                  if ( $input.is('.mismatch-input-event') ) misatchErrorCheck();
                },
                'blur': function(){
                  $input.removeClass('mismatch-input-event');
                  misatchErrorCheck();
                }
              });
            }
            $input.on({
              'input blur': function(){ modal.inputErrorCheck(); }
            });
          }
        });
      }
      
      return $dl;
    },
    /* -------------------------------------------------- *\
       Item common ( textarea, text, number, password )
    \* -------------------------------------------------- */
    'createCommonInput': function( type, data, tab ){
      const defName = ( data.name !== undefined )? data.name: '',
            name = ( tab !== undefined )? tab + '-' + defName: defName,
            defValue = ( data.value !== undefined )? data.value: '',
            inputValue = this.searchValue( this.valueJSON, name ),
            value = ( inputValue === undefined )? defValue: inputValue,
            className = ( data.class !== undefined )? ' ' + data.class: '',
            placeholder = ( data.placeholder !== undefined )? data.placeholder: '';
      
      let $input;
      if ( type !== 'textarea') {
        $input = $('<input>', {
          'type': type,
          'name': name,
          'data-name': defName,
          'class': 'item-' + type + ' ' + defName + className,
          'placeholder' : placeholder,
          'value': value        
        });
      } else if ( type === 'textarea') {
        $input = $('<textarea/>', {
          'type': type,
          'name': name,
          'data-name': defName,
          'class': 'item-' + type + ' ' + defName + className,
          'placeholder' : placeholder,
          'text': value        
        });
      }
      if ( data.required !== undefined ) $input.attr('required', 'required');
      if ( data.min !== undefined ) $input.attr('data-min', data.min );
      if ( data.max !== undefined ) $input.attr('data-max', data.max );
      
      if ( type === 'number') $input.attr('autocomplete', 'off');
      
      return $input;
    },
    /*
    */
    'requiredCheck': function( $input ) {
      const val = $input.val();
      if ( $input.attr('required') !== undefined ) {
        if ( val === '' || val === null ) {
          $input.addClass('required-error');
        } else {
          $input.removeClass('required-error');
        }
      }
    },
    /* -------------------------------------------------- *\
       フェーダーイベント
    \* -------------------------------------------------- */
    'faderEvent': function( $item ) {
      const modal = this,
            $window = $( window ),
            $fader = $item.find('.item-number-range'),
            $input = $item.find('.item-number'),
            $knob = $item.find('.item-number-range-knob'),
            $lower = $fader.find('.item-number-range-lower'),
            $tooltip = $fader.find('.item-number-range-tooltip'),
            min = Number( $input.attr('data-min') ),
            max = Number( $input.attr('data-max') ),
            inputRange = max - min;

      let   width = $fader.width(),
            val = $input.val(),
            ratio, positionX;
      
      modal.requiredCheck( $input );
      
      // 位置をセット
      const setPosition = function(){
        const p =  Math.round( ratio * 100 ) + '%';
        $knob.css('left', p );
        $lower.css('width', p );
      };
      // 割合から位置と値をセット
      const ratioVal = function(){
        if ( ratio <= 0 ) ratio = 0;
        if ( ratio >= 1 ) ratio = 1;
        val = Math.round( inputRange * ratio ) + min;
        $input.val( val );
        
        setPosition();
      };
      // 値から位置をセット
      const valPosition = function(){
        if ( val === '') val = min;
        ratio = ( val - min ) / inputRange;
        if ( Number.isNaN( ratio ) ) ratio = 0;
        positionX = Math.round( width * ratio );
        
        setPosition();
        modal.requiredCheck( $input );
      };
      valPosition();
      
      $fader.on({
        'mousedown': function( mde ){
          if ( mde.button === 0 ) {
            getSelection().removeAllRanges();

            $fader.addClass('active');
            const clickX = mde.pageX - $fader.offset().left;

            width = $fader.width();
            ratio = clickX / width;
            positionX = Math.round( width * ratio );

            ratioVal();

            $window.on({
              'mouseup.faderKnob': function(){
                $fader.removeClass('active');
                $window.off('mouseup.faderKnob mousemove.faderKnob');
                valPosition();
              },
              'mousemove.faderKnob': function( mme ){
                const moveX = mme.pageX - mde.pageX;
                ratio = ( positionX + moveX ) / width;                  
                ratioVal();
              }
            });
          }
        },
        // ツールチップ
        'mouseenter': function(){
          const left =  $fader.offset().left,
                top = $fader.offset().top;
          $tooltip.show();
          width = $fader.width();
          $window.on({
            'mousemove.faderTooltip': function( mme ){
              const tRatio = ( mme.pageX - left ) / width;
              let   tVal = Math.round( inputRange * tRatio ) + min;
              if ( tVal < min ) tVal = min;
              if ( tVal > max ) tVal = max ;
              $tooltip.text( tVal );
              $tooltip.css({
                'left': mme.pageX,
                'top': top
              });
            }
          });
        },
        'mouseleave': function(){
          $tooltip.hide();
          $window.off('mousemove.faderTooltip');
        }
      });
      
      $input.on('input', function(){
        val = $input.val();
        width = $fader.width();
        if ( val !== '') {
          if ( val < min ) {
            $input.val( min );
            val = min;
          }
          if ( val > max ) {
            $input.val( max );
            val = max;
          }
        } else {
          val = '';
        }
        valPosition();
      });
    },
    /* -------------------------------------------------- *\
       input TEXT
    \* -------------------------------------------------- */
    'createInput': function( text, tabNumber ){
      const modal = this,
            $item = modal.createCommonItem('text', text, tabNumber );

      // タブ名と入力を合わせる
      const $tabNameInput = $item.find('.tab-name-link');
      if ( $tabNameInput.length ) {
        $tabNameInput.on({
          'input': function(){
            const $this = $( this ),
                  $tab = $this.closest('.modal-tab-block'),
                  defaultTitle = $tab.find('.modal-tab-item').attr('data-default'),
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
      return $item;
    },
    /* -------------------------------------------------- *\
       Number
    \* -------------------------------------------------- */
    'createNumber': function( number, tabNumber ){
      const modal = this,
            $item = modal.createCommonItem('number', number, tabNumber );
      
      return $item;
    },
    /* -------------------------------------------------- *\
       Textarea
    \* -------------------------------------------------- */
    'createTextarea': function( textarea, tabNumber ){
      const modal = this,
            $item = modal.createCommonItem('textarea', textarea, tabNumber );
            
      return $item;
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
      const modal = this,
            $item = modal.createCommonItem('password', password, tabNumber ),
            $pass = $item.find('.item-password');
      
      const passwrodClassCheck = function( val ){
        if ( val === '') {
          $pass.removeClass('password-input');
        } else {
          $pass.addClass('password-input');
        }
      };
      passwrodClassCheck( $pass.val() );
      
      // パスワード入力１文字以上あれば
      $item.find('.item-password').on('input', function(){
        const val = $( this ).val();
        passwrodClassCheck( val );
      });
      
      // パスワード入力マスク解除
      $item.find('.item-password-eye').on({
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
      
      return $item;
    },
    /* -------------------------------------------------- *\
       input RADIO
    \* -------------------------------------------------- */
    'createRadio': function( radio, tabNumber ){
      const modal = this,
            $item = modal.createCommonItem('radio', radio, tabNumber );
            
      const name = ( tabNumber !== undefined )? tabNumber + '-' + radio.name: radio.name,
            checkedValue = this.searchValue( this.valueJSON, name ),
            checked = ( checkedValue !== undefined )? name + '-' + checkedValue: undefined,
            className = ( radio.class !== undefined )? ' ' + radio.class: '';
      
      for ( const key in radio.item ) {
        $item.find('.item-radio-list').append(
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
        $item.find('#' + checked ).prop('checked', true );
      } else {
        $item.find('.item-radio').eq(0).prop('checked', true );
      }
      return $item;
    },
    /* -------------------------------------------------- *\
       自由
    \* -------------------------------------------------- */
    'createFreeItem': function( free, tabNumber ){
      const modal = this,
            $item = modal.createCommonItem('freeitem', free, tabNumber );
            
      const name = ( tabNumber !== undefined )? tabNumber + '-' + free.name: free.name,
            freeVal = this.searchValue( this.valueJSON, name ),
            list = ( freeVal === undefined )? {'':''}: JSON.parse( freeVal ),
            className = ( free.class !== undefined )? ' ' + free.class: '';
      
      const addLine = function( key, value ){
        return ''
        + '<li class="item-freeitem-item">'
          + '<div class="item-freeitem-item-move"></div>'
          + '<div class="item-freeitem-item-name"><input class="item-freeitem-input item-text name" type="text" value="' + key + '" placeholder="項目名を入力してください。"></div>'
          + '<div class="item-freeitem-item-content"><input class="item-freeitem-input item-text content" type="text" value="' + value + '" placeholder="項目内容を入力してください。"></div>'
          + '<div class="item-freeitem-item-delete"></div>'
        + '</li>';
      };
      
      let inputHTML = '<ul class="item-freeitem-list">';
      for ( const key in list ) {
        inputHTML += addLine( key, list[key] );
      }
      inputHTML += '</ul>'
      + '<ul class="item-freeitem-menu-list">'
        + '<li class="item-freeitem-menu-item"><button class="epoch-button item-freeitem-add-button add" type="button">項目を追加する</button></li>'
      + '</ul>';
      
      $item.find('.item-freeitem-area').append(
        $('<div/>', {
          'name': name,
          'data-name': free.name,
          'class': 'item-freeitem ' + free.name + className,
          'html': inputHTML
        })
      );      
      
      const deleteCheck = function(){
        const $delete = $item.find('.item-freeitem-item-delete'),
              $move = $item.find('.item-freeitem-item-move');
        if ( $delete.length === 1 ) {
          $delete.add( $move ).addClass('disabled');
        } else {
          $delete.add( $move ).removeClass('disabled');
        }
      };
      deleteCheck();
      
      $item.find('.item-freeitem-add-button').on('click', function(){
        const $add = $( addLine('','') );
        $item.find('.item-freeitem-list').append( $add );
        $add.find('.item-freeitem-input').eq(0).focus();
        deleteCheck();
      });
      // 移動
      $item.on('mousedown', '.item-freeitem-item-move', function( mde ){
        getSelection().removeAllRanges();
        
        const $move = $( this ),
              $window = $( window );
        if ( !$move.is('.disabled') ) {
          const $line = $move.closest('.item-freeitem-item'),
                $list = $line.closest('.item-freeitem-list'),
                height = $line.outerHeight(),
                defaultY = $line.position().top,
                $dummy = $('<li class="item-freeitem-dummy"></li>');
          $list.addClass('active');
          $line.addClass('move').css('top', defaultY ).after( $dummy )
          $dummy.css('height', height );
          
          $window.on({
            'mousemove.freeMove': function( mme ){
              const maxY = $list.outerHeight() - height;
              let positionY = defaultY + mme.pageY - mde.pageY;
              if ( positionY < 0 ) positionY = 0;
              if ( positionY > maxY ) positionY = maxY;
              $line.css('top', positionY );
              if ( $( mme.target ).closest('.item-freeitem-item').length ) {
                const $target = $( mme.target ).closest('.item-freeitem-item'),
                      targetNo = $target.index(),
                      dummyNo = $dummy.index();
                if ( targetNo < dummyNo ) {
                  $target.before( $dummy );
                } else {
                  $target.after( $dummy );
                }
              }
            },
            'mouseup.freeUp': function(){
              $window.off('mousemove.freeMove mouseup.freeUp');
              $list.removeClass('active');
              $line.removeClass('move');
              $dummy.replaceWith( $line );
            }
          });
        }
      });
      // 削除
      $item.on('click', '.item-freeitem-item-delete', function(){
        const $delete = $( this );
        if ( !$delete.is('.disabled') ) {
          $delete.closest('.item-freeitem-item').remove();
          deleteCheck();
        }
      });
      return $item;
    },
    /* -------------------------------------------------- *\
       リスト選択
    \* -------------------------------------------------- */
    'createListSelect': function( select, tabNumber ){
      const modal = this,
            $item = modal.createCommonItem('list-select', select, tabNumber );
            
      const name = ( tabNumber !== undefined )? tabNumber + '-' + select.name: select.name,
            checkedValue = modal.searchValue( modal.valueJSON, name ),
            checkedIdValue = modal.searchValue( modal.valueJSON, name + '-id'),
            checked = ( checkedValue !== undefined )? name + '-' + checkedValue: undefined,
            checkedID = ( checkedIdValue !== undefined )? checkedIdValue: '',
            className = ( select.class !== undefined )? ' ' + select.class: '';
      
      // 選択リスト
      const $selectInfo = $('<dd/>', {
        'class': 'item-list-select select-on' + className
      }).append(
        $('<div/>', {
          'class': 'item-list-select-name'
        })
      ).append(
        $('<input>', {
          'type': 'hidden',
          'class': 'item-list-select-id',
          'name': name + '-id'
        })
      );
      modal.createListSelectSetList( $selectInfo, checkedID, select.list, select.col );
      $item.append( $selectInfo );    
      
      if ( select.button ) {
        // 選択ボタン
        let buttonHTML = ''
        + '<ul class="item-list-select-button-list">';
        for ( const key in select.button ) {
          buttonHTML += ''
          + '<li class="item-list-select-button-item">'
            + '<button class="epoch-button modal-block-button item-list-select-button" data-button="' + key + '">' + modal.fn.textEntities( select.button[key] ) + '</button>'
          + '</li>';
        }
        buttonHTML += '</ul>';

        if ( select.item ) {
          $item.find('.item-list-select-area').append('<ul class="item-radio-list"></ul>')
          for ( const key in select.item ) {
            $item.find('.item-radio-list').append(
              $('<li/>', {'class': 'item-radio-item'}).append(
                $('<input>', {
                  'class': 'item-radio item-radio-' + key + className,
                  'type': 'radio',
                  'id': name + '-' + key,
                  'value': key,
                  'name': name
                }),
                $('<label/>', {
                  'class': 'item-radio-label',
                  'for': name + '-' + key,
                  'text': select.item[key]
                })
              )
            );
          }
          $item.find('.item-radio-item:last-child').append( buttonHTML );

          // ボタンの有効・無効切り替え
          const $checkbox = $item.find('.item-radio'),
                $button = $item.find('.item-list-select-button'),
                $selectName = $item.find('.item-list-select');
          $button.prop('disabled', true );
          $selectName.removeClass('select-on');
          $checkbox.on('change', function(){
            if ( $( this ).is('.item-radio-select') ) {
              $button.prop('disabled', false );
              $selectName.addClass('select-on');
            } else {
              $button.prop('disabled', true );
              $selectName.removeClass('select-on');
            }
          });
          if ( checked !== undefined ) {
            $checkbox.filter('#' + checked ).prop('checked', true );
            if ( $checkbox.filter('#' + checked ).is('.item-radio-select') ) {
              $button.prop('disabled', false );
              $selectName.addClass('select-on');
            }
          } else {
            $checkbox.eq(0).prop('checked', true );
          }

        } else {
          $item.append( $('<dd>', {
            'class': 'item-list-select-button-area',
            'html': buttonHTML
          }));
        }
      }
        
      return $item;
    },
    /* -------------------------------------------------- *\
       セレクトリストの作成
    \* -------------------------------------------------- */
    'createListSelectSetList': function( $target, id, list, col ){
      const modal = this,
            idArray = id.split(',');

      const n = list.filter( function(f) {
        if ( idArray.indexOf( String( f[0] )) !== -1 ) {
          return f;
        }
      });
      const nL = n.length;
      let listHTML = '';
      if ( nL !== 0 ) {
        listHTML += '<ul class="item-list-select-name-list">';
        for ( let i = 0; i < nL; i++ ) {
          listHTML += '<li class="item-list-select-name-item">' + modal.fn.textEntities( n[i][col] )+ '</li>';
        }
        listHTML += '</ul>';
      } else {
        listHTML += '<p class="item-list-select-empty">No data</p>';
      }
      $target.find('.item-list-select-name').html( listHTML );
      $target.find('.item-list-select-id').val( id );
    },
    /* -------------------------------------------------- *\
       メッセージ
    \* -------------------------------------------------- */
    'createMessage': function( message ){
      const $message = $('<dl/>', {'class': 'item-message-block item-block'}),
            className = ( message.class !== undefined )? ' ' + message.class: '',
            color = ( message.color === undefined )? '333333': message.color;
      if ( message.title !== undefined ) {
        $message.append( $('<dt/>', {'class': 'item-message-title item-title', 'text': message.title }) );
      }
      if ( message.text !== undefined ) {
        $message.append(
          $('<dd/>', {'class': 'item-message-area'}).append(
            $('<div/>', {
              'class': 'item-message ' + className,
              'text': message.text,
              'style': 'color:#' + color
            })
          )
        );
      }
      return $message;
    },
    /* -------------------------------------------------- *\
       未入力・エラーの表示
    \* -------------------------------------------------- */
    'errorCount': function( requiredNum, errorNum ){
      const $modal = this.$modal,
            $requiredCount = $modal.find('.modal-required-count'),
            $errorCount = $modal.find('.modal-error-count');
    

        if ( requiredNum === 0 ) {
          $requiredCount.hide();
        } else {
          $requiredCount.show();
          $requiredCount.find('.modal-required-count-num').text( requiredNum );
        }

        if ( errorNum === 0 ) {
          $errorCount.hide();
        } else {
          $errorCount.show();
          $errorCount.find('.modal-error-count-num').text( errorNum );
        }
    },
    /* -------------------------------------------------- *\
       入力内に未入力（必須）、エラーがあればOKボタンを無効化する
    \* -------------------------------------------------- */
    'inputErrorCheck': function(){
      const modal = this;
      if ( modal.$modal !== undefined ) {
        const $target = modal.$modal.find('input, textarea').not(':disabled'),
              $okButton = modal.$modal.find('.modal-menu-button[data-button="ok"]'),
              inputError = $target.filter('.input-error, .input-mismatch-error').length,
              countError = $target.filter('.count-error').length,
              requiredError = $target.filter('.required-error').length,
              errorCount = inputError + countError + requiredError;
        
        if ( errorCount > 0 ) {
          $okButton.prop('disabled', true );
        } else {
          $okButton.prop('disabled', false );
        }

        modal.errorCount( requiredError, inputError + countError );
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