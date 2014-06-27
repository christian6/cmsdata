$(document).ready(function() {
	init();
	$("input[name=type]").on("change", changeRadio);
});
// funtions
var init = function () {
	$(".bs-callout").find('input[type=text],select').each(function() {
		$(this).attr('disabled', true);
	});
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
			}else if(item.value == "2"){
				if (this.name == "period" || this.name == "month") {
					this.disabled = false;
				};
			}else if(item.value == "3"){
				if (this.name == "period" || this.name == "month" || this.name == "code" || this.name == "name") {
					this.disabled = false;
				};
			}else if(item.value == "4"){
				if (this.name == "period" || this.name == "code" || this.name == "name") {
					this.disabled = false;
				};
			};
		});
	};
}