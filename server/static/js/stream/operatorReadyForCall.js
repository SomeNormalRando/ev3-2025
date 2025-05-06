/* eslint-env browser */
/* global io */

import {
	EVNAME_OFFER_FROM_ROBOT, EVNAME_ANSWER_FROM_ROBOT, EVNAME_CANDIDATE_FROM_ROBOT,
	EVNAME_ANSWER_FROM_OPERATOR, EVNAME_CANDIDATE_FROM_OPERATOR,
} from "../util-config.js";


const socket = io();

// this will be used in control.js
export default function operatorReadyForCall(videoFromRobotDisplayElement) {
	let pc;
	let localStream;

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
			socket.emit(EVNAME_CANDIDATE_FROM_OPERATOR, message);
		};

		pc.ontrack = (e) => {
			[videoFromRobotDisplayElement.srcObject] = e.streams;
		};

		localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));
	}

	async function handleOffer(offer) {
		if (pc) {
			console.error("existing PeerConnection");
			return;
		}
		await createPeerConnection();
		await pc.setRemoteDescription(offer);

		const answer = await pc.createAnswer();
		await pc.setLocalDescription(answer);
		console.log("emit: answer", answer);
		socket.emit(EVNAME_ANSWER_FROM_OPERATOR, { type: "answer", sdp: answer.sdp });
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
	navigator.mediaDevices.getUserMedia({ video: false, audio: true })
		.then((stream) => {
			localStream = stream;
			// localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));
			// remoteVideo.srcObject = stream;
		})
		.catch((err) => {
			console.error("getUserMedia() error:", err);
		});

	// logging for debug purposes
	socket.onAny((event, ...args) => {
		if (event === "data-url") return;
		console.log("receive:", event, args);
	});

	socket.on(EVNAME_OFFER_FROM_ROBOT, (offer) => handleOffer(offer));
	socket.on(EVNAME_ANSWER_FROM_ROBOT, (answer) => handleAnswer(answer));
	socket.on(EVNAME_CANDIDATE_FROM_ROBOT, (candidate) => handleCandidate(candidate));
}
