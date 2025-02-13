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

const socket = io();

socket.on(EVNAME_RECEIVE_IMAGE, ({ b64ImageData }) => {
	imgEl.src = `${B64_PREFIX}${b64ImageData}`;

	fpsNumberEl.innerText = calcFPS();
});

function removePressedClassAndSendStopCommand(el) {
	if (el.classList.contains(keyBoxPressedClass)) el.classList.remove(keyBoxPressedClass);
	socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.STOP);
}

const checkForwardKey = (ev) => ev.key.toLowerCase() === "w" || ev.key === "ArrowUp";
const checkLeftKey = (ev) => ev.key.toLowerCase() === "a" || ev.key === "ArrowLeft";
const checkBackKey = (ev) => ev.key.toLowerCase() === "s" || ev.key === "ArrowDown";
const checkRightKey = (ev) => ev.key.toLowerCase() === "d" || ev.key === "ArrowRight";

document.addEventListener("keyup", (ev) => {
	if (checkForwardKey(ev)) removePressedClassAndSendStopCommand(keyBoxForward);
	if (checkLeftKey(ev)) removePressedClassAndSendStopCommand(keyBoxLeft);
	if (checkBackKey(ev)) removePressedClassAndSendStopCommand(keyBoxBack);
	if (checkRightKey(ev)) removePressedClassAndSendStopCommand(keyBoxRight);
});

document.addEventListener("keydown", (ev) => {
	if (checkForwardKey(ev)) {
		keyBoxForward.classList.add(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.FORWARD_CONTINUOUSLY);
	}
	if (checkLeftKey(ev)) {
		keyBoxLeft.classList.add(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.TURN_LEFT_CONTINUOUSLY);
	}
	if (checkRightKey(ev)) {
		keyBoxRight.classList.add(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.TURN_RIGHT_CONTINUOUSLY);
	}
	if (checkBackKey(ev)) {
		keyBoxBack.classList.add(keyBoxPressedClass);
		socket.emit(EVNAME_SEND_MOVEMENT_COMMAND, MovementCommand.BACKWARD_CONTINUOUSLY);
	}
});
