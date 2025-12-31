from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import re
from groq import Groq

# --------------------
# Load env vars
# --------------------
load_dotenv()

# --------------------
# App setup
# --------------------
app = FastAPI(title="Thryakshwari API")

# --------------------
# Groq client setup
# --------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=GROQ_API_KEY)

# --------------------
# In-memory document store
# --------------------
doc_store = {}
MAX_CHARS = 8000  # prevent token overflow

# --------------------
# Models
# --------------------
class QueryRequest(BaseModel):
    doc_id: str
    query: str

# --------------------
# Utility: clean LLM output
# --------------------
def clean_text(text: str) -> str:
    # Remove ASCII control characters
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)
    # Remove internal LLM tokens
    text = re.sub(r"<\|.*?\|>", "", text)
    return text.strip()

# --------------------
# Upload endpoint
# --------------------
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not (
        file.content_type.startswith("application/pdf")
        or file.content_type.startswith("text/")
        or file.content_type.startswith("image/")
    ):
        raise HTTPException(400, "Unsupported file type")

    raw_bytes = await file.read()
    text_content = raw_bytes.decode(errors="ignore")[:MAX_CHARS]

    doc_id = str(hash(file.filename))

    doc_store[doc_id] = {
        "filename": file.filename,
        "content": text_content
    }

    return {
        "doc_id": doc_id,
        "message": "Document uploaded successfully"
    }

# --------------------
# Query endpoint
# --------------------
@app.post("/query")
async def query_document(request: QueryRequest):
    if request.doc_id not in doc_store:
        raise HTTPException(404, "Document not found")

    document_text = doc_store[request.doc_id]["content"]

    prompt = f"""
You are an AI assistant.

Use the document below to answer the user's question.
If the answer is not present, say "The document does not contain this information."

DOCUMENT:
{document_text}

QUESTION:
{request.query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw_answer = response.choices[0].message.content
    clean_answer = clean_text(raw_answer)

    return {"answer": clean_answer}

# --------------------
# Health check (optional)
# --------------------
@app.get("/")
def root():
    return {"status": "API is running"}







