import java.io.*;
import java.net.*;
import java.util.Map;

import org.ardverk.coding.*;

import org.adl.registry.registryproxy.*;
import org.bouncycastle.openpgp.PGPException;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import com.didisoft.pgp.PGPLib;
import com.didisoft.pgp.HashAlgorithm;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
public class RIMLiteDataPump {
	private static final String RESOURCE_DATA = "resource_data";
	private static final String TOS2 = "TOS";
	private static final String SUBMISSION_TOS = "submission_TOS";
	private static final String RESOURCE_LOCATOR = "resource_locator";
	private static final String ADL = "adl";
	private static final String KEYS = "keys";
	private static final String IDENTITY = "identity";
	private static final String SUBMITTER = "submitter";
	private static final String ANONYMOUS = "anonymous";
	private static final String SUBMITTER_TYPE = "submitter_type";
	private static final String LINKED = "linked";
	private static final String PAYLOAD_PLACEMENT = "payload_placement";
	private static final String PAYLOAD_SCHEMA = "payload_schema";
	private static final String ACTIVE = "active";
	private static final String DOC_TYPE = "doc_type";
	private static String SendPost(String target, String data)
			throws IOException {
		String response = "";
		URL url = new URL(target);
		URLConnection conn = url.openConnection();
		// Set connection parameters.
		conn.setDoInput(true);
		conn.setDoOutput(true);
		conn.setUseCaches(false);
		// Make server believe we are form data...
		conn.setRequestProperty("Content-Type", "application/json");
		DataOutputStream out = new DataOutputStream(conn.getOutputStream());
		// Write out the bytes of the content string to the stream.
		out.writeBytes(data);
		out.flush();
		out.close();
		// Read response from the input stream.
		BufferedReader in = new BufferedReader(new InputStreamReader(
				conn.getInputStream()));
		String temp;
		while ((temp = in.readLine()) != null) {
			response += temp + "\n";
		}
		temp = null;
		in.close();
		return response;

	}

	private static String SignEnvelopeData(String message) throws PGPException,
			IOException {
		PGPLib pgp = new PGPLib();

		// clear sign
		String privateKeyPassword = "wegrata";
		String clearSignedMessage = pgp.clearSignString(message,
				"C:\\users\\gratat\\private.key", privateKeyPassword,
				HashAlgorithm.SHA256);
		return clearSignedMessage;

	}

