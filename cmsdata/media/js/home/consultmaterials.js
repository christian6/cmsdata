$(document).ready(function() {
	$("input[name=search]").on("change",changeSearch);
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
	if (code != "") {
		var data = new Object();
		data['code'] = code;
		data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
		$.post('/restful/search/code/', data, function(response) {
			if (response.status) {
				var template = "
				<div class=\"col-md-4\">
					<dl class=\"dl-horizontal\">
						<dt>Code Materials</dt>
						<dd>{{ materials_id }}</dd>
						<dt>Meter </dt>
						<dd></dd>
					</dl>
				</div>
				";
			}else{
				$().Toastmessage("showWarningToast","Not could recover details materials.");
			};
		}, "json");
	};
}