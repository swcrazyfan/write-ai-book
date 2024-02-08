import os
import streamlit as st
from datetime import datetime
import tempfile
import re
from ebooklib import epub
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_book_section(previous_sections, prompt, section_title):
    # Construct messages for the chat history to maintain context
    messages = [{"role": "system", "content": "You are a helpful assistant capable of generating detailed book content."}]
    
    # Add all previous sections to the chat history to maintain context
    for section in previous_sections:
        messages.append({"role": "user", "content": section["prompt"]})
        messages.append({"role": "assistant", "content": section["content"]})
    
    # Add the prompt for the current section
    messages.append({"role": "user", "content": prompt})
    
    # Call the OpenAI API to generate the content for the current section
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        max_tokens=4096,
        temperature=0.7
    )
    
    # Extract the generated content from the response
    content = response['choices'][0]['message']['content']
    return {"title": section_title, "prompt": prompt, "content": content}

def create_epub_book(title, author, sections):
    # Initialize the EPUB book
    book = epub.EpubBook()
    book.set_identifier('id' + str(datetime.now().timestamp()))
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)
    
    # Create a list to define the book's spine (order of content)
    spine = ['nav']
    
    # Initialize the table of contents
    toc = []
    
    # Loop through each section and add it to the book
    for section in sections:
        # Create an EPUB HTML file for the section
        epub_section = epub.EpubHtml(title=section['title'], file_name=f'{section["title"].replace(" ", "_").lower()}.xhtml', lang='en')
        epub_section.content = section['content']
        
        # Add the section to the book
        book.add_item(epub_section)
        
        # Add the section to the table of contents and spine
        toc.append(epub.Link(f'{section["title"].replace(" ", "_").lower()}.xhtml', section['title'], section['title']))
        spine.append(epub_section)
    
    # Set the book's table of contents and spine
    book.toc = toc
    book.spine = spine
    
    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define CSS for the book (optional)
    style = 'BODY {color: black;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    
    # Write the EPUB file
    epub_file_name = f"{title.replace(' ', '_').lower()}.epub"
    epub.write_epub(epub_file_name, book, {})
    
    return epub_file_name

# Streamlit UI for user inputs
st.title("AI-driven EPUB Book Generator")
book_concept = st.text_area("Book Concept:")
book_title = st.text_input("Book Title:")
author_name = st.text_input("Author Name:")

if st.button("Generate Book"):
    sections = []
    
    # Generate the introduction based on the book concept
    intro_prompt = f"Write an introduction for a book with the concept: {book_concept}"
    sections.append(generate_book_section([], intro_prompt, "Introduction"))
    
    # Generate chapters iteratively, using previous sections for context
    for chapter_num in range(1, 6):  # Example: Generate 5 chapters
        chapter_title = f"Chapter {chapter_num}"
        chapter_prompt = f"Continue the story. Generate {chapter_title}."
        sections.append(generate_book_section(sections, chapter_prompt, chapter_title))
    
    # Compile the generated sections into an EPUB book
    epub_file_name = create_epub_book(book_title, author_name, sections)
    st.success(f"Book generated successfully: {epub_file_name}")
