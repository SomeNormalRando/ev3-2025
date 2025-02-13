/* eslint-env browser */
/* global io */
/* eslint-disable no-console, camelcase */

import {
	HSVtoRGB, calcFPS,
	EVNAME_RECEIVE_IMAGE, EVNAME_RECEIVE_DEFAULT_HSV_COLOURS, EVNAME_SEND_HSV_COLOURS_UPDATE,
	B64_PREFIX, imgEl, fpsNumberEl, redDetectionsNumberEl, blueDetectionsNumberEl,
} from "./util-config.js";

const socket = io();

const coloursObj = {
	red1lower: {
		channels: {
			h: { elID: "r1-l-h", curVal: -1, inputEl: null },
			s: { elID: "r1-l-s", curVal: -1, inputEl: null },
			v: { elID: "r1-l-v", curVal: -1, inputEl: null },
		},
		colBox: { elID: "colbox-red1lower", el: null },
	},
	red1upper: {
		channels: {
			h: { elID: "r1-u-h", curVal: -1, inputEl: null },
			s: { elID: "r1-u-s", curVal: -1, inputEl: null },
			v: { elID: "r1-u-v", curVal: -1, inputEl: null },
		},
		colBox: { elID: "colbox-red1upper", el: null },
	},
	red2lower: {
		channels: {
			h: { elID: "r2-l-h", curVal: -1, inputEl: null },
			s: { elID: "r2-l-s", curVal: -1, inputEl: null },
			v: { elID: "r2-l-v", curVal: -1, inputEl: null },
		},
		colBox: { elID: "colbox-red2lower", el: null },
	},
	red2upper: {
		channels: {
			h: { elID: "r2-u-h", curVal: -1, inputEl: null },
			s: { elID: "r2-u-s", curVal: -1, inputEl: null },
			v: { elID: "r2-u-v", curVal: -1, inputEl: null },
		},
		colBox: { elID: "colbox-red2upper", el: null },
	},
	bluelower: {
		channels: {
			h: { elID: "b-l-h", curVal: -1, inputEl: null },
			s: { elID: "b-l-s", curVal: -1, inputEl: null },
			v: { elID: "b-l-v", curVal: -1, inputEl: null },
		},
		colBox: { elID: "colbox-bluelower", el: null },
	},
	blueupper: {
		channels: {
			h: { elID: "b-u-h", curVal: -1, inputEl: null },
			s: { elID: "b-u-s", curVal: -1, inputEl: null },
			v: { elID: "b-u-v", curVal: -1, inputEl: null },
		},
		colBox: { elID: "colbox-blueupper", el: null },
	},
};

for (const [colName, col] of Object.entries(coloursObj)) {
	const colBoxElement = document.getElementById(col.colBox.elID);
	col.colBox.el = colBoxElement;

	for (const colChannel of Object.values(col.channels)) {
		const inputElement = document.getElementById(colChannel.elID);

		inputElement.addEventListener("input", (ev) => {
			// ev.target.value is a string
			colChannel.curVal = parseInt(ev.target.value, 10);

			const colHSV = [col.channels.h.curVal, col.channels.s.curVal, col.channels.v.curVal];

			// CSS doesn't support direct HSV representation -- only RGB and HSL
			const colRGB = HSVtoRGB(...colHSV);
			colBoxElement.style.backgroundColor = `rgb(${colRGB[0]}, ${colRGB[1]}, ${colRGB[2]})`;

			// send new HSV colours to server
			socket.emit(EVNAME_SEND_HSV_COLOURS_UPDATE, colName, colHSV);
		});

		// increase / decrease <input> values using the mouse scroll wheel
		inputElement.addEventListener("wheel", (ev) => {
			ev.preventDefault();
			const currentVal = parseInt(ev.target.value, 10);
			if (ev.deltaY < 0) {
				if ((currentVal + 2) > ev.target.max) return;
				ev.target.value = currentVal + 2;
			} else {
				if ((currentVal - 2) < ev.target.min) return;
				ev.target.value = currentVal - 2;
			}

			const inputEvent = new Event("input");
			ev.target.dispatchEvent(inputEvent);
		});

		colChannel.inputEl = inputElement;
	}
}

socket.on(EVNAME_RECEIVE_DEFAULT_HSV_COLOURS, (receivedColours) => {
	console.log("received default HSV colours from server:", receivedColours);

	const {
		RED1_LOWER, RED1_UPPER, RED2_LOWER, RED2_UPPER, BLUE_LOWER, BLUE_UPPER,
	} = receivedColours;

	const {
		red1lower: { channels: red1lowerC },
		red1upper: { channels: red1upperC },
		red2upper: { channels: red2upperC },
		red2lower: { channels: red2lowerC },
		blueupper: { channels: blueupperC },
		bluelower: { channels: bluelowerC },
	} = coloursObj;
	[red1lowerC.h.curVal, red1lowerC.s.curVal, red1lowerC.v.curVal] = RED1_LOWER;

	[
		red1lowerC.h.inputEl.value, red1lowerC.s.inputEl.value, red1lowerC.v.inputEl.value,
	] = RED1_LOWER;
	[red1upperC.h.curVal, red1upperC.s.curVal, red1upperC.v.curVal] = RED1_UPPER;
	[
		red1upperC.h.inputEl.value, red1upperC.s.inputEl.value, red1upperC.v.inputEl.value,
	] = RED1_UPPER;

	[red2lowerC.h.curVal, red2lowerC.s.curVal, red2lowerC.v.curVal] = RED2_LOWER;
	[
		red2lowerC.h.inputEl.value, red2lowerC.s.inputEl.value, red2lowerC.v.inputEl.value,
	] = RED2_LOWER;
	[red2upperC.h.curVal, red2upperC.s.curVal, red2upperC.v.curVal] = RED2_UPPER;
	[
		red2upperC.h.inputEl.value, red2upperC.s.inputEl.value, red2upperC.v.inputEl.value,
	] = RED2_UPPER;

	[bluelowerC.h.curVal, bluelowerC.s.curVal, bluelowerC.v.curVal] = BLUE_LOWER;
	[
		bluelowerC.h.inputEl.value, bluelowerC.s.inputEl.value, bluelowerC.v.inputEl.value,
	] = BLUE_LOWER;
	[blueupperC.h.curVal, blueupperC.s.curVal, blueupperC.v.curVal] = BLUE_UPPER;
	[
		blueupperC.h.inputEl.value, blueupperC.s.inputEl.value, blueupperC.v.inputEl.value,
	] = BLUE_UPPER;

	// dispatch `input` event to every <input> to update colour boxes
	const event = new Event("input");
	for (const col of Object.values(coloursObj)) {
		for (const colChannel of Object.values(col.channels)) {
			colChannel.inputEl.dispatchEvent(event);
		}
	}
});


socket.on(EVNAME_RECEIVE_IMAGE, ({ b64ImageData, redDetectedObjects, blueDetectedObjects }) => {
	imgEl.src = `${B64_PREFIX}${b64ImageData}`;

	redDetectionsNumberEl.innerText = redDetectedObjects.length;
	blueDetectionsNumberEl.innerText = blueDetectedObjects.length;

	fpsNumberEl.innerText = calcFPS();
});
