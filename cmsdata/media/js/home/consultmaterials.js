$(document).ready(function() {
	$(".panel-primary").hide();
	$("input[name=search]").on("change",changeSearch);
	$(document).on("click", ".btn-price", function (event) {
		event.preventDefault();
		$("input[name=code]").val(this.value);
		$(".table").hide('slide', 600);
		searchPriceCode();
	});
	$("input[name=code], input[name=description]").on("keyup", function (event) {
		event.preventDefault();
		var key = event.keyCode ? event.keyCode : event.which
		if (key == 13) {
			console.log(this.name);
			if (this.name == "code") {
				searchPriceCode();
			}else{
				searchDescription();
			}
		};
	});
});
var changeSearch = function (event) {
	event.preventDefault();
	$("input[name="+this.name+"]").each(function () {
		if (this.checked) {
			$("input[name="+this.value+"]").attr("disabled", false);
		}else{
			$("input[name="+this.value+"]").attr("disabled", true);
		};
	});
}
var searchPriceCode = function () {
	var code = $("input[name=code]").val();
	if (code != "") {
		var data = new Object();
		data['code'] = code;
		data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
		$.getJSON('/restful/search/price/code/', data, function(response) {
			console.log(response);
			if (response.status) {
				var template = "\
					<div class=\"col-md-4\">\
						<div class=\"thumbnail brand-warning\">\
							<dl class=\"dl-horizontal\">\
								<dt>Material Code</dt>\
								<dd>{{ materials_id }}</dd>\
								<dt>Material Name</dt>\
								<dd>{{ matname }}</dd>\
								<dt>Material Measure</dt>\
								<dd>{{ matmet }}</dd>\
								<dt>Material Unit</dt>\
								<dd>{{ matunit }}</dd>\
								<dt>Price</dt>\
					",
					tmpprice = "<dd>{{ price }}  -  <q><em>{{ transfer }}</em></q></dd>";
					var $content = $(".show-details"), cont = "", price = "";
					$content.empty();
					cont = Mustache.render(template, response.materials);
					for (var x in response.materials.prices){
						price = price.concat(Mustache.render(tmpprice, response.materials.prices[x]));
					}
				$content.append(cont.concat(price).concat("<dl></div></div>"));
				$(".panel-primary").show("blind", 600);
			}else{
				$().Toastmessage("showWarningToast","Could not retrieve the item details.");
			};
		});
	};
}
var searchDescription = function () {
	var data = new Object();
	data['desc'] = $("input[name=description]").val();
	$.getJSON('/restful/search/price/description/', data, function(response) {
		console.log(response);
			if (response.status) {
				$(".panel-primary").show('blind', 600);
				var template = "<tr>\
													<td>{{ item }}</td>\
													<td>{{ materials_id }}</td>\
													<td>{{ name }}</td>\
													<td>{{ measure }}</td>\
													<td>{{ unit }}</td>\
													<td><button class=\"btn btn-xs btn-block btn-warning text-black btn-price\" value=\"{{ materials_id }}\"><span class=\"glyphicon glyphicon-chevron-right\"></td>\
												</tr>";
				var $tb = $("table > tbody"); 
				$tb.empty();
				for (var x in response.mats){
					$tb.append(Mustache.render(template, response.mats[x]));
				}
				$(".table").show('slide', 600);
				$(".show-details").empty();
			}else{
				$().Toastmessage("showWarningToast","Could not retrieve the items details.");
			};
	});
}