
var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};

var openDialog = function () {
	jQuery("#dialog").dialog({height: 400, width: 600, modal: true, draggable: false});
	return false;
}

var initFDGraph = function (json) {
	jQuery("#related-keys").html("");
	window.fd = new $jit.ForceDirected({
	    //id of the visualization container
	    injectInto: 'related-keys',
	    //Enable zooming and panning
	    //by scrolling and DnD
	    Navigation: {
	      enable: true,
	      //Enable panning events only if we're dragging the empty
	      //canvas (and not a node).
	      panning: 'avoid nodes',
	      zooming: 50 //zoom speed. higher is more sensible
	    },
	    // Change node and edge styles such as
	    // color and width.
	    // These properties are also set per node
	    // with dollar prefixed data-properties in the
	    // JSON structure.
	    Node: {
	    	color: '#f00',
	    	overridable: true
	    },
	    Edge: {
	      overridable: true,
	      color: '#23A4FF',
	      lineWidth: 0.4
	    },
	    //Native canvas text styling
	    Label: {
	      type: labelType, //Native or HTML
	      size: 10,
	      style: 'bold'
	    },
	    //Add Tips
	    Tips: {
	      enable: true,
	      onShow: function(tip, node) {
	        //count connections
	//        var count = 0;
	//        node.eachAdjacency(function() { count++; });
	        //display node info in tooltip
	        tip.innerHTML = "<div class=\"tip\"><div class=\"tip-title\">" + node.name + "</div>"
	          + "<div class=\"tip-text\"><b>" + node.data.count + " documents found.</b></div></div>";
	      }
	    },
	    // Add node events
	    Events: {
	      enable: true,
	      type: 'Native',
	      //Change cursor style when hovering a node
	      onMouseEnter: function() {
	        fd.canvas.getElement().style.cursor = 'move';
	      },
	      onMouseLeave: function() {
	        fd.canvas.getElement().style.cursor = '';
	      },
	      //Update node positions when dragged
	      onDragMove: function(node, eventInfo, e) {
	          var pos = eventInfo.getPos();
	          node.pos.setc(pos.x, pos.y);
	          fd.plot();
	      },
	      //Implement the same handler for touchscreens
	      onTouchMove: function(node, eventInfo, e) {
	        $jit.util.event.stop(e); //stop default touchmove event
	        this.onDragMove(node, eventInfo, e);
	      },
	      //Add also a click handler to nodes
	      onClick: function(node) {
	        if(!node) return;
	        
	        filterSlice(node.name);
	        // Build the right column relations list.
	        // This is done by traversing the clicked node connections.
	//        var html = "<h4>" + node.name + "</h4><b> connections:</b><ul><li>",
	//            list = [];
	//        node.eachAdjacency(function(adj){
	//          list.push(adj.nodeTo.name);
	//        });
	        //append connections information
	//        $jit.id('inner-details').innerHTML = html + list.join("</li><li>") + "</li></ul>";
	      }
	    },
	    //Number of iterations for the FD algorithm
	    iterations: 200,
	    //Edge length
	    levelDistance: 130,
	    // Add text to the labels. This method is only triggered
	    // on label creation and only for DOM labels (not native canvas ones).
	    onCreateLabel: function(domElement, node){
	      domElement.innerHTML = node.name;
	      var style = domElement.style;
	      style.fontSize = "0.8em";
	      style.color = "#ddd";
	    },
	    // Change node styles when DOM labels are placed
	    // or moved.
	    onPlaceLabel: function(domElement, node){
	      var style = domElement.style;
	      var left = parseInt(style.left);
	      var top = parseInt(style.top);
	      var w = domElement.offsetWidth;
	      style.left = (left - w / 2) + 'px';
	      style.top = (top + 10) + 'px';
	      style.display = '';
	    }
	  });
  // load JSON data.
	window.fd.loadJSON(json);
  // compute positions incrementally and animate.
	window.fd.computeIncremental({
    iter: 40,
    property: 'end',
    onStep: function(perc){
      Log.write(perc + '% loaded...');
    },
    onComplete: function(){
      Log.write('done');
      fd.animate({
        modes: ['linear'],
        transition: $jit.Trans.Elastic.easeOut,
        duration: 2500
      });
    }
  });
  // end
}


