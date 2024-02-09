import streamlit as st
# Assuming a hypothetical updated OpenAI SDK or for illustrative purposes
from openai import OpenAI

# Initialize the OpenAI client with your API key
client = OpenAI(api_key='your_openai_api_key')

def generate_book_outline(book_idea):
    # Detailed prompt asking the AI to create a book outline
    prompt = f"Create a detailed outline for a book based on the following idea or theme: {book_idea}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    # Extracting the generated outline from the response
    # Adjust this line based on the actual structure of the response object
    return response['choices'][0]['message']['content']

st.title('Book Outline Generator')

# User input for the book idea or theme
book_idea = st.text_area("Enter your book idea or theme:", height=150)

if st.button('Generate Outline'):
    if book_idea:
        with st.spinner('Generating outline...'):
            outline = generate_book_outline(book_idea)
            st.subheader('Generated Outline:')
            st.write(outline)
    else:
        st.error('Please enter a book idea or theme to generate an outline.')
