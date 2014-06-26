$(document).ready(function() {
	$(".table-desc").hide()
	$("select[name=type]").on("change" ,changeType);
	$("input[name=code],input[name=desc]").on("keypress", checkmaterial);
	$("input[name=desc]").on("keyup", getdescription);
	$(document).on("click", ".btn-mat", getMaterial);
	$("select[name=period]").on("click", getMonths);
});

// functions
var getdata = function (event) {
	var data = new Object();
	data['code'] = $("[name=codeh]").val();
	data['period'] = $("[name=period]").val();
	data['month'] = $("[name=months]").val();
	console.warn(data);
	$.getJSON('/restful/report/get/data/bymaterials/', data, function(response) {
			console.log(response);
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