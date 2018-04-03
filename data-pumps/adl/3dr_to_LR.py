#!/usr/bin/python
import urllib2
import json
def create_envelope(doc, url):
	envelope = {
           "doc_type":        "resource_data",
           "doc_version":        "0.11.0",
           "active":        True,
           "resource_data_type":    "metadata",
           "submitter_type":    "anonymous",
           "submitter":        "ADL 3d Repository",
		   "TOS" : {"submission_TOS":    "https://www.learningregistry.org/tos-v1-0.html"},
           "resource_locator":    url,
           "keys":        ["3dr"],
           "payload_placement":    "inline",
           "payload_schema":    ["3dr"],
           "resource_data": doc,
		   'publishing_node': '3dr'
          }
	return envelope

def main():
	contentUrl = "http://3dr.adlnet.gov/Public/Model.aspx?ContentObjectID=%s"
	rootUrl = 'http://3dr.adlnet.gov/api/rest/'
	searchUrl = rootUrl + 'search/%s/json'
	metadataUrl = rootUrl + '%s/metadata/json'
	publishUrl = 'http://lrdev1.learningregistry.org/sword'
	response = urllib2.urlopen(searchUrl % 't')
	searchResults = json.load(response)
	print searchResults
	for data in searchResults:
		metadataResponse = urllib2.urlopen(metadataUrl % data['PID'])
		envelope = create_envelope(json.load(metadataResponse),contentUrl % data['PID'])
		request = urllib2.Request(publishUrl,json.dumps(envelope),{'Content-Type':'application/json'})
		response = urllib2.urlopen(request)
		print response.read()
if __name__ == '__main__':
	main()
