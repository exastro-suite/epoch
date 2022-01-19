// JavaScript Document
self.onmessage = function( e ){
    
    const result = {
        'status': '',
        'message': ''
    };
    
    const stepMessage = function( m ){
        result.status = 0;
        result.message = m;
        postMessage( result );
    };
    
    const mimeType = function( type ){
      switch( type ) {
        case 'xlsx':
          return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        case 'csv':
          return 'text/csv';
        case 'html':
        case 'htm':
          return 'text/html';
        default:
          return 'application/octet-stream';
      }
    };
    
    try {
        // import SheetJS
        stepMessage('Step 1/4: Import script.');
        self.importScripts('../library/sheetjs/xlsx.full.min.js');

        // Workbook and sheet
        stepMessage('Step 2/4: Table convert.');
        const wb = XLSX.utils.book_new(),
              st = XLSX.utils.aoa_to_sheet( e.data.data );
        XLSX.utils.book_append_sheet( wb, st );

        // xlsx write
        stepMessage('Step 3/4: ' + e.data.type + ' write.');
        const x = XLSX.write( wb, {'bookType': e.data.type, 'bookSST': false, 'type': 'array'});
        
        // Blob
        const m = mimeType( e.data.type ),
              b = new Blob([x], {'type': m });
        
        // Done
        stepMessage('Step 4/4: Dowmload ready.');
        setTimeout( function(){
            result.status = 200;
            result.message = 'done';
            result.data = b;
            postMessage( result );
        }, 300 );
        
    } catch( e ) {
        // Error
        result.status = 400;
        result.message = e;
        postMessage( result );
    }
    
}