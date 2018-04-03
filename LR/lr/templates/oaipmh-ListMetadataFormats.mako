# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?>
<%!
    from lr.lib import oaipmh as o
%>
<OAI-PMH xmlns="https://www.learningregistry.org/OAI/2.0/"
         xmlns:oai="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://www.learningregistry.org/OAI/2.0/ https://www.learningregistry.org/documents/downloads/OAI-PMH-LR.xsd">
  <responseDate>${c.datetime_now | x}</responseDate>
  % if c.identifier == None:
  <request verb="ListMetadataFormats">${c.path_url | x}</request>
  % else:
    <request verb="ListMetadataFormats" identifier="${c.identifier | x}"
        by_doc_ID="${c.by_doc_ID | x}" by_resource_ID="${c.by_resource_ID | x}">${c.path_url | x}</request>
  % endif
  <ListMetadataFormats>
  % for fmt in c.formats:
   <oai:metadataFormat>
    <oai:metadataPrefix>${o.getMetadataPrefix(fmt["metadataPrefix"]) | n,x}</oai:metadataPrefix>
    <oai:schema>${fmt["schemas"][0] | x}</oai:schema>
    <oai:metadataNamespace></oai:metadataNamespace>
   </oai:metadataFormat>
  % endfor
  </ListMetadataFormats>
</OAI-PMH>
