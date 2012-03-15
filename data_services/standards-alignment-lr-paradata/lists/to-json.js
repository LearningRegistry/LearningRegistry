function(head, req) {
    
    // !code lib/util.js
    var info = GetViewInfo(req);

    var parser = RowParser(info.view);
    var row;
    send('{"documents":[');
    var first = true;
    while(row = getRow()){
       if (first) {
            first = false;
       } else {
            send(",");
       }
       var result_data = {
            resource: parser.resource(row),
            discriminator: parser.discriminator(row),
            value: row.value
       };
       send(JSON.stringify(result_data));

    }
    send(']}');

}