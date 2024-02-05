// Check for Safari, the new IE
window.onload = function () {
	function isSafari() {
		return (
			/Safari/.test(navigator.userAgent) &&
			!(
				/Chrome/.test(navigator.userAgent) ||
				/Chromium/.test(navigator.userAgent)
			)
		);
	}

	if (isSafari()) {
		let marqueeTag = document.querySelector("#profile marquee");
		let marqueeDiv = document.querySelector("#profile .marquee");

		marqueeTag.style.display = "none";
		marqueeDiv.style.display = "block";
	}
};
