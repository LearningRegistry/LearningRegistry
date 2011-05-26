import org.adl.registry.registryproxy.*;
import com.google.gson.Gson;
public class RIMLiteDataPump
{

    public static void main(String[] args)
	{
		Handle CAK = new Handle("[2000.2.4/60");
		Handle registryId = new Handle(" 100.51/jadl");
		String registryURL = "http://operational-adlrim.adlnet.gov/ADLRIM/gateway";
		try
		{
			Envelope e = new Envelope();
			RegistrySearchProxy searchProxy = RegistryProxyBuilder.createRegistrySearchProxy(CAK,registryURL,registryId);
			SearchResults proxyResults = searchProxy.search("a");
			java.util.List<SearchResult> results = proxyResults.getSearchResults();
			System.out.println(results.size());
			for(SearchResult result : results)
			{
				System.out.println(result.getTitle());
			}
			
		}
		catch(Exception ex)
		{
			System.out.println(ex.getMessage());
		}
	}

}