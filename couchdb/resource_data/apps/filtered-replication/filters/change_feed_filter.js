function(doc, req){
    // Don't send the design document.
    try{
          // If there is no query parameters return send the document.
        if (!req.query || !req.query.doc_type){
            log("no req value or doc_type");
            return true;
        }
        if ( !doc || (doc.doc_type != req.query.doc_type)){
            log("Ignore documents that is not of doc_type: '"+req.query.doc_type+"': "+ doc._id);
            return false;
        }
        //Check if the document say has does distribute field. if so don't send it
        if ("do_not_distribute" in doc){
            return false;
        }
    
        // If there is no filter in the parameter just send the document.
        if (!req.query.filter_description && !req.query.predicate){
            log("No filter or predicate available...");
            return true;
        }
     
        
        //check if there is filter predicate function.
        var predicate_test = true;
        if (req.query.predicate){
            try{
                predicate_func = eval(req.query.predicate);
                predicate_test = predicate_func(doc);
            }
            catch (err){
                log("predicate fuction error"+err);
                predicate_test = false;
            }
        }
        if (predicate_test == false)
        {
            log("doc failed predicate test ... returning false")
            return false;
        }
          
        var filter_description;
        if (req.query.filter_description){
            filter_description = JSON.parse(req.query.filter_description);
        }
        else
        {
            log("no filter ... returning predicate result"+predicate_test)
            return predicate_test
        }
        // Check to see the query parameter is valid  node filter description. if not
        // we can filter anything out so send it.
        if(("custom_filter" in filter_description) && filter_description.custom_filter == true &&
            predicate_test == true){
            log("No filtering needed custom filter is being used");
            return true;
        }
    
        log("The filter is: "+JSON.stringify(filter_description, null, 4))
        // Variable to hold if the document is filter out on match.
        // If include_exclude  is T if the filters describe what documents to accept
        // all others are rejected F if the filters describe what documents to reject
        // all others are accepted optional, T if not present
        var include_doc =  (!("include_exclude" in filter_description) || filter_description.include_exclude==true);
        log("Include doc on match: "+include_doc);
        
        //Keep track the see if the document match all the filters.
         var match_all_filters = true;
        
        //Go through all the filters
        for(var i in filter_description.filter){
            var filter_key = filter_description.filter[i]["filter_key"];
            var filter_value = filter_description.filter[i]["filter_value"];
            var matched_value = null;
            var filter_match = null;
            
            if (!filter_key || !filter_value){
                log("Continuing the key/value loop... invalid filter_key: "+filter_key+" or filter_value: "+filter_value );
                continue;
            }
            //create a regular expression for the filter_key to check for matching against
            //the document key.
            var regex_key = new RegExp(filter_key);
            
            //Create regular expression for the key value
            var regex_value = new RegExp(filter_value);
            
            log("Filter key:  "+filter_key+"\tFilter value: "+filter_value+"\t key regx: "+regex_key);
             //Look though the keys and for the variable that matches the filter key
            for (var key in doc){
                log("key: "+key);
                if (!key.match(regex_key)){
                    continue;
                }
                matched_value = doc[key];
                log("find a match: '"+matched_value+"'  for filter key:  "+filter_key);
                
                //Make we have a valid data for filter_value and matched value
                // otherwise keep looping.
                if (!matched_value){
                    log("The matched_value is bad:  '"+matched_value +"'...keep going\n");
                    continue;
                }
                //Check if there is match
                filter_match = JSON.stringify(matched_value).match(regex_value);
                match_all_filters = match_all_filters && (filter_match != null);
                
                log("The match between '"+regex_value+"' and '"+matched_value+" is: "+filter_match+"\n");
                //Exclude the document if there is a match
                if((include_doc == true && !filter_match )){
                    log("There is no match rejecting document...");
                    return false;
                }
            }
        }
        if( (include_doc == false) &&(match_all_filters == true))
        {
            log("rejecting document because it matches exclude filter...\n")
            return false;
        }
        if (predicate_test == false)
        {
            log("rejecting document because it failed predicate test ...\n");
            return false;
        }
        log("The document just match everything...\n");
        return true;
    }
    catch(err)
    {
        log("Filter error: "+err)
        return false;
    }
}
