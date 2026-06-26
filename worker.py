import os
import json
import logging
from celery import Celery
from google import genai
from pydantic import BaseModel, Field
from typing import Optional

import models
from database import SessionLocal

# -----------------------------------------------------------------------------
# Celery Configuration
# -----------------------------------------------------------------------------
# Connects to the Redis container mapped in docker-compose.yml
celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

# Initialize Google Gemini SDK
# The client automatically discovers the GEMINI_API_KEY environment variable.
gemini_client = genai.Client()

# -----------------------------------------------------------------------------
# LLM Output Schema Enforcement
# -----------------------------------------------------------------------------
class AITaskOutput(BaseModel):
    """Pydantic model used to force Gemini into a strict JSON output structure."""
    task: str = Field(description="The actionable task description extracted from the transcript.")
    assignee: Optional[str] = Field(default="Unassigned", description="The person assigned to the task. Use 'Unassigned' if unknown.")
    deadline: Optional[str] = Field(default="TBD", description="The deadline for the task. Use 'TBD' if unknown.")

# -----------------------------------------------------------------------------
# Background Task Definition
# -----------------------------------------------------------------------------
@celery_app.task(name="process_transcript", bind=True, max_retries=3)
def process_transcript_task(self, meeting_id: int, transcript: str):
    """
    Background worker process that communicates with Google's Gemini AI, 
    extracts actionable tasks, and safely saves them into the PostgreSQL database.
    """
    logging.info(f"Worker initiated transcription processing for meeting_id: {meeting_id}")
    
    # Instantiate a clean, isolated DB session specific to this worker thread
    db = SessionLocal()
    
    try:
        # 1. Structure the Prompt
        prompt = f"""
        You are a highly capable executive AI assistant.
        Extract a comprehensive list of actionable tasks from the following meeting transcript.
        If an assignee or deadline is not explicitly mentioned, rely on the defaults.
        
        Transcript:
        {transcript}
        """
        
        # 2. Securely call Gemini API using the strictly typed output schema
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[AITaskOutput],
            },
        )
        
        # Deserialize JSON text response from Gemini
        extracted_tasks = json.loads(response.text)
        logging.info(f"Gemini successfully extracted {len(extracted_tasks)} tasks.")

        # 3. Store parsed tasks in PostgreSQL
        for ai_task in extracted_tasks:
            new_task = models.Task(
                meeting_id=meeting_id,
                task_description=ai_task.get("task"),
                assignee=ai_task.get("assignee", "Unassigned"),
                deadline=ai_task.get("deadline", "TBD"),
                is_completed=False
            )
            db.add(new_task)
            
        # Optional: Mark the overarching meeting as 'completed'
        meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = "completed"
            
        # Commit the transaction safely
        db.commit()
        logging.info(f"Successfully saved {len(extracted_tasks)} tasks for meeting_id {meeting_id}.")
        
        return {
            "status": "success", 
            "meeting_id": meeting_id, 
            "tasks_extracted": len(extracted_tasks)
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"Processing failed for meeting_id {meeting_id}: {str(e)}")
        # Instruct Celery to retry this job 3 times before failing
        raise self.retry(exc=e, countdown=30)
        
    finally:
        # Always terminate the DB connection to prevent pool exhaustion
        db.close()
