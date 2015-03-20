
function showPopoverFor(qsId, popoverTime)
{
	var d = document.getElementById(qsId);
	if (d.className.indexOf("qs-active") == -1)
	{
		d.className = d.className.replace("qs", "qs-active");
		window.setTimeout(function () {
			var d = document.getElementById(qsId);
			d.className = d.className.replace("qs-active", "qs");
		}, popoverTime);	
	}
}
