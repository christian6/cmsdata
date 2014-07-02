$(document).ready(function() {
	init();
	$("input[name=type]").on("change", changeRadio);
	$("input[name=name],input[name=code]").on("keyup", searchDetails);
	$(document).on("click", ".btn-add", addmaterial);
	$(".btn-table-mat").on("click", closeDetails);
	$("select[name=period]").on("change", chargeMonth);
	$(".btn-generate").on("click", showReport);
});
// funtions
var init = function () {
	$(".bs-callout").find('input[type=text],select').each(function() {
		$(this).attr('disabled', true);
	});
	$(".table-mat").hide();
}
var changeRadio = function (event) {
	var item = this;
	if (this.checked) {
		$(".bs-callout").find('input[type=text],select').each(function() {
			$(this).attr('disabled', true);
			if (item.value == "1") {
				if (this.name == "period") {
					this.disabled = false;
				};
				$(".table-mat,.alert-materials").hide("slide", 600);
			}else if(item.value == "2"){
				if (this.name == "period" || this.name == "month") {
					this.disabled = false;
					chargeMonth();
				};
				$(".table-mat,.alert-materials").hide("slide", 600);
			}else if(item.value == "3"){
				if (this.name == "period" || this.name == "month" || this.name == "code" || this.name == "name") {
					this.disabled = false;
					chargeMonth();
				};
				$(".alert-materials").show("slide", 600);
			}else if(item.value == "4"){
				if (this.name == "period" || this.name == "code" || this.name == "name") {
					this.disabled = false;
				};
				$(".alert-materials").show("slide", 600);
			};
		});
	};
}
var searchDetails = function (event) {
	var key = window.Event ? event.keyCode : event.which
	if (key === 13) {
		var url, data;
		if (this.name == "name") {
			url = "/restful/search/inventoy/details/desc/";
			data = {"desc": this.value}
		}else{
			url = "/restful/search/inventoy/details/code/";
			data = {"code": this.value}
		};
		$.getJSON(url, data, function(response) {
			if (response.status) {
				$(".table-mat").show('slide', 600);
				var $tb = $(".table-mat > tbody"),
						template = "\
												<tr>\
												<td>{{ materials_id }}</td>\
												<td>{{ name }}</td>\
												<td>{{ measure }}</td>\
												<td>{{ unit }}</td>\
												<td><button class=\"btn btn-xs btn-default btn-add\" value=\"{{ materials_id }}\" title=\"{{ name }}\" measure=\"{{ measure }}\"><span class=\"glyphicon glyphicon-plus\"></span></button></td>\
												</tr>\
											 ";
				$tb.empty();
				for (var x in response.details){
					$tb.append(Mustache.render(template, response.details[x]));
				}
			};
		});
	};
}
var addmaterial = function (event) {
	event.preventDefault();
	if (this.value != "") {
		var $tab = $(".alert-materials > .row");
		if ($tab.find("#".concat(this.value)).length > 0) {
			$().toastmessage("showWarningToast","The material already exists!");
			return false;
		};
		var template = "<div class=\"col-md-3\">\
											<div class=\"alert bg-primary\" >\
											<a id=\"{{ code }}\" name=\"mats\" class=\"close\">&times;</a>\
											<strong>{{ code }}</strong> <br>\
											<p>{{ name }}</p>\
											<p>{{ measure }}</p>\
											</div>\
										</div>";
 		$tab.append(Mustache.render(template, {'code':this.value,'name':this.title, 'measure': $(this).attr('measure') }));
	};
}
var closeDetails = function (event) {
	event.preventDefault();
	$(".table-mat").hide("slide", 600);
}
var chargeMonth = function () {
	var period = $("select[name=period]").val();
	$.getJSON('/restful/search/inventoy/month/', {'period': period}, function(response) {
		if (response.status) {
			var template = "<option value=\"{{ value }}\">{{ month }}</option>";
			var $month = $("select[name=month]");
			$month.empty();
			for (var x in response.months){
				$month.append(Mustache.render(template, response.months[x]));
			}
		};
	});
} 
var showReport = function (event) {
	event.preventDefault();
	var url = "/report/show/valued/?",
			data = new Object(),
			mats =  "",
			pass = false;
	$("input[name=type]").each(function () {
		if (this.checked) {
			switch (parseInt(this.value)){
				case 1 :
						data['type'] = "period";
						data['period'] = $("select[name=period]").val();
						break;
				case 2 :
						data['type'] = "periodandmonth";
						data['period'] = $("select[name=period]").val();
						data['month'] = $("select[name=month]").val();
						break;
				case 3:
						data['type'] = "periodandmonthandmaterials";
						data['period'] = $("select[name=period]").val();
						data['month'] = $("select[name=month]").val();
						if ($(".alert-materials > .row").find("strong").length <= 0) {
							$().toastmessage("showWarningToast", "Select at least one material.");
						};
						$(".alert-materials > .row").find("strong").each(function () {
							mats = mats.concat(',').concat("'"+this.innerHTML+"'");
						});
						data['materials'] = mats;
						return false;
						break;
				case 4:
						data['type'] = "periodandmaterials";
						data['period'] = $("select[name=period]").val();
						if ($(".alert-materials > .row").find("strong").length <= 0) {
							$().toastmessage("showWarningToast", "Select at least one material.");
						};
						$(".alert-materials > .row").find("strong").each(function () {
							mats = mats.concat(',').concat("'"+this.innerHTML+"'");
						});
						data['materials'] = mats;
						return false;
						break;
			}
		};
	});
	var size = 0
	for(var x in data){
		if (data.hasOwnProperty(x)) size++;
	}
	if (size > 3) {
		if (mats.length == 0) {
			pass = false;
			return pass;
		}else{
			pass = true;
		};
	}else{
		pass = true;
	};
	console.log(pass);
	if (pass) {
		console.log(data);
		window.open(url.concat($.param(data, true)),"Report");
	};
}