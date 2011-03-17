# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?>
<%!
    from datetime import datetime
    import iso8601
%>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>${c.datetime_now | x}</responseDate>
  <request verb="Identify">${c.path_url | x}</request>
  <Identify>
    <repositoryName>${c.identify["repositoryName"] | x}</repositoryName>
    <baseURL>${c.path_url | x}</baseURL>
    <protocolVersion>2.0</protocolVersion>
    <adminEmail>${c.identify["adminEmail"] | x }</adminEmail>
    <earliestDatestamp>${h.convertToISO8601Zformat(c.identify["earliestDatestamp"]) | x}</earliestDatestamp>
    <deletedRecord>${c.identify["deletedRecord"] | x}</deletedRecord>
    <granularity>${c.identify["granularity"] | x}</granularity>
 </Identify>
</OAI-PMH>