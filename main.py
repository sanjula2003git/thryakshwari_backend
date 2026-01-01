from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import re
from groq import Groq
import fitz  # PyMuPDF


load_dotenv()


app = FastAPI(title="Thryakshwari API")


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=GROQ_API_KEY)


doc_store = {}
MAX_CHARS = 8000  # Prevent token overflow


class QueryRequest(BaseModel):
    doc_id: str
    query: str


def clean_text(text: str) -> str:
    
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)
    
    text = re.sub(r"<\|.*?\|>", "", text)
    return text.strip()


def extract_text(file_bytes: bytes, content_type: str) -> str:
    
    if content_type == "application/pdf":
        text = ""
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    
    if content_type.startswith("text/"):
        return file_bytes.decode(errors="ignore")

    
    return ""


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not (
        file.content_type == "application/pdf"
        or file.content_type.startswith("text/")
    ):
        raise HTTPException(400, "Unsupported file type")

    raw_bytes = await file.read()
    text_content = extract_text(raw_bytes, file.content_type)

    if not text_content or not text_content.strip():
        raise HTTPException(400, "No readable text found in document")

    text_content = text_content[:MAX_CHARS]
    doc_id = str(hash(file.filename))

    doc_store[doc_id] = {
        "filename": file.filename,
        "content": text_content
    }

    return {
        "doc_id": doc_id,
        "message": "Document uploaded successfully"
    }


@app.post("/query")
async def query_document(request: QueryRequest):
    if request.doc_id not in doc_store:
        raise HTTPException(404, "Document not found")

    document_text = doc_store[request.doc_id]["content"]

    prompt = f"""
You are an AI assistant.

Answer the user's question strictly using the document below.
If the information is not present, say:
"The document does not contain this information."

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

    if not clean_answer:
        clean_answer = "I could not find relevant information in the document."

    return {"answer": clean_answer}


@app.get("/")
def root():
    return {"status": "API is running"}

