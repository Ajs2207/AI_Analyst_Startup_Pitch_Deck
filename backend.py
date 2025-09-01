import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
import uuid
import hashlib
from typing import Dict
from cachetools import TTLCache
from .processor import extract_text_from_pdf
from .analyzer import analyze_startup_data
from .logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Startup Analyst AI",
    description="API for analyzing startup pitch decks.",
    version="1.0.0"
)

# In-memory storage for job status and results
job_store: Dict[str, Dict] = {}
# In-memory cache for analysis results (100 items, 1-hour TTL)
analysis_cache = TTLCache(maxsize=100, ttl=3600)


def process_and_analyze(job_id: str, file_content: bytes, mime_type: str, filename: str):
    """
    Background task to process and analyze the uploaded file.
    """
    try:
        logger.info(f"Starting analysis for job_id: {job_id}")
        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(file_content, mime_type=mime_type)
        logger.info(f"Text extracted successfully for job_id: {job_id}")
        
        # Analyze the extracted text
        analysis_result = analyze_startup_data(extracted_text)
        logger.info(f"Data analyzed successfully for job_id: {job_id}")
        
        if analysis_result:
            result = {
                "status": "completed",
                "filename": filename,
                "analysis": analysis_result
            }
            job_store[job_id] = result
            # Cache the result
            file_hash = hashlib.sha256(file_content).hexdigest()
            analysis_cache[file_hash] = result
            logger.info(f"Analysis for job_id: {job_id} completed and cached.")
        else:
            job_store[job_id] = {"status": "failed", "error": "Failed to analyze data."}
            logger.error(f"Analysis failed for job_id: {job_id} - No result from analyzer.")

    except Exception as e:
        logger.error(f"An error occurred during processing for job_id: {job_id}", exc_info=True)
        job_store[job_id] = {"status": "failed", "error": str(e)}


@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Accepts a PDF file, starts a background task for processing, and returns a job ID.
    """
    if file.content_type != "application/pdf":
        logger.warning(f"Invalid file type uploaded: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")

    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()

    # Check if the result is already in the cache
    if file_hash in analysis_cache:
        job_id = str(uuid.uuid4())
        job_store[job_id] = analysis_cache[file_hash]
        logger.info(f"Returning cached result for file_hash: {file_hash} with new job_id: {job_id}")
        return {"job_id": job_id, "cached": True}

    job_id = str(uuid.uuid4())
    job_store[job_id] = {"status": "processing", "filename": file.filename}
    
    background_tasks.add_task(
        process_and_analyze, job_id, file_content, file.content_type, file.filename
    )

    return {"job_id": job_id, "cached": False}


@app.get("/analyze/{job_id}")
async def get_analysis(job_id: str):
    """
    Retrieves the analysis results for a given job ID.
    """
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    
    return job_store[job_id]