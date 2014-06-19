$(document).ready(function() {
	$("[name=transfer]").datepicker({ showAnim: "slide", dateFormat: "yy-mm-dd", changeMonth: true, changeYear: true });
	//$(".bedside").hide();
	$(".btn-new").on("click", showBedside);
	$(".btn-supplier").click(function () {
		$.ajax({
			url: 'http://www.sunat.gob.pe/w/wapS01Alias',
			type: 'GET',
			//dataType: 'text', //'default: Intelligent Guess (Other values: xml, json, script, or html)',
			data: {ruc: '10704928501'},
			crossDomain: true,
    	dataType: 'jsonp',
			success: function (response) {
				console.log(""+response+"");
			},
			error: function(obj,er,otr) {
				console.log(er);
			}
		});
		$.get('http://www.sunat.gob.pe/w/wapS01Alias', {ruc: '10704928501'}, function(result) {
			var browserName = navigator.appName;
        var doc;
        if (browserName == 'Microsoft Internet Explorer') {
            doc = new ActiveXObject('Microsoft.XMLDOM');
            doc.async = 'false'
            doc.loadXML(result.results);
        } else {
            doc = (new DOMParser()).parseFromString(result.results, 'text/xml');
        }
        var xml = doc;
       	$(xml).each(function () {
       		console.log(this);
       	})
		}, "jsonp");
	});
});

// functions

var showBedside = function (event) {
	event.preventDefault();
	//$("input[name=new]").val('true');
	//$(".bedside").toggle('blind',600);
	$(this).find('.glyphicon').toggleClass('glyphicon-file').addClass('glyphicon-remove');
	$(this).find('.text').text($(".btn-new").find('.glyphicon-file').length == 1 ? "New Document" : "Cancelar");
	$('.btn-clean,.btn-save,.control').toggleClass('ctrl-disabled');
	$('.btn-clean,.btn-save,.control').attr('disabled', $('.ctrl-disabled').length > 0 ? true : false);
}