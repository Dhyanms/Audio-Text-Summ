import streamlit as st
import requests
import time

# Set your Hugging Face API token here
hf_token = "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"

# Function to transcribe audio
def transcribe_audio(audio_file):
    url = "https://api-inference.huggingface.co/models/facebook/wav2vec2-base-960h"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Read the uploaded audio file
    audio_data = audio_file.read()
    
    # Transcription request loop
    while True:
        response = requests.post(url, headers=headers, data=audio_data)
        
        if response.status_code == 503:
            st.write("Model is loading... retrying in 30 seconds.")
            time.sleep(30)  # Wait for 30 seconds and retry
        elif response.status_code == 200:
            transcription = response.json().get("text", "Transcription failed")
            return transcription
        else:
            st.write(f"Error in transcription: {response.text}")
            return None

# Function to summarize the transcription text
def summarize_text(transcription):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Set up data with parameters for summary
    data = {
        "inputs": transcription,
        "parameters": {
            "max_length": 50,  # Limit summary length
            "min_length": 10,  # Ensure summary is not too short
            "do_sample": False  # Use deterministic output
        }
    }

    # Summarization request
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        summary = response.json()[0].get("summary_text", "Summarization failed")
        return summary
    else:
        st.write(f"Error in summarization: {response.text}")
        return None

# Streamlit App
def main():
    st.title("Audio to Text Transcription & Summarization")

    # File uploader for audio files
    audio_file = st.file_uploader("Upload your audio file (WAV format)", type=["wav"])

    if audio_file is not None:
        st.write("Processing audio file...")

        # Transcription
        transcription = transcribe_audio(audio_file)
        if transcription:
            st.subheader("Transcription:")
            st.write(transcription)

            # Summarization
            st.write("\nSummarizing the transcription...")
            summary = summarize_text(transcription)
            if summary:
                st.subheader("Summary:")
                st.write(summary)
            else:
                st.write("Summarization failed.")
        else:
            st.write("Transcription failed.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
