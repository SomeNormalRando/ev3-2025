/* eslint-env browser */

// config
export const speedAdjustStep = 2;

export const EVNAME_RECEIVE_IMAGE = "data-url";
export const EVNAME_RECEIVE_DEFAULT_HSV_COLOURS = "default-hsv-colours";
export const EVNAME_SEND_HSV_COLOURS_UPDATE = "hsv-colours-update";
export const EVNAME_SEND_MOVEMENT_COMMAND = "movement-command";
export const EVNAME_SEND_FUNNEL_COMMAND = "funnel-command";
export const EVNAME_SEND_AUTO_MODE_COMMAND = "auto-mode-command";
export const B64_PREFIX = "data:image/jpeg;base64,";

export const EVNAME_READY_FROM_ROBOT = "WEBRTC-ready-from-robot";
export const EVNAME_BYE_FROM_ROBOT = "WEBRTC-bye-from-robot";
export const EVNAME_READY_FROM_OPERATOR = "WEBRTC-ready-from-operator";
export const EVNAME_BYE_FROM_OPERATOR = "WEBRTC-bye-from-operator";

export const EVNAME_OFFER_FROM_ROBOT = "WEBRTC-offer-from-robot";
export const EVNAME_ANSWER_FROM_ROBOT = "WEBRTC-answer-from-robot";
export const EVNAME_CANDIDATE_FROM_ROBOT = "WEBRTC-candidate-from-robot";

export const EVNAME_OFFER_FROM_OPERATOR = "WEBRTC-offer-from-operator";
export const EVNAME_ANSWER_FROM_OPERATOR = "WEBRTC-answer-from-operator";
export const EVNAME_CANDIDATE_FROM_OPERATOR = "WEBRTC-candidate-from-operator";

export const MovementCommand = {
	STOP: -2,
	FORWARD_CONTINUOUSLY: 0,
	BACKWARD_CONTINUOUSLY: 2,
	TURN_LEFT_CONTINUOUSLY: 3,
	TURN_RIGHT_CONTINUOUSLY: 4,
	TURN_A_LITTLE_LEFT: -1,
	TURN_A_LITTLE_RIGHT: 1,
};

export const imgEl = document.getElementById("img-el");
export const fpsNumberEl = document.getElementById("fps-number");
export const redDetectionsNumberEl = document.getElementById("red-detections-number");
export const blueDetectionsNumberEl = document.getElementById("blue-detections-number");

const UPDATE_FPS_EVERY_MS = 250;

// from https://gist.github.com/mjackson/5311256
export function HSVtoRGB(h180, s255, v255) {
	// HSV range in cv2: H [0, 179], S [0, 255], [0, 255]
	// scale H, S and V values to a range of [0, 1]
	const h = h180 / 180;
	const s = s255 / 255;
	const v = v255 / 255;

	let r;
	let g;
	let b;

	const i = Math.floor(h * 6);
	const f = h * 6 - i;
	const p = v * (1 - s);
	const q = v * (1 - f * s);
	const t = v * (1 - (1 - f) * s);

	switch (i % 6) {
	case 0: r = v; g = t; b = p; break;
	case 1: r = q; g = v; b = p; break;
	case 2: r = p; g = v; b = t; break;
	case 3: r = p; g = q; b = v; break;
	case 4: r = t; g = p; b = v; break;
	case 5: r = v; g = p; b = q; break;
	default:
	}

	return [r * 255, g * 255, b * 255];
}

let last = performance.now();
let numFramesSinceLast = 0;
let lastFPS = 0;
export function calcFPS() {
	const now = performance.now();

	// don't update FPS (return old FPS value) if elapsed time has not exceeded UPDATE_FPS_EVERY_MS
	if ((now - last) <= UPDATE_FPS_EVERY_MS) {
		numFramesSinceLast += 1;
		return lastFPS;
	}

	const timeDiff = (now - last) / 1000;
	const fpsUnrounded = 1 / (timeDiff / numFramesSinceLast);

	last = now;
	numFramesSinceLast = 0;

	lastFPS = Math.round(fpsUnrounded * 100) / 100;
	return lastFPS;
}
