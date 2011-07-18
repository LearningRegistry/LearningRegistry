function(doc, req){
        // Don't send the design document.
        if ( !doc || (doc.doc_type != "resource_data_distributable")){
            //print("Ignore document that is not resource_data_distributable: "+ doc);
            return false;
        }
        // If there is no query parameters return send the document.
        if (!req){
            //print("no req value");
            return true;
        }
        // Check to see the query parameter is valid  node filter description. if not
        // we can filter anything out so send it.
        if(("custom_filter" in req) && req.custom_filter == true){
            //print("No filtering needed custom filter is being used");
            return true;
        }
        // If there is no filter in the parameter just send the document.
        var filter_doc = req.query;
        if (!filter_doc){
            //print("No filter available...");
            return true;
        }
        // Variable to hold if the document is filter out on match.
        // If include_exclude  is T if the filters describe what documents to accept
        // all others are rejected F if the filters describe what documents to reject
        // all others are accepted optional, T if not present
        var include_doc =  (!("include_exclude" in filter_doc) ||filter_doc.include_exclude==true);
        //print("Include doc on match: "+include_doc);
        
        //Keep track the see if the document match all the filters.
         var match_all_filters = true;
        
        //Go through all the filters
        for(var i in filter_doc.filter){
            var filter_key = filter_doc.filter[i]["filter_key"];
            var filter_value = filter_doc.filter[i]["filter_value"];
            var matched_value = null;
            var filter_match = null;
            
            if (!filter_key || !filter_value){
                //print("Continuing the key/value loop... invalid filter_key: "+filter_key+" or filter_value: "+filter_value );
                continue;
            }
            //create a regular expression for the filter_key to check for matching against
            //the document key.
            var regex_key = new RegExp(filter_key);
            
            //Create regular expression for the key value
            var regex_value = new RegExp(filter_value);
            
            //print("Filter key:  "+filter_key+"\tFilter value: "+filter_value+"\t key regx: "+regex_key);
             //Look though the keys and for the variable that matches the filter key
            for (var key in doc){
                //print("key: "+key);
                if (!key.match(regex_key)){
                    continue;
                }
                matched_value = doc[key];
                //print("find a match: '"+matched_value+"'  for filter key:  "+filter_key);
                
                //Make we have a valid data for filter_value and matched value
                // otherwise keep looping.
                if (!matched_value){
                    //print("The matched_value is bad:  '"+matched_value +"'...keep going\n");
                    continue;
                }
                //Check if there is match
                filter_match = JSON.stringify(matched_value).match(regex_value);
                match_all_filters = match_all_filters && filter_match;
                
                //print("The match between '"+regex_value+"' and '"+matched_value+" is: "+filter_match+"\n");
                //Exclude the document if there is a match
                if((include_doc == true && !filter_match )){
                    //print("There is no match rejecting document...");
                    return false;
                }
            }
        }
        if( (include_doc == false) &&(match_all_filters == true))
        {
            //printf("rejecting document because it matches exclue filter...\n")
            return false;
        }
        //print("The document just match everything...\n");
        return true;
    }
