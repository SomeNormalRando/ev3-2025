/* eslint-env browser */
/* global io */
/* eslint-disable no-console */

// const socket = io();

function round2(num) {
	const padded = num.toFixed(2);
	// add + in front of number if it is positive or 0
	return num >= 0 ? `+${padded}` : padded;
}

const velocityXEl = document.getElementById("velocity-x");
const velocityYEl = document.getElementById("velocity-y");
const velocityZEl = document.getElementById("velocity-z");

const gyro = new Gyroscope({ frequency: 10 });

gyro.addEventListener("reading", () => {
	velocityXEl.innerText = round2(gyro.x);
	velocityYEl.innerText = round2(gyro.y);
	velocityZEl.innerText = round2(gyro.z);
});

gyro.start();

// window.addEventListener("devicemotion", (ev) => {
// 	velocityXEl.innerText = round2(gyro.x * 100);
// 	velocityYEl.innerText = round2(gyro.y * 100);
// 	velocityZEl.innerText = round2(gyro.z * 100);
// });
