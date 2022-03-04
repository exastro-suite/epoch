/*
#   Copyright 2022 NEC Corporation
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
//   結果表示共通
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function wsResultCommon(){
  const ws = this;
  ws.modal = {};
  ws.modal.st = {};
  ws.modal.de = {
      'id': 'result-detail-modal',
      'class': '',
      'title': '',
      'footer': {
          'cancel': {'text': '閉じる', 'type': 'negative'}
      },
      'block': {
          'block1': {
              'item': {
                  'item1': {'type': 'loading', 'id': 'result-detail'},
              }
          }
      }
  };
  ws.modal.fn = new modalFunction( ws.modal, {});
  ws.modal.sub = new modalFunction( ws.modal, {});
  ws.fn = new epochCommon();
  ws.update = false;
  ws.pollingTime = 0;
}
wsResultCommon.prototype = {
    'open': function( width ){
        const ws = this;
        if ( ws.modal.st.block.tabBlock !== undefined ) {
            ws.modal.block = ws.modal.st.block.tabBlock.tab.tabs;
        } else {
            ws.modal.block = ws.modal.st.block;
        }
        ws.modal.fn.open('st', {
            'callback': function(){
                ws.setTable();
            },
            'cancel': function(){
                clearTimeout( ws.timerID );
                ws.modal.fn.close();
            }
        }, width );
    },
    'detail': function( key, width ) {
        const ws = this;
        ws.modal.sub.open('de', {
            'callback': function(){
                ws.setDetaile( key );
            },
            'cancel': function(){
              clearTimeout(ws.detailTimerID);
               ws.modal.sub.close();
            }
        }, width, 'sub');
    },
    'setTable': function() {
        const ws = this;
        for ( const key in ws.modal.block ) {
            const d = ws.data[key];
            d.fn = new epochTable();
            d.fn.setup( d.target, d.header, [], d.option );
            d.fn.loadingStart();
        }
        ws.getData( ws.updateTable );
    },
    'updateTable': function( data ) {
        const ws = this;
        if ( ws.modal.fn.$modal ) {
            for ( const key in ws.modal.block ) {
                const d = ws.data[key];
                if ( d.fn.$table ) {
                    d.result = data[key].rows;
                    d.fn.update( d.change( d.result ));
                    d.fn.loadingEnd();
                }
            }
            if ( ws.update ) {
                ws.timerID = setTimeout( function(){
                    ws.getData( ws.updateTable );
                }, ws.pollingTime );
            }
        }
    },
    'setDetaile': function( key ) {
        const ws = this;
        ws.modal.sub.$modal.find('#result-detail').html(
            ws.data[key].detail.$detail
        );
        
        // トレースID
        ws.modal.sub.$modal.find('.status-trace-id-button').on('click', function(){
            clearTimeout(ws.detailTimerID);
            const $b = $( this ),
                  id = $b.attr('data-traceid');
            ws.data[key].detail.traceid = id;
            ws.updateDetaile( key );
        });
        ws.updateDetaile( key );
    },
    'updateDetaile': function( key ) {
        const ws = this;
        if ( ws.modal.sub.$modal ) {
            const r = ws.result[key].rows,
                  id = ( ws.data[key].detail.targetID )? ws.data[key].detail.targetID: 'trace_id';

            // トレースIDでフィルタ
            let num = -1;
            const data = r.filter(function(v,i){
              if ( String(v[id]) === String(ws.data[key].detail.traceid) ) {
                num = i;
                return true;
              }
            })[0];
            
            if ( num !== -1 ) {
                // トレースID移動ボタン有効・無効
                const prev = ( r[num-1] )? r[num-1][id]: undefined,
                      next = ( r[num+1] )? r[num+1][id]: undefined,
                      first =( prev )? r[0][id]: undefined,
                      last = ( next )? r[r.length-1][id]: undefined;
                ws.traceIdSelecterCheck( first, prev, next, last ); 

                ws.data[key].detail.update( data, key );

                if ( ws.update ) {
                    ws.detailTimerID = setTimeout( function(){
                        ws.updateDetaile( key );
                    }, ws.pollingTime );
                }
            }
        }
    },
    'getData': function( callback ) {
        const ws = this;
        const loadData = function( url, key ){ // keyはダミーデータ用
            return new window.Promise( function( resolve, reject ) {
                if(url.match(/^https/)) {
                    $.ajax({ type:"GET", url: url })
                    .done((data) => {
                        resolve({ "data" : data });
                    })
                    .fail(() => {
                        reject();
                    })
                } else {
                    // TODO:Sprint79 DELETE
                    setTimeout( function(){
                    // 仮結果
                    const result = {
                        'status': 200,
                        'data': ws.dummy[key] // ダミーデータを入れる
                    }              

                    if ( result.status === 200 ) {
                        resolve( result );
                    } else {
                        reject('Failed to read the task list.');
                    }
                    }, 500 );
                }
            });
        }
    
        const dataList = [];
        for ( const key in ws.modal.block ) {
            dataList.push( loadData( ws.data[key].url, key ));
        }
            
        window.Promise.all( dataList )
            // 全てのリストの読み込みが完了したら
            .then(function( result ){
                  let count = 0;
                  ws.result = {};
                  for ( const key in ws.modal.block ) {
                    ws.result[key] = result[count++].data;
                  }
                  if ( callback ) callback.call( ws, ws.result );
            })
            // 読み込み失敗
            .catch(function( error ){
                alert("読み込みに失敗しました");
                window.console.error( error );
            });
    },
    'item': function( className, title, text, url ) {
        text = ( url !== '')? `<a href="${encodeURI(url)}" target="_blank">${text}</a>`: text;
        return `<dl class="item-block item-horizontal">`
        + `<dt class="item-header">${title}</dt>`
        + `<dd class="item-area ${className}">${text}</dd></dl>`;
    },
    'traceIdSelecter': function( numberTitle ){
        if ( !numberTitle ) numberTitle = 'TRACE ID';
        return ``
        + `<div class="status-trace-id-block item-block">`
          + `<div class="status-trace-id-item"><button class="status-trace-id-button icon icon-First" data-button="first"></button></div>`
          + `<div class="status-trace-id-item"><button class="status-trace-id-button icon icon-Prev" data-button="prev"></button></div>`
          + `<div class="status-trace-id-item status-trace-id-number" data-title="${numberTitle}"></div>`
          + `<div class="status-trace-id-item"><button class="status-trace-id-button icon icon-Next" data-button="next"></button></div>`
          + `<div class="status-trace-id-item"><button class="status-trace-id-button icon icon-Last" data-button="last"></button></div>`
        + `</div>`;
    },
    'traceIdSelecterCheck': function( first, prev, next, last ){
      const ws = this;
      const buttonList = {
        'first': first,
        'prev': prev,
        'next': next,
        'last': last        
      };
      for ( const type in buttonList ) {
          const d = ( buttonList[type] )? false: true;
          ws.modal.sub.$modal.find(`.status-trace-id-button[data-button="${type}"]`).attr('data-traceid', buttonList[type] ).prop('disabled', d );
      }
    }
};

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   アプリケーションコードリポジトリ結果確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function wsAppCodeRepoCheck( gitService ) {
  const ws = this;
  ws.cmn = new wsResultCommon();
  
  // モーダル構造
  ws.cmn.modal.st = {
      'id': 'application-code-repository-check',
      'footer': {
          'cancel': {'text': '閉じる', 'type': 'negative'}
      },
      'block': {
      }
  };
  const commitBlock = {
      'item': {
          'item1': {
            'type': 'loading',
            'id': 'application-code-repository'
          }
      }
  };
  
  // 表示データ
  ws.cmn.data = {
      'commit': {
          'url': workspace_api_conf.api.ci_pipeline.git.commits.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id')),
          'header': [
              {'className': 'repository rs', 'title': 'リポジトリ', 'type': 'text', 'sort': 'on', 'filter': 'on'},
              {'className': 'branch rs', 'title': 'ブランチ', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
              {'className': 'message lb rs', 'title': 'メッセージ', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
              {'className': 'changer lb rs', 'title': '更新者', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
              {'className': 'update rs', 'title': '更新日時', 'type': 'date', 'sort': 'on', 'filter': 'on'},
              {'className': 'commit-id lb rs', 'title': 'Commit ID', 'align': 'center', 'type': 'link', 'sort': 'on', 'filter': 'on'}
          ],
          'option': {
            'className': 'table-grid commit-status application-code', 'download': 'on'
          },
          'change': function( data ) {
              const body = [],
                    length = data.length;
              for ( let i = 0; i < length; i++ ) {
                const d = data[i],
                      cid = d.commit_id.slice( 0, 6 ),
                      cDate = ws.cmn.fn.formatDate( d.date, 'yyyy/MM/dd HH:mm:ss');
                body.push([d.repository, d.branch, d.message, d.name, cDate, [ d.html_url, cid ] ]);
              }
              return body;
          }
      }
  };
  
  // GitHub Webhook
  if ( gitService['git-service-select'] === 'github') {
      commitBlock.title = 'Commit一覧';
      ws.cmn.data.commit.target = '#commit-application-code-repository';
      ws.cmn.modal.st.title = 'アプリケーションコードリポジトリ';
      ws.cmn.modal.st.class = 'layout-tab-fixed';
      ws.cmn.modal.st.block.tabBlock =   {
          'tab': {
              'id': 'application-code-repository-check-tab',
              'type': 'common',
              'tabs': {
                  'commit': commitBlock,
                  'webhook': {
                      'title': 'Webhook一覧',
                      'item': {
                          'item1': {
                            'type': 'loading',
                            'id': 'application-code-repository'
                          }
                      }
                  }
              }
          }
      };
  
      // Webhook詳細モーダル
      ws.cmn.modal.de = {
          'id': 'application-code-repository-webhook-detail',
          'title': 'Webhook レスポンス結果',
          'footer': {
              'cancel': {'text': '閉じる', 'type': 'negative'}
          },
          'block': {
              'detail': {
                  'item': {
                      'loading': {
                        'type': 'loading',
                        'id': 'application-code-repository-webhook-detail'
                      }
                  }
              }
          }
      }
      // Webhookテーブルデータ
      ws.cmn.data.webhook = {
          'url': workspace_api_conf.api.ci_pipeline.git.hooks.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id')),
          'target': '#webhook-application-code-repository',
          'header': [
              {'className': 'status-icon', 'title': '結果', 'type': 'status', 'align': 'center', 'list': {'Succeeded': '正常', 'Failed': '異常'}, 'sort': 'on', 'filter': 'on'},
              {'className': 'repository lb rs', 'title': 'リポジトリ', 'type': 'text', 'sort': 'on', 'filter': 'on'},
              {'className': 'branch lb rs', 'title': 'ブランチ', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
              {'className': 'payload lb rs','title': 'Payload URL', 'type': 'link', 'sort': 'on', 'filter': 'on'},        
              {'className': 'trigger lb rs','title': 'トリガー', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
              {'className': 'status lb rs','title': 'ステータス', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
              {'className': 'update lb rs','title': '更新日時', 'type': 'date', 'sort': 'on', 'filter': 'on'},
              {'className': 'result lb','title': '詳細', 'type': 'button', 'buttonClass': 'result-button table-button icon icon-Detail'},
              {'type': 'class'}
          ],
          'option': {'className': 'table-grid commit-status webhook','dowmload':'on'},
          'change': function( data ) {
              const body = [],
                    length = data.length;
              for ( let i = 0; i < length; i++ ) {
                  const d = data[i],
                        s = (  d.status_code === 202 )? 'Succeeded': 'Failed';
                  body.push([
                      s,
                      d.repository,
                      d.branch,
                      [d.url,d.url],
                      d.event,
                      d.status,
                      ws.cmn.fn.formatDate( d.date, 'yyyy/MM/dd HH:mm:ss'),
                      i,
                      s
                  ]);
              }
              return body;
          }
      };
  } else {
      ws.cmn.data.commit.target = '#application-code-repository';
      ws.cmn.modal.st.title = 'アプリケーションコードリポジトリ Commit一覧';
      ws.cmn.modal.st.class = 'layout-tab-fixed layout-padding-0';
      ws.cmn.modal.st.block.commit = commitBlock;
  }

// TODO:Sprint79 DELETE
//   // ダミーデータ --------------------------------------------------
//   ws.cmn.dummy = {
//       'commit': {
//         "rows": [
//           {
//             "repository": "epoch / sample-app", // ???
//             "branch": "master",
//             "commit_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
//             "name": "更新者",
//             "date": "2021-11-29T08:07:10Z",
//             "message": "メッセージメッセージメッセージメッセージメッセージ",
//             "html_url": "https://github.com/",
//           },
//           {
//             "repository": "epoch / sample-app-2", // ???
//             "branch": "master",
//             "commit_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
//             "name": "更新者",
//             "date": "2021-11-29T08:07:10Z",
//             "message": "メッセージメッセージメッセージメッセージメッセージ",
//             "html_url": "https://github.com/",
//           }
//         ]
//       },
//       'webhook': {
//         "rows": [
//           {
//             "repository": "epoch / sample-app", // ???
//             "branch": "master",
//             "url": "https://xxxxx/api/listener/2", //【Payload URL】
//             "date": "2021-11-30T02:09:25Z", // 【実行日時】
//             "status": "Succeeded", // 【ステータス】
//             "status_code": 202, // 【正常／異常コード】
//             "event": "push", // 【トリガー】
//           },
//           {
//             "repository": "epoch / sample-app-2", // ???
//             "branch": "master",
//             "url": "https://xxxxx/api/listener/2", // 【Payload URL】
//             "date": "2021-11-30T02:09:25Z", // 【実行日時】
//             "status": "failed to connect to host",  // 【ステータス】
//             "status_code": 502, // 【正常／異常コード】
//             "event": "push", // 【トリガー】
//           }
//         ]
//       }
//     }
//     // --------------------------------------------------
  
  ws.cmn.open( 960 );
  
  ws.cmn.modal.fn.$modal.on('click', '.result-button', function(){
    const n = Number( $( this ).attr('data-button') );
    ws.cmn.modal.sub.open('de', {
      'callback': function(){
        ws.cmn.modal.sub.$modal.find('#application-code-repository-webhook-detail').html(
            '<div class="item-block"><pre class="item-pre">'
            + JSON.stringify( ws.cmn.result.webhook.rows[n] , null, 4 )
            + '</pre></div>'
        );
      }
    }, '640');
  });
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   TEKTON結果確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function wsTektonCheck() {
  const ws = this;
  ws.cmn = new wsResultCommon();
  
  // モーダル構造
  ws.cmn.modal.st = {
    'id': 'tekton-check',
    'class': 'layout-tab-fixed',
    'title': 'TEKTONタスク実行状況',
    'footer': {
        'cancel': {'text': '閉じる', 'type': 'negative'}
    },
    'block': {
      'tabBlock': {
        'tab': {
            'id': 'task',
            'type': 'common',
            'tabs': {
              'new': {
                'title': '最新のタスク実行状況',
                'item': {
                  'item01': {'type': 'loading', 'id': 'task'}
                }
              },
              'all': {
                'title': '全てのタスク実行状況',
                'item': {
                  'item01': {'type': 'loading', 'id': 'task'}
                }
              }
            }
        }
      }
    }
  };
  
  const commonDataHeader = [
          {'className': 'status', 'title': '状態', 'type': 'status', 'sort': 'on', 'filter': 'on', 'align': 'center', 'list': {
            'Succeeded': '完了',
            'Failed': 'エラー',
            'Running': '実行中',
            'Pending': '保留'
          }},
          {'className': 'repository lb rs', 'title': 'アプリケーションコードリポジトリ', 'type': 'link', 'sort': 'on', 'filter': 'on'},
          {'className': 'image lb rs', 'title': 'イメージ出力先（タグ含む）', 'type': 'text', 'sort': 'on', 'filter': 'on'},
          {'className': 'date lb rs', 'title': '開始日時', 'type': 'date', 'sort': 'on', 'filter': 'on'},
          {'className': 'branch lb rs', 'title': 'ブランチ', 'type': 'text', 'sort': 'on', 'filter': 'on'},
          {'className': 'task lb','title': '詳細', 'type': 'button', 'buttonClass': 'execution-status-button table-button icon icon-Detail'},
          {'type': 'class'}
      ];
  const commonDataOption = {
        'className': 'table-grid tekton-task', 'download': 'on'
      };
  const commonDataChange = function( data ) {
          const body = [],
                length = data.length;
          for ( let i = 0; i < length; i++ ) {
            const d = data[i];
            body.push([
                d.status,
                [ d.repository_url, d.repository_url ],
                d.container_image,
                d.start_time,
                d.build_branch,
                d.task_id,
                d.status,
            ]);
          }
          return body;
      };
  
  // 表示データ
  ws.cmn.data = {
      'new': {'header': commonDataHeader, 'option': commonDataOption, 'change': commonDataChange, 'detail': {} },
      'all': {'header': commonDataHeader, 'option': commonDataOption, 'change': commonDataChange, 'detail': {} }
  };

  ws.cmn.data.new.url = workspace_api_conf.api.ciResult.pipelinerun.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id')) + "?latest=True";
  ws.cmn.data.new.target = '#new-task';
  ws.cmn.data.all.url = workspace_api_conf.api.ciResult.pipelinerun.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id'));
  ws.cmn.data.all.target = '#all-task';

// TODO:Sprint79 DELETE
//   // ダミーデータ --------------------------------------------------
//   function dummyTaskListData( number ) {
//     const rows = [];

//     const resultData = ['Succeeded','Failed','Running','Pending'],
//           years = ['2021','2022','2023','2024','2025'];

//     for ( let i = 1; i <= number; i++ ) {

//         const result1 = resultData[ Math.floor( Math.random() * resultData.length ) ],
//               result2 = resultData[ Math.floor( Math.random() * resultData.length ) ],
//               result3 = resultData[ Math.floor( Math.random() * resultData.length ) ],
//               result4 = resultData[ Math.floor( Math.random() * resultData.length ) ],
//               year = years[ Math.floor( Math.random() * years.length ) ];

//         const d = new Date();
//         d.setSeconds(d.getSeconds() - i);
//         d.setMinutes(d.getMinutes() - i);
//         d.setHours(d.getHours() - i);

//         const date = ws.cmn.fn.formatDate( d, 'yyyy/MM/dd HH:mm:ss'),
//               taskrun_name_d = number - i + 1,
//               container_image = ws.cmn.fn.formatDate( d, 'yyyyMMdd-HHmmss');
//         rows[i-1] = {
//             "task_id": number - i + 1,
//             "pipeline_id": number - i + 1,
//             "pipelinerun_name": "pipeline-run-dummy-8nftm",
//             "repository_url": "https://github.com/",
//             "build_branch": "master",
//             "start_time": date,
//             "finish_time": date,
//             "status": result1,
//             "container_image": "xxx/xxx:master." + container_image ,
//             "tasks": [
//                 {
//                     "name": "task-start",
//                     "taskrun_name": "pipeline-run-dummy-xxxxx-task-start-xxxxx" + taskrun_name_d,
//                     "start_time": date,
//                     "finish_time": "2021/09/13 04:54:43",
//                     "status": result2,
//                     'log': '123456789'
//                 },
//                 {
//                     "name": "task-git-clone",
//                     "taskrun_name": "pipeline-run-dummy-xxxxx-task-git-clone-xxxxx" + taskrun_name_d,
//                     "start_time": date,
//                     "finish_time": "2021/09/13 04:56:51",
//                     "status": result3,
//                     'log': '123456789'
//                 },
//                 {
//                     "name": "task-build-and-push",
//                     "taskrun_name": "pipeline-run-dummy-xxxxx-task-build-and-push-xxxxx" + taskrun_name_d,
//                     "start_time": date,
//                     "finish_time": "2021/09/13 04:57:17",
//                     "status": result4,
//                     'log': '123456789'
//                 },
//                 {
//                     "name": "task-complete",
//                     "taskrun_name": "pipeline-run-dummy-xxxxx-task-complete-xxxxx" + taskrun_name_d,
//                     "start_time": date,
//                     "finish_time": "2021/09/13 04:57:25",
//                     "status": result1,
//                     'log': '123456789'
//                 }
//             ]
//         };
//     }
//     return rows;
// }
//   ws.cmn.dummy = {
//       'new': {
//         "rows": dummyTaskListData(5)
//       },
//       'all': {
//         "rows": dummyTaskListData(1000)
//       }
//     }
//     // --------------------------------------------------
  
  ws.cmn.open( 800 );
  
  // 実行状況詳細画面
  ws.cmn.modal.de.title = 'タスク実行状況';
  ws.cmn.modal.de.class = 'tekton-result-check';
  
  const detailInfo = [],
        detailInfoList = [
    ['repository','アプリケーションコードリポジトリ'],
    ['image','イメージ出力先（タグ含む）'],
    ['date','開始日時'],
    ['branch','ブランチ']
  ];
    
  const detailInfoLength = detailInfoList.length;
  for ( let i = 0; i < detailInfoLength; i++ ) {
    detailInfo.push(ws.cmn.item( detailInfoList[i][0], detailInfoList[i][1], '', ''));
  }
  
  const taskHTML = function( tasks ){
    let task = '';
    
  };
  
  
  const $detail = $(''
  + ws.cmn.traceIdSelecter('TASK ID')
  + detailInfo.join('')
  + '<div class="item-block">'
    + '<div class="item-header">タスク実行状況</div>'
    + '<div class="task-info">'
      + '<div class="task-detail">'
        + '<ul class="task-detail-list"></ul>'
      + '</div>'
    + '</div>'
  + '</div>'
  );
  
  const update = function( d, k ) {
      const setData = {
        '.status-trace-id-number': d.task_id,
        '.repository': `<a href="${encodeURI(d.repository_url)}" taregt="_blank">${d.repository_url}</a>`,
        '.image': d.container_image,
        '.date': d.start_time,
        '.branch': d.build_branch,
      };      
      
      const $modal = ws.cmn.modal.sub.$modal;
      
      // タスク詳細
      const taskLength = d.tasks.length;
      
      // タスク一覧
      if ( $modal.find('.task-detail-list').is(':empty') ) {
          let taskHTML = '';
          for ( let i = 0; i < taskLength; i++ ) {
              taskHTML += `<li class="task-detail-item">`
                + `<div class="task-detail-status"></div>`
                + `<div class="task-detail-name">${d.tasks[i].name}</div>`
                + `<div class="task-detail-date"></div>`
                + `<div class="task-detail-log-open"><button class="et-bu task-status-open epoch-popup-m" title="ログ"><span class="et-bui"></span></button></div>`
                + `<div class="task-detail-log"></div>`
              + `</li>`;
          }
          $modal.find('.task-detail-list').html(taskHTML);
          $modal.find('.task-status-open').on('click', function(){
              const $task = $(this).closest('.task-detail-item');
              $task.toggleClass('task-status-show').find('.task-detail-log').stop(0,0).animate({ height: 'toggle' }, 200 );
          });
      }
      
      const list = ws.cmn.data[k].header[0].list;
      for ( let i = 0; i < taskLength; i++ ) {
          const status = ( d.tasks[i].status )? d.tasks[i].status: 'Pending',
                taskSetData = {
              '.task-detail-status': ws.cmn.data[k].fn.statusHTML( list[ status ], '', status ),
              '.task-detail-date': d.tasks[i].start_time,
              '.task-detail-log': d.tasks[i].log
          };
          $modal.find('.task-detail-item').eq(i).attr('data-status', status);
          for ( const key in taskSetData ) {
              $modal.find('.task-detail-item').eq(i).find( key ).html( taskSetData[key] );
          }
      }
      
      for ( const key in setData ) {
          $modal.find( key ).html( setData[key] );
      }
  };

  ws.cmn.data.new.detail.$detail = $detail;
  ws.cmn.data.all.detail.$detail = $detail;
  
  ws.cmn.data.new.detail.update = update;
  ws.cmn.data.all.detail.update = update;
  
  ws.cmn.modal.fn.$modal.on('click', '.table-button', function(){
      const type = ( $(this).closest('#all-task').length )? 'all': 'new';
      ws.cmn.data[type].detail.traceid = $( this ).attr('data-button');
      ws.cmn.data[type].detail.targetID = 'task_id';
      ws.cmn.detail( type, 760 );
  });
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Manifestリポジトリ結果確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function wsManiRepoCheck( environment ) {
  const ws = this;
  ws.cmn = new wsResultCommon();
  
  // モーダル構造
  ws.cmn.modal.st = {
      'id': 'manifest-repository-check',
      'class': 'layout-tab-fixed',
      'title': 'Manifestリポジトリ Commit一覧',
      'footer': {
          'cancel': {'text': '閉じる', 'type': 'negative'}
      },
      'block': {
          'tabBlock': {
              'tab': {
                  'id': 'manifest-repository-check-tab',
                  'type': 'common',
                  'tabs': {}
              }
          }
      }
  };
  
  const commonHeader = [      
      {'className': 'manifest-file', 'width': '240px', 'title': 'Manifest', 'type': 'link', 'filter': 'on'},
      {'className': 'branch lb', 'width': '160px', 'title': 'ブランチ', 'type': 'text', 'filter': 'on'},        
      {'className': 'message lb', 'title': 'メッセージ', 'type': 'text', 'filter': 'on'},        
      {'className': 'changer lb', 'title': '更新者', 'type': 'text', 'filter': 'on'},        
      {'className': 'update', 'title': '更新日時', 'type': 'date', 'filter': 'on'},
      {'className': 'commit-id lb', 'width': '100px', 'title': 'Commit ID', 'align': 'center', 'type': 'link', 'filter': 'on'},     
  ];
  const commonOption = {
            'className': 'table-grid commit-status manifest', 'download': 'on'
          };
  const commonChenge = function( data ) {
      const body = [],
            length = data.length;
      for ( let i = 0; i < length; i++ ) {
        const d = data[i],
              cid = d.commit_id.slice( 0, 6 ),
              cDate = ws.cmn.fn.formatDate( d.date, 'yyyy/MM/dd HH:mm:ss');
        body.push([['#', d.manifest_file ], d.branch, d.message, d.name, cDate, [ d.html_url, cid ] ]);
      }
      return body;
  };
  
  // 環境の数だけタブを用意する
  ws.cmn.data = {};
  ws.cmn.dummy = {};
  for ( const key in environment ) {
      const repositoryName = environment[key][key + '-git-service-argo-repository-url'].replace(/^.+\/([^\/]+)\/([^\/]+).git$/, '$1 / $2');
      ws.cmn.modal.st.block.tabBlock.tab.tabs[key] = {
          'title': environment[key].text,
          'item': {
              'repository': {
                  'type': 'string',
                  'title': 'リポジトリ名',
                  'text': repositoryName
              },
              'tableArea': {
                'type': 'loading',
                'id': 'manifest-repository'
              }
          }
      };
      ws.cmn.data[key] = {
          'header': commonHeader,
          'option': commonOption,
          'change': commonChenge,
          'url': workspace_api_conf.api.cd_pipeline.git.commits.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id')),
          'target': '#' + key + '-manifest-repository'
      };
         
      // ダミーデータ ----------------------------------------
      ws.cmn.dummy[key] = {
        "rows": [
          {
            "branch": "master",
            "manifest_file": key + ".yaml",
            "commit_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", //【コミットID】
            "name": '【更新者】',
            "date": "2021-11-29T08:07:10Z", // 【実行日時】
            "message": "メッセージメッセージメッセージメッセージメッセージ",
            "html_url": "https://github.com/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", // 【コミット詳細のURL】
          },
          {
            "branch": "master",
            "manifest_file": "xxx2.yaml",
            "commit_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",// 【コミットID】
            "name": '【更新者】',
            "date": "2021-11-29T08:07:10Z", // 【実行日時】
            "message": "メッセージメッセージメッセージメッセージメッセージ",
            "html_url": "https://github.com/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
          }
        ]
      };
      // --------------------------------------------------
  }

  ws.cmn.open( 1080 );
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   レジストリサービス結果確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function wsRegiSerCheck() {
    const ws = this;
    ws.cmn = new wsResultCommon();

    // ポーリング設定
    ws.cmn.update = true;
    ws.cmn.pollingTime = 3000;
    
    // モーダル構造
    ws.cmn.modal.st = {
        'id': 'registry-service-check',
        'class': 'layout-tab-fixed layout-padding-0',
        'title': 'レジストリサービス イメージ一覧',
        'footer': {
            'cancel': {'text': '閉じる', 'type': 'negative'}
        },
        'block': {
            'manifest': {
                'item': {
                    'item1': {
                      'type': 'loading',
                      'id': 'registry-service'
                    }
                }
            }
        }
    };

    // 表示データ
    ws.cmn.data = {
        'manifest': {
            'url': workspace_api_conf.api.ci_pipeline.registry.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id')),
            'target': '#registry-service',
            'header': [
                {'className': 'image', 'title': 'イメージ名', 'type': 'link', 'width': '20%', 'sort': 'on', 'filter': 'on'},
                {'className': 'tag lb', 'title': 'TAG', 'type': 'text', 'width': '20%', 'sort': 'on', 'filter': 'on'},        
                {'className': 'push lb', 'title': 'Push日時', 'type': 'date', 'width': '160px', 'sort': 'on', 'filter': 'on'},        
                {'className': 'size lb', 'title': 'サイズ', 'type': 'text', 'width': '100px', 'align': 'right', 'sort': 'on', 'filter': 'on'},        
                {'className': 'repository lb', 'title': 'ビルドリポジトリ名', 'type': 'link', 'width': '20%', 'sort': 'on', 'filter': 'on'},        
                {'className': 'branch lb', 'title': 'ビルドブランチ', 'type': 'text', 'width': 'auto', 'sort': 'on', 'filter': 'on'}
            ],
            'option': {
                'download': 'on', 'className': 'resigry'
            },
            'change': function( data ) {
                const body = [],
                      length = data.length;
                for ( let i = 0; i < length; i++ ) {
                    const d = data[i],
                          size = Math.round( d.registry.full_size / 1024 / 1024 * 100 ) / 100; 
                    body.push([
                        [ d.registry.url, d.registry.name ], // イメージ名
                        d.registry.tag, // TAG
                        ws.cmn.fn.formatDate( d.registry.tag_last_pushed, 'yyyy/MM/dd HH:mm:ss'), // Push日時
                        size + ' MB', // サイズ
                        [ d.repository.url, d.repository.name ], // ビルドリポジトリ名
                        d.repository.branch // ビルドブランチ
                    ]);
                }
                return body;
            }
        }
    };

    // ダミーデータ --------------------------------------------------
    ws.cmn.dummy = {
        'manifest': {
          "rows": [
            {
              "registroy" : {
                "name": "xxxxx/aplication1",
                "url": "https://hub.docker.com/r/xxxxx/aplication1",
                "tag": "master.20211206-152408",
                "tag_last_pushed": "2021-12-06T06:26:19.631546Z",
                "full_size": 93005290
              },
              "repository": {
                "name" : "xxxxx/aplication1",
                "url": "https://github.com/xxxxx/aplication1",
                "branch": "master"
              }
            },
            {
              "registroy" : {
                "name": "xxxxx/aplication2",
                "url": "https://hub.docker.com/r/xxxxx/aplication2",
                "tag": "staging1.20211201-152408",
                "tag_last_pushed": "2021-12-06T06:26:19.631546Z",
                "full_size": 93005290
              },
              "repository": {
                "name" : "xxxxx/aplication2",
                "url": "https://github.com/xxxxx/aplication2",
                "branch": "staging1"
              }
            }
          ]
        }
      };
      // --------------------------------------------------

    ws.cmn.open( 1200 );
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   ArgoCD結果確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function wsArgocdCheck() {
    const ws = this;
    ws.cmn = new wsResultCommon();
    
    // ポーリング設定
    ws.cmn.update = true;
    ws.cmn.pollingTime = 3000;

    // モーダル構造
    ws.cmn.modal.st = {
        'id': 'argocd-check',
        'class': 'layout-tab-fixed layout-padding-0',
        'title': 'ArgoCD 実行結果一覧',
        'footer': {
            'cancel': {'text': '閉じる', 'type': 'negative'}
        },
        'block': {
            'argocd': {
                'item': {
                    'item1': {
                      'type': 'loading',
                      'id': 'argocd-result'
                    }
                }
            }
        }
    };

    // 表示データ
    ws.cmn.data = {
        'argocd': {
            'url': workspace_api_conf.api.cd_pipeline.argocd.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id')),
            'target': '#argocd-result',
            'header': [
                {'className': 'status-icon', 'iconClass': 'icon icon-', 'title': 'APP ST', 'type': 'status', 'align': 'center', 'sort': 'on', 'filter': 'on',
                    'list': {
                        'Healthy':'Healthy',
                        'Progressing':'Progressing',
                        'Degraded':'Degraded',
                        'Suspended':'Suspended',
                        'Missing':'Missing',
                        'Unknown':'Unknown'
                    }
                },
                {'className': 'sync-icon lb rs', 'iconClass': 'icon icon-','title': 'SYNC STATUS', 'type': 'status', 'sort': 'on', 'filter': 'on',
                    'list': {'Synced':'Synced','OutOfSync':'OutOfSync'}
                },     
                {'className': 'sync', 'title': 'SYNC STATUS TEXT', 'type': 'text' },        
                {'className': 'head lb rs', 'title': 'from HEAD', 'type': 'link', 'sort': 'on', 'filter': 'on'},
                {'className': 'start lb rs', 'title': '同期開始日時', 'type': 'date', 'sort': 'on', 'filter': 'on'},        
                {'className': 'finish lb rs', 'title': '同期終了日時', 'type': 'date', 'sort': 'on', 'filter': 'on'},
                {'className': 'environment lb rs', 'title': '環境', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
                {'className': 'trace-id lb rs', 'title': 'トレースID', 'type': 'text', 'sort': 'on', 'filter': 'on'},
                {'className': 'execution-status lb','title': '詳細', 'type': 'button', 'buttonClass': 'execution-status-button table-button icon icon-Detail'},
                {'type': 'class'}
            ],
            'option': {'className': 'table-grid argocd-result','download':'on'},
            'change': function( data ) {
                const body = [],
                      length = data.length;
                for ( let i = 0; i < length; i++ ) {
                    const d = data[i],
                          head = d.argocd_results.sync_status.revision.slice( 0, 6 );
                    body.push([
                        d.argocd_results.health.status, // Healthアイコン 
                        d.argocd_results.sync_status.status, // Syncアイコン
                        d.argocd_results.sync_status.status, // Sync
                        [ d.argocd_results.sync_status.repo_url, head ], // Head
                        ws.cmn.fn.formatDate( d.argocd_results.startedAt, 'yyyy/MM/dd HH:mm:ss'), // 同期開始日時
                        ws.cmn.fn.formatDate( d.argocd_results.finishedAt, 'yyyy/MM/dd HH:mm:ss'), // 同期終了日時
                        d.environment_name, // 環境名
                        d.trace_id, // トレースID
                        d.trace_id, // ボタンID（トレースID）
                        'health-status-' + d.argocd_results.health.status.toLowerCase() // 行クラス
                    ]);
                }
                return body;
            },
            'detail': {}
        }
    };

    // ダミーデータ --------------------------------------------------
    ws.cmn.dummy = {
        'argocd': {
            "rows": [
                {
                    "trace_id": "0000000010",
                    "environment_name": "development",
                    "namespace": "argo-test",
                    "argocd_results": {
                        "health": {
                            "status": "Healthy"
                        },
                        "sync_status": {
                            "status": "Synced",
                            "repo_url": "https://github.com/",
                            "server": "https://kubernetes.default.svc",
                            "revision": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                        },
                        "resource_status": [
                            {
                                "kind": "Rollout",
                                "name": "api-app",
                                "health_status": "Healty",
                                "sync_status": "Synced",
                                "message": "rollout.argoproj.io/api-app unchanged"
                            },
                            {
                                "kind": "Rollout",
                                "name": "ui-app",
                                "health_status": "Progressing",
                                "status": "Synced",
                                "message": "rollout.argoproj.io/ui-app unchanged"
                            }
                        ],
                        "startedAt": "2022-01-20T08:27:39Z",
                        "finishedAt": "2022-01-20T08:27:49Z"
                    } 
                },
                {
                    "trace_id": "0000000011",
                    "environment_name": "development2",
                    "namespace": "argo-test2",
                    "argocd_results": {
                        "health": {
                            "status": "Progressing"
                        },
                        "sync_status": {
                            "status": "OutOfSync",
                            "repo_url": "https://github.com/",
                            "server": "https://kubernetes.default.svc",
                            "revision": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                        },
                        "resource_status": [
                            {
                                "kind": "Rollout",
                                "name": "api-app",
                                "health_status": "Degraded",
                                "sync_status": "OutOfSync",
                                "message": "rollout.argoproj.io/api-app unchanged"
                            },
                            {
                                "kind": "Rollout",
                                "name": "ui-app",
                                "health_status": "Progressing",
                                "status": "OutOfSync",
                                "message": "rollout.argoproj.io/ui-app unchanged"
                            }
                        ],
                        "startedAt": "2022-01-20T08:27:39Z",
                        "finishedAt": "2022-01-20T08:27:49Z"
                    } 
                }
            ]
        }
    };
    
    // 5秒後に変更する
    setTimeout( function(){
        ws.cmn.dummy.argocd.rows[0].argocd_results.health.status = 'Degraded';
        ws.cmn.dummy.argocd.rows[1].argocd_results.health.status = 'Healthy';
        console.log( ws.cmn.dummy )
    }, 5000 );
    
    
    // --------------------------------------------------

    ws.cmn.open( 800 );
    
    
    
    // 実行状況詳細画面
    ws.cmn.modal.de.title = 'ArgoCD 実行状況確認';
    
    const detailInfo = [],
          detailInfoList = [
      ['argocd-environment','環境名'],
      ['argocd-argocd-manifest','Manifestリポジトリ'],
      ['argocd-server','Kubernetes API Server URL'],
      ['argocd-namespace','Namespace']
    ];
    
    const detailInfoLength = detailInfoList.length;
    for ( let i = 0; i < detailInfoLength; i++ ) {
      detailInfo.push(ws.cmn.item( detailInfoList[i][0], detailInfoList[i][1], '', ''));
    }
    
    ws.cmn.data.argocd.detail.$detail = $(''
    + ws.cmn.traceIdSelecter()
    + detailInfo.join('')
    + '<div class="item-block">'
    + '<div class="item-header">ArgoCD 実行状況</div>'
    + '<div class="argocd-exe-info">'
      + '<div class="argocd-health">'
        + `<div class="argocd-health-title">APP HEALTH</div>`
        + '<div class="argocd-health-status"></div>'
      + '</div>'
      + '<div class="argocd-sync">'
        + '<div class="argocd-sync-title">SYNC STATUS</div>'
        + `<div class="argocd-sync-status"></div>`
        + '<div class="argocd-sync-head"></div>'
        + '<div class="argocd-sync-sync"><button class="argocd-sync-button"><span class="icon icon-Update"></span> SYNC</button></div>'
      + '</div>'
      + '<div class="argocd-resource">'
        + '<ul class="argocd-resource-list"></ul>'
      + '</div>'
    + '</div>'
    + '</div>');
    
     ws.cmn.data.argocd.detail.update = function( d ){
      const mURL = d.argocd_results.sync_status.repo_url,
            manifest = `<a href="${encodeURI(mURL)}" taregt="_blank">${mURL}</a>`,
            healthStatus = d.argocd_results.health.status,
            syncStatus = d.argocd_results.sync_status.status,
            headID = d.argocd_results.sync_status.revision.slice( 0, 6 ),
            health = `<span class="icon icon-${healthStatus}"></span>${healthStatus}`,
            sync = `<span class="icon icon-${syncStatus}"></span>${syncStatus}`,
            head = `from <a href="${encodeURI(mURL)}" target="_blank">HEAD(${headID})</a>`,
            resource = [];
      
      const resourceRow = function( r ){
        const rHealth = '<span class="icon icon-' + r.health_status + '"></span>' + r.health_status,
              rSync = '<span class="icon icon-' + r.sync_status + '"></span>' + r.sync_status;
        return `<li class="argocd-resource-item">`
          + `<div class="argocd-resource-kind">${r.kind}</div>`
          + `<div class="argocd-resource-name">${r.name}</div>`
          + `<div class="argocd-resource-health_status status-${r.health_status}">${rHealth}</div>`
          + `<div class="argocd-resource-sync_status status-${r.sync_status}">${rSync}</div>`
          + `<div class="argocd-resource-message">${r.message}</div>`
        + `</li>`;
      };
      for ( const key in d.argocd_results.resource_status ) {
        resource.push( resourceRow( d.argocd_results.resource_status[key]) );
      }
      
      const setData = [
        ['.status-trace-id-number', d.trace_id ],
        ['.argocd-environment', d.environment_name ],
        ['.argocd-argocd-manifest', manifest ],
        ['.argocd-server', d.argocd_results.sync_status.server ],
        ['.argocd-namespace', d.namespace ],
        ['.argocd-health-status', health ],
        ['.argocd-sync-status', sync ],
        ['.argocd-sync-head', head ],
        ['.argocd-resource-list', resource.join('') ]
      ];
      const setDataLength = setData.length;
    
      for ( let i = 0; i < setDataLength; i++ ) {
          ws.cmn.modal.sub.$modal.find( setData[i][0] ).html( setData[i][1] );
      }
    };
    
    ws.cmn.modal.fn.$modal.on('click', '.execution-status-button', function(){
        ws.cmn.data.argocd.detail.traceid = $( this ).attr('data-button');
        ws.cmn.detail('argocd', 720 );
    });
    
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   IT Automation結果確認
// 
////////////////////////////////////////////////////////////////////////////////////////////////////
function wsItaCheck() {
    const ws = this;
    ws.cmn = new wsResultCommon();

    // ポーリング設定
    ws.cmn.update = true;
    ws.cmn.pollingTime = 3000;
    
    // モーダル構造
    ws.cmn.modal.st = {
        'id': 'ita-check',
        'class': 'layout-tab-fixed layout-padding-0',
        'title': 'Exastro IT Automation 結果確認',
        'footer': {
            'cancel': {'text': '閉じる', 'type': 'negative'}
        },
        'block': {
            'ita_result': {
                'item': {
                    'item1': {
                      'type': 'loading',
                      'id': 'ita-result-check'
                    }
                }
            }
        }
    };

    // 表示データ
    ws.cmn.data = {
        'ita_result': {
            'url': workspace_api_conf.api.cd_pipeline.ita.get.replace('{workspace_id}', (new URLSearchParams(window.location.search)).get('workspace_id')),
            'target': '#ita-result-check',
            'header': [
                {'className': 'status-icon', 'title': '状態', 'type': 'status', 'align': 'center', 'sort': 'on', 'filter': 'on', 'list':{'Succeeded': '正常終了','Running':'実行中','reserve':'予約','Failed': 'エラー'}},
                {'className': 'date lb rs', 'title': '実行開始日時', 'type': 'date', 'sort': 'on', 'filter': 'on'},
                {'className': 'user lb rs', 'title': '実行者', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
                {'className': 'environment lb rs', 'title': '環境名', 'type': 'text', 'sort': 'on', 'filter': 'on'},        
                {'className': 'trace-id lb rs', 'title': 'トレースID', 'type': 'text', 'sort': 'on', 'filter': 'on'},
                {'className': 'menu nb', 'title': '','type': 'menu', 'align': 'right', 'menu': [
                    {'type': 'cancel', 'icon': 'icon-Cal_off', 'text': '予約取消'},
                    {'type': 'exe-status', 'icon': 'icon-Detail', 'text': '実行状況確認'}
                ]},
                {'type':'class'}
            ],
            'option': {
                'className': 'table-grid ita-result',
                'download': 'on'
            },
            'change': function( data ) {
                const body = [],
                      length = data.length;
                for ( let i = 0; i < length; i++ ) {
                    const d = data[i];
                    
                    const statusList = {
                              '実行中': 'Running',
                              '予約': 'reserve',
                              'エラー': 'Failed',
                              '正常終了': 'Succeeded'
                          },
                          status = statusList[d.cd_status_name],
                          date = ws.cmn.fn.formatDate( d.contents.ita_results.CONDUCTOR_INSTANCE_INFO.TIME_START, 'yyyy/MM/dd HH:mm:ss'),
                          reserve = ( status === 'reserve')? d.trace_id: '__none__' ;
                    
                    body.push([
                        status, // 状態
                        date, // 実行開始日時
                        d.username, // 実行者
                        d.environment_name, // 環境名,
                        d.trace_id, // トレースID
                        [ reserve, d.trace_id ], // メニュー
                        status, // 状態
                    ]);
                }
                return body;
            },
            'detail': {}
        }        
    };

    // ダミーデータ --------------------------------------------------
    ws.cmn.dummy = {
        'ita_result': {
            'rows': [
                {
                    "workspace_id": 2,
                    "trace_id": "0000000001",
                    "cd_status": "Start",
                    "cd_status_name": "実行中",
                    "environment_name": "staging",
                    "namespace": "epoch-sample-20220131-115244",
                    "username": "owner-user",
                    "create_at": "Mon, 31 Jan 2022 02:52:59 GMT",
                    "update_at": "Mon, 31 Jan 2022 02:55:46 GMT",
                    "contents": {
                        "ita_results": {
                            "CONDUCTOR_INSTANCE_INFO": {
                                "CONDUCTOR_INSTANCE_ID": "3",
                                "CONDUCTOR_CLASS_NO": "3",
                                "STATUS_ID": "7",
                                "EXECUTION_USER": "システム管理者",
                                "ABORT_EXECUTE_FLAG": "1",
                                "OPERATION_NO_IDBH": "17",
                                "OPERATION_NAME": "CD実行:https://github.com/xxxxxx/epoch-sample-staging-manifest.git",
                                "TIME_BOOK": null,
                                "TIME_START": "2022/01/17 17:07:13",
                                "TIME_END": null
                            },
                            "manifest_embedding": {
                                "execute_logs": "Using /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************",
                                "error_logs": ""
                            },
                            "manifest_commit_push": {
                                "execute_logs": "commit and push\\nfinish.",
                                "error_logs": ""
                            }
                        },
                        "argocd_results": {},
                        "workspace_info": {
                            "common": {
                                "name": "owner-user-20220131_115244",
                                "note": "ワークスペースowner-user-20220131_115244"
                            },
                            "cd_config": {
                                "environments": [
                                    {
                                        "name": "staging",
                                        "cd_exec_users": {
                                            "user_id": "",
                                            "user_select": "all"
                                        },
                                        "git_repositry": {
                                            "url": ""
                                        },
                                        "environment_id": "t17eae0cbb439da",
                                        "deploy_destination": {}
                                    }
                                ]
                            },
                            "ci_config": {
                                "environments": [
                                    {
                                        "manifests": [
                                            {
                                                "file": "ui-app.yaml",
                                                "file_id": "2",
                                                "parameters": {
                                                    "image": "exastro/epochsampleappui",
                                                    "param01": "1",
                                                    "param02": "31001",
                                                    "param03": "32001",
                                                    "image_tag": "master.20210708183910"
                                                }
                                            }
                                        ],
                                        "environment_id": "t17eae0cbb439da"
                                    }
                                ]
                            },
                            "create_at": "Mon, 31 Jan 2022 02:52:59 GMT",
                            "update_at": "Mon, 31 Jan 2022 02:55:46 GMT"
                        }
                    }
                },
                {
                    "workspace_id": 3,
                    "trace_id": "0000000002",
                    "cd_status": "Start",
                    "cd_status_name": "予約",
                    "environment_name": "staging",
                    "namespace": "epoch-sample-20220131-115244",
                    "username": "owner-user",
                    "create_at": "Mon, 31 Jan 2022 02:52:59 GMT",
                    "update_at": "Mon, 31 Jan 2022 02:55:46 GMT",
                    "contents": {
                        "ita_results": {
                            "CONDUCTOR_INSTANCE_INFO": {
                                "CONDUCTOR_INSTANCE_ID": "3",
                                "CONDUCTOR_CLASS_NO": "3",
                                "STATUS_ID": "7",
                                "EXECUTION_USER": "システム管理者",
                                "ABORT_EXECUTE_FLAG": "1",
                                "OPERATION_NO_IDBH": "17",
                                "OPERATION_NAME": "CD実行:https://github.com/xxxxxx/epoch-sample-staging-manifest.git",
                                "TIME_BOOK": null,
                                "TIME_START": "2022/01/17 17:07:13",
                                "TIME_END": null
                            },
                            "manifest_embedding": {
                                "execute_logs": "Using /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\nUsing /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] *********************************************************************\\n",
                                "error_logs": ""
                            },
                            "manifest_commit_push": {
                                "execute_logs": "commit and push\\nfinish.",
                                "error_logs": ""
                            }
                        },
                        "argocd_results": {},
                        "workspace_info": {
                            "common": {
                                "name": "owner-user-20220131_115244",
                                "note": "ワークスペースowner-user-20220131_115244"
                            },
                            "cd_config": {
                                "environments": [
                                    {
                                        "name": "staging",
                                        "cd_exec_users": {
                                            "user_id": "",
                                            "user_select": "all"
                                        },
                                        "git_repositry": {
                                            "url": ""
                                        },
                                        "environment_id": "t17eae0cbb439da",
                                        "deploy_destination": {}
                                    }
                                ]
                            },
                            "ci_config": {
                                "environments": [
                                    {
                                        "manifests": [
                                            {
                                                "file": "ui-app.yaml",
                                                "file_id": "2",
                                                "parameters": {
                                                    "image": "exastro/epochsampleappui",
                                                    "param01": "1",
                                                    "param02": "31001",
                                                    "param03": "32001",
                                                    "image_tag": "master.20210708183910"
                                                }
                                            }
                                        ],
                                        "environment_id": "t17eae0cbb439da"
                                    }
                                ]
                            },
                            "create_at": "Mon, 31 Jan 2022 02:52:59 GMT",
                            "update_at": "Mon, 31 Jan 2022 02:55:46 GMT"
                        }
                    }
                },
                {
                    "workspace_id": 3,
                    "trace_id": "0000000003",
                    "cd_status": "Start",
                    "cd_status_name": "実行中",
                    "environment_name": "staging",
                    "namespace": "epoch-sample-20220131-115244",
                    "username": "owner-user",
                    "create_at": "Mon, 31 Jan 2022 02:52:59 GMT",
                    "update_at": "Mon, 31 Jan 2022 02:55:46 GMT",
                    "contents": {
                        "ita_results": {
                            "CONDUCTOR_INSTANCE_INFO": {
                                "CONDUCTOR_INSTANCE_ID": "3",
                                "CONDUCTOR_CLASS_NO": "3",
                                "STATUS_ID": "7",
                                "EXECUTION_USER": "システム管理者",
                                "ABORT_EXECUTE_FLAG": "1",
                                "OPERATION_NO_IDBH": "17",
                                "OPERATION_NAME": "CD実行:https://github.com/xxxxxx/epoch-sample-staging-manifest.git",
                                "TIME_BOOK": null,
                                "TIME_START": "2022/01/17 17:07:13",
                                "TIME_END": null
                            },
                            "manifest_embedding": {
                                "execute_logs": "Using /etc/ansible/ansible.cfg as config file\\n\\nPLAY [all] ***************************************************************************************************************************************************************************************************************************************",
                                "error_logs": ""
                            },
                            "manifest_commit_push": {
                                "execute_logs": "commit and push\\nfinish.",
                                "error_logs": ""
                            }
                        },
                        "argocd_results": {},
                        "workspace_info": {
                            "common": {
                                "name": "owner-user-20220131_115244",
                                "note": "ワークスペースowner-user-20220131_115244"
                            },
                            "cd_config": {
                                "environments": [
                                    {
                                        "name": "staging",
                                        "cd_exec_users": {
                                            "user_id": "",
                                            "user_select": "all"
                                        },
                                        "git_repositry": {
                                            "url": ""
                                        },
                                        "environment_id": "t17eae0cbb439da",
                                        "deploy_destination": {}
                                    }
                                ]
                            },
                            "ci_config": {
                                "environments": [
                                    {
                                        "manifests": [
                                            {
                                                "file": "ui-app.yaml",
                                                "file_id": "2",
                                                "parameters": {
                                                    "image": "exastro/epochsampleappui",
                                                    "param01": "1",
                                                    "param02": "31001",
                                                    "param03": "32001",
                                                    "image_tag": "master.20210708183910"
                                                }
                                            }
                                        ],
                                        "environment_id": "t17eae0cbb439da"
                                    }
                                ]
                            },
                            "create_at": "Mon, 31 Jan 2022 02:52:59 GMT",
                            "update_at": "Mon, 31 Jan 2022 02:55:46 GMT"
                        }
                    }
                }
            ]
        }
    };
    
     // 変更する
    setTimeout( function(){
        ws.cmn.dummy.ita_result.rows[0].cd_status_name = '正常終了';
        ws.cmn.dummy.ita_result.rows[1].cd_status_name = '実行中';
    }, 4000 );
    setTimeout( function(){
        ws.cmn.dummy.ita_result.rows[1].cd_status_name = 'エラー';
        ws.cmn.dummy.ita_result.rows[1].contents.ita_results.manifest_embedding.error_logs = 'ERROE!'
    }, 8000 );
    // --------------------------------------------------
    
    ws.cmn.open( 640 );
    
  
    // 実行状況詳細画面
    ws.cmn.modal.de.title = 'IT Automation 実行状況確認';
    ws.cmn.modal.de.class = 'ita-result-check';
    
    // 実行状況ベース
    const itaConductor = ''
    + '<div class="conductor-area"><div class="conductor-area-inner">'
      + '<div class="node conductor-start"><div class="node-main"><div class="node-cap node-in"></div><div class="node-body"><div class="node-circle"><span class="node-gem"><span class="node-gem-inner node-gem-length-1">S</span></span><span class="node-running"></span><span class="node-result" data-result-text=""></span></div><div class="node-type"><span>Conductor</span></div><div class="node-name"><span>Start</span></div></div><div id="terminal-1" class="node-terminal node-out connect-a connected"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div></div></div>'
      + '<div class="node conductor-end"><div class="node-main"><div id="terminal-2" class="node-terminal node-in connected connect-a"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div><div class="node-body"><div class="node-circle"><span class="node-gem"><span class="node-gem-inner node-gem-length-1">E</span></span><span class="node-running"></span><span class="node-result" data-result-text=""></span></div><div class="node-type"><span>Conductor</span></div><div class="node-name"><span>End</span></div></div><div class="node-cap node-out"></div></div></div>'
      + '<div class="node conductor-epoch"><div class="node-main"><div id="terminal-3" class="node-terminal node-in connected connect-a"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div><div class="node-body"><div class="node-circle"><span class="node-gem"><span class="node-gem-inner node-gem-length-1">1</span></span><span class="node-running"></span><span class="node-result" data-result-text=""></span></div><div class="node-type"><span>EPOCH</span></div><div class="node-name"><span>Manifest</span></div></div><div id="terminal-4" class="node-terminal node-out connect-a connected"><span class="connect-mark"></span><span class="hole"><span class="hole-inner"></span></span></div></div></div>'
      + '<div class="conductor-line1"></div>'
      + '<div class="conductor-line2"></div>'
    + '</div></div>';
    
    
    const body = {
      'block01': {
        'item': {
          'item01': {'type': 'html', 'title': 'IT Automation 実行状況', 'class': 'ita-conductor', 'html': itaConductor },
          'item02': {'type': 'string', 'title': '実行開始日時', 'mainClass': 'item-horizontal item-half', 'class': 'ita-start'},
          'item03': {'type': 'string', 'title': '実行終了日時', 'mainClass': 'item-horizontal item-half', 'class': 'ita-end'},
          'item04': {'type': 'string', 'title': '状態', 'mainClass': 'item-horizontal item-half', 'class': 'ita-status'},
          'item05': {'type': 'string', 'title': '環境名', 'mainClass': 'item-horizontal item-half', 'class': 'ita-environment'}
        }
      },
      'block02': {
        'tab': {
          'type': 'common',
          'tabs': {
            'tab01': {
              'title': 'Manifestパラメータ',
              'item': {
                'item01': {'type': 'loading', 'id': 'ita-manifest-parameter'}
              }
            },
            'tab02': {
              'title': '実行ログ',
              'item': {
                'item01': {'type': 'html', 'title': 'Manifest埋め込み処理 実行ログ', 'mainClass': 'exe-log', 'class': 'item-log', 'accordion': 'on', 'help': '実行した際の標準出力の内容'},
                'item02': {'type': 'html', 'title': 'Manifest埋め込み処理 エラーログ', 'mainClass': 'exe-error-log','class': 'item-log error', 'accordion': 'on', 'help': '実行した際の標準エラー出力の内容またはデータ矛盾等のansible実行時のエラー出力内容'},
                'item03': {'type': 'html', 'title': 'Manifest Commit & Push 実行ログ', 'mainClass': 'commit-log','class': 'item-log', 'accordion': 'on', 'help': '実行した際の標準出力の内容'},
                'item04': {'type': 'html', 'title': 'Manifest Commit & Push エラーログ', 'mainClass': 'commit-error-log','class': 'item-log error', 'accordion': 'on', 'help': '実行した際の標準エラー出力の内容またはデータ矛盾等のansible実行時のエラー出力内容'}
              }
            }
          }
        }
      }
    };
    const $detailBody = ws.cmn.modal.sub.createBody( body );

    $detailBody.find('.modal-block').eq(0).prepend( ws.cmn.traceIdSelecter() ); 
    
    ws.cmn.data.ita_result.detail.$detail = $( $detailBody.html() );

    
     ws.cmn.data.ita_result.detail.update = function( d ){
      const start = ws.cmn.fn.formatDate( d.contents.ita_results.CONDUCTOR_INSTANCE_INFO.TIME_START, 'yyyy/MM/dd HH:mm:ss'),
            end = ws.cmn.fn.formatDate( d.contents.ita_results.CONDUCTOR_INSTANCE_INFO.TIME_END, 'yyyy/MM/dd HH:mm:ss');

      // Manifestパラメータ
      const $manifest = ws.cmn.modal.sub.$modal.find('#tab01-ita-manifest-parameter'),
            manifests = d.contents.workspace_info.ci_config.environments[0].manifests,
            manifestLength = manifests.length;
      
      if ( $manifest.find('.modal-loading-inner').length ) {
        ws.cmn.modal.sub.tabEvent();
        ws.cmn.modal.sub.accordionEvent();
        
        $manifest.empty();
        for ( let i = 0; i < manifestLength; i++ ) {
          const parameters = manifests[i].parameters;
          let parameterHTML = '<table class="c-table"><tbody>';
          for ( const key in parameters ) {
              parameterHTML += `<tr class="c-table-row">`
                + `<th class="c-table-col c-table-col-header"><div class="c-table-ci">${key}</div></th>`
                + `<td class="c-table-col"><div class="c-table-ci">${parameters[key]}</div></td>`
              + `</tr>`;
          }       
          parameterHTML += '</tbody></table>';
           $manifest.append(ws.cmn.modal.sub.createHtml({
              'type': 'html', 'title': manifests[i].file, 'accordion': 'on', 'html': parameterHTML
           }));
        }
      }
    
      const setData = {
        '.status-trace-id-number': d.trace_id,
        '.ita-start': start,
        '.ita-end': end ,
        '.ita-status': d.cd_status_name,
        '.ita-environment': d.environment_name
      };

      // (BEGIN) APIの結果に所定項目が無いときの対処
      // (修正前)
      //   const logData = {
      //     '.exe-log': d.contents.ita_results.manifest_embedding.execute_logs.replace(/\\n/g, '<br>'),
      //     '.exe-error-log': d.contents.ita_results.manifest_embedding.error_logs.replace(/\\n/g, '<br>'),
      //     '.commit-log': d.contents.ita_results.manifest_commit_push.execute_logs.replace(/\\n/g, '<br>') ,
      //     '.commit-error-log': d.contents.ita_results.manifest_commit_push.error_logs.replace(/\\n/g, '<br>')
      //   };
      // (修正後)
      const logData = {
        '.exe-log': "",
        '.exe-error-log': "",
        '.commit-log': "",
        '.commit-error-log': ""
      }
      try { logData['.exe-log'] = d.contents.ita_results.manifest_embedding.execute_logs.replace(/\\n/g, '<br>'); } catch {}
      try { logData['.exe-error-log'] = d.contents.ita_results.manifest_embedding.error_logs.replace(/\\n/g, '<br>'); } catch {}
      try { logData['.commit-log'] = d.contents.ita_results.manifest_commit_push.execute_logs.replace(/\\n/g, '<br>'); } catch {}
      try { logData['.commit-error-log'] = d.contents.ita_results.manifest_commit_push.error_logs.replace(/\\n/g, '<br>'); } catch {}
      // (END) APIの結果に所定項目が無いときの対処

      const $modal = ws.cmn.modal.sub.$modal;
      for ( const key in setData ) {
          $modal.find( key ).html( setData[key] );
      }
      for ( const key in logData ) {
          const $log = $modal.find( key );
          if ( !logData[key] || logData[key] === '' ) {
              $log.addClass('empty');
          } else {
              $log.removeClass('empty');
          }
          $log.find('.item-log').html( logData[key] );
      }
      
      // Conductor
      const $conductor = ws.cmn.modal.sub.$modal.find('.conductor-area');
      switch (  d.cd_status_name ) {
          case '実行中':
              $conductor.attr('data-mode','running');
          break;
          case '正常終了':
              $conductor.attr('data-mode','success');
          break;
          case 'エラー':
              $conductor.attr('data-mode','error');
          break;
          default:
              $conductor.attr('data-mode','checking');
      }      
      
    };
    
    ws.cmn.modal.fn.$modal.on('click', '.table-button', function(){
        const $b = $( this ),
              type = $b.attr('data-button'),
              id = $b.attr('data-value');
        
        switch ( type ) {
            case 'exe-status':
                ws.cmn.data.ita_result.detail.traceid = id;
                ws.cmn.detail('ita_result', 800 );
            break;
            case 'cancel': {
                const r = ws.cmn.result.ita_result.rows;
                const d = r.filter(function(v){
                    return v.trace_id === id;
                }).shift();

                const confirm = new modalFunction({
                          'confirm': {
                              'id': 'confirm',
                              'title': '予約をキャンセルしますか？',
                              'footer': {
                                  'ok': {'text': '予約をキャンセルする', 'type': 'danger'},
                                  'cancel': {'text': '閉じる', 'type': 'negative'}
                              },
                              'block': {
                                  'confirm': {
                                      'item': {
                                          'date': {
                                              'type': 'string',
                                              'title': '実行開始日時',
                                              'mainClass': 'item-horizontal',
                                              'text': ws.cmn.fn.formatDate( d.contents.ita_results.CONDUCTOR_INSTANCE_INFO.TIME_START, 'yyyy/MM/dd HH:mm:ss')
                                          },
                                          'traceId': {
                                              'type': 'string',
                                              'title': 'トレースID',
                                              'mainClass': 'item-horizontal',
                                              'text': d.trace_id
                                          }
                                      }
                                  }
                              }
                          }
                      }, {});
                 confirm.open('confirm', {
                    'ok': function(){alert('キャンセルしました');}
                 }, '480');
            } break;
        }
    });
}