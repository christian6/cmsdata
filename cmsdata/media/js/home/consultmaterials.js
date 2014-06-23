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