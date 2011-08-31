# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?>
<%!
    from datetime import datetime
    import iso8601
%>
<OAI-PMH xmlns="http://www.learningregistry.org/OAI/2.0/"
         xmlns:oai="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/OAI/2.0/OAI-PMH-LR.xsd">
 <responseDate>${c.datetime_now | x}</responseDate> 
 <request verb="ListRecords"
            from="${c.from_date | x}"
            until="${c.until_date | x}" 
            metadataPrefix="${c.metadataPrefix | x}">${c.path_url | x}</request>
 <ListRecords>
    % for doc in c.records:
        % if doc["active"] == True:
  <record>
    <header>
      <identifier>${doc["doc_ID"] | x}</identifier> 
      <% tstamp = iso8601.parse_date(doc["node_timestamp"]) %><datestamp>${h.harvestTimeFormat(tstamp) | x}</datestamp>
    </header>
    <metadata>
        ${doc["resource_data"] | n} 
    </metadata>
  </record>
        % else:
  <record>
    <header status="deleted">
      <identifier>${doc["doc_ID"] | x}</identifier>
      <% tstamp = iso8601.parse_date(doc["node_timestamp"]) %><datestamp>${h.harvestTimeFormat(tstamp) | x}</datestamp>
    </header>
  </record>
        % endif
    % endfor
 </ListRecords>
</OAI-PMH>