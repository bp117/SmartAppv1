import streamlit as st
import PyPDF2
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load the LLaMA model and tokenizer
model_name = "path_to_your_local_llama_model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

def generate_prompt(text, criterion):
    return f"Evaluate the following text based on the criterion '{criterion}':\n\n{text}\n\nScore (0-10):"

def get_score_from_model(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(inputs, max_length=50)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract the score from the generated text
    try:
        score = float(result.split()[-1])
    except ValueError:
        score = 0.0  # Default to 0 if the score extraction fails
    return score

def summarize_text(text):
    prompt = f"Summarize the following text in approximately 300 words:\n\n{text}"
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
    summary_ids = model.generate(inputs, max_length=600, min_length=300, num_return_sequences=1, no_repeat_ngram_size=2, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def evaluate_text(text):
    criteria = ["Relevance", "Comprehensive Story", "Language", "Originality", "Problem Definition"]
    scores = {}
    
    for criterion in criteria:
        prompt = generate_prompt(text, criterion)
        score = get_score_from_model(prompt)
        scores[criterion] = score
    
    total_score = sum(scores.values()) / len(criteria)
    scores["Total Score"] = total_score
    return scores

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        text += page.extract_text()
    return text

# Streamlit app layout
st.title("PDF Summarizer and Evaluator")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    st.write("Extracted Text:", text[:1000] + "...")  # Display first 1000 characters of extracted text

    if st.button("Summarize"):
        summary = summarize_text(text)
        st.write("Summary:", summary)

    if st.button("Evaluate"):
        scores = evaluate_text(text)
        st.write("Evaluation Scores:")
        st.write(f"Relevance: {scores['Relevance']}")
        st.write(f"Comprehensive Story: {scores['Comprehensive Story']}")
        st.write(f"Language: {scores['Language']}")
        st.write(f"Originality: {scores['Originality']}")
        st.write(f"Problem Definition: {scores['Problem Definition']}")
        st.write(f"Total Score: {scores['Total Score']}")

if __name__ == "__main__":
    st.run()
