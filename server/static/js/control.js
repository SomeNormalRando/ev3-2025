/* eslint-disable function-paren-newline */
/* eslint-env browser */
/* global io */
/* eslint-disable no-console, camelcase */
import {
	calcFPS, EVNAME_RECEIVE_IMAGE, EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand,
	B64_PREFIX, imgEl, fpsNumberEl,
} from "./util-config.js";

const keyBoxForward = document.getElementById("key-box-forward");
const keyBoxLeft = document.getElementById("key-box-left");
const keyBoxBack = document.getElementById("key-box-back");
const keyBoxRight = document.getElementById("key-box-right");
const keyBoxPressedClass = "key-box-pressed";

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

const dict = [
	{
		buttonElement: keyBoxForward,
		command: MovementCommand.FORWARD_CONTINUOUSLY,
		keys: ["W", "w", "ArrowUp"],
	},
	{
		buttonElement: keyBoxLeft,
		command: MovementCommand.TURN_LEFT_CONTINUOUSLY,
		keys: ["A", "a", "ArrowLeft"],
	},
	{
		buttonElement: keyBoxBack,
		command: MovementCommand.BACKWARD_CONTINUOUSLY,
		keys: ["S", "s", "ArrowDown"],
	},
	{
		buttonElement: keyBoxRight,
		command: MovementCommand.TURN_RIGHT_CONTINUOUSLY,
		keys: ["D", "d", "ArrowRight"],
	},
];

for (const d of dict) {
	d.buttonElement.addEventListener("click", () => {
		if (d.buttonElement.classList.contains(keyBoxPressedClass)) {
			d.buttonElement.classList.remove(keyBoxPressedClass);
			socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.STOP, currentSpeed());
			return;
		}
		for (const d2 of dict) {
			d2.buttonElement.classList.remove(keyBoxPressedClass);
		}
		d.buttonElement.classList.add(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, d.command, currentSpeed());
	});
}

document.addEventListener("keyup", (ev) => {
	for (const d of dict) {
		if (d.keys.includes(ev.key)) {
			d.buttonElement.dispatchEvent(new Event("click"));
		}
	}
});

document.addEventListener("keydown", (ev) => {
	for (const d of dict) {
		if (d.keys.includes(ev.key) && !d.buttonElement.classList.contains(keyBoxPressedClass)) {
			d.buttonElement.dispatchEvent(new Event("click"));
		}
	}

	if (ev.key === "Shift") {
		speedSlider.value = currentSpeed() - 2;
		speedSlider.dispatchEvent(new Event("input"));
	}
	if (ev.key === " ") {
		// disable scrolling on space
		ev.preventDefault();
		speedSlider.value = currentSpeed() + 2;
		speedSlider.dispatchEvent(new Event("input"));
	}
});
