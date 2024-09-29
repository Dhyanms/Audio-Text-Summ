import streamlit as st
import requests
import time
from jiwer import wer
from rouge_score import rouge_scorer

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

# Function to calculate WER and ROUGE scores
def evaluate_transcription_and_summary(ground_truth, transcription, reference_summary, generated_summary):
    wer_score = wer(ground_truth, transcription)
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    rouge_scores = scorer.score(reference_summary, generated_summary)

    return wer_score, rouge_scores

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

            # Evaluate with ground truth and reference summary (replace these with your actual texts)
            ground_truth = "THIS IS AN EXAMPLE REGARDING THE M O M MODEL WHICH I HAVE CREATED I WANTED TO SEE HOW THE RESULTS GO IN THIS MODEL AND EVALUATE IF MY MODEL IS WORKING FINE OR NOT WORKING FINE"  # Replace with the actual ground truth
            reference_summary = "THIS IS AXAMPLE REGARDING FOR THE M O M MODEL WHICH I HAVE CREATED I HONOR SEE HOW THE RESULTS GO IN THIS MODEL AND EVALUATE IF MY MODEL IS WORKING FINE OR NOT WORKING FINE"  # Replace with the actual reference summary

            wer_score, rouge_scores = evaluate_transcription_and_summary(ground_truth, transcription, reference_summary, summary)

            # Display scores
            st.subheader("Evaluation Metrics:")
            st.write(f"Word Error Rate (WER): {wer_score}")
            st.write(f"ROUGE-1: {rouge_scores['rouge1']}")
            st.write(f"ROUGE-2: {rouge_scores['rouge2']}")
            st.write(f"ROUGE-L: {rouge_scores['rougeL']}")
        else:
            st.write("Transcription failed.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
