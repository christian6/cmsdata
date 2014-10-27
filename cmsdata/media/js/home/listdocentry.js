$(document).ready(function() {
	$("[name=dstart],[name=dend]").datepicker({ dateFormat: "yy-mm-dd", showAnim: "slide" });
	$("[name=search]").on("change", changeSearch);
	$(".btn-change-status").on("click", changeStatus);
});

// functions

var changeSearch = function (event) {
	event.preventDefault();
	$("[name=search]").each(function () {
		if (this.checked) {
			$("."+this.value).attr("disabled", false);
		}else{
			$("."+this.value).attr("disabled", true);
		}
	});
}

var changeStatus = function (event) {
	var btn = this;
	data = new Object();
	data.csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
	data.pk = this.value;
	data.editDocument = true;
	data.document = btn.getAttribute("data-type");
	console.log(data);
	$.post("/restful/document/change/status/edit/", data, function (response) {
		console.log(response);
		if (response.status) {
			if (data.document == "ENTRY"){
				location.href="/add/document/In/?new=0&details=1&serie="+btn.getAttribute("data-serie")+"&ruc="+btn.getAttribute("data-ruc")+"";
			}else if(data.document == "OUTPUT"){
				location.href="/add/document/output/?new=0&details=1&serie="+btn.getAttribute("data-serie")+"&ruc="+btn.getAttribute("data-ruc")+"";
			}
		}else{
			$().toastmessage("showWarningToast", "No se puede editar este documento.");
		};
	}, "json");
}