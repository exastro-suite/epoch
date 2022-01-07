// JavaScript Document

function epochTable() {
  const newUniqueID = function() {
    const strong = 9999,
          uniqueID = 'ta' + new Date().getTime().toString(16) + Math.floor( strong * Math.random()).toString(16);
    return uniqueID;
  }
  this.tableID = newUniqueID();
}
epochTable.prototype = {
  'setup': function( target, thArray, tbArray, option ){
      
      const et = this;

      et.fn = new epochCommon();
      et.ws = new webStorage();
      
      // Modal
      et.modal = new modalFunction();
      
      et.target = target;

      // Option set
      et.option = {};
      if ( option === undefined ) option = {};
      if ( option.filter !== undefined ) et.option.filter = option.filter;
      if ( option.paging !== undefined ) et.option.filter = option.paging;
      if ( option.bodyHead !== undefined ) et.option.bodyHead = option.bodyHead;
      if ( option.callback !== undefined ) et.option.callback = option.callback;
      if ( option.output !== undefined ) et.option.output = option.output;

      // Table main
      et.$table = $('<div/>', {
        'class': 'epoch-table-container',
        'id': et.tableID
      });

      if ( et.option.bodyHead === 'on') et.$table.addClass('et-bh');

      et.$target = $( target );
      et.th = $.extend( true, [], thArray ); // thead
      et.tb = tbArray.concat(); // tbody
      et.tbCopy = tbArray.concat(); // 初期値として使う

      // Filter
      if ( option.filter !== 'off') {
        const etHeaderHTML = ''
        + '<div class="eth">'
          + '<div class="etf-s">'
            + '<div class="etf-si">'
              + '<button class="etf-b epoch-popup-m" data-button="filter-open" title="フィルタ">'
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
        + '</div>'
        + '<div class="etf-c">'
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
        + '</div>';
        et.$table.addClass('et-filter').append( etHeaderHTML );
      }

      // Body
      const etBodyHTML = ''
      + '<div class="etb">'
        + '<table class="et">'
          + '<thead class="et-h">'
          + '</thead>'
          + '<tbody class="et-b">'
          + '</tbody>'
        + '</table>'
      + '</div>';
      et.$table.append( etBodyHTML );

      // チェックボックスがある場合はinputを追加する
      et.$checkedList = {};
      et.checkedList = {};
      const thLength = et.th.length;
      for ( let i = 0; i < thLength; i++ ) {
        if ( et.th[i].type === 'checkbox' || et.th[i].type === 'rowCheck') {
          const inputID = et.tableID + '-' + et.th[i].id;
          et.$checkedList[inputID] = $('<input>', {
            'class': 'et-cb-i', 'type': 'hidden', 'name': inputID
          });
          // 初期値があるか
          if ( option.checked && option.checked[inputID] ) {
            et.$checkedList[inputID].val(option.checked[inputID].join(','));
          }
          et.checkedList[ inputID ] = [];
          et.$table.append( et.$checkedList[inputID] );
        }
      }

      // Footer(paging)
      const pagingID = 'etp-s-r-' + et.target,
            pagingRowsPattern = [ 200, 100, 50, 25, 10 ],
            pagingRowsPatternLength = pagingRowsPattern.length;
      
      let pagingRowsHTML = '';
      for ( let i = 0; i < pagingRowsPatternLength; i++ ) {
        const n = String( pagingRowsPattern[i] );
        pagingRowsHTML += ''
        + '<li class="etp-si">'
          + '<input type="radio" name="' + pagingID + '" id="' + et.tableID + '-' + pagingID + n + '" class="etp-sr" value="' + n + '">'
          + '<label for="' + et.tableID + '-' + pagingID + n + '" class="etp-sb">' + n + '</label>'
        + '</li>';
      }
      
      if ( option.paging !== 'off') {
        const etFooterHTML = ''
        + '<div class="ett">'
          + '<div class="etp">'
            + '<div class="etp-w">'
              + '<div class="etp-ih">行数</div>'
              + '<div class="etp-ib">'
                + '<div class="etp-s">'
                  + '<div class="etp-sn"></div>'
                  + '<ul class="etp-sl">'
                    + pagingRowsHTML
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
              + '<div class="etp-ib etp-pc">'
                + '<div class="etp-pc-t">'
                  + '<div class="etp-pc-c">'
                    + '<input type="number" class="etp-pc-i">'
                    + '<div class="etp-pc-w"></div>'
                  + '</div>'
                + '</div>'
              + '</div>'
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
          + '</div>'
          + '<div class="etd"></div>'
        + '</div>';
        et.$table.append( etFooterHTML );
      }

      // Style
      const etStyleHTML = ''
      + '<style class="ets"></style>';
      et.$table.append( etStyleHTML );

      // ソート値
      et.cSortCol = null;
      et.cSortType = null;

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
      et.$currentPageNum = et.$table.find('.etp-pc-i');
      et.$currentPageWidth = et.$table.find('.etp-pc-w');

      et.$datalist = et.$table.find('.etd');

      et.$filterBlock = et.$table.find('.etf-ab');

      et.pagingTotalPage = 0;

      et.$target.html( et.$table );

      et.setHeaderHTML();
      et.setFilterHTML();

      et.setFilter();
      et.setFilterStatus();

      et.setting( option );

      // et.datalistHTML();

      // フィルタイベント
      if ( option.filter !== 'off') {
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
              et.setting({
                'page': 1,
                'sortCol': et.cSortCol,
                'sortType': et.cSortType
              });
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
              et.setting({
                'page': 1,
                'sortCol': et.cSortCol,
                'sortType': et.cSortType
              });
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
          et.setting({
            'page': 1,
            'sortCol': et.cSortCol,
            'sortType': et.cSortType
          });
          et.setBodyHTML();
        });
      }

      // ページング
      if ( option.paging !== 'off') {
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
        et.$currentPageNum.on({
          'input': function(){
            et.$currentPageWidth.text( $( this ).val() );
            et.footerSizeCheck();
          },
          'change': function(){
            et.pageChange( $( this ).val() );
          }
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
          et.footerSizeCheck();
        });
      }
      
      // チェックボックス
      et.$tbody.on({
        'change': function(){
          const $cb = $( this ),
                c = $cb.prop('checked'),
                v = $cb.val(),
                t = $cb.attr('data-target');
          if ( c ) {
            if ( et.checkedList[t].indexOf( v ) === -1 ) {
              et.checkedList[t].push( v );
            }
          } else {
            const index = et.checkedList[t].indexOf( v );
            $cb.closest('.et-r').removeClass('et-r-c');
            if ( index !== -1 ) {
              et.checkedList[t].splice( index, 1 );
            }
          }
          et.$checkedList[t].val( et.checkedList[t].join(',') ).trigger('change');

        },
        'input': function(){
          const $cb = $( this ),
                col = $cb.attr('data-col'),
                row = $cb.attr('data-row');
          et.colCheckboxCheck(col);
          if ( !$cb.is('.et-cb-rc') ) {
            et.rowCheckboxCheck(row);
          }
        }
      }, '.et-cb');
      
      // すべて選択
      const rowAllCheck = function($target){
          $target.each(function(){
            et.colCheckboxCheck($(this).attr('data-col'));
          });
      };
      const colAllCheck = function($target){
          $target.each(function(){
            et.rowCheckboxCheck($(this).attr('data-row'));
          });
      };
      
      et.$tbody.on({
        'click': function(){
          const $allBtn = $( this ),
                $row = $allBtn.closest('.et-r'),
                type = $allBtn.attr('data-type');
          if ( type === 'all-check' || type === 'some-check') {
            const $target = $row.find('.et-cb:checked').not('.et-cb-rc');
            $target.prop('checked', false ).removeClass('uncheck-target').change();
            rowAllCheck( $target );
          } else {
            const $target = $row.find('.et-cb').not('.et-cb-rc');
            $target.prop('checked', true ).removeClass('check-target').change();
            rowAllCheck( $target );
          }
          et.rowCheckboxCheck($row.attr('data-rows'));
          $allBtn.trigger('mouseenter');
        }
      }, '.et-cb-ra');
      
      et.$thead.on({
        'click': function(){
          const $allBtn = $( this ),
                col = $allBtn.attr('data-col'),
                $col = et.$tbody.find('.cn' + col ),
                type = $allBtn.attr('data-type');
          if ( type === 'all-check' || type === 'some-check') {
            const $target = $col.find('.et-cb:checked');
            $target.prop('checked', false ).removeClass('uncheck-target').change();
            colAllCheck( $target );
          } else {
            const $target = $col.find('.et-cb');
            $target.prop('checked', true ).removeClass('check-target').change();
            colAllCheck( $target );
          }
          et.colCheckboxCheck( col );
          $allBtn.trigger('mouseenter');
        }
      }, '.et-cb-ca');
      
      et.setBodyHTML();
      
      if ( option.paging !== 'off') {
        et.footerSizeCheck();
      }
      return et.$table;
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
  'colCheckboxCheck': function( col ){
    const et = this,
          $allColCheck = et.$thead.find('.cn' + col ).find('.et-cb-ca'),
          $colCheckbox = et.$tbody.find('.cn' + col ).find('.et-cb'),
          colCheckLength = $colCheckbox.length,
          colCheckedLength = $colCheckbox.filter(':checked').length;
    if ( colCheckLength === colCheckedLength ) {
      $allColCheck.attr('data-type', 'all-check');
    } else if ( colCheckedLength >= 1 ) {
      $allColCheck.attr('data-type', 'some-check');
    } else {
      $allColCheck.removeAttr('data-type');
    }
},
'rowCheckboxCheck': function( row ){
    const et = this,
          $allRowCheck = et.$tbody.find('.rn' + row ).find('.et-cb-ra'),
          $rowCheckbox = et.$tbody.find('.rn' + row ).find('.et-cb').not('.et-cb-rc'),
          rowCheckLength = $rowCheckbox.length,
          rowCheckedLength = $rowCheckbox.filter(':checked').length;
    if ( rowCheckLength === rowCheckedLength ) {
      $allRowCheck.attr('data-type', 'all-check');
    } else if ( rowCheckedLength >= 1 ) {
      $allRowCheck.attr('data-type', 'some-check');
    } else {
      $allRowCheck.removeAttr('data-type');
    }
  },
  'setCheckboxCheck': function(){
      const et = this,
            thLength = et.th.length;
      for ( let i = 0; i < thLength; i++ ) {
        if ( et.th[i].type === 'checkbox' || et.th[i].type === 'rowCheck') {
          et.colCheckboxCheck(i);
        }
        if ( et.th[i].type === 'allCheck') {
          const cp = et.pagingPage,
                pn = et.pagingNumber,
                na = et.tb.length,
                ns = 1 + pn * ( cp - 1 ),
                ne = ( na > ns + pn - 1 )? ns + pn - 1: na;
          for( let j = ns - 1; j < ne; j++ ) {
            et.rowCheckboxCheck(j);
          }
        }
      }      
  },  
  // thead and style
  'setHeaderHTML': function(){
      const et = this,
            op = et.option,
            th = et.th,
            thLength = th.length;
      if ( op.bodyHead !== 'on') {
      let thHTML = '',
          tStyle = '';
      thHTML += '<tr class="et-r">';
      for( let i = 0; i < thLength; i++ ) {
          // HTML
          const exclusionType = ['hoverMenu', 'class', 'attr']; // 表示しないタイプ
          if ( exclusionType.indexOf( th[i].type ) === -1 ) {
              thHTML += ''
              + '<th class="et-c et-c-' + th[i].type + ' cn' + i + '">'
                + '<div class="et-ci';
              if ( th[i].type === 'checkbox') {
                thHTML += '"><div class="et-cb-t">' + th[i].title + '</div><div class="et-cbw"><div class="et-cb-ca" data-col="' + i + '"><span></span></div></div></div>';
              } else if ( th[i].type === 'rowCheck') {
                thHTML += '"><div class="et-cbw"><div class="et-cb-ca" data-col="' + i + '"><span></span></div></div></div>';
              } else {
                if ( th[i].sort === 'on') thHTML += ' et-cs'; // Srot
                thHTML += '" data-column-index="' + i + '"><div class="et-ht">' + th[i].title + '</div></div>';
                if ( th[i].resize === 'on') thHTML += '<div class="et-cr"></div>'; // Resize
              }
              thHTML += '</th>';
          }
          // Style
          const width = th[i].width,
                align = th[i].align;
          tStyle += '#' + et.tableID + ' .et-c.cn' + i + '{';
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
              tStyle += '#' + et.tableID + ' .et-b .et-c.cn' + i + ' .et-ci{'
              + 'text-align:' + align + ';'
              + 'justify-content:' + align + ';'
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

          et.sort( index, sort );
          et.setBodyHTML();
      });
      }
  },
  // tbody
  'setBodyHTML': function(){
      const et = this,
            op = et.option,
            th = et.th,
            tb = et.tb,
            na = tb.length; // 件数
      
      if ( na >= 1 ) {
          et.$table.removeClass('et-nodata');
          
          const cp = et.pagingPage,
                pn = et.pagingNumber,
                ns = 1 + pn * ( cp - 1 ),
                ne = ( na > ns + pn - 1 )? ns + pn - 1: na;

          let tbHTML = '';

          for( let i = ns - 1; i < ne; i++ ) {
              let trHTML = '',
                  idName = '',
                  rowClassName = ['et-r'],
                  attr = ['data-rows="' + i + '"'];

              const cLength = tb[i].length;
              for( let j = 0; j < cLength; j++ ) {
                  const thd = th[j],
                        tbd = tb[i][j];

                  // Type = [ id, class, attr ]
                  if ( ['id','class','attr'].indexOf( thd.type ) !== -1 ) {
                      if ( tbd !== null ) {
                          switch( thd.type ){
                              case 'id':
                                  idName = tbd;
                                  break;
                              case 'class':
                                  rowClassName.push( tbd );
                                  break;
                              case 'attr':
                                  attr.push('data-' + thd.attr + '="' + tbd + '"' );
                                  break;
                              default:
                          }
                      }
                  } else {
                      let cellClassName = 'et-c cn' + j + ' et-c-' + thd.type;
                      if ( thd.className !== undefined ) cellClassName += ' ' + thd.className;

                      trHTML += '<td class="' + cellClassName + '">';

                      if ( op.bodyHead === 'on' && ['status','button'].indexOf( thd.type ) === -1 ) {
                        trHTML += '<div class="et-ct">' + thd.title + '</div>';
                      }

                      trHTML += '<div class="et-ci">';

                      if ( tbd !== null ) {
                          switch( thd.type ){
                              case 'text':
                              case 'list':
                              case 'date':
                              case 'number':
                                  trHTML += et.fn.textEntities( tbd );
                                  break;
                              case 'url':
                                  trHTML += '<a href="' + encodeURI(tbd) + '">' + et.fn.textEntities( tbd ) + '</a>';
                                  break;
                              case 'html':
                                  trHTML += tbd;
                                  break;
                              case 'hoverMenu':
                                  trHTML += et.hoverMenuListHTML( thd.menu, tbd );
                                  break;
                              case 'status':
                                  trHTML += et.statusHTML( thd.list[tbd], tbd );
                                  break;
                              case 'button':
                                  trHTML += et.buttonHTML( thd.title, thd.buttonClass );
                                  break;
                              case 'checkbox':
                              case 'rowCheck': {
                                  // thd.id有りだと、動作しないためコメントアウト
                                  // const inputID = et.tableID + '-' + thd.id,
                                  //       checked = ( et.checkedList[inputID].indexOf( String( tbd )) !== -1  )? true: false;
                                  const inputID = et.tableID,
                                        checked = ( et.checkedList[inputID] !== -1  )? true: false;
                                  trHTML += et.checkboxHTML( thd.id, tbd, checked, i, j, thd.type );
                                  } break;
                              case 'div':
                                  trHTML += '<div class="' + thd.divClass + '"><span></span></div>'
                                  break;
                              case 'itemList': {
                                  trHTML += et.itemListHTML( tbd, thd.item );
                                  } break;
                              case 'allCheck':
                                  trHTML += '<div class="et-cbw"><div class="et-cb-ra"><span></span></div></div></div>';
                                  break;                                  
                              default:
                          }
                      }
                      trHTML += ''
                        + '</div>'
                      + '</td>';
                  }
              }
              tbHTML += '<tr id="' + idName + '" class="' + rowClassName.join(' ') + ' rn' + i + '" ' + attr.join(' ') + '>' + trHTML + '</tr>';
          }
          et.$tbody.html( tbHTML );
      } else {
          const noDataHTML = ''
          + '<div class="et-nd"><div class="et-ndi">データがありません。</div></div>';
          et.$table.addClass('et-nodata');
          et.$tbody.html( noDataHTML );
          et.pagingPage = 1;
      }
      
      et.pagingStatus();
      et.setCheckboxCheck();
      if ( et.option.callback !== undefined ) et.option.callback();
  },
  /* ------------------------------ *\
     Paging status
  \* ------------------------------ */
  'pagingStatus': function(){
    const et = this,
          targetPage = et.pagingPage, // 表示ページ
          pageNumber = et.pagingNumber, // 1頁表示件数
          rowLength = et.tb.length, // 件数
          rowDigit = String( rowLength ).length, // 件数桁数
          allPageNumber = Math.ceil( rowLength / pageNumber ), // ページ数
          currentPage = ( rowLength === 0 )? 0: targetPage,
          pageStart = ( rowLength === 0 )? 0: 1 + pageNumber * ( targetPage - 1 ),
          pageEnd = ( rowLength > pageStart + pageNumber - 1 )? pageStart + pageNumber - 1: rowLength;
    
    et.pagingTotalPage = allPageNumber;
    
    et.$allNum.text( rowLength.toLocaleString() );
    et.$startNum.html( et.zeroPadding( pageStart, rowDigit ) );
    et.$endNum.html( et.zeroPadding( pageEnd, rowDigit ) );

    et.$currentPageNum.val( currentPage ).trigger('input');
    et.$allPageNum.text( allPageNumber.toLocaleString() );
    
    et.pagingCheck();
  },
  /* ------------------------------ *\
     Filter input datalist
  \* ------------------------------ */
  'datalistHTML': function(){
    const et = this,
          th = et.th,
          tb = et.tb,
          tbL = tb.length,
          datalist = {};
    for ( let i = 0; i < tbL; i++ ) {
      const col = tb[i].length;
      for ( let j = 0; j < col; j++ ) {
        if ( th[j].type === 'text' && th[j].filter === 'on') {
          if ( datalist[j] === undefined ) datalist[j] = [];
          if ( datalist[j].indexOf( tb[i][j] ) === -1 ) {
            datalist[j].push( tb[i][j] );
          }
        }
      }
    }
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
     Button HTML
  \* ------------------------------ */  
  'buttonHTML': function( text, className, popup ) {
    if ( popup === undefined ) popup = true;
    const popupClass = ( popup === true )? ' epoch-popup-m': '';
    return ''
      + '<button class="et-bu ' + className + popupClass + '" title="' + text + '">'
        + '<span class="et-bui"></span>'
      + '</button>';
  },
  /* ------------------------------ *\
     Checkbox HTML
  \* ------------------------------ */  
  'checkboxHTML': function( thid, id, checked, row, col, type ) {
    const c = ( checked )? ' checked': '',
          et = this,
          name = et.tableID + '-' + thid + '-et-cb',
          forID = name + '-' + row + '-' + col + '-' + id,
          classNmae = ( type === 'rowCheck')? ' et-cb-rc': '';
    const checkboxHTML = '<div class="et-cbw">'
        + '<input data-col="' + col + '" data-row="' + row + '" data-type="' + thid + '" data-target="' + et.tableID + '-' + thid + '" class="et-cb' + classNmae + '" name="' + name + '" id="' + forID + '" type="checkbox" value="' + id + '"' + c + '>'
        + '<label class="et-cbl" for="' + forID + '"></label';
    + '</div>';
    return checkboxHTML;
  },
  /* ------------------------------ *\
     Item list HTML
  \* ------------------------------ */  
  'itemListHTML': function( value, list ) {
    const a = value.split(','),
          l = a.length;
    let h = '<ul class="et-il-l">'
    for ( let i = 0; i < l; i++ ) {
      const d = list.filter(function(v){
        if ( v[0] === a[i] ) return v;
      })[0];
      h += '<li class="et-il-i">' + d[1] + '</li>';
    }
    h += '</ul>';
    return h;
  },
  /* ------------------------------ *\  
     ソート
  \* ------------------------------ */
  'sort': function( index, order ){
      const et = this,
            tb = et.tb;
      
      et.cSortCol = index;
      et.cSortType = order;
      
      if ( et.$thead !== undefined ) {
        et.$thead.find('.et-ci').removeAttr('data-sort');
        et.$thead.find('.et-ci[data-column-index="' + index + '"]').attr('data-sort', order );
    }
          
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
    const et = this;
    if ( page <= 1 ) page = 1;    
    if ( page > et.pagingTotalPage ) page = et.pagingTotalPage;
    et.pagingPage = Number ( page );
    et.setBodyHTML();
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
    let filterHTML = '',
        tabID = '';
    // タブの中の場合inputのnameにTab IDを追加する
    if ( et.$table.closest('.modal-tab-body-block').length ) {
        tabID = '-' + et.$table.closest('.modal-tab-body-block').attr('id') + '-';
    } 
    for ( let i = 0; i < thength; i++ ) {
      if ( th[i].filter === 'on') {
        const nameID = tabID + i
        filterHTML += ''
        + '<div class="etf-fc" type="' + th[i].type+ '" data-array="' + i + '">'
          + '<div class="etf-fh">' + th[i].title + '</div>'
          + '<div class="etf-fb">';
        switch( th[i].type ) {
        case 'url':
        case 'number':
        case 'text':
          filterHTML += ''
            + '<div class="etf-fb-iwf"><input type="text" class="etf-fb-i etf-fb-it" list="list' + i + '"></div>'
            + '<div class="etf-fb-iwf">'
              + '<ul class="etf-fb-fol">'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="r" class="etf-fb-fob" id="' + et.tableID + '-etf-fb-r' + nameID + '"><label for="' + et.tableID + '-etf-fb-r' + nameID + '" class="etf-fb-fot">正規表現</label></div>'
                + '</li>'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="l" class="etf-fb-fob" id="' + et.tableID + '-etf-fb-l' + nameID + '"><label for="' + et.tableID + '-etf-fb-l' + nameID + '" class="etf-fb-fot">大文字小文字を区別</label></div>'
                + '</li>'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="m" class="etf-fb-fob" id="' + et.tableID + '-etf-fb-m' + nameID + '"><label for="' + et.tableID + '-etf-fb-m' + nameID + '" class="etf-fb-fot">完全一致</label></div>'
                + '</li>'
                + '<li class="etf-fb-foi">'
                  + '<div class="etf-fb-foc"><input type="checkbox" value="n" class="etf-fb-fob" id="' + et.tableID + '-etf-fb-n' + nameID + '"><label for="' + et.tableID + '-etf-fb-n' + nameID + '" class="etf-fb-fot">否定</label></div>'
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
                + '<input name="etf-fb-scb-' + nameID + '" id="' + et.tableID + '-etf-fb-scb-' + nameID + '-' + j + '" type="checkbox" class="etf-fb-scb" value="' + tbList[j] + '">'
                + '<label for="' + et.tableID + '-etf-fb-scb-' + nameID + '-' + j + '" class="etf-fb-scl">'
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
                + '<input name="etf-fb-scb-' + nameID + '" id="' + et.tableID + '-etf-fb-scb-' + nameID + '-' + key + '" type="checkbox" class="etf-fb-scb" value="' + key + '">'
                + '<label for="' + et.tableID + '-etf-fb-scb-' + nameID + '-' + key + '" class="etf-fb-scl">'
                  + et.statusHTML( th[i].list[key], key, false ) + '<span class="etf-fb-st">' + th[i].list[key] + '</span>'
                + '</label>'
              + '</div>'
            + '</li>'
          }
          filterHTML += '</ul>'
          } break;
        case 'checkbox': {
          filterHTML += '<ul class="etf-fb-cl">';
          th[i].list = {
            'all': '全て',
            'checked': '選択済み',
            'unchecked': '未選択'
          }
          for ( const key in th[i].list ) {
            filterHTML += ''
            + '<li class="etf-fb-ci">'
              + '<div class="etf-fb-cc">'
                + '<input name="etf-fb-ccb-' + nameID + '" id="' + et.tableID + '-etf-fb-ccb-' + nameID + '-' + key + '" type="radio" class="etf-fb-ccb" value="' + key + '">'
                + '<label for="' + et.tableID + '-etf-fb-ccb-' + nameID + '-' + key + '" class="etf-fb-ccl">'
                  + th[i].list [key]
                + '</label>'
              + '</div>'
            + '</li>'
          }
          filterHTML += '</ul>';
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
          case 'url':
          case 'number':
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
          case 'url':
          case 'number':
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
          case 'url':
          case 'number':
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
    const et = this;
    return '<li class="etf-sai">'
        + '<dl class="etf-sad">'
          + '<dt class="etf-sad-t">' + title + '</dt>'
          + '<dd class="etf-sad-c">' + et.fn.textEntities( content ) + '</dd>'
          + '<dd class="etf-sad-d"><span  title="削除" class="epoch-popup-m etf-sad-di" data-col="' + colNumber + '"></span></dd>'
        + '</dl>'
      + '</li>';
  },
  // フィルタ
  'setFilter': function(){
    const et = this,
          th = et.th,
          thLength = th.length;
    et.tb = et.tbCopy.filter( function( row ){
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
            case 'url': 
            case 'number':
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
    et.tb = et.tbCopy.concat();
    et.$header.find('.etf-sal').html('');
    et.$header.find('.etf-b[data-button="filter-clear"]').prop('disabled', true );
  },
  'setting': function( option ) {
    const et = this;
    if ( option === undefined ) option = {};
    if ( option !== undefined ) {
      // 表示するページ
      if ( option.page === undefined ) {
        et.pagingPage = 1;
      } else {
        et.pagingPage = option.page;
      }
      // 1頁に表示する行数
      if ( option.pagingNumber === undefined ) {
        if ( et.pagingNumber === undefined ) {
          et.pagingNumber = 50;
        }
      } else {
        et.pagingNumber = option.pagingNumber;
      }
    }
    // チェックボックス
    if ( option.checked !== undefined ) {
      et.checkedList = option.checked;
    }
    // ソート
    if ( option.sortCol !== undefined && option.sortType !== undefined ) {
      et.sort( option.sortCol, option.sortType );
    } else if ( et.cSortCol !== null && et.cSortType !== null ) {
      et.sort( et.cSortCol, et.cSortType );
    }
  },
  /* ------------------------------ *\
     値を更新する
  \* ------------------------------ */  
  'update': function( tb, option ){
    if ( option === undefined ) option = {};
    const et = this;
    
    et.tb = tb.concat();
    et.tbCopy = tb.concat();
    
    et.setFilter();
    et.setting( option );
    
    et.setBodyHTML();
  },
  /* ------------------------------ *\
     フッターバーのサイズを調整する
  \* ------------------------------ */  
  'footerSizeCheck': function(){
    const et = this,
          $footerBar = et.$footer.find('.etp'),
          sWidth = $footerBar.get(0).scrollWidth,
          cWidth = $footerBar.get(0).offsetWidth;
    if ( cWidth < sWidth ) {
      $footerBar.css('transform', 'scale(' + ( cWidth / sWidth ) + ')')
    } else {
      $footerBar.removeAttr('style');
    }
  },
  /* ------------------------------ *\
     Loading start
  \* ------------------------------ */
  'loadingStart': function(){
    this.$table.addClass('et-wait');
    this.$table.append('<div class="et-wt"><div class="log-now-loading-icon"><span></span></div></div>');
  },
  /* ------------------------------ *\
     Loading end
  \* ------------------------------ */
  'loadingEnd': function(){
    this.$table.removeClass('et-wait');
    this.$table.find('.et-wt').remove();
  },
  /* ------------------------------ *\
     Output Excel(xlsx)
  \* ------------------------------ */
  'excel': function(){
    const et = this;
    
    // header
    const header = [[]],
          thLength = et.th.length;
    for ( let i = 0; i < thLength; i++ ) {
        const title = ( et.th[i].title !== undefined )? et.th[i].title: '';
        header[0].push(title);
    }
    
    // WebWorker
    const js = './common/js/ww_tablejs_sheetjs.js',
          ww = new Worker( js );
    
    ww.onmessage = function( e ){
        const result = e.data;
        if ( result.status === 200 ) {
            if ( result.data.constructor.name === 'Blob') {
                const url = window.URL.createObjectURL( result.data ),
                      a = document.createElement('a');
                document.body.appendChild( a );
                a.href = url;
                a.download = "out.xlsx";
                a.click();
                window.URL.revokeObjectURL( url );
                document.body.removeChild( a );
            } else {
                window.console.error('"XlSX Blob" convert error.');
            }
        } else {
            window.console.error( result.message );
        }
    }
    ww.postMessage( header.concat( et.tb ));
  }
};