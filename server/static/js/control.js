/* eslint-disable function-paren-newline */
/* eslint-env browser */
/* global io */
/* eslint-disable no-console, camelcase */
import {
	calcFPS, EVNAME_RECEIVE_IMAGE, EVNAME_SEND_MOVEMENT_COMMAND, EVNAME_SEND_FUNNEL_COMMAND,
	EVNAME_SEND_AUTO_MODE_COMMAND, MovementCommand, B64_PREFIX, speedAdjustStep, imgEl, fpsNumberEl,
} from "./util-config.js";

const keyBoxPressedClass = "key-box-pressed";

const keyBoxAutoMode = document.getElementById("key-box-auto-mode");

const speedSlider = document.getElementById("speed-slider");
const speedDisplay = document.getElementById("speed-display");

const socket = io();

socket.on(EVNAME_RECEIVE_IMAGE, ({ b64ImageData }) => {
	imgEl.src = `${B64_PREFIX}${b64ImageData}`;

	fpsNumberEl.innerText = calcFPS();
});

speedSlider.min = 1;
speedSlider.max = 100;
speedSlider.value = 50;
speedDisplay.innerText = speedSlider.value;

speedSlider.addEventListener("input", () => {
	speedDisplay.innerText = speedSlider.value;
});

const currentSpeed = () => parseInt(speedSlider.value, 10);

const movementMap = [
	{
		buttonElementID: "key-box-forward",
		buttonElement: null,
		command: MovementCommand.FORWARD_CONTINUOUSLY,
		keys: ["W", "w", "ArrowUp"],
	},
	{
		buttonElementID: "key-box-left",
		buttonElement: null,
		command: MovementCommand.TURN_LEFT_CONTINUOUSLY,
		keys: ["A", "a", "ArrowLeft"],
	},
	{
		buttonElementID: "key-box-back",
		buttonElement: null,
		command: MovementCommand.BACKWARD_CONTINUOUSLY,
		keys: ["S", "s", "ArrowDown"],
	},
	{
		buttonElementID: "key-box-right",
		buttonElement: null,
		command: MovementCommand.TURN_RIGHT_CONTINUOUSLY,
		keys: ["D", "d", "ArrowRight"],
	},
];

// -1: close, 1: open, 0: stop
const funnelMap = [
	{
		buttonElementID: "key-box-close-funnel",
		buttonElement: null,
		command: -1,
		keys: ["Shift"],
	},
	{
		buttonElementID: "key-box-open-funnel",
		buttonElement: null,
		command: 1,
		keys: [" "],
	},
];

for (const d of movementMap) {
	d.buttonElement = document.getElementById(d.buttonElementID);

	d.buttonElement.addEventListener("click", () => {
		if (d.buttonElement.classList.contains(keyBoxPressedClass)) {
			d.buttonElement.classList.remove(keyBoxPressedClass);
			socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.STOP, currentSpeed());
			return;
		}

		for (const d2 of movementMap) {
			d2.buttonElement.classList.remove(keyBoxPressedClass);
		}

		d.buttonElement.classList.add(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, d.command, currentSpeed());
	});
}

for (const d of funnelMap) {
	d.buttonElement = document.getElementById(d.buttonElementID);

	d.buttonElement.addEventListener("click", () => {
		if (d.buttonElement.classList.contains(keyBoxPressedClass)) {
			d.buttonElement.classList.remove(keyBoxPressedClass);
			socket.emit(EVNAME_SEND_FUNNEL_COMMAND, 0);
			return;
		}

		for (const d2 of funnelMap) {
			d2.buttonElement.classList.remove(keyBoxPressedClass);
		}

		d.buttonElement.classList.add(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_FUNNEL_COMMAND, d.command);
	});
}

document.addEventListener("keyup", (ev) => {
	for (const d of movementMap) {
		if (d.keys.includes(ev.key)) {
			d.buttonElement.classList.remove(keyBoxPressedClass);
			socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.STOP, currentSpeed());
		}
	}
	for (const d of funnelMap) {
		if (d.keys.includes(ev.key)) {
			d.buttonElement.classList.remove(keyBoxPressedClass);
			socket.emit(EVNAME_SEND_FUNNEL_COMMAND, 0);
		}
	}
});

document.addEventListener("keydown", (ev) => {
	for (const d of movementMap) {
		if (d.keys.includes(ev.key) && !d.buttonElement.classList.contains(keyBoxPressedClass)) {
			d.buttonElement.dispatchEvent(new Event("click"));
		}
	}

	for (const d of funnelMap) {
		if (d.keys.includes(ev.key) && !d.buttonElement.classList.contains(keyBoxPressedClass)) {
			ev.preventDefault();
			d.buttonElement.dispatchEvent(new Event("click"));
		}
	}

	if (ev.key.toLowerCase() === "q") {
		speedSlider.value = currentSpeed() - speedAdjustStep;
		speedSlider.dispatchEvent(new Event("input"));
	} else if (ev.key.toLowerCase() === "e") {
		speedSlider.value = currentSpeed() + speedAdjustStep;
		speedSlider.dispatchEvent(new Event("input"));
	}

	if (ev.key === "Enter") {
		keyBoxAutoMode.dispatchEvent(new Event("click"));
	}
});

keyBoxAutoMode.addEventListener("click", () => {
	if (keyBoxAutoMode.classList.contains(keyBoxPressedClass)) {
		keyBoxAutoMode.classList.remove(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_AUTO_MODE_COMMAND, 0);
		return;
	}

	keyBoxAutoMode.classList.add(keyBoxPressedClass);
	socket.emit(EVNAME_SEND_AUTO_MODE_COMMAND, 1);
});
