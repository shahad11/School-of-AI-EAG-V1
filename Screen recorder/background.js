let mediaRecorder;
let recordedChunks = [];
let isMuted = false;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'startRecording':
      startRecording(message.stream);
      break;
    case 'toggleMute':
      toggleMute(message.isMuted);
      break;
    case 'stopRecording':
      stopRecording();
      break;
  }
});

function startRecording(stream) {
  recordedChunks = [];
  mediaRecorder = new MediaRecorder(stream, {
    mimeType: 'video/webm;codecs=vp9'
  });

  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      recordedChunks.push(event.data);
    }
  };

  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, {
      type: 'video/webm'
    });
    
    const url = URL.createObjectURL(blob);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    chrome.downloads.download({
      url: url,
      filename: `screen-recording-${timestamp}.webm`,
      saveAs: true
    });

    stream.getTracks().forEach(track => track.stop());
  };

  mediaRecorder.start();
}

function toggleMute(muted) {
  isMuted = muted;
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stream.getAudioTracks().forEach(track => {
      track.enabled = !isMuted;
    });
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
} 