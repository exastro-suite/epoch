// JavaScript Document

$(function(){

    const fn = new epochCommon();

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    //   CI/CD実行画面 Tektonタスクリスト・ログの読み込み
    // 
    ////////////////////////////////////////////////////////////////////////////////////////////////////

    // タスクリスト
    function getTektonTaskList( callback ){
        const getTektonTask = function( type ){
            return new Promise((resolve, reject) => {

              $.ajax({
                "type": "GET",
                "url": workspace_api_conf.api.ciResult.pipelinerun.get.replace('{workspace_id}', workspace_id),
                "data": {"latest": type == "new" ? "True" : "False"},
              }).done(function(data) {
                console.log("DONE : CI実行結果(TEKTON)取得 -> " + type);
                // console.log(typeof(data));
                console.log(JSON.stringify(data));

                data_pipelinerun = data['rows'];
                // 成功
                resolve(data_pipelinerun);

              }).fail(function() {
                console.log("FAIL : CI実行結果(TEKTON)取得");
                // 失敗
                reject();
              });

            });
        }
        const getTektonTaskList = [
            getTektonTask('new'),
            getTektonTask('all')
        ];
        window.Promise.all( getTektonTaskList )
            // 全てのリストの読み込みが完了したら
            .then(function( result ){
                callback( {
                    'new': result[0],
                    'all': result[1]
                });
            })
            // 読み込み失敗
            .catch(function( error ){
                alert( error );
                modal.close();
            });
    }

    // タスクログ
    function getTektonTaskLog( taskRunName, callback ){
      $.ajax({
        "type": "GET",
        "url": workspace_api_conf.api.ciResult.taskrunlogs.get.replace('{workspace_id}', workspace_id).replace('{taskrun_name}', taskRunName),
      }).done(function(data) {
        console.log("DONE : CI実行結果(TEKTON TASK LOG)取得");
        // console.log(typeof(data));
        // console.log(JSON.stringify(data));

        callback( data.log );

      }).fail(function() {
        alert('Failed to read the task log.');
      });
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    //   CI/CD実行画面 Tektonタスクの表示
    // 
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    function tektonTaskStatus(){
    
        // ステータスリスト
        const status = {
          'Succeeded': '完了',
          'Failed': 'エラー',
          'Running': '実行中',
          'Pending': '保留'
        };
    
        // テーブルヘッダ
        const taskHead = [
          {
            'title': 'ステータス',
            'type': 'status',
            'list': status,
            'filter': 'on',
            'className': 'task-main-status-icon task-main-status-border'
          },
          {
            'title': 'Task ID',
            'type': 'text',
            'filter': 'on',
            'sort': 'on',
            'className': 'task-id task-main-status-border'
          },
          {
            'title': 'アプリケーションコードリポジトリ',
            'type': 'url',
            'filter': 'on'
          },
          {
            'title': 'イメージ出力先（タグ含む）',
            'type': 'text',
            'filter': 'on'
          },
          {
            'title': '開始日時',
            'type': 'date',
            'filter': 'on',
            'sort': 'on'
          },
          {
            'title': 'ブランチ',
            'type': 'text',
            'filter': 'on'
          },
          {
            'title': 'タスク実行状況',
            'type': 'button',
            'buttonClass': ''
          },
          {
            'title': 'タスク実行状況',
            'type': 'hidden',
            'className': 'task-status'
          },
          {
            'type': 'class'
          },
          {
            'type': 'attr',
            'attr': 'task-id'
          },
          {
            'type': 'attr',
            'attr': 'pipeline-id'
          }
        ];
        
        const modal = '#pipeline-tekton-check',
              $modal = $( modal ),
              $update = $modal.find('.tekton-task-update'),
              tasksNew = new epochTable(),
              tasksAll = new epochTable();
        
        let taskNewList = [],
            taskAllList = [];
        
        // テーブル表示用データを作成
        const tableBody = function( list ){
          const tbodyList = [],
                listLength = list.length;
          for ( let i = 0; i < listLength; i++ ) {
            tbodyList[i] = [
              list[i].status,
              list[i].task_id,
              list[i].repository_url,
              list[i].container_image,
              list[i].start_time,
              list[i].build_branch,
              '',
              '',
              'task-status-' + list[i].status.toLowerCase(),
              list[i].task_id,
              list[i].pipeline_id,
            ];
          }
          return tbodyList;
        };
        
        const taskNewID = '#pipelineTektonTaskNew-pipeline-tekton-task-new',
              taskAllID = '#pipelineTektonTaskAll-pipeline-tekton-task-all',
              taskNewOpen = [],
              taskAllOpen = [];
        const taskReOpen = function( target, openList, tasks ){
          $( target ).find('.et-r').each(function(){
            const $row = $( this ),
                  taskID = Number( $row.attr('data-task-id') );
            if ( openList.indexOf( taskID ) !== -1 ) {
              const taskData = getTaskData( tasks, taskID );
              $row.addClass('task-status-show').find('.task-status').stop(0,0).show();
              $row.find('.task-status .et-ci').html( tasksHTML( taskData.tasks ) );
            }
          });      
        };
        const taskNewReOpen = function(){
          taskReOpen( taskNewID, taskNewOpen, taskNewList );
        };
        const taskAllReOpen = function(){
          taskReOpen( taskAllID, taskAllOpen, taskAllList );
        };
        
        // Table option
        const tableOption = {
          'bodyHead': 'on',
          'pagingNumber': 50,
          'sortCol': 4,
          'sortType': 'desc'
        };
        
        // 最新のタスク実行状況
        taskHead[6].buttonClass = 'task-status-open task-new';
        tableOption.callback = taskNewReOpen;
        tasksNew.setup( taskNewID, taskHead, taskNewList, tableOption );
        
        // 全てのタスク実行履歴
        taskHead[6].buttonClass = 'task-status-open task-all';
        tableOption.callback = taskAllReOpen;
        tasksAll.setup( taskAllID, taskHead, taskAllList, tableOption );    
        
        // 読み込み中
        const loadingStartTask = function(){
          tasksNew.loadingStart();
          tasksAll.loadingStart();
        };
        
        // 読み込み完了
        const loadingEndTask = function(){
          tasksNew.loadingEnd();
          tasksAll.loadingEnd();
        };
        
        // 内容更新
        const updateTaskList = function( taskList ){
            // モーダルチェック
            if ( $modal.is(':visible') ) {
                loadingEndTask();
                taskNewList = taskList.new;
                taskAllList = taskList.all;
    
                tasksNew.update( tableBody( taskNewList ) );
                tasksAll.update( tableBody( taskAllList ) );
    
                // 更新後一定時間後にボタンを復活する
                const disabledTime = 300;
                setTimeout( function(){ $update.attr('disabled', false ); }, disabledTime );
            }
        };
        
        // 表示内容を更新する
        const updateTask = function(){      
          $update.attr('disabled', true );
          loadingStartTask();
          getTektonTaskList( updateTaskList );
        };
        updateTask();
        
        // 更新ボタン
        $update.on('click', function(){
          updateTask();
        });
        
        // Task IDからデータを取得
        const getTaskData = function( taskData, taskID ){
          const t = taskData.filter(function(v){
            return taskID === v.task_id;
          });
          if ( t.length === 1 ) {
            return t[0];  
          } else {
            // 見つからないか、２つ以上存在する場合はエラー
            window.console.error('Task id error.');
            return undefined;
          }      
        };
        
        // タスク実行状況HTML
        const tasksHTML = function( tasks ){
          const taskLength = tasks.length;
          let detailHTML = '<ul class="task-status-list">';
          
          for ( let i = 0; i < taskLength; i++ ) {
            const d = tasks[i],
                  s = d.status ? d.status : "Pending",
                  statusHTML = tasksNew.statusHTML( status[s], s );
            detailHTML += ''
            + '<li class="task-status-item status-' + s.toLowerCase() + '" style="z-index:' + ( taskLength - i ) + ';">'
              + '<div class="task-status-task">'
                + '<div class="task-status-icon">'
                  + statusHTML
                + '</div>'
                + '<div class="task-status-name">'
                  + d.name
                + '</div>'
                + '<div class="task-status-start">'
                  + '<div class="task-status-start-title">開始日時</div>'
                  + '<div class="task-status-start-date">' + d.start_time + '</div>'
                + '</div>'
                + '<div class="task-status-log-open">';
            if ( s !== 'Pending') {
              detailHTML += '<button type="button" class="et-bu epoch-popup-m task-status-log-open-button" title="ログ" data-target-name="' + d.taskrun_name + '"><span class="et-bui"></span></button>';
            }
            detailHTML += ''
                + '</div>'
                + '<div class="task-status-log"><textarea data-taskrun-name="' + d.taskrun_name + '" class="task-status-log-area" readonly="readonly"></textarea></div>'
              + '</div>'
            + '</li>';
          }
          detailHTML += '</ul>';
          
          return detailHTML;
        };
        
        // 実行状況の開閉状態
        const addTaskOpenID = function( taskOpen, id ){
          if ( taskOpen.indexOf(id) === -1 ) {
            taskOpen.push(id);
          }
        };
        const removeTaskOpenID = function( taskOpen, id ){
          const target = taskOpen.indexOf(id);
          if ( target !== -1 ) {
            taskOpen.splice( target, 1 );
          }
        };
            
        // タスク実行状況を表示する
        $modal.on('click', '.task-status-open', function(){
          const $b = $( this ),
                $row = $b.closest('.et-r'),
                taskID = Number( $row.attr('data-task-id') ),
                type = ( $b.is('.task-new') )? 'new': 'all';
          
          // 実行状況を追加する
          if ( !$row.find('.task-status-list').length ) {
            const taskData = ( type === 'new')? getTaskData( taskNewList, taskID ): getTaskData( taskAllList, taskID );
            $row.find('.task-status .et-ci').html( tasksHTML( taskData.tasks ) );
          }
          
          // 実行状況の開閉
          if ( $row.is('.task-status-show') ) {
            $row.removeClass('task-status-show').find('.task-status').stop(0,0).slideUp( 300 );
            removeTaskOpenID( (( type === 'new' )? taskNewOpen: taskAllOpen ), taskID );
          } else {
            $row.addClass('task-status-show').find('.task-status').stop(0,0).slideDown( 300 );
            addTaskOpenID( (( type === 'new' )? taskNewOpen: taskAllOpen ), taskID );
          }
          
        });
    
        // ログの読み込み準備
        const tektonTaskLogStart = function( taskRunName, $item ) {
          const $log = $item.find('[data-taskrun-name="' + taskRunName + '"]'),
                $logWrap = $log.closest('.task-status-log');
    
          $logWrap.addClass('log-now-loading').append('<div class="log-now-loading-icon"><span></span></div>');
    
          // ログの読み込みが完了したら
          const tektonTaskLogEnd = function( log ){
            $log.addClass('log-loading-completed').val( log );
            $logWrap.removeClass('log-now-loading').find('.log-now-loading-icon').remove();
          }
    
          // ログの読み込み開始
          getTektonTaskLog( taskRunName, tektonTaskLogEnd );
        };
    
        // ログの開閉
        $modal.on('click', '.task-status-log-open-button', function(){
          const $b = $( this ),
                $i = $b.closest('.task-status-item'),
                $w = $i.find('.task-status-log'),
                taskRunName = $b.attr('data-target-name');
    
          $b.mouseleave();
          $i.toggleClass('task-log-show');
          $w.stop(0,0).slideToggle( 300 );
    
          // 初回のみログの読み込みをする
          if ( !$b.is('.log-open-check') ) {
            $b.addClass('log-open-check');
            tektonTaskLogStart( taskRunName, $i );       
          }
        });
        
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    //   モーダル
    // 
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    const modalData = {
      'pipelineTektonCheck': {
        'id': 'pipeline-tekton-check',
        'class': 'layout-tab-fixed',
        'title': 'TEKTON',
        'footer': {
          'cancel': {
            'text': '閉じる',
            'type': 'negative'
          }
        },
        'block': {
          'pipelineTektonTask': {
            'title': 'タスク実行状況',
            'button': {
              'class': 'tekton-task-update',
              'value': '更新'
            },
            'tab': {
              'id': 'pipeline-tekton-task-status',
              'type': 'common',
              'tabs': {
                'pipelineTektonTaskNew': {
                  'title': '最新のタスク実行状況',
                  'item': {
                    'pipelineTektonTaskNewBody': {
                      'type': 'loading',
                      'id': 'pipeline-tekton-task-new'
                    }
                  }
                },
                'pipelineTektonTaskAll': {
                  'title': '全てのタスク実行履歴',
                  'item': {
                    'pipelineTektonTaskAllBody': {
                      'type': 'loading',
                      'id': 'pipeline-tekton-task-all'
                    }
                  }
                }
              }
            }
          }
        }
      }
    };
    
    const modal = new modalFunction( modalData, {} );
    
    $('#ws-pipeline-tekton').find('.modal-tekton-check').on('click', function(){
      modal.open( 'pipelineTektonCheck', {
        'callback': function(){ tektonTaskStatus(); }
      }, 960 );
    });
    
    
    });