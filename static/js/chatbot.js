function sendMessage() {
    const input = document.getElementById("chat-input").value;
    if (!input) return;
    fetch("/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
    })
    .then(res => res.json())
    .then(data => {
        const chatbox = document.getElementById("chatbox");
        chatbox.innerHTML += `<p><b>Kamu:</b> ${input}</p>`;
        chatbox.innerHTML += `<p><b>Bot:</b> ${data.reply}</p>`;
        document.getElementById("chat-input").value = "";
    });
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'id-ID';
    recognition.start();
    recognition.onresult = function(event) {
        const result = event.results[0][0].transcript;
        document.getElementById("chat-input").value = result;
    };
}
