import logging
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import models
import schemas
from database import engine, SessionLocal
from worker import process_transcript_task

# Create tables synchronously for now
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Meeting Task Extractor API",
    description="High-performance async API for extracting tasks from meeting transcripts using AI.",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Annotated[Session, Depends(get_db)]

@app.post(
    "/upload-transcript",
    response_model=schemas.MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new transcript",
    description="Creates a meeting record and asynchronously queues an AI job to extract tasks."
)
async def upload_transcript(request: schemas.MeetingCreate, db: DbSession):
    try:
        db_meeting = models.Meeting(
            title=request.title,
            transcript=request.transcript,
            status="processing"
        )
        db.add(db_meeting)
        db.commit()
        db.refresh(db_meeting)
        
        # Dispatch real Celery task
        process_transcript_task.delay(db_meeting.id, request.transcript)
        
        return db_meeting
        
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = str(e)
        logging.error(f"DB Error on upload: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error details: {error_msg}"
        )


@app.get(
    "/tasks/{meeting_id}",
    response_model=schemas.MeetingResponse,
    summary="Get meeting and extracted tasks"
)
async def get_tasks(meeting_id: int, db: DbSession):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found."
        )
        
    return meeting


@app.patch(
    "/tasks/{task_id}/complete",
    response_model=schemas.TaskResponse,
    summary="Mark task as completed"
)
async def complete_task(task_id: int, db: DbSession):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found."
        )
    
    task.is_completed = True
    
    try:
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task status: {str(e)}"
        )


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def delete_task(task_id: int, db: DbSession):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found."
        )
    
    try:
        db.delete(task)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )