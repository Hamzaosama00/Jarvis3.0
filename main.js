let recognizing = false;
let recognition;

function startListening() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Speech Recognition not supported!");
    return;
  }

  if (recognizing && recognition) {
    recognition.stop();
    recognizing = false;
    return;
  }

  recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    recognizing = true;
    document.querySelector("button").textContent = "🎤 Listening...";
  };

  recognition.onend = () => {
    recognizing = false;
    document.querySelector("button").textContent = "🎤 Speak to Jarvis";
  };

  recognition.onerror = (event) => {
    recognizing = false;
    alert("Mic Error: " + event.error);
  };

  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    document.getElementById("response").textContent = "🧑 You: " + text;
    askJarvis(text);
  };

  recognition.start();
}

function askJarvis(text) {
  fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  })
    .then(res => res.json())
    .then(data => {
      const reply = data.response;
      document.getElementById("response").textContent += "\n🤖 Jarvis: " + reply;
      speakJarvis(reply);
    });
}

function speakJarvis(text) {
  fetch("/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  })
    .then(res => res.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    })
    .catch(err => console.error("TTS Error:", err));
}
