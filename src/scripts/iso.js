// Icosahedron
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, 160 / 160, 0.1, 1000);
camera.position.z = 1.7;

var renderer = new THREE.WebGLRenderer({ alpha: true });
var container = document.getElementById("ico");
renderer.setSize(160, 160);
renderer.domElement.style.position = "absolute";
renderer.domElement.style.top = "0";
renderer.domElement.style.left = "0";
container.appendChild(renderer.domElement);

var icosahedronGeometry = new THREE.IcosahedronGeometry(1);
var wireframeMaterial = new THREE.MeshBasicMaterial({
	color: 0xffffff,
	wireframe: true,
});
var icosahedron = new THREE.Mesh(icosahedronGeometry, wireframeMaterial);
scene.add(icosahedron);

// Convert degrees to radians because Three.js uses radians for rotation
// var degreesToRadians = (degrees) => (degrees * Math.PI) / 180;

// Set initial rotation
// icosahedron.rotation.x = degreesToRadians(149);
// icosahedron.rotation.y = degreesToRadians(0);

var mouse = new THREE.Vector2();
var target = new THREE.Vector2();
var windowHalf = new THREE.Vector2(
	window.innerWidth / 2,
	window.innerHeight / 2
);

function onMouseOrTouchMove(event) {
	if (event.type == "touchmove") {
		mouse.x = event.touches[0].clientX - windowHalf.x;
		mouse.y = event.touches[0].clientY - windowHalf.y;
	} else {
		mouse.x = event.clientX - windowHalf.x;
		mouse.y = event.clientY - windowHalf.y;
	}
}

window.addEventListener("mousemove", onMouseOrTouchMove, false);
window.addEventListener("touchmove", onMouseOrTouchMove, false);

function animate() {
	requestAnimationFrame(animate);
	target.x = (1 - mouse.x) * 0.003;
	target.y = (1 - mouse.y) * 0.003;

	icosahedron.rotation.x += 0.05 * (target.y - icosahedron.rotation.x);
	icosahedron.rotation.y += 0.05 * (target.x - icosahedron.rotation.y);

	renderer.render(scene, camera);
}

animate();
