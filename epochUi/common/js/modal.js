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
    this.modalJSON = modalJSON,
    this.valueJSON = valueJSON;    
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
       ユニークなTab IDを返す
    \* -------------------------------------------------- */
    'getUniqueTabID': function( ) {
      const newUniqueTabID = function() {
        const strong = 9999,
              UniqueTabID = 't' + new Date().getTime().toString(16) + Math.floor( strong * Math.random()).toString(16);
        // 念のためすでに使われているか確認する
        if ( $('#' + UniqueTabID ).length ) {
          newUniqueTabID();
        } else {
          return UniqueTabID;
        }
      }
      return newUniqueTabID();
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
        } else if ( type === 'string') {
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
    'open': function( target, funcs, width ){
        const modal = this,
              $modalContainer = $('#modal-container'),
              $modal = modal.createMain( modal.modalJSON[target], width );
        $('body').addClass('modal-open');
        $modalContainer.html( $modal ).css('display','flex');
        
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
              funcs.ok( $modal );
              modal.close();
              break;
          }
        });
        
        // タブ
        if ( $modal.find('.modal-tab-block').length ) {
          $modal.find('.modal-tab-block').each(function(){
            const $tabBlock = $( this );

            // タブ切り替え、幅調整
            $tabBlock.on({
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
               
        if ( funcs.callback !== undefined ) {
          funcs.callback();
        }

    },
    /* -------------------------------------------------- *\
       モーダルを閉じる
    \* -------------------------------------------------- */
    'close': function(){
      $('#modal-container').empty().css('display','none');
      $('body').removeClass('modal-open');
    },
    /* -------------------------------------------------- *\
       モーダルを切り替える
    \* -------------------------------------------------- */
    'change': function( type, funcs, width ){
      $('#modal-container').empty();
      this.open( type, funcs, width );
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
      for ( let key in footer ) {
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
              $('<div/>', {'class': 'modal-block-header'}).append(
                $('<div/>', {'class': 'modal-block-title', 'text': block[key].title }),
                ( $button !== false )? $button: ''
              ),
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
              const tabID = modal.getUniqueTabID();
              
              const $item = $('<li/>', {
                'class': 'modal-tab-item',
                'data-id': tabID
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
        const target = this.valueJSON[ tab.target.key1 ];
        if ( Object.keys( target ).length > 0 ) {
          for ( const key in target ) {
            $tabList.append(
              $('<li/>', {
                'class': 'modal-tab-item',
                'data-id': key,
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
                'id': key,
                'class': 'modal-tab-body-block'
              }).append(
                this.createItem( tab.item, key )
              )
            );
          }
        } else {
          emptyTab();
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
      $tabBlock.find('.modal-tab-item').css('width', 'auto');
      
      $tab.addClass('open');
      $tabBlock.find('.modal-tab-body-block').eq( tabNumber ).addClass('open');
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
              case 'textarea': return modal.createTextarea( data, tabNumber );
              case 'password': return modal.createPassword( data, tabNumber );
              case 'radio': return modal.createRadio( data );
              case 'loading': return modal.createLoadingBlock( data, tabNumber );
              case 'reference': return modal.createReference( data, tabNumber );
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
      const $input = $('<dl/>', {'class': 'item-text-block item-block'}),
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
        ( text.note !== undefined )? $('<dd/>', {'class': 'item-text-note'}): ''
      );
      // タブ名と入力を合わせる
      const $tabNameInput = $input.find('.tab-name-link');
      if ( $tabNameInput.length ) {
        $tabNameInput.on({
          'input': function(){
            const $input = $( this ),
                  id = $input.closest('.modal-tab-body-block').attr('id'),
                  val = $input.val(),
                  reg = new RegExp( text.regexp );
            let repositoryName;
            if ( val.match( reg ) ) {
              repositoryName = val.replace( reg, '$1');    
            } else {
              repositoryName = '';
            }
            $('[data-id="' + id + '"]').find('.modal-tab-text').text(repositoryName);
          }
        });
      }
      return $input;
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
          })
        )
      );
      return $textarea;
    },
    /* -------------------------------------------------- *\
       Reference
    \* -------------------------------------------------- */
    'createReference': function( reference, tabNumber ){
      const $input = $('<dl/>', {'class': 'item-reference-block item-block'}),
            value = this.searchValue( this.valueJSON, tabNumber + '-' + reference.target );
      $input.append(
        $('<dt/>', {'class': 'item-reference-title item-title', 'text': reference.title }),
        $('<dd/>', {'class': 'item-reference-area'}).append(
          $('<span/>', {
            'text': value,
            'class': 'item-reference'
          })
        )
      );
      return $input;
    },
    /* -------------------------------------------------- *\
       input PASSWORD
    \* -------------------------------------------------- */
    'createPassword': function( password, tabNumber ){
      const $input = $('<dl/>', {'class': 'item-password-block item-block'}),
            value = this.searchValue( this.valueJSON, password.name ),
            name = ( tabNumber !== undefined )? tabNumber + '-' + password.name: password.name;
      $input.append(
        $('<dt/>', {'class': 'item-password-title item-title', 'text': password.title }),
        $('<dd/>', {'class': 'item-password-area'}).append(
          $('<input>', {
            'type': 'password',
            'name': name,
            'class': 'item-password ' + password.name,
            'placeholder' : password.placeholder,
            'value': value
          }),
          $('<span/>', {
            'class': 'item-password-eye'
          })
        ),
        $('<dd/>', {'class': 'item-password-note'})
      );
      return $input;
    },
    /* -------------------------------------------------- *\
       input RADIO
    \* -------------------------------------------------- */
    'createRadio': function( radio ){
      const $radio = $('<dl/>', {'class': 'item-radio-block item-block'}).prepend(
              ( radio.title !== undefined )? $('<dt/>', {'class': 'item-radio-title item-title', 'text': radio.title }): '',
              $('<dd/>', {'class': 'item-radio-area'}).append(
                $('<ul/>', {'class': 'item-radio-list'})
              ),
              ( radio.note !== undefined )? $('<dd/>', {'class': 'item-radio-note'}): ''
            ),
            checked = radio.name + '-' + this.searchValue( this.valueJSON, radio.name );
      for ( let key in radio.item ) {
        $radio.find('.item-radio-list').append(
          $('<li/>', {'class': 'item-radio-item'}).append(
            $('<input>', {
              'class': 'item-radio',
              'type': 'radio',
              'id': radio.name + '-' + key,
              'value': key,
              'name': radio.name
            }),
            $('<label/>', {
              'class': 'item-radio-label',
              'for': radio.name + '-' + key,
              'text': radio.item[key]
            })
          )
        );
      }
      $radio.find('#' + checked ).prop('checked', true );
      return $radio;
    }
};