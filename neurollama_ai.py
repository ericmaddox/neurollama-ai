import os
import pyttsx3
import subprocess
import json
from textblob import TextBlob

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Initialize conversation history
conversation_history = []

# Define the path to the configuration file
config_path = os.path.join(os.getcwd(), 'config.json')

# Load configuration from config.json
try:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    config = {
        'voice': 'com.apple.voice.compact.en-US.Samantha',
        'history_file': os.path.join(os.getcwd(), 'conversation_history.json'),
        'interaction_memory': 10,
        'timeout': 30
    }

# Function to convert text to speech
def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()

# Function to generate text with Ollama 3.2, including conversation history
def generate_text_with_ollama(prompt, conversation_history):
    history = " ".join([entry['user'] + " " + entry['AI'] for entry in conversation_history[-config['interaction_memory']:] if 'user' in entry and 'AI' in entry])
    full_prompt = f"{history} User: {prompt} AI:"
    result = subprocess.run(['ollama', 'run', 'llama3.2', full_prompt], capture_output=True, text=True)
    return result.stdout.strip()

# Load conversation history from a file
def load_history():
    try:
        if not os.path.exists(config['history_file']):
            return []
        with open(config['history_file'], 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save conversation history to a file
def save_history():
    with open(config['history_file'], 'w') as file:
        json.dump(conversation_history, file, indent=4)

# Analyze user input sentiment
def analyze_sentiment(user_input):
    blob = TextBlob(user_input)
    return blob.sentiment.polarity  # Polarity ranges from -1 (negative) to 1 (positive)

# Main loop for interactive chat
if __name__ == "__main__":
    conversation_history = load_history()
    print("Chat with AI. Type 'exit' to end the conversation.")

    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break

        sentiment = analyze_sentiment(prompt)

        # Analyze sentiment and adjust AI's response
        if sentiment < -0.3:  # Negative sentiment
            generated_text = "I sense some frustration. I'm here to assist you."
        elif sentiment > 0.3:  # Positive sentiment
            generated_text = "I'm glad to hear your positivity! Let's continue."
        else:
            generated_text = generate_text_with_ollama(prompt, conversation_history)

        # Add to conversation history and save
        conversation_history.append({
            "user": prompt,
            "AI": generated_text,
            "mood": "negative" if sentiment < -0.3 else "positive" if sentiment > 0.3 else "neutral"
        })
        save_history()

        print(f"AI: {generated_text}")
        text_to_speech(generated_text)
