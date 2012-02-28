function(doc) {
    if (doc._id.match(/^_design\//) && doc.views) {
        for (var viewname in doc.views) {
            if (doc.views[viewname]["data-service"]) {
                emit([doc._id, viewname], doc.views[viewname]["data-service"]);
            }
        } 

    }
}