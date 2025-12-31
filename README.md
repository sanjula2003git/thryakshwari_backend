How to Use Swagger (Step-by-Step)

Step 1: Open Swagger UI

Open the following URL in your browser:

https://thryakshwari-backend.onrender.com/docs

You will see:

API endpoints listed

Buttons like Try it out

Input fields for requests

Step 2: Upload a Document

2.1 Locate the Upload Endpoint

POST /upload

2.2 Click Try it out

This enables input fields.

2.3 Choose a File

Click Choose File

Select a PDF or text document from your system

2.4 Execute the Request

Click Execute

2.5 Verify Response

You should see a response like:
{
  "message": "Document uploaded successfully"
}

Step 3: Ask a Question About the Document

3.1 Locate the Query Endpoint

Find:

POST /query

3.2 Click Try it out

3.3 Enter the Query

In the Request Body, enter:
{
  "query": "What is this document about?"
}

3.4 Execute

Click Execute

3.5 Read the Answer

You will receive:
{
  "answer": "This document appears to be a resume or professional summary..."
}

This is the AI-generated response based on your uploaded document.

Step 4: Ask More Questions (Optional)

You can repeat Step 3 with different questions:

“What skills are mentioned?”

“Summarize the document”

“Who is the candidate?”

No need to re-upload unless the document changes.

Important Notes:

Upload must be done first, otherwise /query may return an empty answer

Uploading a new document replaces the previous one

Swagger reflects real API behavior (same as frontend)

IN THE ABOVE AFTER UPLOADING YOU WILL DOC ID AND YOU NEED TO COPY AND PASTE IT ALONG WITH WITH DOC ID IN QUERY PART ABOVE.