var initGraph = function(model) {
	
	jQuery("#related-keys").html("");
	
	//init RGraph
    window.rgraph = new $jit.RGraph({
        //Where to append the visualization
        injectInto: 'related-keys',
        //Optional: create a background canvas that plots
        //concentric circles.
//        background: {
//          CanvasStyles: {
//            strokeStyle: '#555'
//          }
//        },
        //Add navigation capabilities:
        //zooming by scrolling and panning.
        Navigation: {
          enable: true,
          panning: true,
          zooming: 10
        },
        //Set Node and Edge styles.
        Node: {
            color: '#f00',
            type: 'circle',
            overridable: true
        },
        
        Edge: {
          color: '#C17878',
          lineWidth:1,
          overridable: true
        },
        
        levelDistance: 200,
        
        onBeforeCompute: function(node){
            Log.write("centering " + node.name + "...");
            //Add the relation list in the right column.
            //This list is taken from the data property of each JSON node.
            //$jit.id('inner-details').innerHTML = node.data.relation;
        },
        
        //Add the name of the node in the correponding label
        //and a click handler to move the graph.
        //This method is called once, on label creation.
        onCreateLabel: function(domElement, node){
            domElement.innerHTML = node.name;
            domElement.onclick = function(){
                rgraph.onClick(node.id, {
                    onComplete: function() {
                        Log.write("done");
                    }
                });
            };
        },
        //Change some label dom properties.
        //This method is called each time a label is plotted.
        onPlaceLabel: function(domElement, node){
            var style = domElement.style;
            style.display = '';
            style.cursor = 'pointer';

//            if (node._depth <= 1) {
                style.fontSize = "0.8em";
                style.color = "#ccc";
            
//            } else if(node._depth == 2){
//                style.fontSize = "0.7em";
//                style.color = "#494949";
//            
//            } else {
//                style.display = 'none';
//            }

            var left = parseInt(style.left);
            var w = domElement.offsetWidth;
            style.left = (left - w / 2) + 'px';
        }
    });
    //load JSON data
    window.rgraph.loadJSON(model);
    //trigger small animation
    window.rgraph.graph.eachNode(function(n) {
      var pos = n.getPos();
      pos.setc(-200, -200);
    });
    window.rgraph.compute('end');
    window.rgraph.fx.animate({
      modes:['polar'],
      duration: 2000
    });
	
}



window.cur_related_keys = {};

var relatedKeys = function(envelope) {
	if (envelope.keys) {
		used = {}
		for (var i=0; i<envelope.keys.length; i++) {
			var clean = envelope.keys[i].toLowerCase().trim();
			if (!window.cur_related_keys[clean]) {
				window.cur_related_keys[clean] = 0;
			}
			if (!used[clean] || used[clean] < 1 ) {
				window.cur_related_keys[clean] += 1;
				used[clean] = 1;
			}
		}
	}
	
	
}

var keywordModel = function() {
	var template = jQuery("#keywordModelTemplate").html();
	var cur_keys = jQuery("#cur-keys");
	
	var children = "";
	var op = "";
	
	var max = window.cur_related_keys[cur_keys.val()];
	
	for (var key in window.cur_related_keys) {
		if (key == cur_keys.val()) continue;
		children += op + jQuery.mustache(template, {
			"keyword": key,
			"count": window.cur_related_keys[key],
			"children": "",
			"dim": window.cur_related_keys[key]/max
		});
		op = ","
			
	}
	

	var json = jQuery.mustache(template, {
		"keyword": cur_keys.val(),
		"count": window.cur_related_keys[cur_keys.val()],
		"children": children,
		"dim": 1
	});
	
	var obj;
	obj = eval("obj = "+json);
	//console.dir(obj);
	
	return obj;
	
	
}


