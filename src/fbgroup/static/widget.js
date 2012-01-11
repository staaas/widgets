function facebook_group_widget(group_id) {

// Localize jQuery variable
var jQuery;

/******** Load jQuery if not present *********/
if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.6.4') {
    var script_tag = document.createElement('script');
    script_tag.setAttribute("type","text/javascript");
    script_tag.setAttribute("src",
        "http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js");
    if (script_tag.readyState) {
      script_tag.onreadystatechange = function () { // For old versions of IE
          if (this.readyState == 'complete' || this.readyState == 'loaded') {
              scriptLoadHandler();
          }
      };
    } else { // Other browsers
      script_tag.onload = scriptLoadHandler;
    }
    // Try to find the head, otherwise default to the documentElement
    (document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
} else {
    // The jQuery version on the window is the one we want to use
    jQuery = window.jQuery;
    main();
}

/******** Called once jQuery has loaded ******/
function scriptLoadHandler() {
    // Restore $ and window.jQuery to their previous values and store the
    // new jQuery in our local jQuery variable
    jQuery = window.jQuery.noConflict(true);
    // Call our main function
    main(); 
}

/******** Our main function ********/
function main() { 
    jQuery(document).ready(function($) { 
	var css_link = $("<link>", { 
            rel: "stylesheet", 
            type: "text/css", 
            href: "http://widgets.garage22.net/fbgroup/static/widget.css" 
        });
        css_link.appendTo('head');
	$('#fb-groups').html("<div class=\"fb-group-loading\"><img alt=\"loading\" src=\"http://widgets.garage22.net/fbgroup/static/loading.gif\" style=\"display: block; margin: auto; padding: 10px 0;\"/></div><div class=\"fb-group-ready\" style=\"display: none\"></div>");

	var widget_url = "http://widgets.garage22.net/fbgroup/" + group_id + "?callback=?"
	$.getJSON(widget_url, function(data) {
	    $('.fb-group-ready').html(data.html);
	    $(window).load(function () {
		$('.fb-group-loading').hide();
		$('.fb-group-ready').show();
	    });
	});
    });
}

}
