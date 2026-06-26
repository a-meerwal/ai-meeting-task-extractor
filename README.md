#  AI Meeting Task Extractor

A robust, distributed, and highly scalable backend service built with FastAPI, Celery, Redis, and PostgreSQL. This system is designed to asynchronously process meeting transcripts using Google's Gemini AI, extracting highly structured, actionable tasks without blocking the main web threads.

---

##  System Architecture

This project is built on an event-driven, microservices-style layout orchestrating four distinct, highly specialized containers via Docker Compose:

### 1. `web` (FastAPI) - The Synchronous Gateway
* **Role**: Serves as the primary API entry point for user interactions.
* **Responsibilities**: Handles incoming HTTP requests, manages direct synchronous writes to the database for `Meeting` metadata, and hands off heavy AI processing payloads to the Celery broker. 
* **Design Pattern**: Implements dependency injection (`get_db`) to cleanly manage PostgreSQL session lifecycles for every request.

### 2. `worker` (Celery) - The Asynchronous Brain
* **Role**: The background task processor.
* **Responsibilities**: Continuously polls the Redis message queue. Upon receiving a job, it constructs a prompt, connects to the Google Gemini API, enforces a strictly typed JSON schema for the AI output (`list[TaskOutput]`), and synchronously writes the extracted tasks directly to PostgreSQL on an isolated database connection.

### 3. `redis` (Redis) - The Message Broker
* **Role**: The high-speed, in-memory bridge between FastAPI and Celery.
* **Responsibilities**: Acts as the message broker. It queues the `(meeting_id, transcript)` payloads safely until a Celery worker is free to process them.

### 4. `db` (PostgreSQL) - The Persistence Layer
* **Role**: The primary relational database.
* **Responsibilities**: Stores the raw `meetings` records and the generated `tasks` records. Uses standard SQLAlchemy Object-Relational Mapping (ORM) to define and map the One-to-Many foreign key relationships.

---

##  Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3)
* **Task Queue:** [Celery](https://docs.celeryq.dev/)
* **Message Broker:** [Redis](https://redis.io/)
* **Database:** [PostgreSQL](https://www.postgresql.org/)
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) & [Pydantic](https://docs.pydantic.dev/)
* **AI Engine:** Google Gemini (`gemini-2.5-flash`)
* **Containerization:** Docker & Docker Compose

---

##  The Request Flow (Under the Hood)

Here is exactly what happens when you upload a transcript:

1. **API Trigger:** You submit a `POST` request with `{meeting_title, transcript}` to the FastAPI `/upload-transcript` endpoint.
2. **Synchronous Persistence:** FastAPI opens a DB transaction, saves the `Meeting` record, and retrieves the auto-generated `meeting_id`.
3. **Queueing (Non-Blocking):** FastAPI executes `process_transcript_task.delay(meeting_id, transcript)`. This serializes the job and drops it in the Redis queue. The API immediately returns a `200 OK` response with a polling URL, without waiting for the AI to finish.
4. **AI Generation:** The background Celery worker detects the job in Redis, fires the transcript over to the Gemini API, and instructs the LLM to return a deterministic array of JSON objects containing `task`, `assignee`, and `deadline`.
5. **Final Storage:** The Celery worker opens its *own* DB connection and saves the newly generated `Tasks` into PostgreSQL, linking them to the original `meeting_id` via a foreign key. The user can now see the tasks when polling the GET endpoint.



## Setup & Installation

### Prerequisites
* [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/) installed on your system.
* A valid Google Gemini API Key.

### 1. Environment Configuration
Create a `.env` file in the root directory of the project:
```env
# Required for the Celery Worker to authenticate with Google
GEMINI_API_KEY=your_actual_google_api_key_here

# (Optional) Database Config - Defaults are defined in docker-compose.yml
# POSTGRES_USER=myuser
# POSTGRES_PASSWORD=mypassword
# POSTGRES_DB=meeting_db
```

### 2. Bootstrapping the Infrastructure
Open your terminal, navigate to the project directory, build the images, and spin up the containers in detached mode:
```bash
docker-compose up -d --build
```

To verify everything is running smoothly:
```bash
docker-compose ps
```
You should see all four services (`web`, `worker`, `db`, `redis`) returning an `Up` status.

---

##  API Endpoints & Usage

Once the containers are successfully running, FastAPI automatically generates interactive OpenAPI documentation. 
Navigate to: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### `POST /upload-transcript`
Upload a meeting transcript to trigger the asynchronous AI extraction.
* **Payload:** `{"meeting_title": "Q3 Planning", "transcript": "..."}`
* **Response:** Yields a `meeting_id` and a `check_status_url`.

### `GET /tasks/{meeting_id}`
Poll the status of the AI job.
* **Response:** Returns `"status": "processing"` if Celery is still actively analyzing the transcript, or `"status": "completed"` with the fully extracted list of tasks once finished.

### `PATCH /tasks/{task_id}/complete`
Mark a specific extracted task as completed in the database.

### `DELETE /tasks/{task_id}`
Delete a task from the system entirely.

---

##  Operations & Maintenance

**Monitor Background Jobs:**
To watch the Celery worker interact with the queue and the Gemini AI in real-time:
```bash
docker-compose logs -f worker
```

**View Web Server Logs:**
```bash
docker-compose logs -f web
```

**Teardown the Environment:**
To gracefully stop the application and remove the containers:
```bash
docker-compose down
```
*(Note: To completely wipe the database volumes and reset your data, append the `-v` flag: `docker-compose down -v`)*
