// Cursor
const myCircle = document.getElementById("circle");
const ico = document.getElementById("ico");
const cursorSize = myCircle.offsetWidth;

// get the dimensions and position of the ico element
const rect = ico.getBoundingClientRect();

// calculate the center of the ico element
let mousePos = {
	x: rect.left + (rect.width - cursorSize) / 2,
	y: rect.top + (rect.height - cursorSize) / 2,
};

const myMouse = {
	follow: function (event) {
		const width = document.documentElement.clientWidth - cursorSize;
		const height = document.documentElement.scrollHeight - cursorSize;

		let x = event.pageX - cursorSize / 2;
		let y = event.pageY - cursorSize / 2;

		x = x < 0 ? 0 : x > width ? width : x;
		y = y < 0 ? 0 : y > height ? height : y;

		mousePos.x = x;
		mousePos.y = y;
	},
};

function updateCirclePosition() {
	myCircle.style.left = mousePos.x + "px";
	myCircle.style.top = mousePos.y + "px";

	requestAnimationFrame(updateCirclePosition);
}

document.onmousemove = myMouse.follow;
updateCirclePosition();

// Get all <div> elements with the class "scaled"
const scaledDivs = document.getElementsByClassName("scaled");
for (let div of scaledDivs) {
	// Scale myCircle to 200% when mouse is over <div> tag with the class "scaled"
	div.addEventListener("mouseover", function () {
		myCircle.style.transform = "scale(2)";
	});

	// Remove transform when mouse leaves the <div> tag
	div.addEventListener("mouseout", function () {
		myCircle.style.transform = "scale(1)";
	});
}

// Get all <a> elements within the parent class of 'work'
const workLinks = document.querySelectorAll(".work a");
for (let link of workLinks) {
	// Scale myCircle to 200% when mouse is over <a> tag within the parent class of 'work'
	link.addEventListener("mouseover", function () {
		myCircle.style.transform = "scale(2)";
	});

	// Remove transform when mouse leaves the <a> tag
	link.addEventListener("mouseout", function () {
		myCircle.style.transform = "scale(1)";
	});
}

// CSS Styles for mobile
function isElementCentered(el) {
	var rect = el.getBoundingClientRect();
	var viewHeight = Math.max(
		document.documentElement.clientHeight,
		window.innerHeight
	);
	var quarterHeight = viewHeight / 4;
	return rect.top > quarterHeight && rect.bottom < quarterHeight * 3;
}

function adjustStyles() {
	let workItems = document.querySelectorAll(".container .work a .work-item");
	let wireframeSiteItems = document.querySelectorAll(
		".container .work a .work-item > .wireframe-site"
	);
	let colorSiteItems = document.querySelectorAll(
		".container .work a .work-item > .color-site"
	);

	if (window.innerWidth <= 459) {
		for (let i = 0; i < workItems.length; i++) {
			if (isElementCentered(workItems[i])) {
				wireframeSiteItems[i].style.opacity = 0;
				colorSiteItems[i].style.opacity = 1;
				colorSiteItems[i].style.filter = "none";
			} else {
				wireframeSiteItems[i].style.opacity = "";
				colorSiteItems[i].style.opacity = "";
				colorSiteItems[i].style.filter = "";
			}
		}
	} else {
		for (let i = 0; i < workItems.length; i++) {
			wireframeSiteItems[i].style.opacity = "";
			colorSiteItems[i].style.opacity = "";
			colorSiteItems[i].style.filter = "";
		}
	}
}

window.addEventListener("resize", adjustStyles);
window.addEventListener("scroll", adjustStyles);
window.addEventListener("DOMContentLoaded", adjustStyles);
