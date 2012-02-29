var ASNPatterns = [
    /https?:\/\/purl\.org\/ASN\/resources\/[A-Z0-9]+/g,
    /https?:\/\/asn\.jesandco\.org\/resources\/[A-Z0-9]+/g
];

var Alignment = {
    
    parseDCT_ConformsTo: function(resource_data, parser) {
        var stds = {};
        try {
                var nsdl = eval(resource_data);
                var dct = new Namespace("http://purl.org/dc/terms/");

                conformsToElems = nsdl..dct::conformsTo

                for (idx in conformsToElems) {
                    if (!stds[conformsToElems[idx].toString().trim()]) {
                        var shouldBreak = parser(conformsToElems[idx].toString().trim());
                        stds[conformsToElems[idx].toString().trim()] = 1;
                        if (shouldBreak) {
                            break;
                        }
                    } 
                }

        } catch (error) {
            // bury error
        }
        return stds;
    }

};
function convertDateToSeconds(doc){
    return Math.floor(Date.parse(doc.node_timestamp)/1000);
}
