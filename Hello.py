import os
import streamlit as st
from datetime import datetime
from ebooklib import epub
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_initial_outline(book_concept):
    print("Generating initial book outline...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating detailed book outlines."},
            {"role": "user", "content": f"Create an outline for a book with the concept: {book_concept}. Include an introduction and titles/summaries for up to 8 chapters."}
        ],
        max_tokens=1024,
        temperature=0.7
    )
    # Corrected way to access the content
    outline = response.choices[0].message.content
    return outline

def expand_outline(outline):
    print("Expanding book outline...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of expanding book outlines into detailed outlines."},
            {"role": "user", "content": f"Take the following outline and expand it with more details:\n\n{outline}"}
        ],
        max_tokens=2048,
        temperature=0.7
    )
    # Corrected way to access the content
    detailed_outline = response.choices[0].message.content
    return detailed_outline

def generate_book_section(previous_sections, prompt, section_title, detailed_outline):
    print(f"Generating section: {section_title}")  # Logging
    messages = [
        {"role": "system", "content": "You are a helpful assistant capable of generating detailed book content."},
        {"role": "user", "content": detailed_outline}
    ]
    
    for section in previous_sections:
        messages.append({"role": "user", "content": section["prompt"]})
        messages.append({"role": "assistant", "content": section["content"]})
    
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        max_tokens=12000,
        temperature=0.7
    )
    
    content = response.choices[0].message['content']
    return {"title": section_title, "prompt": prompt, "content": content}

# The `create_epub_book` function remains the same as in the previous example.

# Streamlit UI for user inputs
st.title("AI-driven EPUB Book Generator")
book_concept = st.text_area("Book Concept:")
book_title = st.text_input("Book Title:")
author_name = st.text_input("Author Name:")

if st.button("Generate Book"):
    sections = []
    
    # Generate the initial outline based on the book concept
    initial_outline = generate_initial_outline(book_concept)
    
    # Expand the initial outline into a detailed outline
    detailed_outline = expand_outline(initial_outline)
    
    # Use the detailed outline to generate the introduction and chapters
    intro_prompt = "Write an introduction based on the detailed outline above."
    sections.append(generate_book_section([], intro_prompt, "Introduction", detailed_outline))
    
    for chapter_num in range(1, 9):  # Generate chapters based on the detailed outline
        chapter_title = f"Chapter {chapter_num}"
        chapter_prompt = f"Continue the story based on the detailed outline. Generate {chapter_title}."
        sections.append(generate_book_section(sections, chapter_prompt, chapter_title, detailed_outline))
    
    epub_file_name = create_epub_book(book_title, author_name, sections)
    st.success(f"Book generated successfully: {epub_file_name}")