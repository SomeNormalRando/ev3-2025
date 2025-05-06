/* eslint-env browser */
/* global io */
/* eslint-disable no-use-before-define */

import {
	EVNAME_BYE_FROM_ROBOT,
	EVNAME_OFFER_FROM_ROBOT, EVNAME_ANSWER_FROM_ROBOT, EVNAME_CANDIDATE_FROM_ROBOT,
	EVNAME_OFFER_FROM_OPERATOR, EVNAME_ANSWER_FROM_OPERATOR, EVNAME_CANDIDATE_FROM_OPERATOR,
} from "../util-config.js";

const startButton = document.getElementById("startButton");

const localVideo = document.getElementById("local-video");
const remoteVideo = document.getElementById("remote-video");

let pc;
let localStream;

const socket = io();

// logging for debug purposes
socket.onAny((event, ...args) => {
	if (event === "data-url") return;
	console.log("receive:", event, args);
});
socket.on(EVNAME_OFFER_FROM_OPERATOR, (offer) => handleOffer(offer));
socket.on(EVNAME_ANSWER_FROM_OPERATOR, (answer) => handleAnswer(answer));
socket.on(EVNAME_CANDIDATE_FROM_OPERATOR, (candidate) => handleCandidate(candidate));

startButton.addEventListener("click", async () => {
	localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
	localVideo.srcObject = localStream;

	startButton.disabled = true;

	console.log("makeCall()");
	makeCall();
});

function createPeerConnection() {
	pc = new RTCPeerConnection();
	pc.onicecandidate = (e) => {
		const message = {
			candidate: null,
		};
		if (e.candidate) {
			message.candidate = e.candidate.candidate;
			message.sdpMid = e.candidate.sdpMid;
			message.sdpMLineIndex = e.candidate.sdpMLineIndex;
		}
		console.log("emit: candidate", message);
		socket.emit(EVNAME_CANDIDATE_FROM_ROBOT, message);
	};
	pc.ontrack = (e) => {
		[remoteVideo.srcObject] = e.streams;
	};
	localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));
}

async function makeCall() {
	createPeerConnection();

	const offer = await pc.createOffer();
	await pc.setLocalDescription(offer);

	console.log("emit: offer", offer);
	socket.emit(EVNAME_OFFER_FROM_ROBOT, { type: "offer", sdp: offer.sdp });
}

async function handleOffer(offer) {
	if (pc) {
		console.error("existing PeerConnection");
		return;
	}
	await createPeerConnection();
	await pc.setRemoteDescription(offer);

	const answer = await pc.createAnswer();
	console.log("emit: answer", answer);
	socket.emit(EVNAME_ANSWER_FROM_ROBOT, { type: "answer", sdp: answer.sdp });
	await pc.setLocalDescription(answer);
}

async function handleAnswer(answer) {
	if (!pc) {
		console.error("no PeerConnection");
		return;
	}
	await pc.setRemoteDescription(answer);
}

async function handleCandidate(candidate) {
	if (!pc) {
		console.error("no PeerConnection");
		return;
	}
	if (!candidate.candidate) {
		// await pc.addIceCandidate(null);
	} else {
		await pc.addIceCandidate(candidate);
	}
}
