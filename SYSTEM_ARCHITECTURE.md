# Meeting AI System - Architecture Documentation

## 1. FULL FILE HIERARCHY

```text
meeting-ai-system/
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
├── RUN_GUIDE.md
├── requirements.txt
├── database.py
├── main.py
├── models.py
├── schemas.py
├── worker.py
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── postcss.config.js
    ├── tailwind.config.js
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── components/
        │   ├── Dashboard.tsx
        │   ├── TaskDataTable.tsx
        │   └── UploadSection.tsx
        └── hooks/
            └── useMeetingTasks.ts
```

## 2. FILE-BY-FILE PURPOSE

### Root / Infrastructure Files
- **`.env`**: Stores secret environment variables securely (e.g., database credentials, Redis connection URLs, and the Gemini API key).
- **`.gitignore`**: Specifies which files and directories should be excluded from Git version control (such as `venv/`, `node_modules/`, `__pycache__/`).
- **`docker-compose.yml`**: Defines the multi-container orchestration setup. It configures the PostgreSQL database, Redis message broker, FastAPI web service, and the Celery worker, managing their networking, port mapping, and data volume persistence.
- **`Dockerfile`**: A multi-stage build blueprint for the backend services. The first stage builds required dependencies to optimize the final image size. The second stage creates a hardened, minimal runtime environment that utilizes a non-root user for improved security.
- **`README.md` & `RUN_GUIDE.md`**: Project documentation files providing setup details, execution instructions, and high-level summaries of the repository's purpose.
- **`requirements.txt`**: Lists the exact Python dependencies required for the backend services to run (e.g., FastAPI, Celery, SQLAlchemy, google-genai).

### Backend Core Files (Python)
- **`database.py`**: Configures the SQLAlchemy database engine, defining the session maker and declarative base needed to connect with the PostgreSQL database.
- **`main.py`**: The primary FastAPI application entry point. It defines the REST API endpoints (`/upload-transcript`, `/tasks/{meeting_id}`, `/tasks/{task_id}/complete`, `/tasks/{task_id}`) and delegates long-running tasks to the async worker.
- **`models.py`**: Defines the SQLAlchemy ORM models, mapping the underlying Python classes (`Meeting` and `Task`) to their corresponding relational database tables.
- **`schemas.py`**: Contains strictly typed Pydantic models (e.g., `TaskCreate`, `MeetingResponse`) for API request and response validation, guaranteeing data integrity at the application boundary.
- **`worker.py`**: The Celery background worker module. It defines `process_transcript_task`, which communicates with Google's Gemini AI, enforces a strict JSON schema for extracting tasks, and commits the results safely to the database.

### Frontend Files (React/Vite)
- **`frontend/package.json` & `package-lock.json`**: Define npm dependencies, scripts, and exact package versions required for the React application.
- **`frontend/postcss.config.js` & `tailwind.config.js`**: Configurations for Tailwind CSS, managing utility classes, themes, and CSS post-processing directives.
- **`frontend/vite.config.ts`**: Configuration for Vite, the ultra-fast build tool and development server used to bundle and run the frontend.
- **`frontend/index.html`**: The main HTML entry point where the React application is mounted into the DOM.
- **`frontend/src/main.tsx`**: The main React bootstrapping file. It initializes the app and renders `App.tsx`.
- **`frontend/src/App.tsx`**: The root component wrapping the application's top-level layout and routing logic.
- **`frontend/src/index.css`**: Global stylesheet that pulls in base styles and Tailwind directives.
- **`frontend/src/components/Dashboard.tsx`**: The main container view that orchestrates the transcript upload form and the resulting task data table.
- **`frontend/src/components/TaskDataTable.tsx`**: A component that displays the extracted tasks, their assignees, deadlines, and completion statuses in a formatted tabular layout.
- **`frontend/src/components/UploadSection.tsx`**: A component that provides the UI for users to paste and submit new meeting transcripts to the backend API.
- **`frontend/src/hooks/useMeetingTasks.ts`**: A custom React Hook responsible for state management and network calls—such as fetching meeting data, submitting transcripts, and updating task statuses.

## 3. OPERATIONAL WORKFLOW

When a user submits a meeting transcript through the frontend interface, the data traverses the system as follows:

1. **Frontend Submission**: The user pastes a transcript into the `UploadSection.tsx` UI and hits submit. The `useMeetingTasks.ts` hook fires a `POST /upload-transcript` request containing the text payload to the backend.
2. **API Ingestion (FastAPI)**: The `main.py` router receives the request. It validates the data via `schemas.py`, creates a `Meeting` record in PostgreSQL with a default `processing` status, and generates a primary key ID.
3. **Task Delegation (Celery + Redis)**: Before closing the request, the API invokes `process_transcript_task.delay(meeting_id, transcript)`. This packages the job and pushes a message to the Redis message broker queue. The FastAPI endpoint immediately returns the created meeting object to the frontend, preventing the HTTP connection from blocking.
4. **Background AI Processing (Gemini AI)**: 
   - The `worker.py` Celery daemon, constantly listening to the Redis queue, picks up the background task.
   - It constructs an executive prompt wrapping the transcript and communicates with the Google Gemini API.
   - It forces a strict output format using a `response_schema` mapped to the `AITaskOutput` Pydantic model, ensuring the AI responds with an array of reliably structured JSON objects containing actionable tasks, assignees, and deadlines.
5. **Data Persistence**: The worker securely parses the JSON, creating multiple `Task` database records linked via foreign key to the parent `meeting_id`. It then upgrades the overarching `Meeting` status to `completed` and commits the atomic transaction via `database.py`.
6. **Frontend Polling & Updates**: The frontend (via the React hook) requests updates using `GET /tasks/{meeting_id}`. It receives the fully populated meeting object complete with all newly extracted tasks and dynamically updates the `TaskDataTable.tsx` UI to reflect the results.

## 4. INFRASTRUCTURE & ORCHESTRATION

The architecture leverages Docker and Docker Compose to containerize, orchestrate, and isolate the micro-services efficiently.

- **Service Containerization (`Dockerfile`)**: The backend uses a multi-stage Dockerfile to maintain a minimal, secure image footprint. Stage 1 compiles complex C-extensions and wheels, while Stage 2 copies only the compiled binaries. It creates an `appuser` to ensure the process does not run as root, an essential security best practice.
- **Orchestration (`docker-compose.yml`)**: Four distinct, dependent services are defined to create the full ecosystem:
  - **`db`**: A robust PostgreSQL 15 database container. It uses persistent volume mounts (`postgres_data`) to ensure application data survives container restarts and upgrades.
  - **`redis`**: An Alpine-based Redis cache acting as the high-speed, in-memory message broker between the FastAPI ingestion layer and the Celery workers.
  - **`web`**: The main FastAPI server container. It uses volume mounts for local live reloading, exposes port 8000 for network access, and is configured with health check dependencies to only start after `db` and `redis` are ready.
  - **`worker`**: A parallel container running the exact same backend image as `web`, but it overrides the startup command to launch Celery. This decoupled architecture is critical, as it allows engineers to scale the number of intensive AI workers independently of standard web traffic.
