
## Step 1: Add Your API Key
The MTE needs to connect to Google Gemini  first 
1. Open the `.env` file
2. Ensure you have your key set like this:
   ```env
   GEMINI_API_KEY=your_actual_google_api_key_here
   ```

## Step 2: Start the Backend Containers
Open your terminal in this project directory and run:
```bash
docker-compose up -d --build
```
Verify the backend is running by executing `docker-compose ps`. You should see `db`, `redis`, `web`, and `worker` as "Up".

## Step 3: Start the React Frontend Dashboard
We've built a sleek React dashboard located in the `/frontend` directory. It uses Vite, Tailwind CSS, and connects directly to your FastAPI backend via a configured proxy!

Open a **new terminal tab**, navigate into the frontend folder, and start it:
```bash
cd frontend
npm install
npm run dev
```

## Step 4: Test the Platform
1. Open your browser and navigate 
**http://localhost:5173** 
2. Type in a Meeting Title          (e.g. "Q3 Planning").
3. Paste a test transcript        (e.g. *"Okay everyone, let's get started. Sarah, I need you to finish the frontend mockups by Friday. John, please set up the database schema by tomorrow."*).
4. Click **Extract Tasks**.
5. The frontend will show a beautiful glassmorphism loading state. Once Celery finishes its job, the Data Table will dynamically populate with the AI-extracted tasks!
6. Click the checkmarks to complete tasks or trash icons to delete them.

## Step 5: Shutting Down
When you are completely finished, stop the React app (Ctrl+C in terminal) and stop the backend services:
```bash
docker-compose down
```