	private static JSONObject CreateEnvelopeFromSearchResult(SearchResult result)
			throws JSONException, IOException {
		JSONObject envelope = new JSONObject();
		envelope.put(DOC_TYPE, RESOURCE_DATA);
		envelope.put(ACTIVE, true);
		JSONArray schema = new JSONArray();
		schema.put(result.getMetadataSchema());
		envelope.put(PAYLOAD_SCHEMA, schema);
		envelope.put(PAYLOAD_PLACEMENT, LINKED);
		envelope.put("resource_data_type", "metadata");
		envelope.put("doc_version", "0.21.0");
		JSONObject id = new JSONObject();
		id.put(SUBMITTER_TYPE, ANONYMOUS);
		id.put(SUBMITTER, ANONYMOUS);
		envelope.put(IDENTITY, id);
		envelope.append(KEYS, ADL);
		envelope.put(RESOURCE_LOCATOR, result.getInstanceURL());
		JSONObject tos = new JSONObject();
		tos.put(SUBMISSION_TOS,
				"http://www.learningregistry.org/tos/cc0/v0-5/");
		envelope.put(TOS2, tos);
		envelope.put(RESOURCE_DATA, result.getObjectURL());
		return envelope;
	}
	private static void StripFieldFromObject(JSONObject obj, String field)
	{
		if (obj.has(field))
			obj.remove(field);
	}
	private static Map CreateCleanMap(JSONObject obj) throws JSONException
	{
		JSONObject tos = obj.getJSONObject(TOS2);
		JSONObject identity = obj.getJSONObject(IDENTITY);
		JSONArray schema = obj.getJSONArray(PAYLOAD_SCHEMA);
		JSONArray keys = obj.getJSONArray(KEYS);
		boolean active = obj.getBoolean(ACTIVE);
		obj.remove(ACTIVE);
		obj.put(ACTIVE, Boolean.toString(active));
		obj.remove(TOS2);
		obj.remove(IDENTITY);
		obj.remove(KEYS);
		obj.remove(PAYLOAD_SCHEMA);
		String[] fieldsToRemove = {"digital_signature","_id","_rev", "doc_ID","publishing_node","update_timestamp","node_timestamp","create_timestamp"};
		for(String field : fieldsToRemove){
			StripFieldFromObject(obj, field);
		}
		Map mainMap = obj.map;
		mainMap.put(PAYLOAD_SCHEMA, schema.myArrayList.toArray());
		mainMap.put(KEYS, keys.myArrayList.toArray());
		mainMap.put(TOS2, tos.map);
		mainMap.put(IDENTITY, identity.map);
		return mainMap;
		
	}
	private static String Bencode(JSONObject obj) throws IOException,
			JSONException {
		Map mainMap = CreateCleanMap(obj);
		ByteArrayOutputStream s = new ByteArrayOutputStream();
		BencodingOutputStream bencoder = new BencodingOutputStream(s);		
		bencoder.writeMap(mainMap);
		bencoder.flush();
		String encodedString = s.toString();
		s.close();
		return encodedString;
	}
	private static String hash(String content) throws NoSuchAlgorithmException
	{
		MessageDigest md = MessageDigest.getInstance("SHA-256");
		md.update(content.getBytes());
		byte[] mdbytes  = md.digest();
        StringBuffer hexString = new StringBuffer();
    	for (int i=0;i<mdbytes.length;i++) {	
    		String hex = Integer.toHexString(0xFF & mdbytes[i]);
    		if (hex.length() == 1) {
    		    // could use a for loop, but we're only dealing with a single byte
    		    hexString.append('0');
    		}
    		hexString.append(hex);
    	}		
    	return hexString.toString();
	}
	private static JSONObject ProcessSearchResult(SearchResult result) throws IOException, JSONException, NoSuchAlgorithmException, PGPException
	{
		String signData = Bencode(CreateEnvelopeFromSearchResult(result));
		String hash = hash(signData);
		String signature = SignEnvelopeData(hash);
		JSONObject envelope = CreateEnvelopeFromSearchResult(result);
		JSONObject digitalSignature = new JSONObject();
		digitalSignature.append("key_location", "http://keyserver1.pgp.com/vkd/DownloadKey.event?keyid=0x7FCAEF08E2FE78AA");
		digitalSignature.put("signing_method", "LR-PGP.1.0");
		digitalSignature.put("signature", signature);
		envelope.put("digital_signature", digitalSignature);
		return envelope;
	
	}
	public static void main(String[] args) {
		Handle CAK = new Handle("wgrata001/AAddLL##2011");
		Handle registryId = new Handle("100.51/jadl");
		String registryURL = "http://practice-adlrim.adlnet.gov/ADLRIM/gateway";
		String publishUrl = "http://lrdev05.learningregistry.org/publish";
		JSONObject docs = new JSONObject();
		try {
			RegistrySearchProxy searchProxy = RegistryProxyBuilder
					.createRegistrySearchProxy(CAK, registryURL, registryId);
			SearchResults proxyResults = searchProxy.search("repositoryIdentifier:100.51/*");

			java.util.List<SearchResult> results = proxyResults
					.getSearchResults();
			JSONArray documents = new JSONArray();
			int i = 0;
			for (SearchResult result : results) {

				documents.put(ProcessSearchResult(result));
				i++;
			}

			StringWriter writer = new StringWriter();
			docs.put("documents", documents);
			docs.write(writer);
			String data = writer.toString();
			writer.close();
			try {
				String response = SendPost(publishUrl, data);
				JSONTokener jst = new JSONTokener(response);
				JSONObject publishResults = new JSONObject(jst);
				if (publishResults.getBoolean("OK")) {
					JSONArray r = publishResults
							.getJSONArray("document_results");
					for (int j = 0; j < r.length(); j++) {
						JSONObject res = r.getJSONObject(j);
						if (res.getBoolean("OK")) {
							System.out.println(res.getString("doc_ID"));
						}
					}
				}
			} catch (IOException ex) {
				System.out.println(ex);
			}

		} catch (Exception ex) {
			System.out.println(ex.getMessage());
		}
	}

}
