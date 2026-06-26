## Prerequisites
- Docker & Docker Compose
- Node.js & npm
- A Google Gemini API key

---

## Step 1: Environment Initialization

Open the `.env` file in the root directory and set your API key:

```env
GEMINI_API_KEY=your_actual_google_api_key_here
```

---

## Step 2: Start the Backend

From the root directory, build and start all Docker containers:

```bash
docker-compose up -d --build
```

Verify all containers are running:

```bash
docker-compose ps
```

The `db`, `redis`, `web`, and `worker` containers should all show an **Up** status.

---

## Step 3: Start the Frontend

Open a new terminal, navigate to the frontend directory, and install dependencies:

```bash
cd frontend
npm install
npm run dev
```

---

## Step 4: Using the App

1. Open [http://localhost:5173](http://localhost:5173) in your browser.
2. Enter a **Meeting Title** (e.g., `Q3 Planning`).
3. Paste the raw **transcript** into the input field.
4. Click **Extract** to trigger processing.
5. Wait for the Celery background task to complete — the table will populate automatically with extracted tasks, assignees, and deadlines.
6. Use the UI toggles to mark tasks as complete or delete them.

---

## Step 5: Teardown

Stop the React dev server with `Ctrl+C`, then bring down the backend:

```bash
docker-compose down
```