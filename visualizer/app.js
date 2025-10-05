const visualizer = new AudioVisualizer('audioVisualizer');
const chat = new ChatInterface();

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');

let isListening = false;
let recognition = null;

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.error('Speech recognition not supported');
        chat.addAssistantMessage('Sorry, speech recognition is not supported in your browser. Please use Chrome or Edge.');
        return null;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        console.log('Speech recognition started');
        chat.setStatus('listening', 'Listening...');
    };

    recognition.onresult = (event) => {
        const lastResultIndex = event.results.length - 1;
        const transcript = event.results[lastResultIndex][0].transcript.trim();

        console.log('Heard:', transcript);

        chat.addMessage(transcript, 'user');

        chat.addTypingIndicator();
        chat.setStatus('processing', 'Processing...');

        setTimeout(() => {
            const response = generateResponse(transcript);
            chat.addAssistantMessage(response);
            chat.setStatus('listening', 'Listening...');
        }, 500 + Math.random() * 1000);
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);

        if (event.error === 'no-speech') {
            return;
        }

        if (event.error === 'not-allowed') {
            chat.addAssistantMessage('Microphone access denied. Please allow microphone access to use voice features.');
            stopListening();
        }
    };

    recognition.onend = () => {
        console.log('Speech recognition ended');
        if (isListening) {
            recognition.start();
        }
    };

    return recognition;
}

function generateResponse(input) {
    const lowerInput = input.toLowerCase();

    const responses = {
        'hello': 'Hello! How can I help you today?',
        'hi': 'Hi there! What can I do for you?',
        'how are you': "I'm doing great! Thanks for asking. How are you?",
        'what time': `The current time is ${new Date().toLocaleTimeString()}.`,
        'what date': `Today is ${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}.`,
        'thank you': "You're welcome! Happy to help.",
        'thanks': "You're welcome!",
        'bye': 'Goodbye! Have a great day!',
        'goodbye': 'See you later! Take care!',
        'help': 'You can ask me about the time, date, or just have a conversation. Try asking me questions!',
    };

    for (const [keyword, response] of Object.entries(responses)) {
        if (lowerInput.includes(keyword)) {
            return response;
        }
    }

    const genericResponses = [
        "That's interesting! Tell me more.",
        "I understand. Is there anything specific you'd like help with?",
        "Got it! How can I assist you further?",
        "Interesting question! Let me think about that.",
        "I'm here to help with whatever you need.",
    ];

    return genericResponses[Math.floor(Math.random() * genericResponses.length)];
}

async function startListening() {
    const audioStarted = await visualizer.startListening();

    if (!audioStarted) {
        chat.addAssistantMessage('Could not access microphone. Please check your permissions.');
        return;
    }

    if (!recognition) {
        recognition = initSpeechRecognition();
        if (!recognition) return;
    }

    try {
        recognition.start();
        isListening = true;

        startBtn.disabled = true;
        stopBtn.disabled = false;

        chat.setStatus('listening', 'Listening...');
        chat.addAssistantMessage("I'm listening! You can start speaking now.");
    } catch (error) {
        console.error('Error starting speech recognition:', error);
        chat.addAssistantMessage('Error starting speech recognition. Please try again.');
    }
}

function stopListening() {
    if (recognition) {
        recognition.stop();
    }

    visualizer.stopListening();
    isListening = false;

    startBtn.disabled = false;
    stopBtn.disabled = true;

    chat.setStatus('ready', 'Ready');
    chat.addAssistantMessage('Stopped listening. Click "Start Listening" to resume.');
}

startBtn.addEventListener('click', startListening);
stopBtn.addEventListener('click', stopListening);

chat.addAssistantMessage('Welcome! Click "Start Listening" to begin using voice commands.');
