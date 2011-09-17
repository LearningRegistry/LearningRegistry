# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?>
<%!
    from datetime import datetime
    import iso8601
%>
<OAI-PMH xmlns="http://www.learningregistry.org/OAI/2.0/"
         xmlns:oai="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/documents/downloads/OAI-PMH-LR.xsd">
  <responseDate>${c.datetime_now | x}</responseDate>
  <request verb="Identify">${c.path_url | x}</request>
  <Identify>
    <oai:repositoryName>${c.identify["repositoryName"] | x}</oai:repositoryName>
    <oai:baseURL>${c.path_url | x}</oai:baseURL>
    <oai:protocolVersion>2.0</oai:protocolVersion>
    <oai:adminEmail>${c.identify["adminEmail"] | x }</oai:adminEmail>
    <oai:earliestDatestamp>${h.harvestTimeFormat(c.identify["earliestDatestamp"]) | x}</oai:earliestDatestamp>
    <oai:deletedRecord>${c.identify["deletedRecord"] | x}</oai:deletedRecord>
    <oai:granularity>${c.identify["granularity"] | x}</oai:granularity>
 </Identify>
</OAI-PMH>