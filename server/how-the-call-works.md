## How to start the call
1. Open the operator interface page
2. Press 'START' on the operator interface page
3. Open the robot interface page (the page will automatically initiate the call to the operator interfac page)

## WebRTC call timeline
*emit means send to the other page via socket.io
| operator interface page | robot interface page |
| --- | --- |
| load | load |
| getUserMedia() | getUserMedia() |
| - | makeCall() <br> - create peer connection <br> ---> on new ICE candidate, emit <br> ---> add tracks from getUserMedia() to peer connection <br> - create offer <br> - set local description to offer <br> - emit offer |
| on receive offer, handleOffer() <br> - create peer connection <br> ---> on new ICE candidate, emit <br> ---> add tracks from getUserMedia() to peer connection <br> - set remote description to offer <br> - create answer <br> - set local description to answer <br> - emit answer | - |
| - | on receive answer, set remote description to answer|
