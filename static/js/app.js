//initializing variables

URL = window.URL || window.webkitURL;

var gumStream; 						// Stream from getUserMedia()
var rec; 							// Recorder.js object
var input; 							// MediaStreamAudioSourceNode we'll be recording

// Chips for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext // Audio context to help us record

var record = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var recordedAudio = document.getElementById("recordedAudio");



// Add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);






// Starting of recording 



function startRecording() {
console.log("recordButton clicked");


// Simple constraints object
var constraints = { audio: true, video:false }

// Disable the record button until we get a success or fail from getUserMedia() 
recordButton.disabled = true;
stopButton.disabled = false;

// We're using the standard promise based getUserMedia() 

navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
	console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

	
	// Create an audio context after getUserMedia is called
		
	audioContext = new AudioContext();

	// Assign to gumStream for later use  
	gumStream = stream;
	
	// Use the stream 
	input = audioContext.createMediaStreamSource(stream);

	// Create the Recorder object and configure to record mono sound (1 channel)
	rec = new Recorder(input,{numChannels:1});

	// Start the recording process
	rec.record();
	console.log("Recording started");

}).catch(function(err) {
	// Enable the record button if getUserMedia() fails
	recordButton.disabled = false;
	stopButton.disabled = true;
	});
}



//Posting of image to front

function images(){
	var timestamp = new Date().getTime();     
	var bc = document.getElementById("barchart"); 
	bc.src = "/static/images/hoold.png?t=" + timestamp;    
	bc.classList.remove("hidden");
	var sig = document.getElementById("signal"); 
	sig.src = "/static/images/signal.png?t=" + timestamp;    
	sig.classList.remove("hidden");

};





// Ending of recording 


function stopRecording() {
console.log("stopButton clicked");

// Disable the stop button, enable the record too allow for new recordings
stopButton.disabled = true;
recordButton.disabled = false;

// Stop the recording
rec.stop();

// Stop microphone access
gumStream.getAudioTracks()[0].stop();

// Create the wav blob and pass it on to createProcessAudio
// rec.exportWAV(createProcessAudio);

rec.exportWAV(
	(file) => {
		let formData = new FormData();
		formData.delete('file');
		formData.append("file", file);

		$.ajax({
			type: "POST",
			url: "/predict",
			data: formData,
			contentType: false,
			cache: false,
			processData: false,
			async: true,
			success: function (data) {
				document.getElementById("barchart").innerHTML= images();
				document.getElementById("signal").innerHTML= images();

				var element=document.getElementById("output-person")
				element.innerText = data.person

				var element=document.getElementById("output-scentence")
				element.innerText = data.sentence

	
			}})
	}
)
}




// Record button visibility function



const toggleTo2 = document.getElementById("recordButton");
const toggleTo1 = document.getElementById("stopButton");

const hide = el => el.style.setProperty("display", "none");
const show = el => el.style.setProperty("display", "block");

hide(toggleTo1);

toggleTo2.addEventListener("click", () => {
  hide(toggleTo2);
  show(toggleTo1);
});

toggleTo1.addEventListener("click", () => {
  hide(toggleTo1);
  show(toggleTo2);
});



