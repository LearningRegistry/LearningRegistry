# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?> 
<%!
    from datetime import datetime
    import iso8601
%>
<OAI-PMH 
            xmlns="http://www.learningregistry.org/OAI/2.0/"
            xmlns:oai="http://www.openarchives.org/OAI/2.0/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/documents/downloads/OAI-PMH-LR.xsd" 
>
  <responseDate>${c.datetime_now | x}</responseDate>
  <request verb="GetRecord" identifier="${c.identifier | x}"
           metadataPrefix="${c.metadataPrefix | x}"
           by_doc_ID="${c.by_doc_ID | x}"
           by_resource_ID="${c.by_resource_ID | x}">${c.path_url | x}</request>
 % if c.docList != None:
  <GetRecord>
    % for doc in c.docList:
   <record> 
    <oai:header>
      <oai:identifier>${doc["doc_ID"] | x}</oai:identifier> 
      <%
        tstamp = iso8601.parse_date(doc["node_timestamp"])
      %>
      <oai:datestamp>${h.harvestTimeFormat(tstamp) | x}</oai:datestamp>
    </oai:header>
    <oai:metadata>
      ${doc["resource_data"] | n}
    </oai:metadata>
  </record>
    % endfor
 </GetRecord>
 % endif
</OAI-PMH>