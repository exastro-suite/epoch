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

function epochTable() {}
epochTable.prototype = {
  'setup': function( target, thArray, tbArray ){
      
      if ( tbArray.length ) { 
        const et = this;
      
        et.pagingPage = 1;
        et.pagingNumber = 100;
        et.pagingTotalPage= 0;

        et.fn = new epochCommon();
        et.ws = new webStorage();

        et.$table = $('<div/>', {
          'class': 'epoch-table-container'
        }).append(
          // Header
          $('<div/>', {
            'class': 'eth'
          }).append(''
            + '<div class="etf-s">'
              + '<div class="etf-si">'
                + '<button class="etf-b epoch-popup-m" data-button="filter-open" title="フィルタを追加します。">'
                  + '<svg viewBox="0 0 64 64" class="etf-sis">'
                    + '<polygon points="64,0 36.88,0 27.12,0 0,0 0,10.47 27.12,35.02 27.12,64 36.88,57.02 36.88,35.02 64,10.47 "/>'
                  + '</svg>'
                + '</button>'
              + '</div>'
              + '<div class="etf-sa">'
                + '<ul class="etf-sal">'
                + '</ul>'
              + '</div>'
              + '<div class="etf-sc">'
                + '<button class="etf-b epoch-popup-m" title="フィルタをクリアします。" data-button="filter-clear" disabled>'
                  + '<span class="etf-sci"></span>'
                + '</button>'
              + '</div>'
            + '</div>'
          ),
          // Body
          $('<div/>', {
            'class': 'etb'
          }).append(
            // Table
            $('<table/>', {
              'class': 'et'
            }).append(
              // thead
              $('<thead/>', {
                'class': 'et-h'
              }),
              // tbody
              $('<tbody/>', {
                'class': 'et-b'
              })
            )
          ),
          // Footer
          $('<div/>', {
            'class': 'ett'
          }).append(
            $('<div/>', {
              'class': 'etp'
            }).append(''
              + '<div class="etp-w">'
                + '<div class="etp-ih">表示する行数</div>'
                + '<div class="etp-ib">'
                  + '<div class="etp-s">'
                    + '<div class="etp-sn"></div>'
                    + '<ul class="etp-sl">'
                      + '<li class="etp-si"><input type="radio" name="etp-s-r" id="etp-s-r100" class="etp-sr" value="100"><label for="etp-s-r100" class="etp-sb">100</label></li>'
                      + '<li class="etp-si"><input type="radio" name="etp-s-r" id="etp-s-r50" class="etp-sr" value="50"><label for="etp-s-r50" class="etp-sb">50</label></li>'
                      + '<li class="etp-si"><input type="radio" name="etp-s-r" id="etp-s-r25" class="etp-sr" value="25"><label for="etp-s-r25" class="etp-sb">25</label></li>'
                      + '<li class="etp-si"><input type="radio" name="etp-s-r" id="etp-s-r10" class="etp-sr" value="10"><label for="etp-s-r10" class="etp-sb">10</label></li>'
                    + '</ul>'
                  + '</div>'
                + '</div>'
                + '<div class="etp-if">行</div>'
              + '</div>'
              + '<div class="etp-w">'
                + '<div class="etp-ib etp-ns"></div>'
                + '<div class="etp-ib">-</div>'
                + '<div class="etp-ib etp-ne"></div>'
                + '<div class="etp-ib">/</div>'
                + '<div class="etp-ib etp-na"></div>'
                + '<div class="etp-if">件</div>'
              + '</div>'
              + '<div class="etp-w">'
                + '<div class="etp-ib etp-pc"></div>'
                + '<div class="etp-ib">/</div>'
                + '<div class="etp-ib etp-pa"></div>'
                + '<div class="etp-if">頁</div>'
              + '</div>'
              + '<div class="etp-w">'
                + '<div class="etp-ib"><button class="etp-b" data-button="start"></button></div>'
                + '<div class="etp-ib"><button class="etp-b" data-button="prev"></button></div>'
                + '<div class="etp-ib"><button class="etp-b" data-button="next"></button></div>'
                + '<div class="etp-ib"><button class="etp-b" data-button="end"></button></div>'
              + '</div>'
            )
          ),
          // Filter
          $('<div/>', {
            'class': 'etf-c'
          }).append(''
            + '<div class="etf-a">'
              + '<div class="etf-ah">'
                + '<div class="etf-ah-t">フィルタ</div>'
                + '<div class="etf-ah-c"><button class="etf-ah-cb" data-button="cancel"></butto></div>'
              + '</div>'
              + '<div class="etf-ab">'
              + '</div>'
              + '<div class="etf-af">'
                + '<ul class="etf-af-ml">'
                  + '<li class="etf-af-mi">'
                    + '<button class="epoch-button etf-af-mb positive" data-button="ok">フィルタ</button>'
                  + '</li>'
                  + '<li class="modal-menu-item">'
                    + '<button class="epoch-button etf-af-mb negative" data-button="cancel">閉じる</button>'
                  + '</li>'
                + '</ul>'
              + '</div>'
            + '</div>'
          ),
          // Style
          $('<style/>', {
            'class': 'ets'
          })
        );

        // $キャッシュ
        et.$header = et.$table.find('.eth');
        et.$body = et.$table.find('.etb');
        et.$footer = et.$table.find('.ett');
        et.$filter = et.$table.find('.etf-c');
        et.$style = et.$table.find('.ets');

        et.$thead = et.$table.find('.et-h');
        et.$tbody = et.$table.find('.et-b');

        et.$rowNumber = et.$table.find('.etp-sn');
        et.$rowSelectList = et.$table.find('.etp-sl');
        et.$rowSelectRadio = et.$table.find('.etp-sr');

        et.$allNum = et.$table.find('.etp-na');
        et.$startNum = et.$table.find('.etp-ns');
        et.$endNum = et.$table.find('.etp-ne');

        et.$allPageNum = et.$table.find('.etp-pa');
        et.$currentPageNum = et.$table.find('.etp-pc');

        et.$filterBlock = et.$table.find('.etf-ab');

        // ページング
        et.allPageNumber = 0;

        et.$target = $( target );
        et.th = thArray.concat(); // thead
        et.tb = tbArray.concat(); // tbody
        et.tdCopy = tbArray.concat(); // 初期値として使う

        et.$target.html( et.$table );

        et.setHeaderHTML();
        et.setFilterHTML();

        et.setFilter();
        et.setFilterStatus();

        et.setBodyHTML();

        // フィルタオープン
        et.$header.find('.etf-b').on('click', function(){
          const $button = $( this ),
                type = $button.attr('data-button');
          switch( type ) {
            case 'filter-open':
              et.$filter.show();
              et.setFilterValue();
              break;
            case 'filter-clear':
              $button.mouseleave();
              et.clearFilter();
              et.sortClear();
              et.pagingPage = 1;
              et.setBodyHTML();
              break;
          }
        });
        // フィルタダイアログ
        et.$filter.find('.epoch-button, .etf-ah-cb').on('click', function(){
          const $button = $( this ),
                type = $button.attr('data-button');
          switch( type ) {
            case 'ok':
              et.getFilterValue();
              et.setFilter();
              et.setFilterStatus();
              et.pagingPage = 1;
              et.sortClear();
              et.setBodyHTML();
              et.$filter.hide();
              break;
            case 'cancel':
              et.$filter.hide();
              break;
          }
        });
        // フィルタ削除
        et.$header.find('.etf-sa').on('click', '.etf-sad-di', function(){
          const $button = $( this ),
                colNumber = $button.attr('data-col');
          $button.mouseleave();
          if ( et.$header.find(('.etf-sai')).length === 1 ) {
            et.clearFilter();
          } else {
            $button.closest('.etf-sai').remove();
            if ( et.th[colNumber] !== undefined && et.th[colNumber]['filterOption'] !== undefined ) {
              delete et.th[colNumber]['filterOption'];
            }
            et.setFilter();
          }
          et.pagingPage = 1;
          et.sortClear();
          et.setBodyHTML();
        });

        // ページング
        et.$footer.find('.etp-b').on('click', function(){
          const $button = $( this ),
                type = $button.attr('data-button');
          switch( type ) {
            case 'start':
              et.pageChange( 1 );
              break;
            case 'prev':
              et.pageChange( et.pagingPage - 1 );
              break;
            case 'next':
              et.pageChange( et.pagingPage + 1 );
              break;
            case 'end':
              et.pageChange( et.pagingTotalPage );
              break;
          }
          et.pagingCheck();
        });

        // 行数変更
        et.$rowNumber.text( et.pagingNumber ).on('click', function(){
          et.$rowSelectList.show();
          $( window ).on('click.pagingNumber', function(e){
            if ( !$( e.target ).closest('.etp-s').length ) {
              $( this ).off('click.pagingNumber');
              et.$rowSelectList.hide();
            }
          });
        });
        et.$rowSelectRadio.val([et.pagingNumber]).on('change', function(){
          et.pagingNumber = Number( $( this ).val() );
          et.pagingPage = 1;
          et.$rowNumber.text( et.pagingNumber );
          et.$rowSelectList.hide();
          et.setBodyHTML();
        });

        return et.$table;

      } else {
        // データがない場合
        const noDataHTML = ''
        + '<div class="et-nd"><div class="et-ndi">データがありません。</div></div>';
        $( target ).html( noDataHTML );
        return false;
      }
  },
  // ページングボタンDisabled制御
  'pagingCheck': function(){
      const et = this,
            $button = et.$footer.find('.etp-b');
      if ( et.pagingPage <= 1 ) {
        $button.filter('[data-button="start"],[data-button="prev"]').prop('disabled', true );
      } else {
        $button.filter('[data-button="start"],[data-button="prev"]').prop('disabled', false );
      }
      if ( et.pagingPage >= et.pagingTotalPage ) {
        $button.filter('[data-button="end"],[data-button="next"]').prop('disabled', true );
      } else {
        $button.filter('[data-button="end"],[data-button="next"]').prop('disabled', false );
      }
  },
  // thead and style
  'setHeaderHTML': function(){
      const et = this,
            th = et.th,
            thLength = th.length;
      let thHTML = '',
          tStyle = '';
      thHTML += '<tr class="et-r">';
      for( let i = 0; i < thLength; i++ ) {
          // HTML
          if ( ['hoverMenu'].indexOf( th[i].type ) === -1 ) {
          thHTML += ''
          + '<th class="et-c cn' + i + '">'
            + '<div class="et-ci';
          if ( th[i].sort === 'on') thHTML += ' et-cs'; // Srot
          thHTML += '" data-column-index="' + i + '">' + th[i].title + '</div>';
          if ( th[i].resize === 'on') thHTML += '<div class="et-cr"></div>'; // Resize
          thHTML += '</th>';
          }
          // Style
          const width = th[i].width,
                align = th[i].align;
          tStyle += '.et-c.cn' + i + '{';
          if ( width ) {
              if ( width === 'auto') {
                  tStyle += ''
                  + 'max-width:none;'
                  + 'flex: 1 1 auto;';
              } else {
                  tStyle += ''
                  + 'max-width:' + width + ';'
                  + 'flex: 0 0 ' + width + ';';
              }
          }
          tStyle += 'z-index:' + ( thLength - i ) + ';'
          tStyle += '}';
          if ( align ) {
              tStyle += '.et-b .et-c.cn' + i + '{'
              + 'text-align:' + align + ';'
              + '}'
          }
      }
      thHTML += '</tr>';
      et.$thead.html( thHTML );
      et.$style.html( tStyle );  
      
      // Sort
      et.$thead.find('.et-cs').on('click', function(){
          const sortType = function( s ) {
              if ( s === 'asc' || s === undefined ) {
                  s = 'desc';
              } else if ( s === 'desc') {
                  s = 'asc';
              }
              return s;
          };
          const $sort = $( this ),
                sort = sortType( $sort.attr('data-sort') ),
                index = $sort.attr('data-column-index');

          et.$thead.find('.et-cs').removeAttr('data-sort');
          $sort.attr('data-sort', sort );
          et.sort( index, sort );
          et.setBodyHTML();
      });
      
  },
  // tbody
  'setBodyHTML': function(){
      const et = this,
            th = et.th,
            tb = et.tb,
            na = tb.length,
            nd = String( na ).length,
            cp = et.pagingPage,
            pn = et.pagingNumber,
            ns = 1 + pn * ( cp - 1 ),
            ne = ( na > ns + pn - 1 )? ns + pn - 1: na,
            pa = Math.ceil( na / pn ),
            pd = String( pa ).length;
      
      et.pagingTotalPage = pa;
      
      et.$allNum.text( na.toLocaleString() );
      et.$startNum.html( et.zeroPadding( ns, nd ) );
      et.$endNum.html( et.zeroPadding( ne, nd ) );
      
      et.$allPageNum.text( pa.toLocaleString() );
      et.$currentPageNum.html( et.zeroPadding( cp, pd ) );
      
      let tbHTML = '';

      for( let i = ns - 1; i < ne; i++ ) {
          tbHTML += '<tr id="et-r' + i + '" class="et-r">';
          const cLength = tb[i].length;
          for( let j = 0; j < cLength; j++ ) {
              const thd = th[j],
                    tbd = tb[i][j];
              tbHTML += ''
              + '<td class="et-c cn' + j + ' et-c-' + thd.type + '">'
                + '<div class="et-ci">';

              if ( tbd !== null ) {
                  switch( thd.type ){
                      case 'text':
                      case 'list':
                      case 'date':
                      case 'number':
                          tbHTML += et.fn.textEntities( tbd );
                          break;
                      case 'html':
                          tbHTML += tbd;
                          break;
                      case 'hoverMenu':
                          tbHTML += et.hoverMenuListHTML( thd.menu, tbd );
                          break;
                      case 'status':
                          tbHTML += et.statusHTML( thd.list[tbd], tbd );
                          break;
                  }
              }
              tbHTML += ''
                + '</div>'
              + '</td>';
          }
          tbHTML += '</tr>';
      }
      et.$tbody.html( tbHTML );
      et.pagingCheck();
  },
  /* ------------------------------ *\
     Hover Menu HTML
  \* ------------------------------ */  
  'hoverMenuListHTML': function( menu, idKey ){
    let hoverMenuHTML = '<ul class="et-hm-l">';
    for ( const key in menu ) {
      hoverMenuHTML += '<li class="et-hm-i';
      if ( menu[key]['separate'] === 'on') hoverMenuHTML += ' et-hm-s';
      hoverMenuHTML += '">'
            + '<button class="et-hm-b epoch-popup-m" title="' + menu[key]['text'] + '" data-key="' + idKey + '" data-button="' + key + '">'
            + '<svg viewBox="0 0 64 64" class="et-hm-i"><use xlink:href="#' + menu[key]['icon'] + '" /></svg></button>'
        + '</li>';
    }
    hoverMenuHTML += '</ul>';
    return hoverMenuHTML;
  },
  /* ------------------------------ *\
     ステータスアイコン HTML
  \* ------------------------------ */  
  'statusHTML': function( text, type, popup ) {
    if ( popup === undefined ) popup = true;
    const popupClass = ( popup === true )? ' epoch-popup-m': '';
    return ''
      + '<span class="et-si' + popupClass + '" title="' + text + '" data-type="' + type +'">'
        + '<span class="et-sii"></span>'
      + '</span>';
  },
  /* ------------------------------ *\
     ソート
  \* ------------------------------ */  
  'sort': function( index, order ){
      const tb = this.tb;
      tb.sort(function( a, b ){
          const aS = ( typeof a[index] === 'number' && isFinite( a[index] ) )?
                      a[index]: String( a[index] ).toLowerCase(),
                bS = ( typeof b[index] === 'number' && isFinite( b[index] ) )?
                      b[index]: String( b[index] ).toLowerCase();
          if ( aS < bS ) {
              return ( order === 'asc')? -1: 1;
          } else if ( aS > bS ) {
              return ( order === 'asc')? 1: -1;
          } else {
            return 0;
          }
      });
  },
  // ソートクリア
  'sortClear': function(){
    this.$thead.find('.et-cs').removeAttr('data-sort');
  },
  // 指定ページを表示
  'pageChange': function( page ){
    this.pagingPage = page;
    this.setBodyHTML( this.tb );
  },
  // カンマ付きの0埋め
  'zeroPadding': function( num, digit ){
    let zeroPaddingNumber = '0';
    for ( let i = 1; i < digit; i++ ) {
      zeroPaddingNumber += '0';
    }
    zeroPaddingNumber = ( Number('1' + zeroPaddingNumber ) + num ).toLocaleString().slice(1).replace(/^,/, '');
    return zeroPaddingNumber.replace(/^([0,]+)/,'<span class="etp-z">$1</span>');    
  },
  // フィルタ入力欄HTML
  'setFilterHTML': function(){
    const et = this,
          th = et.th,
          thength = th.length;
    let filterHTML = '';
    for ( let i = 0; i < thength; i++ ) {
      if ( th[i].filter === 'on') {
        filterHTML += ''
        + '<div class="etf-fc" type="' + th[i].type+ '" data-array="' + i + '">'
          + '<div class="etf-fh">' + th[i].title + '</div>'
          + '<div class="etf-fb">';
        switch( th[i].type ) {
        case 'text':
          filterHTML += ''
            + '<div class="etf-fb-iwf"><input type="text" class="etf-fb-i etf-fb-it"></div>'
            + '<div class="etf-fb-iwf">'
              + '<ul class="etf-fb-fol">'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="r" class="etf-fb-fob" id="etf-fb-r' + i + '"><label for="etf-fb-r' + i + '" class="etf-fb-fot">正規表現</label></div>'
                + '</li>'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="l" class="etf-fb-fob" id="etf-fb-l' + i + '"><label for="etf-fb-l' + i + '" class="etf-fb-fot">大文字小文字を区別</label></div>'
                + '</li>'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="m" class="etf-fb-fob" id="etf-fb-m' + i + '"><label for="etf-fb-m' + i + '" class="etf-fb-fot">完全一致</label></div>'
                + '</li>'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="n" class="etf-fb-fob" id="etf-fb-n' + i + '"><label for="etf-fb-n' + i + '" class="etf-fb-fot">否定</label></div>'
                + '</li>'
              + '</ul>'
            + '</div>';
          break;
        case 'date':
          filterHTML += ''
            + '<div class="etf-fb-iw"><input type="text" class="etf-fb-i etf-fb-id etf-fb-ids"></div>'
            + '<div class="etf-fb-idb">-</div>'
            + '<div class="etf-fb-iw"><input type="text" class="etf-fb-i etf-fb-id etf-fb-ide"></div>';
          break;
        case 'list': {
          const tb = et.tb,
                tbLength = tb.length,
                tbList = [];
          for ( let row = 0; row < tbLength; row++ ) {
            if ( tbList.indexOf( tb[row][i] ) === -1 ) {
              tbList.push( tb[row][i] );
            }
          }
          tbList.sort();
          const valueLength = tbList.length;
          filterHTML += '<ul class="etf-fb-sl">';
          for ( let j = 0; j < valueLength; j++ ) {
            filterHTML += ''
            + '<li class="etf-fb-si">'
              + '<div class="etf-fb-sc">'
                + '<input id="etf-fb-scb-' + i + '-' + j + '" type="checkbox" class="etf-fb-scb" value="' + tbList[j] + '">'
                + '<label for="etf-fb-scb-' + i + '-' + j + '" class="etf-fb-scl">'
                  + '<span class="etf-fb-st">' + tbList[j] + '</span>'
                + '</label>'
              + '</div>'
            + '</li>'
          }
          filterHTML += '</ul>'
        } break;
        case 'status': {
          filterHTML += '<ul class="etf-fb-sl">';
          for ( const key in th[i].list ) {
            filterHTML += ''
            + '<li class="etf-fb-si">'
              + '<div class="etf-fb-sc">'
                + '<input id="etf-fb-scb-' + i + '-' + key + '" type="checkbox" class="etf-fb-scb" value="' + key + '">'
                + '<label for="etf-fb-scb-' + i + '-' + key + '" class="etf-fb-scl">'
                  + et.statusHTML( th[i].list[key], key, false ) + '<span class="etf-fb-st">' + th[i].list[key] + '</span>'
                + '</label>'
              + '</div>'
            + '</li>'
          }
          filterHTML += '</ul>'
          } break;
        default:
        }
        filterHTML += '</div></div>';
      }
    }
    et.$filterBlock.html( filterHTML );
    
    // データピッカー
    et.$filterBlock.find('.etf-fb-id').datePicker({});
    
  },
  // フィルタ入力欄に値をセット
  'setFilterValue': function(){
    const et = this,
          th = et.th;
    et.$filterBlock.find('.etf-fc').each(function(){
      const $filterArea = $( this ),
            arrayNumber = Number( $filterArea.attr('data-array') ),
            col = th[arrayNumber];
      if ( col !== undefined ) {
        switch( col.type ) {
          case 'list':
          case 'status': {
            let value = [];
            if ( col.filterOption !== undefined && col.filterOption.value !== undefined ) {
              value = col.filterOption.value;
            }
            $filterArea.find('.etf-fb-scb').each(function(){
              const $check = $( this );
              if ( value.indexOf( $check.attr('value')) !== -1 ) {
                $check.prop('checked', true );
              } else {
                $check.prop('checked', false );
              }
            });
            } break;
          case 'text': {
            let value = '',
                option = [];
            if ( col.filterOption !== undefined ) {
              if ( col.filterOption.value !== undefined ) {
                value = col.filterOption.value;
              }
              if ( col.filterOption.option !== undefined ) {
                option = col.filterOption.option;
              }
            }
            $filterArea.find('.etf-fb-it').val( value );
            $filterArea.find('.etf-fb-fob').each(function(){
              const $check = $( this );
              if ( option.indexOf( $check.attr('value')) !== -1 ) {
                $check.prop('checked', true );
              } else {
                $check.prop('checked', false );
              }
            });
            } break;
          case 'date': {
            let start = '', end = '';
            if ( col.filterOption !== undefined ) {
              if ( col.filterOption.start !== undefined ) {
                start = col.filterOption.start;
              }
              if ( col.filterOption.end !== undefined ) {
                end = col.filterOption.end;
              }
            }
            $filterArea.find('.etf-fb-ids').val( start );
            $filterArea.find('.etf-fb-ide').val( end );
            } break;
        }
      }
    });
  },
  // フィルタに入力されている内容を取得
  'getFilterValue': function(){
    const et = this,
          th = et.th;
    et.$filterBlock.find('.etf-fc').each(function(){
      const $filterArea = $( this ),
            arrayNumber = Number( $filterArea.attr('data-array') );
      if ( th[arrayNumber] !== undefined ) {
        switch( th[arrayNumber].type ) {
          case 'list':
          case 'status': {
            const value = [],
                  statusText = [];
            $filterArea.find('.etf-fb-scb:checked').each(function(){
              const $check = $( this );
              value.push( $check.val() );
              statusText.push( $check.next().text() );
            });
            if ( value.length >= 1 ) {
              th[arrayNumber]['filterOption'] = {
                'value': value
              };
            } else {
              delete th[arrayNumber]['filterOption'];
            }
            } break;
          case 'text': {
            const option = [];
            $filterArea.find('.etf-fb-fob:checked').each(function(){
              option.push( $(this).val() );
            });
            const value = $filterArea.find('.etf-fb-i').val();
            if ( value !== '') {
              th[arrayNumber]['filterOption'] = {
                'value': value,
                'option': option
              };
            } else {
              delete th[arrayNumber]['filterOption'];
            }
            } break;
          case 'date': {
            const start = $filterArea.find('.etf-fb-ids').val(),
                  end = $filterArea.find('.etf-fb-ide').val();
            if ( start !== '' || end !== '') {
              th[arrayNumber]['filterOption'] = {
                'start': start,
                'end': end
              };
            } else {
              delete th[arrayNumber]['filterOption'];
            }
            } break;
        }
      }
    });
  },
  // フィルタの内容をステータスバーに表示
  'setFilterStatus': function(){
    const et = this,
          th = et.th,
          thLength = th.length;
    let filterStatusHTML = '';
    for ( let i = 0; i < thLength; i++ ) {
      const filter = th[i].filterOption,
            title = th[i].title;
      if ( filter !== undefined ) {
        switch( th[i].type ) {
          case 'list':
            if ( filter.value !== undefined && filter.value.length >= 1 ) {
              filterStatusHTML += et.statusBarHTML( title, filter.value.join(','), i );
            }
            break;
          case 'status': {
            const statusLength = filter.value.length,
                  statusText = [];
            for ( let j = 0; j < statusLength; j++ ) {
              statusText.push( th[i].list[ filter.value[j] ] );
            }
            if ( filter.value !== undefined && filter.value.length >= 1 ) {
              filterStatusHTML += et.statusBarHTML( title, statusText.join(','), i );
            }
            } break;
          case 'text':
            if ( filter.value !== undefined && filter.value !== '') {
              filterStatusHTML += et.statusBarHTML( title, filter.value, i );
            }
            break;
          case 'date': {
            const start = ( filter.start !== undefined )? filter.start: '',
                  end = ( filter.end !== undefined )? filter.end: '';
            if ( start !== '' && end !== '') {
              filterStatusHTML += et.statusBarHTML( title, start + ' - ' + end, i );
            } else if ( start === '' && end !== '') {
              filterStatusHTML += et.statusBarHTML( title, '- ' + end, i );
            } else if ( start !== '' && end === '') {
              filterStatusHTML += et.statusBarHTML( title, start + ' -', i );
            }
            } break;
        }
      }
    }
    if ( filterStatusHTML !== '') {
      et.$header.find('.etf-b[data-button="filter-clear"]').prop('disabled', false );
    }
    et.$header.find('.etf-sal').html( filterStatusHTML );
  },
  'statusBarHTML': function( title, content, colNumber ){
    return '<li class="etf-sai">'
        + '<dl class="etf-sad">'
          + '<dt class="etf-sad-t">' + title + '</dt>'
          + '<dd class="etf-sad-c">' + content + '</dd>'
          + '<dd class="etf-sad-d"><span  title="削除" class="epoch-popup-m etf-sad-di" data-col="' + colNumber + '"></span></dd>'
        + '</dl>'
      + '</li>';
  },
  // フィルタ
  'setFilter': function(){
    const et = this,
          th = et.th,
          thLength = th.length;
    et.tb = et.tdCopy.filter( function( row ){
      let matchFlag = new Array( thLength );
      for ( let i = 0; i < thLength; i++ ) {
        if ( th[i]['filterOption'] !== undefined ) {
          const thfl = th[i]['filterOption'];
          switch( th[i].type ) {
            case 'list':
            case 'status':
              if ( thfl.value.length >= 1 ) {
                if ( thfl.value.indexOf( row[i] ) !== -1 ) {
                  matchFlag[i] = 'true';
                } else {
                  matchFlag[i] = 'false';
                }
              }
              break;
            case 'text': { 
              const option = thfl.option,
                    leterFlg = ( option.indexOf('l') !== -1 )? true: false,
                    notFlg = ( option.indexOf('n') !== -1 )? true: false,
                    regexFlg = ( option.indexOf('r') !== -1 )? true: false,
                    matchFlg = ( option.indexOf('m') !== -1 )? true: false,
                    trueFlag = ( notFlg === true )? 'false': 'true',
                    falseFlag  = ( notFlg === true )? 'true': 'false';
              if ( thfl.value !== '') {
                if ( regexFlg ) {
                  // 正規表現
                  const regex = ( leterFlg === true )? new RegExp( thfl.value, 'g'): new RegExp( thfl.value, 'gi');
                  ( regex.test( row[i] ) )? matchFlag[i] = trueFlag: matchFlag[i] = falseFlag;
                } else {
                  const value = ( leterFlg === true )? String( row[i] ): String( row[i] ).toLowerCase(),
                        filter = ( leterFlg === true )? String( thfl.value ): String( thfl.value ).toLowerCase();
                  if ( matchFlg ) {
                    // 完全一致
                    ( value === filter )? matchFlag[i] = trueFlag: matchFlag[i] = falseFlag;
                  } else {
                    // 部分一致
                    ( value.indexOf( filter ) !== -1 )? matchFlag[i] = trueFlag: matchFlag[i] = falseFlag;
                }
                }
              }
              } break;
            case 'date': {
              const start = ( thfl.start !== '')? thfl.start: '0000/00/00 00:00:00',
                    end = ( thfl.end !== '')? thfl.end: '9999/99/99 23:59:59';
              if ( start <= row[i] && row[i] <= end ) {
                matchFlag[i] = 'true';
              } else {
                matchFlag[i] = 'false';
              }
              } break;
          }
        }
      }
      // マッチしなかったものがなければ true
      if ( matchFlag.indexOf('false') === -1 ) {
        return true;
      } else {
        return false;
      }
    });
  },
  // フィルタクリア
  'clearFilter': function(){
    const et = this,
          th = et.th,
          thLength = th.length;
    for ( let i = 0; i < thLength; i++ ) {
      if ( th[i]['filterOption'] !== undefined ) {
        delete th[i]['filterOption'];
      }
    }
    et.tb = et.tdCopy.concat();
    et.$header.find('.etf-sal').html('');
    et.$header.find('.etf-b[data-button="filter-clear"]').prop('disabled', true );
  },
  // 更新して再表示する
  'update': function( tb ){
    const et = this;
    et.tb = tb;
    et.pagingPage = 1;
              et.sortClear();
              et.setBodyHTML();
  }
};