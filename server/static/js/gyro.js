/* eslint-env browser */
/* global io */
/* eslint-disable no-console */

/*
const GYRO_FREQUENCY = 1000;
const dt = 1 / GYRO_FREQUENCY;

function round2(num) {
	const padded = num.toFixed(2);
	// add + in front of number if it is positive or 0
	return num >= 0 ? `+${padded}` : padded;
}

function radiansToDegrees(rad) {
	return rad * (180 / Math.PI);
}

function sum(arr) {
	return arr.reduce((acc, curVal) => acc + curVal, 0);
}

const velocityXEl = document.getElementById("velocity-x");
const velocityYEl = document.getElementById("velocity-y");
const velocityZEl = document.getElementById("velocity-z");
const orientationXEl = document.getElementById("orientation-x");
const orientationYEl = document.getElementById("orientation-y");
const orientationZEl = document.getElementById("orientation-z");
*/

/* GYROSCOPE
const gyro = new Gyroscope({ frequency: GYRO_FREQUENCY });

const velocitiesX = [];
const velocitiesY = [];
const velocitiesZ = [];

let orientationX = 0;
let orientationY = 0;
let orientationZ = 0;

gyro.addEventListener("reading", () => {
	// velocitiesX.push(gyro.x);
	// velocitiesY.push(gyro.y);
	// velocitiesZ.push(gyro.z);

	// const avgX = velocitiesX.slice(-25);
	// const avgY = velocitiesY.slice(-25);
	// const avgZ = velocitiesZ.slice(-25);

	// velocityXEl.innerText = round2((sum(avgX) / avgX.length));
	// velocityYEl.innerText = round2((sum(avgY) / avgY.length));
	// velocityZEl.innerText = round2((sum(avgZ) / avgZ.length));

	orientationX += gyro.x * dt;
	orientationY += gyro.y * dt;
	orientationZ += gyro.z * dt;

	velocityXEl.innerText = round2(radiansToDegrees(gyro.x));
	velocityYEl.innerText = round2(radiansToDegrees(gyro.y));
	velocityZEl.innerText = round2(radiansToDegrees(gyro.z));

	orientationXEl.innerText = round2(radiansToDegrees(orientationX));
	orientationYEl.innerText = round2(radiansToDegrees(orientationY));
	orientationZEl.innerText = round2(radiansToDegrees(orientationZ));
});

gyro.start();
*/

/* DEVICE MOTION
const readIntervalEl = document.getElementById("read-interval");

const alphaEl = document.getElementById("orientation-alpha");
const betaEl = document.getElementById("orientation-beta");
const gammaEl = document.getElementById("orientation-gamma");

const alphaVals = [];
const betaVals = [];
const gammaVals = [];

window.addEventListener("devicemotion", (ev) => {
	const { interval } = ev; // in ms
	readIntervalEl.innerText = interval;

	const intervalSeconds = interval / 1000;

	// rotation axes: alpha: Z, beta: X, gamma: Y (unit: degree/s)
	const { alpha, beta, gamma } = ev.rotationRate;

	alphaVals.push(alpha * intervalSeconds);
	betaVals.push(beta * intervalSeconds);
	gammaVals.push(gamma * intervalSeconds);

	alphaEl.innerText = round2(sum(alphaVals));
	betaEl.innerText = round2(sum(betaVals));
	gammaEl.innerText = round2(sum(gammaVals));
});
*/
function radiansToDegrees(rad) {
	return rad * (180 / Math.PI);
}

const socket = io();
const EVNAME_CURRENT_ORIENTATION = "orientation";

const sensor = new AbsoluteOrientationSensor({ frequency: 60 });

sensor.addEventListener("reading", () => {
	// quaternion representing the orientation
	const q = sensor.quaternion;

	// Convert quaternion to Euler angles (roll, pitch, yaw)
	const roll = Math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] * q[1] + q[2] * q[2]));
	const pitch = Math.asin(2 * (q[0] * q[2] - q[3] * q[1]));
	const yaw = Math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3]));

	const rollDeg = radiansToDegrees(roll);
	const pitchDeg = radiansToDegrees(pitch);
	const yawDeg = radiansToDegrees(yaw);

	document.getElementById("roll").innerText = rollDeg.toFixed(2);
	document.getElementById("pitch").innerText = pitchDeg.toFixed(2);
	document.getElementById("yaw").innerText = yawDeg.toFixed(2);

	socket.emit(EVNAME_CURRENT_ORIENTATION, rollDeg, pitchDeg, yawDeg);
});

sensor.start();
