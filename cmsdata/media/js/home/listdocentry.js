$(document).ready(function() {
	$("[name=dstart],[name=dend]").datepicker({ dateFormat: "yy-mm-dd", showAnim: "slide" });
	$("[name=search]").on("change", changeSearch);
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