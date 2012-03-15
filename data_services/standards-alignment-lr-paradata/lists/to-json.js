function(head, req) {
  var _ = require("lib/underscore-min");
  var util = require("lib/util").init();

  var info = util.GetViewInfo(req);
  var parser = util.RowParser(info.view);

  var row;
  var first_group = true;
  var groups = {cur_group:null, prev_group:null};
  var result_data = {}; 
  var count = 0;
  send('{"documents":[');
  while(row = getRow()){
     count++;
     
     groups = util.GroupIt(parser.group_length, groups, row);
     if (groups.changed) {
      if (first_group) {
        first_group = false;
      } else {
        send("]},");
      }

      result_data = {
          resource: parser.resource(row),
          discriminator: parser.discriminator(row)
      };
      
      send('{"result_data":'+JSON.stringify(result_data)+',');
      send('"resource_data":[');
      send(JSON.stringify(parser.either(row)));
     } else {
      send(','+JSON.stringify(parser.either(row)));
     }

  }
  if (count > 0) {
    send("]}");
  }
  send(']}');

}