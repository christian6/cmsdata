$(document).ready(function() {
	$("[name=transfer]").datepicker({ showAnim: "slide", dateFormat: "yy-mm-dd", changeMonth: true, changeYear: true });
	//$(".bedside").hide();
	$(".btn-new").on("click", showBedside);
	$(".btn-supplier").click(function () {
		if ($("[name=supplier_id]").val() == "") {
			$().toastmessage("showWarningToast", "Warning, Ruc invalido, campo vacio.");
			return false;
		};
		if ($("[name=supplier_id]").val().length < 11) {
			$().toastmessage("showWarningToast", "Warning, Ruc formato invalido.");
			return false;
		};
		if ($("[name=supplier_id]").val().length == 11) {
			$.getJSON('/restful/search/sunat/ruc/', {ruc: $("[name=supplier_id]").val()}, function(response) {
					console.log(response);
					if (response.status) {
						$("[name=reason]").val(response.reason);
					}else{
						$().toastmessage("showErrorToast", "Ups!, nuestro servidor se a quedado dormido, no se a conectado a la Sunat.");
					};
			});
		};
	});
});

// functions

var showBedside = function (event) {
	event.preventDefault();
	$("input[name=new]").val('true');
	//$(".bedside").toggle('blind',600);
	$(this).find('.glyphicon').toggleClass('glyphicon-file').addClass('glyphicon-remove');
	$(this).find('.text').text($(".btn-new").find('.glyphicon-file').length == 1 ? "New Document" : "Cancelar");
	$('.btn-clean,.btn-save,.control').toggleClass('ctrl-disabled');
	$('.btn-clean,.btn-save,.control').attr('disabled', $('.ctrl-disabled').length > 0 ? true : false);
}