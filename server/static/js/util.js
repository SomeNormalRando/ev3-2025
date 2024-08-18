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
