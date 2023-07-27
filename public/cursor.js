// Cursor
const myCircle = document.getElementById("circle");
const ico = document.getElementById("ico");
const cursorSize = myCircle.offsetWidth;

let mousePos = { x: 0, y: 0 };

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

	centerToIco: function () {
		const rect = ico.getBoundingClientRect();

		mousePos.x = rect.left + (rect.width - cursorSize) / 2;
		mousePos.y = rect.top + (rect.height - cursorSize) / 2;
	},
};

function updateCirclePosition() {
	myCircle.style.left = mousePos.x + "px";
	myCircle.style.top = mousePos.y + "px";

	requestAnimationFrame(updateCirclePosition);
}

document.onmousemove = myMouse.follow;
document.onmouseleave = myMouse.centerToIco;
updateCirclePosition();
