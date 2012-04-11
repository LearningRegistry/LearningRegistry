try{
    if (!window["exports"]) {
        window["exports"] = {};
    }
} catch (e) {
    window["exports"] = {};
}

exports.alignment = (function() {
    try {
        if (!log && console.log){
            var log = console.log;
        } else {
            var log = function() { throw arguments; }
        }
    } catch (e) {
        var log = function() { throw e; }
    }

    var ASNPatterns = [
        /https?:\/\/purl\.org\/ASN\/resources\/[A-Z0-9]+/g,
        /https?:\/\/asn\.jesandco\.org\/resources\/[A-Z0-9]+/g
    ];


    var Alignment = {
        
        parseDCT_ConformsTo: function(resource_data, parser) {
            var stds = {};
            try {
                    var nsdl = new XML(resource_data);
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
                log(error);
            }
            return stds;
        },

        parseLRParadata: function(resource_data, parser) {
            var result = null;
            try {

                var verb = resource_data.activity.verb.action;

                var merge = function(a, b) {
                    if (b === null && a !== null) {
                        b = a;
                        return;
                    } else if (a === null) {
                        return;
                    } else {
                        for (var key in a) {
                            if (b[key]) {
                                b[key] += a[key];
                            } else {
                                b[key] = a[key];
                            }
                        }
                    }
                }

                var searchObjectForPattern = function(obj, regex) {
                    var rs = {};
                    var tmp = {};
                    if (Object.prototype.toString.apply(obj) === "[object String]") {
                        tmp = parser(obj.trim(), verb);
                    } else if (Object.prototype.toString.apply(obj) === "[object Array]") {
                        for (var j=0; j<obj.length; j++) {
                            merge(searchObjectForPattern(obj[j], regex), tmp); 
                        }
                    } else if (Object.prototype.toString.apply(obj) === "[object Object]") {
                        for (var key in obj) {
                            merge(searchObjectForPattern(obj[key], regex), tmp);
                        }
                    } 
                    if (tmp != undefined && tmp != null) {
                        for (var key in tmp) {
                            if (rs[key]) {
                                rs[key] += tmp[key];
                            } else {
                                rs[key] = tmp[key];
                            }
                        }
                    }

                    return rs;
                };

                result = searchObjectForPattern(resource_data,ASNPatterns);
            } catch (error) {
                log(error);
            } finally {
                return result;
            }

        }

    };
    function convertDateToSeconds(doc){
        return Math.floor(Date.parse(doc.node_timestamp)/1000);
    }

    return {
        ASNPatterns: ASNPatterns,
        Alignment: Alignment,
        convertDateToSeconds: convertDateToSeconds
    };
})();


