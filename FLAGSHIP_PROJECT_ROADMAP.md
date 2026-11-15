# Flagship AI Travel Planner Roadmap

Your current project is a promising prototype, but it needs stronger reliability, architecture, product depth, and measurable evaluation before adding advanced AI patterns.

## Current baseline

- Streamlit frontend: [app.py](app.py)
- FastAPI backend: [main.py](main.py)
- LangGraph workflow: [agent/agentic_workflow.py](agent/agentic_workflow.py)
- Prompt layer: [prompt_library/prompt.py](prompt_library/prompt.py)
- External integrations currently implemented as local LangChain tools
- No strong persistence, authentication, observability, evaluation, or deployment story yet

## Target product

Build an **AI Travel Operating System** that:

1. Understands a traveller's preferences, constraints, and budget.
2. Researches live travel information using MCP servers.
3. Uses specialized agents for planning, budgeting, weather, safety, and verification.
4. Produces a structured, editable, evidence-backed itinerary.
5. Re-plans when the user changes dates, budget, weather, or preferences.
6. Tracks source freshness and uncertainty.
7. Measures quality using automated evaluations.

## Recommended architecture

```text
Streamlit/Web Client
        |
FastAPI API + Authentication
        |
Travel Orchestrator / LangGraph
        |
Supervisor Agent
   |       |        |        |
Research  Budget   Route   Safety
Agent     Agent    Agent   Agent
        |
MCP Gateway
   |        |        |        |
Places   Weather  Maps   Currency
MCP      MCP      MCP    MCP
        |
PostgreSQL + Redis + Object Storage
        |
Tracing, Evaluation, Feedback, Metrics
```

## MCP recommendation

Do not convert every function into an MCP server.

Use MCP for:

- Google Places or another places provider
- Weather data
- Maps, routing, and travel time
- Currency conversion
- Flight or hotel search
- Visa and travel advisory information
- Calendar integration
- Exporting to email, PDF, or calendar

Keep these local:

- Budget calculations
- Schema validation
- Policy checks
- Itinerary scoring
- Date and duration calculations
- Agent orchestration
- Deterministic business rules

MCP should represent **capabilities and data access**. It should not replace every internal function.

## Phased implementation plan

### Phase 0 - Stabilize the prototype

**Goal:** Make the current application reliable before expanding it.

Tasks:

- Fix incomplete LangGraph initialization in [agent/agentic_workflow.py](agent/agentic_workflow.py).
- Centralize model, prompt, and tool configuration.
- Remove duplicated tool implementations.
- Add typed request and response schemas.
- Replace `print` statements with structured logging.
- Add explicit timeout and retry handling for external APIs.
- Fix frontend error handling and conversation history.
- Stop generating the graph PNG on every request.
- Restrict CORS origins.
- Add `.env.example`.
- Add a proper README with local setup and architecture.

**Acceptance criteria:**

- A request succeeds end-to-end.
- Missing API keys produce clear configuration errors.
- External API failures are surfaced without silently returning incomplete plans.
- The API returns a stable JSON response shape.

### Phase 1 - Introduce a structured travel domain model

**Goal:** Stop returning unstructured Markdown as the primary output.

Create Pydantic models such as:

```text
TripRequest
- origin
- destination
- start_date
- end_date
- travellers
- budget
- currency
- interests
- dietary_preferences
- mobility_constraints
- accommodation_preference

TravelPlan
- summary
- assumptions
- itinerary_days
- accommodation_options
- restaurants
- activities
- transportation
- budget_breakdown
- weather
- safety_notes
- sources
- confidence
- generated_at
```

Each recommendation should include:

- Name
- Location
- Estimated cost
- Opening hours, if available
- Source URL
- Retrieved timestamp
- Confidence or freshness indicator

Structured outputs enable editing, validation, exports, UI components, database persistence, and automated evaluation.

### Phase 2 - Build a real multi-agent workflow

Use a supervisor-led graph rather than independent agents chatting freely.

Recommended agents:

#### 1. Intake Agent

Extracts and validates:

- Destination
- Dates
- Budget
- Traveller profile
- Preferences
- Missing information

#### 2. Research Agent

Collects:

- Attractions
- Restaurants
- Hotels
- Activities
- Transportation
- Local constraints

#### 3. Itinerary Agent

Creates a day-by-day plan while considering:

- Geography
- Opening hours
- Travel time
- Energy level
- Budget
- Weather

#### 4. Budget Agent

Calculates:

- Accommodation
- Food
- Transportation
- Activities
- Taxes and fees
- Contingency
- Per-person and per-day costs

#### 5. Safety and Compliance Agent

Checks:

- Weather risks
- Travel advisories
- Visa requirements
- Health requirements
- Unsafe or unrealistic activities
- Contradictions in the plan

#### 6. Critic/Verifier Agent

Reviews the final plan for:

- Unsupported claims
- Invalid dates
- Duplicate locations
- Impossible travel times
- Budget inconsistencies
- Missing citations

The supervisor should decide which agents run and whether additional research is needed.

### Phase 3 - Add MCP integrations

Implement separate MCP servers or adapters with narrow, typed interfaces.

Suggested initial MCPs:

1. **Places MCP**
   - Search attractions
   - Search restaurants
   - Search hotels
   - Retrieve ratings and opening hours

2. **Weather MCP**
   - Current weather
   - Historical climate
   - Forecast
   - Weather alerts

3. **Maps MCP**
   - Distance matrix
   - Travel time
   - Route optimization
   - Neighbourhood clustering

4. **Currency MCP**
   - Exchange rates
   - Historical rates
   - Currency conversion