var displayKeys = function() {
	var related_keys = jQuery("#related-keys");
	var template = jQuery("#relatedKeyTemplate").html();
	related_keys.html("");
	for (var key in window.cur_related_keys) {		
		related_keys.prepend(jQuery.mustache(template, { 
			"related_key": key,
			"count": window.cur_related_keys[key]
		}));
	}
}

var getThumbnail = function(resource_locator) {
	
	var template = jQuery("#thumbnailTemplate").html();
	
	return jQuery.mustache(template, {
		"resource_locator": encodeURIComponent(resource_locator)
	});
}


var filterSlice = function(filter) {
	
	var template = jQuery("#resourceRowTemplate").html();
	var target = jQuery("#resource_body");
	
	if (!(filter && window.results)) return;
	
	var data = window.results;
	
	target.html("");
	if (data.documents) {
//		console.log("have documents");
		doc = data.documents;
		for (var i=0; i < data.documents.length; i++) {
			
//			console.dir(doc[i]);
			if (doc[i].resource_data_description && 
					doc[i].resource_data_description.resource_locator && 
					doc[i].resource_data_description.keys ){
				var use = false;
				for (key in doc[i].resource_data_description.keys) {
					console.log("1: "+doc[i].resource_data_description.keys[key].trim().toLowerCase());
					console.log("2: "+filter.trim());
					if (doc[i].resource_data_description.keys[key].trim().toLowerCase() == filter.trim()) {
	
						use = true;
						continue;
					}
						
				}
				if (!use) continue;
				
//				console.log("locator");
				thumb_url = getThumbnail(doc[i].resource_data_description.resource_locator);
				target.prepend(jQuery.mustache(template, 
					{ 
						"thumbnail": thumb_url,
						"resource_locator_url": doc[i].resource_data_description.resource_locator,
						"identity": (doc[i].resource_data_description.identity ? doc[i].resource_data_description.identity : null)
					} 
				));
				relatedKeys(doc[i].resource_data_description);
			}
			
		}
	}
}

var handleSlice = function(data) {
	window.cur_related_keys = {};
	window.results = data;
	//console.log(data);
//	for (key in data) {
//		console.log("key:"+key);
//	}
	var template = jQuery("#resourceRowTemplate").html();
	var target = jQuery("#resource_body");
	
	target.html("");
	if (data.documents) {
		jQuery("#resource_head").css("visibility", "visible");
//		console.log("have documents");
		doc = data.documents;
		for (var i=0; i < data.documents.length; i++) {
			
//			console.dir(doc[i]);
			if (doc[i].resource_data_description && 
					doc[i].resource_data_description.resource_locator) {
//				console.log("locator");
				thumb_url = getThumbnail(doc[i].resource_data_description.resource_locator);
				target.prepend(jQuery.mustache(template, 
					{ 
						"thumbnail": thumb_url,
						"resource_locator_url": doc[i].resource_data_description.resource_locator,
						"identity": (doc[i].resource_data_description.identity ? doc[i].resource_data_description.identity : null)
					} 
				));
				relatedKeys(doc[i].resource_data_description);
			}
			
		}
		
		//displayKeys();
		var keyModel = keywordModel();
		
//		initGraph(keyModel);
		initFDGraph(keyModel);
	}
	
	
}

var doSlice = function() {	
	var keys = jQuery("#keys");
	var cur_keys = jQuery("#cur-keys");

	cur_keys.val(keys.val());
	
	jQuery.getJSON("/slice", { "any_tags": keys.val(), "stale": true, "limit" : 100 }, handleSlice);
}


jQuery(function() {
	jQuery("#search-form").submit(function() {
		doSlice();
		return false;
	})
});