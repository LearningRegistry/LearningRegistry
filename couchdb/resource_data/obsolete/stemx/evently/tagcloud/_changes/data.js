function (data) {
	
	document.data = data;
	
	var wordlist = [];
	
	for (var i=0; i < data.rows.length; i++) {
		wordlist[wordlist.length] = {
			"text": data.rows[i]["key"],
			"weight": data.rows[i]["value"]
		}
	}
	
	document.wordlist = wordlist;
	
	return {
		"wordlist": wordlist 
	}
}