exports.alignment_data = [
    {
        "_id": "c9966f4e59e04b168c733b19d7fcb4ad",
        "_rev": "1-a6aae49518aa1ec59f223d4631e9eef4",
        "keys": ["nanometer", "atom", "standards alignment", "Cells", "Environmental Issues", "ions", "magnetic field", "English-Language Arts", "California Academic Content Standards", "Equations and Inequalities", "Music", "Vocabulary & Spelling", "Physics", "Factoring", "delta", "predicatable text", "Botany and Plant Science", "California's Common Core Content Standards", "Algebra & Functions", "Earth & Space Science", "Grade 12", "Grade 11", "Grade Pre-K", "Chemistry", "Grade 10", "Biochemistry", "aurora borealis", "Mathematics", "natural resource", "watershed", "particle", "conservation", "electron", "charged particles", "Grade K", "water", "northern lights", "Life Sciences", "Structure and Function in Living Things", "Reading Comprehension", "nano", "Science", "water cycle", "Grade 9", "Visual Arts", "Literary Analysis", "Grade 8", "Grade 5", "Grade 6", "Grade 3", "Grade 1", "Grade 2", "high frequency"],
        "TOS": {
            "submission_attribution": "Copyright 2011 California Department of Education: CC-BY-3.0",
            "submission_TOS": "http://creativecommons.org/licenses/by/3.0/"
        },
        "payload_placement": "inline",
        "node_timestamp": "2012-02-28T17:01:59.202435Z",
        "create_timestamp": "2012-02-28T17:01:59.202435Z",
        "update_timestamp": "2012-02-28T17:01:59.202435Z",
        "active": true,
        "publishing_node": "3b7ea975ac0f4c2c89a62268be6cbb03",
        "resource_locator": "http://www.readwritethink.org/lessons/lesson_view.asp?id=131",
        "identity": {
            "signer": "Brokers of Expertise",
            "submitter": "Brokers of Expertise",
            "submitter_type": "agent"
        },
        "doc_type": "resource_data",
        "resource_data": {
            "activity": {
                "content": "A resource found at http://www.readwritethink.org/lessons/lesson_view.asp?id=131 was matched to the academic content standard with ID http://purl.org/ASN/resources/S10000FE by a member of the Brokers of Expertise Standards Matching Group on November 7, 2011",
                "related": [{
                    "content": "Recognize that sentences in print are made up of separate words.",
                    "id": "http://purl.org/ASN/resources/S10000FE",
                    "objectType": "academic standard"
                }],
                "verb": {
                    "action": "matched",
                    "date": "2011-11-07",
                    "context": {
                        "objectType": "LMS",
                        "id": "http://www.myboe.org/go/resource/7238",
                        "description": "Brokers of Expertise resource management page"
                    }
                },
                "actor": {
                    "url": "http://myboe.org/go/groups/standards_matchers",
                    "displayName": "Brokers of Expertise Standards Matching Group",
                    "objectType": "group"
                },
                "object": {
                    "id": "http://www.readwritethink.org/lessons/lesson_view.asp?id=131"
                }
            }
        },
        "resource_data_type": "paradata",
        "payload_schema": ["LR Paradata 1.0"],
        "doc_version": "0.23.0",
        "doc_ID": "c9966f4e59e04b168c733b19d7fcb4ad"
    },
    {
        "_id": "f68a4ed260a1410893782a90d97fa93b",
        "_rev": "1-9eb4586b389bcff5f67d15a1120fab7a",
        "resource_data": "<nsdl_dc:nsdl_dc xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:dct=\"http://purl.org/dc/terms/\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns=\"http://www.openarchives.org/OAI/2.0/\" schemaVersion=\"1.02.000\" xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n  <dc:identifier xsi:type=\"dct:URI\">http://ag.arizona.edu/AZWATER/arroyo/101comm.html</dc:identifier>\n  <dct:conformsTo xsi:type=\"dct:URI\">http://purl.org/ASN/resources/S101AF46</dct:conformsTo>\n  <dct:conformsTo xsi:type=\"dct:URI\">http://purl.org/ASN/resources/S1005605</dct:conformsTo>\n  <dc:date xsi:type=\"dct:W3CDTF\">1997-08</dc:date>\n  <dc:title>Sharing Colorado River Water: History, Public Policy and the Colorado River Compact</dc:title>\n  <dc:subject>Hydrology</dc:subject>\n  <dc:subject>Policy issues</dc:subject>\n  <dc:subject>water marketing</dc:subject>\n  <dc:subject>Indian water rights</dc:subject>\n  <dc:subject>Colorado River use</dc:subject>\n  <dc:subject xsi:type=\"nsdl_dc:GEM\">Science</dc:subject>\n  <dc:subject xsi:type=\"nsdl_dc:GEM\">Earth science</dc:subject>\n  <dc:subject xsi:type=\"nsdl_dc:GEM\">Physical sciences</dc:subject>\n  <dc:subject xsi:type=\"nsdl_dc:GEM\">Agriculture</dc:subject>\n  <dc:subject xsi:type=\"nsdl_dc:GEM\">History of science</dc:subject>\n  <dc:subject xsi:type=\"nsdl_dc:GEM\">Astronomy</dc:subject>\n  <dc:subject xsi:type=\"nsdl_dc:GEM\">Space sciences</dc:subject>\n  <dc:description>This page presents a narrative history of the Colorado River Compact, which has provided the management framework for this natural resource since 1922.</dc:description>\n  <dc:creator>Joe Gelt</dc:creator>\n  <dc:rights>Copyright 2003, The Arizona Board of Regents, for the College of Agriculture and Life Sciences, The University of Arizona.</dc:rights>\n  <dc:identifier xsi:type=\"nsdl_dc:ResourceHandle\">hdl:2200/20061003161437665T</dc:identifier>\n  <dct:educationLevel xsi:type=\"nsdl_dc:NSDLEdLevel\">Undergraduate (Lower Division)</dct:educationLevel>\n  <dct:educationLevel xsi:type=\"nsdl_dc:NSDLEdLevel\">Higher Education</dct:educationLevel>\n  <dct:educationLevel xsi:type=\"nsdl_dc:NSDLEdLevel\">Undergraduate (Upper Division)</dct:educationLevel>\n  <dct:educationLevel xsi:type=\"nsdl_dc:NSDLEdLevel\">Graduate/Professional</dct:educationLevel>\n  <dct:educationLevel xsi:type=\"nsdl_dc:NSDLEdLevel\">Informal Education</dct:educationLevel>\n  <dct:educationLevel xsi:type=\"nsdl_dc:NSDLEdLevel\">General Public</dct:educationLevel>\n  <dc:type xsi:type=\"nsdl_dc:NSDLType\">Image/Image Set</dc:type>\n  <dc:type xsi:type=\"nsdl_dc:NSDLType\">Audio/Visual</dc:type>\n  <dc:type xsi:type=\"dct:DCMIType\">Text</dc:type>\n  <dc:type xsi:type=\"nsdl_dc:NSDLType\">Reference Material</dc:type>\n  <dc:type xsi:type=\"nsdl_dc:NSDLType\">Movie/Animation</dc:type>\n  <dc:type xsi:type=\"nsdl_dc:NSDLType\">Photograph</dc:type>\n  <dc:format xsi:type=\"dct:IMT\">text/html</dc:format>\n  <dc:format xsi:type=\"dct:IMT\">text</dc:format>\n  <dc:subject>Geoscience</dc:subject>\n  <dc:subject>History/Policy/Law</dc:subject>\n  <dc:subject>Ecology, Forestry and Agriculture</dc:subject>\n  <dc:subject>Space Science</dc:subject>\n  <dc:language>English</dc:language>\n  <!--The National Science Digital Library (NSDL) has normalized this metadata record for use across its systems and services.-->\n</nsdl_dc:nsdl_dc>",
        "keys": ["Undergraduate (Lower Division)", "Space Science", "Physical sciences", "Graduate/Professional", "History of science", "380599", "Digital Water Education Library (DWEL)", "Astronomy", "Informal Education", "water marketing", "Higher Education", "Hydrology", "Undergraduate (Upper Division)", "Science", "Indian water rights", "Colorado River use", "English", "History/Policy/Law", "General Public", "Policy issues", "Ecology, Forestry and Agriculture", "Earth science", "Agriculture", "Geoscience", "Space sciences"],
        "TOS": {
            "submission_attribution": "The National Science Digital Library",
            "submission_TOS": "http://nsdl.org/help/?pager=termsofuse"
        },
        "payload_placement": "inline",
        "node_timestamp": "2011-10-28T19:49:39.212590Z",
        "create_timestamp": "2011-10-28T19:49:39.212590Z",
        "update_timestamp": "2011-10-28T19:49:39.212590Z",
        "active": true,
        "publishing_node": "cad60ef7493246868f6394fa764397c3",
        "resource_locator": "http://ag.arizona.edu/AZWATER/arroyo/101comm.html",
        "identity": {
            "signer": "The National Science Digital Library <nsdlsupport@nsdl.ucar.edu>",
            "submitter": "SRI International on behalf of The National Science Digital Library",
            "submitter_type": "agent",
            "curator": "The National Science Digital Library"
        },
        "doc_type": "resource_data",
        "digital_signature": {
            "key_location": ["http://pool.sks-keyservers.net:11371/pks/lookup?op=get&search=0xBFF13965146B1740", "https://keyserver2.pgp.com/vkd/DownloadKey.event?keyid=0xBFF13965146B1740"],
            "key_owner": "The National Science Digital Library <nsdlsupport@nsdl.ucar.edu>",
            "signing_method": "LR-PGP.1.0",
            "signature": "-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA1\n\n8b5860ae3dc965f05562031a650d766bd53105bd6c727fa015334e3bb535d9e6\n-----BEGIN PGP SIGNATURE-----\nVersion: GnuPG v1.4.10 (GNU/Linux)\n\niQIcBAEBAgAGBQJOqwc9AAoJEN3QUpzaJ39HZDcQALKNDUBWWhvUisDnKhrF0lw4\nYnndEGWXj0t/6N62S/JMJlLPrTjWnnANTbrE0rVpehytnBOhtqsxidC/Z9EjuTd5\n2LIgk+xwrc/Y2+Ys91P5KRNG4tYEYC4IiztKA8El6wQBX7rxHEHTiNNGgg3jSEsV\nneOimK9JS+1IEJrViCS7aAX1W+RXKDQp1g0l5288VLxA41mDVT+DHd2TJdoetxEj\nTAR68/YwIQc4pxHpaV9JZMyA2QmzcwIHK1VqKoG60NyxaNEXc2O/15vlv2yInJ9n\nGCRTtBbtGj0HFWQTlP+wZJy6bGWPTfyo68N9aCTs5hKHRh+/E0ZkLy11ot/Xh4d4\nlNAXIRA9PkpINkdeCU+5A9l7XVK7suj/RR8MnZMkkxyl6oGazbXBA+tizRU/NUfj\nV1sJrB3w7ap73G/Ev8isSgLyH3511EvwRpX8/mQyXOp7buc0uuJYhypsHGswUUJX\nyqY5e2GcxoFg2DiQxDA1RW3qRcs3VbnXIRz46yuAR4tSi8brXwMdY8ZgVhjd88Cg\nkSNg+iyq7kMqtk+p4wbW0BUe9bGy2H/HBmja7gvue/ulVipzvt3jBQRl2AZzGP7B\nSppGC5VGHGd4NJPxPW+RwneEGOGdDT9FUIDkq2VdjODnjANyuy25CQUP+VR1lhsi\nnxcQcBVeFvNqfhXEXab1\n=qkBx\n-----END PGP SIGNATURE-----\n"
        },
        "resource_data_type": "metadata",
        "payload_schema_locator": "http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
        "payload_schema": ["nsdl_dc"],
        "doc_version": "0.23.0",
        "doc_ID": "f68a4ed260a1410893782a90d97fa93b"
    }
];