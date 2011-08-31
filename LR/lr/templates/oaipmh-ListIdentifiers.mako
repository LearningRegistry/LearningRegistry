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
  <request verb="ListIdentifiers" 
            from="${h.harvestTimeFormat(c.from_date) | x}"
            until="${h.harvestTimeFormat(c.until_date) | x}" 
            metadataPrefix="${c.metadataPrefix | x}">${c.path_url | x}</request>
  <ListIdentifiers>
  % if c.identifiers != None and len(c.identifiers) > 0:
    % for ident in c.identifiers:
       <header>  
        <identifier>${ident["doc_ID"] | x}</identifier>
        <% tstamp = iso8601.parse_date(ident["node_timestamp"]) %><datestamp>${h.harvestTimeFormat(tstamp) | x}</datestamp>
       </header>
    % endfor
  % endif
 </ListIdentifiers>
</OAI-PMH>