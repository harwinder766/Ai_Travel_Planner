# AI Travel Planner

An AI-assisted travel planning prototype with a Streamlit client, FastAPI API, LangGraph orchestration, live travel-data tools, and explicit runtime configuration.

## Local setup

1. Create and activate a Python 3.10+ environment.
2. Install dependencies:

   ```powershell
   uv sync
   ```

3. Copy `.env.example` to `.env` and set `GROQ_API_KEY` (or the key for the selected `MODEL_PROVIDER`).
4. Start the API:

   ```powershell
   uv run uvicorn main:app --reload
   ```

5. In another terminal, start Streamlit:

   ```powershell
   uv run streamlit run app.py
   ```

The API is available at `http://localhost:8000`; the Streamlit client is available at `http://localhost:8501`.

## API

- `GET /health` checks that the API process is running.
- `POST /query` accepts `{ "question": "Plan a five-day trip to Goa" }`.

The API caches the compiled LangGraph per model provider and does not regenerate graph images during requests. Live-data tools validate their own API keys when called and return explicit errors when configuration is incomplete.

## Configuration

See [.env.example](.env.example). Keep `.env` and all credentials out of version control.
