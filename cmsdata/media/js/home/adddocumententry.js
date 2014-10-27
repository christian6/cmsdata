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
	$(document).on("click", ".btn-edit-mat", showEditMaterials);
	$(document).on("click", ".btn-del-mat", showDelMaterials);
	$(".edit-materials").on("click", editMaterials);
	$(".del-materials").on("click", delMaterials);
	$(".btn-finish-document").on("click", finishDocument);
	$(".btn-annular").on("click", annularDocument);
	$("input[name=currencycurrent]").on("change", activateChangeCurrency);
	$("input[name=typeccu]").val($("input[name=02]").attr("data-purchase"));
});

var dataProvider = new Object();
// functions
var activateChangeCurrency = function (event) {
	if (this.checked) {
		$("input[name=typeccu]").attr("disabled", false);
	}else{
		$("input[name=typeccu]").attr("disabled", true);
	};
}
var finishDocument = function (event) {
	event.preventDefault();
	$().toastmessage("showToast",{
		text: 'Really want to end the document?',
		sticky: true,
		type: 'confirm',
		buttons: [{value:'Yes'},{value:'No'}],
		success: function (result) {
			if (result == "Yes") {
				var data = new Object();
				data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
				data['entry'] = $("input[name=det-serie]").val()+""+$("input[name=ruc]").val();
				$.post('/restful/document/in/finish/', data, function(response) {
					if (response.status) {
						location.href = "/add/document/In/";
					}else{
						$().toastmessage("showErrorToast", "Error, transaction not fount.");
					};
				}, "json");
			};
		}
	});
}
var delMaterials = function (event) {
	event.preventDefault();
	$().toastmessage("showToast",{
		text: 'want Delete Materials?',
		sticky: true,
		type: 'confirm',
		buttons: [{value:'No'},{value:'Yes'}],
		success: function (result) {
			if (result == "Yes") {
				var data = new Object();
				data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
				data['id'] = $("input[name=id_del]").val();
				data['materials'] = $("input[name=materials_del]").val();
				data['entry'] = $("input[name=det-serie]").val()+""+$("input[name=ruc]").val();
				if (data.quantity != "" && data.materials != "" && data.id != "") {
					$.post('/restful/document/in/details/delete/', data, function(response) {
						console.log(response);
						if (response.status) {
							//listDocumentInDetails();
							var $tr = $("tr."+data['id']);
							$tr.remove();
							$(".mdel").modal("hide");
							var counter = 1;
							$("table.table-detailsIn > tbody > tr.text-black").each(function () {
								$(this).find("td").eq(0).html(counter);
								counter += 1;
							});
						}else{
							$().toastmessage("showErrorToast", "Error: transaction not found!");
						};
					});
				};
			};
		}
	});
}
var editMaterials = function (event) {
	event.preventDefault();
	$().toastmessage("showToast",{
		text: 'want edit Materials?',
		sticky: true,
		type: 'confirm',
		buttons: [{value:'No'},{value:'Yes'}],
		success: function (result) {
			if (result == "Yes") {
				var data = new Object();
				data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
				data['id'] = $("input[name=id_edit]").val();
				data['materials'] = $("input[name=materials_edit]").val();
				data['quantity'] = $("input[name=quantity_edit]").val();
				data['price'] = $("input[name=price_edit]").val();
				/*aqui transform price*/
				var currency = $("select[name=currencyedit]").val();
				if (currency != "01"){
					if ($("input[name=currencycurrent]").is(":checked")) {
						var buy = parseFloat($("input[name=typeccu]").val().replace(",","."));
						data['price'] = (buy * parseFloat(data['price']));
					}else{
						var $exchange = $("input[name="+ currency +"]");
						if ($exchange.length > 0) {
							var buy = parseFloat($exchange.attr("data-purchase").replace(",","."));
							data['price'] = (buy * parseFloat(data['price']));
						}else{
							$().toastmessage("showErrorToast", "Currency not support.");
							return false;
						};
					};
					/*var $exchange = $("input[name="+ currency +"]");
					if ($exchange.length > 0) {
						var buy = parseFloat($exchange.attr("data-purchase").replace(",","."));
						data['price'] = (buy * parseFloat(data['price']));
					}else{
						$().toastmessage("showErrorToast", "Currency not support.");
						return false;
					};*/
				}
				data['entry'] = $("input[name=det-serie]").val()+""+$("input[name=ruc]").val();
				if (data.quantity != "" && data.materials != "" && data.id != "") {
					$.post('/restful/document/in/details/edit/', data, function(response) {
						console.log(response);
						if (response.status) {
							//listDocumentInDetails();
							var $td = $("tr."+data['id']+" > td");
							$td.eq(1).html(data['quantity']);
							$td.eq(2).html(data['price'].toFixed(2));
							$td.eq(6).find('button').val(data['quantity']);
							$td.eq(6).find('button').attr("data-price",data['price']);
							$(".medit").modal("hide");
						}else{
							$().toastmessage("showErrorToast", "Error: transaction not found!");
						};
					});
				};
			};
		}
	});
}
var showDelMaterials = function (event) {
	var id = $(this).attr("idid"),
			mid = $(this).attr("idmat");
			$("input[name=id_del]").val(id);
			$("input[name=materials_del]").val(mid);
	$(".mdel").modal("show");
}
var showEditMaterials = function (event) {
	var id = $(this).attr("idid"),
			mid = $(this).attr("idmat"),
			qua = $(this).val(),
			price = $(this).attr("data-price");
			$("input[name=id_edit]").val(id);
			$("input[name=materials_edit]").val(mid);
			$("input[name=quantity_edit]").val(qua);
			$("input[name=price_edit]").val(price);
	$(".medit").modal("show");
}
var listDocumentInDetails = function () {
	var $serie = $("[name=det-serie]");
	if ($serie.val().trim() != "") {
		$.getJSON('/restful/document/in/details/list/', {entry: $serie.val()+$("input[name=ruc]").val()}, function(response) {
				if (response.status) {
					var template = "<tr class=\"{{ id }} {{ addnow }} text-black\"><td>{{ item }}</td><td>{{ quantity }}</td><td>{{ price }}</td><td>{{ matunit }}</td><td>{{ materiales_id }}</td><td>{{ matname }} {{ matmet }}</td><td><button class=\"btn btn-link text-black btn-xs btn-edit-mat\" idmat=\"{{ materiales_id }}\" idid=\"{{ id }}\" value=\"{{ quantity }}\" data-price=\"{{ price }}\"><span class=\"glyphicon glyphicon-pencil\"></span></button></td><td><button class=\"btn btn-link text-black btn-xs btn-del-mat\" idmat=\"{{ materiales_id }}\" idid=\"{{ id }}\"><span class=\"glyphicon glyphicon-trash\"></span></button></td></tr>";
					var $tb = $(".table-detailsIn > tbody"),
							$mid = $(".id-mat").html();
					$tb.empty();
					for (var x in response.list){
						response.list[x].item = (parseInt(x) + 1)
						if ($mid == response.list[x].materiales_id) {
							response.list[x].addnow = "success"
						};
						$tb.append(Mustache.render(template, response.list[x]));
					}
				};
		});
		$(".table-detailsIn > tbody > .success").ScrollTo({
			duration: 600,
			callback: function () {
				setTimeout(function() {
					$(".well").ScrollTo({
						duration: 600
					});
					$("[name=description]").focus();
				}, 800);
			}
		});
	};
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
		data['entry'] = $("input[name=det-serie]").val()+""+$("input[name=ruc]").val();
		data['flag'] = true;
		data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
		// Transform price in Soles
		var currency = $("select[name=currency]").val();
		if (currency != "01"){
			if ($("input[name=currencycurrent]").is(":checked")) {
				var buy = parseFloat($("input[name=typeccu]").val().replace(",","."));
				data['price'] = (buy * parseFloat(data['price']));
			}else{
				var $exchange = $("input[name="+ currency +"]");
				if ($exchange.length > 0) {
					var buy = parseFloat($exchange.attr("data-purchase").replace(",","."));
					data['price'] = (buy * parseFloat(data['price']));
				}else{
					$().toastmessage("showErrorToast", "Currency not support.");
					return false;
				};
			};
			/*var $exchange = $("input[name="+ currency +"]");
			if ($exchange.length > 0) {
				var buy = parseFloat($exchange.attr("data-purchase").replace(",","."));
				data['price'] = (buy * parseFloat(data['price']));
			}else{
				$().toastmessage("showErrorToast", "Currency not support.");
				return false;
			};*/
		}
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
		$(".btn-bedside, .bedside").hide("slide","fast");
		$(".show-details").show('blind',600);
		listDocumentInDetails();
	};
}
var saveBedside = function (event) {
	event.preventDefault();
	var data = new Object(),
			pass = false;
	$(".panel-bedside").find('input, select').each(function () {
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
		data['entry_id'] = $("input[name=serie]").val()+""+$("input[name=supplier]").val();
		$.post('', data, function(response) {
			if (response.status) {
				$("input[name=det-serie]").val(response.serie);
				$("input[name=ruc]").val(response.ruc);
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
			console.log(response);
				if (response.status) {
					dataProvider = response;
					$("[name=reason]").val(response.reason);
				}else{
					$().toastmessage("showErrorToast", "Ups!, nuestro servidor se a quedado dormido, no se a conectado a la Sunat.");
				};
		});
	};
}
var annularDocument = function (event) {
	event.preventDefault();
	$().toastmessage("showToast", {
		text: 'Want Annular the document?',
		type: 'confirm',
		sticky: true,
		buttons: [{value:'Yes'}, {value:'No'}],
		success: function (result) {
			if (result == "Yes") {
				var data = {
					"type": 'entryannular',
					"entry": $("input[name=det-serie]").val() + $("input[name=ruc]").val(),
					"csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
				}
				$.post("/restful/document/entry/annular/", data, function (response) {
					if (response.status) {
						$().toastmessage("showNoticeToast", "Success document delete.");
						setTimeout(function() {
							location.href = "/add/document/In/";
						}, 2600);
					}else{
						$().toastmessage("showWarningToast", "Failure in the server." + response.raise);
					};
				});
			};
		}
	});
}