5. **Travel Advisory MCP**
   - Visa information
   - Safety advisories
   - Entry requirements

6. **Calendar MCP**
   - Export itinerary events
   - Detect conflicts
   - Add travel reminders

Every MCP tool should define:

- Input schema
- Output schema
- Authentication requirements
- Timeout
- Retry policy
- Rate-limit behavior
- Source metadata
- Cache duration

### Phase 4 - Add persistence and user features

Add PostgreSQL for:

- Users
- Trips
- Trip versions
- Preferences
- Agent runs
- Tool calls
- Citations
- Feedback
- Evaluation results

Add Redis for:

- Short-lived research caching
- Rate-limit counters
- Background job state
- Session state

Important product features:

- Save and reopen trips
- Edit individual itinerary days
- Regenerate only one day
- Change budget and recalculate
- Compare two plans
- Duplicate a trip
- Export Markdown, PDF, and `.ics`
- Share a read-only itinerary
- Maintain plan version history

### Phase 5 - Improve the user experience

Upgrade the current Streamlit interface from a chat-only screen.

Recommended pages:

- Trip setup wizard
- Itinerary overview
- Interactive day-by-day timeline
- Map view
- Budget dashboard
- Weather and safety panel
- Sources and confidence panel
- Saved trips
- Agent activity/debug view

Useful interactions:

- "Make this cheaper"
- "Replace museums with outdoor activities"
- "Reduce walking"
- "Add a free day"
- "Avoid this neighbourhood"
- "Re-plan because of rain"
- "Optimize for food"
- "Show only verified recommendations"

Use streaming responses and display agent progress such as:

```text
Understanding preferences
Researching destination
Checking weather
Optimizing routes
Validating budget
Verifying recommendations
```

### Phase 6 - Reliability, safety, and security

Add:

- API key validation at startup
- Secret management through environment variables
- Request authentication
- Per-user authorization
- Input length limits
- Prompt-injection filtering for retrieved content
- SSRF protection for URLs
- Tool allowlists
- MCP server authentication
- Rate limits
- Request IDs
- Audit logs
- PII minimization
- Safe handling of travel advisories

Never allow an agent to:

- Make bookings without explicit approval
- Send emails without confirmation
- Spend money automatically
- Treat generated prices as guaranteed
- Present uncertain information as fact

### Phase 7 - Evaluation and observability

This is one of the strongest CV differentiators.

Add tracing with OpenTelemetry or Langfuse.

Track:

- End-to-end latency
- Agent latency
- Token usage
- Tool success rate
- MCP failures
- Cache hit rate
- Cost per trip
- Retry counts
- User feedback
- Plan regeneration rate

Create an evaluation dataset containing travel requests such as:

- Budget travel
- Family travel
- Accessibility constraints
- Multi-city trips
- Bad-weather scenarios
- Very short trips
- Conflicting preferences
- Unsupported destinations

Score each result for:

- Schema validity
- Factual grounding
- Citation coverage
- Budget arithmetic
- Route feasibility
- Constraint satisfaction
- Weather awareness
- Completeness
- Hallucination rate
- Response latency

Create a regression test that fails if quality drops between model or prompt changes.

### Phase 8 - Production deployment

Suggested deployment:

- FastAPI on Render, Railway, Fly.io, or AWS
- Streamlit on Streamlit Community Cloud or a container platform
- PostgreSQL database
- Redis instance
- Docker and Docker Compose for local development
- GitHub Actions for CI/CD
- Sentry or OpenTelemetry for monitoring

CI pipeline:

1. Formatting
2. Linting
3. Type checking
4. Unit tests
5. API tests
6. MCP contract tests
7. Evaluation subset
8. Docker build
9. Deployment

## Suggested repository structure

```text
ai_travel_planner/
├── app/
│   ├── api/
│   ├── ui/
│   └── dependencies.py
├── domain/
│   ├── models.py
│   ├── policies.py
│   └── validators.py
├── agents/
│   ├── supervisor.py
│   ├── intake.py
│   ├── research.py
│   ├── itinerary.py
│   ├── budget.py
│   ├── safety.py
│   └── verifier.py
├── orchestration/
│   ├── graph.py
│   ├── state.py
│   └── checkpoints.py
├── mcp_servers/
│   ├── places/
│   ├── weather/
│   ├── maps/
│   ├── currency/
│   └── advisories/
├── infrastructure/
│   ├── database.py
│   ├── cache.py
│   ├── tracing.py
│   └── settings.py
├── prompts/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── evaluations/
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Recommended execution order

1. Stabilize the current workflow.
2. Introduce structured Pydantic outputs.
3. Add database persistence.
4. Build the supervisor and three core agents.
5. Add Places, Weather, and Maps MCP integrations.
6. Add verifier and citation support.
7. Build the improved Streamlit UI.
8. Add observability and evaluations.
9. Add authentication and production security.
10. Deploy with CI/CD and publish technical documentation.

## CV-level project description

> Built a production-oriented multi-agent AI travel planning platform using LangGraph, MCP servers, FastAPI, Streamlit, PostgreSQL, Redis, and OpenTelemetry. Implemented specialized research, itinerary, budgeting, safety, and verification agents with structured outputs, citation tracking, route optimization, budget validation, caching, human approval workflows, and automated evaluation benchmarks.

The most important principle is: **demonstrate measurable engineering quality, not just the number of agents or MCP servers.** A smaller system with reliable structured outputs, citations, evaluation scores, observability, and deployment will look more impressive than a large collection of loosely connected agents.
