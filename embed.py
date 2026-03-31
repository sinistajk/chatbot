from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def get_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def embed_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = content.split('===')
    sections = [s.strip() for s in sections if s.strip()]

    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            title = sections[i].strip()
            body = sections[i + 1].strip()
            chunks = chunk_text(body)

            print(f"Embedding: {title} ({len(chunks)} chunks)")

            for chunk in chunks:
                embedding = get_embedding(chunk)
                supabase.table("documents").insert({
                    "content": chunk,
                    "embedding": embedding,
                    "metadata": title
                }).execute()

    print("Done! All chunks embedded and stored.")

embed_file("data.txt")