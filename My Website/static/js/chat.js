// chat.js

var socket = io("http://89.111.47.124:27767");
var deviceId = localStorage.getItem("device_id") || uuid.v4();
localStorage.setItem("device_id", deviceId);
var username = "";

// List of swear words to filter
const swearWords = ["badword1", "badword2", "badword3"]; // Add more words as necessary

// Function to escape special characters in input to prevent XSS
function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function (match) {
        const escapeChars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return escapeChars[match];
    });
}

// Function to check and filter swear words
function filterSwearWords(message) {
    return message.split(' ').map(word => {
        return swearWords.includes(word.toLowerCase()) ? '****' : word;
    }).join(' ');
}

function checkUsername() {
    fetch("/get_username", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device_id: deviceId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            username = data.username;
            document.getElementById("username-form").style.display = "none";
            document.getElementById("chat-container").style.display = "block";
            loadChatHistory();
        }
    });
}

function setUsername() {
    let input = document.getElementById("username").value.trim();
    if (input === "") {
        alert("Username cannot be empty");
        return;
    }
    fetch("/set_username", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: input, device_id: deviceId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            username = data.username;
            document.getElementById("username-form").style.display = "none";
            document.getElementById("chat-container").style.display = "block";
            loadChatHistory();
        } else {
            alert("Username already taken. Choose another.");
        }
    });
}

function loadChatHistory() {
    fetch("/get_messages")
    .then(response => response.json())
    .then(messages => {
        let chatBox = document.getElementById("chat-box");
        chatBox.innerHTML = "";
        messages.forEach(msg => {
            chatBox.innerHTML += `<p><strong>${msg.username}:</strong> ${escapeHtml(msg.message)}</p>`;
        });
    });
}

function sendMessage() {
    let message = document.getElementById("chat-input").value.trim();
    if (message !== "") {
        let filteredMessage = filterSwearWords(message);
        socket.emit("send_message", { device_id: deviceId, message: filteredMessage });
        document.getElementById("chat-input").value = "";
    }
}

socket.on("receive_message", function(data) {
    document.getElementById("chat-box").innerHTML += `<p><strong>${data.username}:</strong> ${escapeHtml(data.message)}</p>`;
});

checkUsername();
