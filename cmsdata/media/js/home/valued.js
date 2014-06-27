$(document).ready(function() {
	$(".table-desc").hide()
	$("select[name=type]").on("change" ,changeType);
	$("input[name=code],input[name=desc]").on("keypress", checkmaterial);
	$("input[name=desc]").on("keyup", getdescription);
	$(document).on("click", ".btn-mat", getMaterial);
	$("select[name=period]").on("click", getMonths);
	$(".btn-generate").on("click", getdata);
});

// functions
var getdata = function (event) {
	var prms = new Object(), pass = false;
	prms['code'] = $("[name=codeh]").val();
	prms['period'] = $("[name=period]").val();
	prms['month'] = $("[name=months]").val();
	if (prms.code == "" || prms.period == null) {
		$().toastmessage("showWarningToast", "Fields empty, exit!");
		return false;
	};
	var data = new Object(), initial = new Object();
	$.getJSON('/restful/report/get/balance/back/materials/', prms, function(response) {
		console.log(response);
		if (response.status) {
			initial = response;
			$.getJSON('/restful/report/get/data/bymaterials/', prms, function(response) {
				console.log(response);
				if (response.status) {
					pass = true;
					if (pass) {
						console.log('ready');
						console.table(data);
						console.info(initial);
						var star = "\
												<tr>\
												<td></td><td></td><td colspan='2'>SALDO INICIAL</td><td>16</td>\
												<td>{{ starquantity }}</td><td>{{ starprice }}</td><td>{{ starimport }}</td>\
												<td></td><td></td><td></td><td>{{ endquantity }}</td><td>{{ endprice }}</td><td>{{ endimport }}</td>\
												</tr>\
												";
						var entry = "\
												<tr>\
												<td>{{ transfer }}</td><td></td><td>{{ predoc }}</td><td>{{ postdoc }}</td><td></td>\
												<td>{{ entryquantity }}</td><td>{{ entryprice }}</td><td>{{ entryimport }}</td>\
												<td></td><td></td><td></td><td>{{ endquantity }}</td><td>{{ endprice }}</td><td>{{ endimport }}</td>\
												</tr>\
												";
						var output = "\
												<tr>\
												<td>{{ transfer }}</td><td></td><td>{{ predoc }}</td><td>{{ postdoc }}</td><td></td><td></td><td></td><td></td>\
												<td>{{ outputquantity }}</td><td>{{ outputprice }}</td><td>{{ outputimport }}</td>\
												<td>{{ endquantity }}</td><td>{{ endprice }}</td><td>{{ endimport }}</td>\
												</tr>\
												";
						var $tb = $("table.table-report > tbody");
						$tb.empty();
						var starquantity = initial.initial[0].quantity,
								starprice = initial.initial[0].price,
								endquantity = 0, endprice = 0,
								allentryquantity = 0, alloutputquantity = 0,
								allentryprice = 0, alloutputprice = 0;
						$tb.append(Mustache.render(star, {'starquantity': starquantity, 'starprice': starprice, 'starimport': (starquantity * starprice), 'endquantity': starquantity, 'endprice': starprice, 'endimport': (starquantity * starprice)}));
						for (var x in response.data) {
							if (response.data[x].type == "ENTRY") {
								// entry
								response.data[x].entryquantity = response.data[x].quantity;
								response.data[x].entryprice = response.data[x].price;
								response.data[x].entryimport = (response.data[x].quantity * response.data[x].price);
								// end data
								if (parseInt(x) == 0) {
									response.data[x].endquantity = (starquantity + response.data[x].quantity);
									response.data[x].endprice = response.data[x].price;
									endquantity = (starquantity + response.data[x].quantity);
									response.data[x].endimport = (endquantity * response.data[x].price);
								}else{
									response.data[x].endquantity = (endquantity + response.data[x].quantity);
									response.data[x].endprice = response.data[x].price;
									endquantity = (endquantity + response.data[x].quantity);
									response.data[x].endimport = (endquantity * response.data[x].price);
								};
								allentryquantity += response.data[x].quantity;
								allentryprice += response.data[x].price;
								$tb.append(Mustache.render(entry, response.data[x]));
							}else if(response.data[x].type == "OUTPUT"){
								// output
								response.data[x].outputquantity = response.data[x].quantity;
								response.data[x].outputprice = response.data[x].price;
								response.data[x].outputimport = (response.data[x].quantity * response.data[x].price);
								// end data
								if (parseInt(x) == 0) {
									response.data[x].endquantity = (starquantity - response.data[x].quantity);
									response.data[x].endprice = response.data[x].price;
									endquantity = (starquantity - response.data[x].quantity);
									response.data[x].endimport = (endquantity * response.data[x].price);
								}else{
									response.data[x].endquantity = (endquantity - response.data[x].quantity);
									response.data[x].endprice = response.data[x].price;
									endquantity = (endquantity - response.data[x].quantity);
									response.data[x].endimport = (endquantity * response.data[x].price);
								};
								alloutputquantity += response.data[x].quantity;
								alloutputprice += response.data[x].price;
								$tb.append(Mustache.render(output, response.data[x]));
							};
						}
						$(".fteq").html(allentryquantity);
						$(".ftsq").html(alloutputquantity);
						$(".ftep").html(allentryprice);
						$(".ftsp").html(alloutputprice);
					};
				};
			});
		};
	});
}
var getMonths = function (event) {
	event.preventDefault();
	var period = this.value;
	if (Boolean(period)) {
		var data = new Object(),
				code = $("inputp[name=codeh]").val();
		if (Boolean(code)) {
			data['code'] = code;
			data['period'] = period;
		}else{
			data['period'] = period;
		};
		$.getJSON('/restful/search/inventoy/month/', data, function(response) {
			console.log(response);
			if (response.status) {
				var template = "<option value=\"{{ value }}\">{{ month }}</option>",
				    $month = $("select[name=months]");
				$month.empty();
				$month.append(Mustache.render(template, {'value': "", 'month' :"-- All --"}));
				for (var x in response.months){
					$month.append(Mustache.render(template, response.months[x]));
				}
			}else{
				$().toastmessage("showWarningToast","Nothing months for consult!");
			};
		});
	}else{
		$().toastmessage("showWarningToast","No selected period!");
	};
}
var getMaterial = function (event) {
	event.preventDefault();
	var code = this.value;
	if (Boolean(code).valueOf()) {
		var data = new Object();
		data['code'] = code;
		$.getJSON('/restful/search/inventoy/period/', data, function(response) {
			if (response.status) {
				var template = "<option value=\"{{ period }}\">{{ period }}</option>",
						$sel = $("select[name=period]");
				$sel.empty();
				for (var x in response.period){
					$sel.append(Mustache.render(template,response.period[x]));
				}
				$("input[name=codeh]").val(code);
				$(".table-desc").hide("blind",600);
			}else{
				$().toastmessage("showWarningToast","Not found period for material.");
			};
		});
	};
}
var getdescription = function (event) {
	event.preventDefault();
	var key = window.Event ? event.keyCode : event.which
	if (key === 13) {
		var data = new Object();
		data['desc'] =  this.value;
		$.getJSON('/restful/search/inventoy/details/desc/', data, function(response) {
				if (response.status) {
					var template = "\
						<tr class=\"success\" name={{ materials_id }}>\
						<td>{{ item }}</td>\
						<td>{{ materials_id }}</td>\
						<td>{{ name }}</td>\
						<td>{{ measure }}</td>\
						<td>{{ unit }}</td>\
						<td><button class=\"btn btn-link btn-xs btn-mat\" value=\"{{ materials_id }}\"><span class=\"glyphicon glyphicon-chevron-right\"></span></button></td>\
						</tr>\
					";
					var $tb = $(".table-desc");
					$tb.empty();
					for (var x in response.details){
						response.details[x].item = (parseInt(x) + 1);
						$tb.append(Mustache.render(template, response.details[x]));
					}
					$(".table-desc").show("blind",600);
				}else{
					$().toastmessage("showWarningToast", "no results were found for the description.");
				};
		});
	};
}
var checkmaterial = function (event) {
	if (this.name == "code") {
		$("input[name=desc]").val("");
	}else{
		$("input[name=code]").val("");
	};
}
var changeType = function (event) {
	event.preventDefault();
	if (this.value == "") {
		$("[name=code],[name=desc]").attr("disabled", true);
		$("[name=period],[name=months],button").attr("disabled", true);
		$().toastmessage("showWarningToast", "must select at least one item.");
		return false;
	};
	if (this.value == "one") {
		$("[name=code],[name=desc]").attr("disabled", false);
	};
	if (this.value == "all") {
		$("[name=code],[name=desc]").attr("disabled", true);
	};
	$("[name=period],[name=months],button").attr("disabled", false);
	$("input[name=codeh]").val("");
}