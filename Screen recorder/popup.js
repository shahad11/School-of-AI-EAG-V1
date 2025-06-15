let mediaRecorder;
let recordedChunks = [];
let stream = null;
let startTime;
let timerInterval;
let isMuted = false;

const recordBtn = document.getElementById('recordBtn');
const muteBtn = document.getElementById('muteBtn');
const stopBtn = document.getElementById('stopBtn');
const timerDisplay = document.getElementById('timer');

function updateTimer() {
  const now = Date.now();
  const diff = now - startTime;
  const hours = Math.floor(diff / 3600000);
  const minutes = Math.floor((diff % 3600000) / 60000);
  const seconds = Math.floor((diff % 60000) / 1000);
  timerDisplay.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

recordBtn.addEventListener('click', async () => {
  try {
    stream = await navigator.mediaDevices.getDisplayMedia({
      video: true,
      audio: true
    });

    recordedChunks = [];
    let options = { mimeType: 'video/webm;codecs=vp9' };
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      options = { mimeType: 'video/webm' };
    }
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      options = {};
    }
    mediaRecorder = new MediaRecorder(stream, options);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `screen-recording-${new Date().toISOString().replace(/[:.]/g, '-')}.webm`;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }, 100);
      stream.getTracks().forEach(track => track.stop());
    };

    mediaRecorder.start();

    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);

    recordBtn.disabled = true;
    muteBtn.disabled = false;
    stopBtn.disabled = false;

    recordBtn.querySelector('.icon').textContent = '●';
    recordBtn.textContent = 'Recording...';
  } catch (err) {
    console.error('Error starting recording:', err, err.name, err.message);
    alert(`Error: ${err.name}\n${err.message}`);
  }
});

muteBtn.addEventListener('click', () => {
  isMuted = !isMuted;
  if (stream) {
    stream.getAudioTracks().forEach(track => {
      track.enabled = !isMuted;
    });
  }
  muteBtn.querySelector('.icon').textContent = isMuted ? '🔇' : '🔊';
  muteBtn.textContent = isMuted ? 'Unmute' : 'Mute';
});

stopBtn.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
  clearInterval(timerInterval);
  timerDisplay.textContent = '00:00:00';

  recordBtn.disabled = false;
  muteBtn.disabled = true;
  stopBtn.disabled = true;

  recordBtn.querySelector('.icon').textContent = '●';
  recordBtn.textContent = 'Start Recording';
  muteBtn.querySelector('.icon').textContent = '🔊';
  muteBtn.textContent = 'Mute';
  isMuted = false;
}); 