import os
import re
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from dotenv import load_dotenv

load_dotenv()

# Get configuration from environment variables
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION")  # e.g., "us"
GCP_PROCESSOR_ID = os.getenv("GCP_PROCESSOR_ID")  # The ID of your Document AI processor


def clean_and_validate_text(text: str) -> str:
    """
    Cleans and validates the extracted text.

    Args:
        text: The raw text extracted from the document.

    Returns:
        The cleaned text.
    """
    # Remove extra whitespace and newlines
    text = " ".join(text.split())
    
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Basic validation: ensure text is not empty
    if not text.strip():
        raise ValueError("No valid text content found after cleaning.")
        
    return text


def extract_text_from_pdf(file_content: bytes, mime_type: str = "application/pdf") -> str:
    """
    Extracts text from a PDF file using Google Cloud Document AI.

    Args:
        file_content: The content of the PDF file in bytes.
        mime_type: The MIME type of the file.

    Returns:
        The extracted text from the document.
    """
    if not all([GCP_PROJECT_ID, GCP_LOCATION, GCP_PROCESSOR_ID]):
        raise ValueError("Missing Google Cloud configuration in .env file.")

    if mime_type != "application/pdf":
        raise ValueError("Unsupported file format. Only PDF files are accepted.")

    try:
        # You must set the `api_endpoint` if you use a location other than "us".
        opts = ClientOptions(api_endpoint=f"{GCP_LOCATION}-documentai.googleapis.com")

        client = documentai.DocumentProcessorServiceClient(client_options=opts)

        name = client.processor_path(GCP_PROJECT_ID, GCP_LOCATION, GCP_PROCESSOR_ID)

        # Load binary data
        raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

        # Configure the process request
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        result = client.process_document(request=request)
        document = result.document

        # Clean and validate extracted text
        # Clean and validate extracted text
        cleaned_text = clean_and_validate_text(document.text)

        return cleaned_text

    except Exception as e:
        print(f"An error occurred during document processing: {e}")
        # Re-raise the exception to be handled by the caller
        raise
