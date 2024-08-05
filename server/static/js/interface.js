/* eslint-env browser */
/* global io */
/* eslint-disable no-console */

const SOCKETIO_EVENT_NAME = "data-url";
const B64_PREFIX = "data:image/jpeg;base64,";
const UPDATE_FPS_EVERY_MS = 250;

const socket = io();

const imgEl = document.getElementById("img-el");
const fpsNumberDisplay = document.getElementById("fps-number-display");
const redDetectionsNumberDisplay = document.getElementById("red-detections-number-display");
// const blueDetectionsNumberDisplay = document.getElementById("blue-detections-number-display");

let last = performance.now();
let numFramesSinceLast = 0;

socket.on(SOCKETIO_EVENT_NAME, ({ b64ImageData, redDetectedObjects }) => {
	imgEl.src = `${B64_PREFIX}${b64ImageData}`;

	// console.log(detectedObjects)
	redDetectionsNumberDisplay.innerText = redDetectedObjects.length;
	// blueDetectionsNumberDisplay.innerText = blueDetectedObjects.length;

	const now = performance.now();
	if ((now - last) <= UPDATE_FPS_EVERY_MS) {
		numFramesSinceLast += 1;
		return;
	}

	const timeDiff = (now - last) / 1000;
	const fpsUnrounded = 1 / (timeDiff / numFramesSinceLast);

	fpsNumberDisplay.innerText = Math.round(fpsUnrounded * 100) / 100;
	last = now;
	numFramesSinceLast = 0;
});
