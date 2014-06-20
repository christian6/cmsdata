$(document).ready(function() {
	$("[name=transfer]").datepicker({ showAnim: "slide", dateFormat: "yy-mm-dd", changeMonth: true, changeYear: true });
	$(".bedside,.show-details").hide();
	$(".btn-new").on("click", showBedside);
	$(".btn-save").on("click", saveBedside);
	$(".btn-clean").on("click", cleanBedside);
	$(".btn-supplier").click(function () {
		connectCross();
	});
	$("[name=description]").on("keyup", keyUpDescription);
	$("[name=description]").on("keypress", function (event) {
		var key = event.keyCode ? event.keyCode : event.which
		if (key != 13) {
			getDescription(this.value.trim().toLowerCase());
		};
	});
	$("[name=meter]").on("click", getSummaryMaterials);
	$("input[name=code-material],input[name=quantity],input[name=price]").on("keypress",function (event) {
		var key = window.Event ? event.which : event.keyCode
		return (key >= 48 && key <= 57 || key == 8 || key == 13 || key == 46)
	});
	$("input[name=code-material]").on("keyup", function (event) {
		var key = event.keyCode ? event.which : event.keyCode
		if (key == 13) {
			searchMaterialCode(this.value);
		};
	});
	$(".btn-add-in").on("click", aggregateDetIn);
	showDetails();
});

var dataProvider = new Object();
// functions
var listDocumentInDetails = function () {
	
}
var aggregateDetIn = function (event) {
	var data =  new Object(),
			pass = false;
	// validate data
	$(".id-mat,input[name=quantity],input[name=price]").each(function () {
		if (this.value != "") {
			if (this.name == "quantity" || this.name == "price") {
				data[this.name] = $.trim(this.value);
			}else{
				data['materials'] = this.innerHTML;
			}
			pass = true;
		}else{
			$().toastmessage("showWarningToast", "Field {0} invalid, empty!".replace("{0}",this.name));
			this.focus();
			pass = false;
			return pass;
		};
	});
	if (pass) {
		data['serie'] = $("input[name=det-serie]").val();
		data['flag'] = true;
		data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
		$.post('/restful/document/in/details/save/', data, function(response) {
			console.log(response);
			if (response.status) {
				// list document in details
				listDocumentInDetails();
			}else{
				$().toastmessage("showWarningToast", "Not found transaction.");
			};
		}, "json");
	};
}
var showDetails = function () {
	var $newd = $("input[name=new]"),
			$details = $("input[name=details]"),
			$serie = $("input[name=det-serie]");
	if (!Boolean(parseInt($newd.val())) && Boolean(parseInt($details.val())) && $serie.val() != "") {
		$(".btn-bedside").hide("slide","fast");	
		$(".show-details").show('blind',600);
	};
}
var saveBedside = function (event) {
	event.preventDefault();
	var data = new Object(),
			pass = false;
	$(".panel-bedside").find('input').each(function () {
		if (this.name == "motive" || this.name == "reference") {
			data[this.name] = this.value;
			return true;
		};
		if ($.trim(this.value) != "") {
			data[this.name] = this.value;
			pass = true
		}else{
			pass = false;
			this.focus();
			$().toastmessage("showWarningToast", "El campo {0} se encuentra vacio.".replace('{0}',this.name));
			return pass
		};
	});
	if (pass) {
		data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
		data['data_s'] = JSON.stringify(dataProvider);
		console.log(data);
		$.post('', data, function(response) {
			console.log(response);
			if (response.status) {
				$("input[name=det-serie]").val(response.serie);
				$("input[name=new]").val("0");
				$("input[name=details]").val("1");
				showDetails();
			}else{
				$().toastmessage("showErrorToast","Error<br/> en la transacción, no se a podido completar.");
			};
		}, "json");
	}
}
var cleanBedside = function (event) {
	$(".panel-bedside").find("input").each(function () {
		if (this.name == "destination") {
			this.value = "JR. SAN MARTIN MZA. E  LOTE. 6 LOS HUERTOS DE HUACHIPA (ALT. KM 7 DE LA AUTOPISTA RAMIRO PRIALE) LIMA LIMA LURIGANCHO";
		}else{
			this.value = "";	
		};
	});
}
var showBedside = function (event) {
	event.preventDefault();
	$("input[name=new]").val('true');
	$(".bedside").toggle('blind',600);
	$(this).find('.glyphicon').toggleClass('glyphicon-file').addClass('glyphicon-remove');
	$(this).find('.text').text($(".btn-new").find('.glyphicon-file').length == 1 ? "New Document" : "Cancelar");
	$('.btn-clean,.btn-save,.control').toggleClass('ctrl-disabled');
	$('.btn-clean,.btn-save,.control').attr('disabled', $('.ctrl-disabled').length > 0 ? true : false);
	if ($(".btn-new").find('.glyphicon-file').length == 0) {
		cleanBedside();
	}
}

var connectCross = function () {
	if ($("[name=supplier]").val() == "") {
		$().toastmessage("showWarningToast", "Warning, Ruc invalido, campo vacio.");
		return false;
	};
	if ($("[name=supplier]").val().length < 11) {
		$().toastmessage("showWarningToast", "Warning, Ruc formato invalido.");
		return false;
	};
	if ($("[name=supplier]").val().length == 11) {
		$.getJSON('/restful/search/sunat/ruc/', {ruc: $("[name=supplier]").val()}, function(response) {
				if (response.status) {
					console.info(response);
					dataProvider = response;
					$("[name=reason]").val(response.reason);
				}else{
					$().toastmessage("showErrorToast", "Ups!, nuestro servidor se a quedado dormido, no se a conectado a la Sunat.");
				};
		});
	};
}