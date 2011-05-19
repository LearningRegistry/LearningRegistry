function(head, req) {	
    start(
    	{
    	    "headers":{
    	    	"Content-Type": "application/json"
    	    }	
    	}
    );
    var row;
    
    while (row = getRow()){
    	send(JSON.stringify(row.doc));
    }
}
