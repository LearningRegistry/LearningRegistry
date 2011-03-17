curl -v -H "Content-Type: application/json" -X POST -d '{"documents" :[{
"doc_type": "resource_data",
"doc_version": "0.10.0",
"active": true,
"update_timestamp": "1/12/2011",
"create_timestamp": "1/12/2011",
"resource_data_type": "metadata",
"submitter_type": "anonymous",
"submitter": "nsdl",
"submission_TOS": "http://www.learningregistry.org/tos-v1-0.html",
"resource_locator": "http://www.instructorweb.com/docs/pdf/convdistance.pdf",
"publishing_node": "nsdl",
"keys": ["xml", "test", "nsdl", "DC"],
"payload_placement": "inline",
"payload_schema": ["DC"],
"resource_data": "<oai_dc:dc xmlns:oai_dc=\"http://www.openarchives.org/OAI/2.0/oai_dc/\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xsi:schemaLocation=\"http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd\"><dc:identifier>http://www.instructorweb.com/docs/pdf/convdistance.pdf</dc:identifier><dc:title>Measurement: Converting Distances</dc:title><dc:description>This lesson helps students understand and practice converting measurements in both English and metric systems. The 8-page pdf begins with a brief introduction to measuring length, English measurement systems, and metric measurement. Students then learn to convert measurements within each system. At the end of the lesson, there are 18 review problems for students to convert measurements on their own. Answers are provided.</dc:description><dc:subject>convert, conversion</dc:subject><dc:subject>Measurement</dc:subject><dc:subject>Measurement</dc:subject><dc:subject>Systems of measurement</dc:subject><dc:subject>Measurement</dc:subject><dc:subject>Systems of measurement</dc:subject><dc:subject>English</dc:subject><dc:subject>Measurement</dc:subject><dc:subject>Systems of measurement</dc:subject><dc:subject>Metric</dc:subject><dc:language>en-US</dc:language><dc:type>Instructional Material</dc:type><dc:type>Lesson/Lesson Plan</dc:type><dc:type>Problem Set</dc:type><dc:type>Student Guide</dc:type><dc:relation>4.MD.1</dc:relation><dc:relation>5.MD.1</dc:relation><dc:publisher>InstructorWeb</dc:publisher><dc:rights>Copyright 2006 InstructorWeb</dc:rights><dc:rights>http://www.instructorweb.com/terms.asp</dc:rights><dc:rights>Free access with registration</dc:rights><dc:format>application</dc:format><dc:format>application/pdf</dc:format><dc:date>2006</dc:date></oai_dc:dc>>"
}]}' http://lrdev1.learningregistry.org/publish > publish.htm && firefox publish.htm &
