function(head, req) {
    send("{");
    var row;
    send("\"rows\": [");
    var first = true;
    while (row = getRow()) {
        if (!first) {
            send(",");
        } else {
            first = false;
        }
        send(JSON.stringify(row));
    }
    send("],");
    send("\"head\":"+JSON.stringify(head)+",");
    send("\"req\":"+JSON.stringify(req));
    send("}");
}