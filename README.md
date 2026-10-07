# AuditFlow AI

An enterprise AI compliance and audit assistant that combines document retrieval, LangGraph-based agent orchestration, deterministic confidence evaluation, human review, and evidence-backed audit reports.

---

## Overview

AuditFlow AI is an enterprise-grade AI compliance and audit assistant designed to automate complex, manual compliance gap analysis workflows. Organizations can upload policy guidelines and regulatory standards, index them semantically, and ask compliance questions. The system leverages a structured LangGraph orchestration flow to plan audits, retrieve text chunks, identify control gaps, perform risk assessments, recommend remediation steps, evaluate confidence thresholds, and generate persistent, downloadable audit reports.

---

## Problem

Traditional enterprise compliance audits are manual, slow, and prone to errors. Compliance analysts must manually search through corporate policies, compare internal controls against complex regulatory standards, compile evidence, calculate risks, generate remediation recommendations, and produce final reports. This process lacks automated traceability and version control. AuditFlow AI automates these repetitive analytical steps while maintaining strict human-in-the-loop (HITL) gates for high-risk or low-confidence audits, ensuring compliance professionals remain the authoritative arbiters.

---

## Solution

AuditFlow AI implements a controlled, structured agent architecture to perform policy audits rather than a simple chatbot query. The solution decouples AI orchestration from state access, utilizing:
- **Structured Planning**: Planner agents outline specific controls to evaluate.
- **RAG-Backed Ingestion**: Chunks and indexes policies into a vector space with version control.
- **Deterministic Metrics**: Evaluates retrieval accuracy using mathematical confidence scoring.
- **Specialized Multi-Agent Graphs**: Sequentially analyzes compliance, calculates risk levels, and generates remediation checklists.
- **Persistent Reports**: Stores and version-tracks generated Markdown documents inside a Neon PostgreSQL database with evidence citations.

The React frontend communicates exclusively with the FastAPI REST API layer, shielding database instances, LLM providers, and vector databases from client-side vulnerability exposures.

---

## Key Features

- **Document Ingestion**: Seamless ingestion and text extraction support for TXT, PDF, and DOCX files.
- **Document Versioning**: Postgres metadata registry to track active, draft, and deprecated documents.
- **Version-Aware Retrievals**: Automatically filters vector search matches to target only the latest active document versions.
- **Qdrant Vector Indexes**: Low-latency semantic chunk queries mapping embeddings to vector weights.
- **Deterministic Confidence Engine**: Calculates evidence completeness across multiple variables.
- **LangGraph Orchestration**: State-saving compliance analysis, risk scoring, and recommendation generation pipeline.
- **Human-in-the-Loop Review**: Interrupts graph execution when confidence scores drop below thresholds, allowing manual review approval, rejection, or requests for more evidence.
- **Final Report Persistence**: Version-controlled SQLite/PostgreSQL report generation with evidence citations.
- **Markdown Report Generation**: Direct Markdown compilation and download endpoint.
- **React Dashboard**: Enterprise interface with api health checks, audit workspaces, review panels, and report viewers.

---

## System Architecture

```mermaid
flowchart TD

    User[User]
    Frontend[React Frontend]
    API[FastAPI API]

    PG[(Neon PostgreSQL)]
    QD[(Qdrant)]
    GROQ[Groq LLM]

    LG[LangGraph]
    INGEST[Document Ingestion]
    RETRIEVE[Retrieval Service]
    CONF[Confidence Engine]
    HITL[Human Review]
    REPORT[Report Generator]

    User --> Frontend
    Frontend --> API

    API --> INGEST
    INGEST --> PG
    INGEST --> QD

    API --> LG
    LG --> RETRIEVE
    RETRIEVE --> PG
    RETRIEVE --> QD

    LG --> GROQ
    RETRIEVE --> CONF
    LG --> HITL
    LG --> REPORT

    REPORT --> PG
```

---

## End-to-End Workflow

```mermaid
flowchart TD

    A[Upload Documents]
    B[Parse and Chunk]
    C[Generate Embeddings]
    D[Store Metadata in PostgreSQL]
    E[Store Vectors in Qdrant]
    F[Submit Audit Question]
    G[Planner]
    H[Retriever]
    I[Compliance Agent]
    J[Risk Agent]
    K[Recommendation Agent]
    L[Confidence Gate]
    M{Human Review Required?}
    N[Human Review]
    O[Report Generator]
    P[Persist Report]
    Q[Final Report]

    A --> B
    B --> C
    C --> D
    C --> E
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M -->|No| O
    M -->|Yes| N
    N -->|Approve| O
    N -->|Reject| Q
    N -->|More Evidence| Q
    O --> P
    P --> Q
```

---

## Architecture Components

AuditFlow AI is modularly split into a Python FastAPI backend, a vector retrieval pipeline, a LangGraph multi-agent flow, and a React frontend.

---

## Backend Architecture

The backend is built with **FastAPI** to expose REST endpoints. It handles parsing, vector insertions, graph processing, and reports compilation:
- ** lifespan Event**: Automatically boots Neon database schemas on startup and hooks Postgres checkpoint savers into LangGraph.
- ** lifespan checkpointer**: Utilizes `PostgresSaver` connection pools to manage and persist LangGraph thread states.

---

## Frontend Architecture

The frontend is a single-page React app built with **Vite**:
- **Routing**: Client-side parameter routing using `react-router-dom` to coordinate dashboards, documents lists, audits, reviews, and reports workspaces.
- **Unified Service Layer**: Centralized `api.js` HTTP helper maps configuration tokens using `import.meta.env.VITE_API_BASE_URL`.

---

## LangGraph Workflow

The orchestrator builds a sequential directed acyclic graph mapping state changes:
1. **Planner**: Evaluates the question intent and outlines a checklist of controls to analyze.
2. **Retriever**: Executes RAG retrievals to fetch matching policies and regulations.
3. **Compliance**: Compares the retrieved policies against the regulations to find compliance gaps.
4. **Risk**: Evaluates identified compliance gaps to determine Severity, Likelihood, and overall Risk Scores.
5. **Recommendation**: Proposes prioritized remediation steps with practical implementation checklists.
6. **Confidence Gate**: Determinisitically calculates evidence completeness. If scores fall below thresholds or if risks are critical, it flags `review_required = True`.
7. **Human Review**: Triggers a graph execution interrupt before this node. It waits for human interaction via the review workspace.
8. **Report**: Upon review approval (or if no review is required), it generates the persistent final report and writes it to PostgreSQL.

---

## Retrieval Architecture

The retrieval system coordinates data across relational metadata and vector spaces:
- **PostgreSQL**: Stores filename, file path, version, chunk count, and ingestion status. Resolves the latest uploaded version of each policy by default.
- **Qdrant**: Executes cosine similarity search matching text queries to chunk vectors.
- **Retrieval Flow**:
  1. The user asks a question.
  2. The system checks database metadata to identify the latest active version IDs.
  3. Qdrant performs a vector similarity search, filtered strictly by these active IDs.
  4. Matching chunks are transformed into evidence objects.
  5. Reranker filters these chunks to select the top-N evidence fragments.
  6. The confidence engine calculates the evidence reliability.

---

## Human-in-the-Loop Workflow

If the audit triggers `review_required`, execution pauses:
1. The state checkpoint is saved to PostgreSQL.
2. The audit state shifts to `review_required` and displays in the Reviews page.
3. Reviewers inspect read-only control findings, calculated risks, and recommendation checklists.
4. The reviewer selects an action:
   - **Approve** (`continue`): Continues the workflow, triggering the report node.
   - **Reject** (`terminate`): Halts the workflow immediately.
   - **Request More Evidence** (`retrieve_more_evidence`): Stops execution to request additional uploads.
5. The reviewer's decision, comment, and timestamp are written directly to Neon PostgreSQL.

---

## Report Generation

The report generation agent compiles the final state metadata:
- **Data Schema**: Formats findings, risk details, prioritizations, evidence citation sources, and review trails into a unified report.
- **Markdown Export**: Generates a clean Markdown representation that is returned via `GET /reports/{report_id}/download` for local download.

---

## Project Structure

```
AI-Audit-Assistant/
│
├── backend/
│   ├── app/
│   │   ├── agents/      # Specialized LLM agent prompt configurations
│   │   ├── api/         # FastAPI REST endpoint routers
│   │   ├── database/    # Neon database engine and schema models
│   │   ├── graph/       # LangGraph node definitions and workflow configurations
│   │   ├── models/      # Pydantic schemas for request/response validation
│   │   ├── services/    # Ingestion, retrieval, and confidence business logic
│   │   ├── utils/       # Global logger wrappers
│   │   └── config.py    # Settings singleton loading backend environment configurations
│   ├── tests/           # Integrated pytest suites
│   ├── requirements.txt # Python package list
│   └── main.py          # FastAPI application initialization
│
├── frontend/
│   ├── public/          # Static assets
│   ├── src/
│   │   ├── components/  # Page-specific card elements, tables, and scorecards
│   │   ├── pages/       # Dashboard, Documents, Audits, Reviews, and Reports views
│   │   ├── services/    # React api client integration services
│   │   ├── App.jsx      # Route management definitions
│   │   ├── index.css    # Dark enterprise styling and responsive layout configurations
│   │   └── main.jsx     # Vite client entrypoint
│   ├── package.json     # Node libraries package manifest
│   └── vite.config.js   # Vite react build config
│
├── README.md            # System documentation
└── .gitignore           # Version control ignores
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React (v19), Vite (v8), React Router Dom (v7) |
| **Backend** | FastAPI, Uvicorn |
| **Orchestration** | LangGraph, LangChain |
| **Vector DB** | Qdrant Client |
| **Database** | Neon PostgreSQL, SQLAlchemy |
| **LLM Interface** | Groq / ChatGroq |
| **Parsing & Parsing** | PyMuPDF, python-docx, SentenceTransformers |
| **Validation** | Pydantic (v2) |
| **Styling** | Vanilla CSS (Dark enterprise theme with gold accent `#FFD700`) |

---

## Prerequisites

- **Python**: v3.11.9+
- **Node.js**: v18.0.0+
- **npm**: v9.0.0+
- **Docker Desktop**: Required to host local Qdrant container
- **Neon Cloud Account**: Hosting Neon PostgreSQL database
- **Groq API Key**: For LLM processing

---

## Environment Variables

### Backend Environment (`backend/.env`)
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=qwen/qwen3.6-27b
DATABASE_URL=postgresql://neondb_owner:...@ep-sparkling-mud...neon.tech/neondb?sslmode=require
QDRANT_HOST=localhost
QDRANT_PORT=6335
QDRANT_COLLECTION=audit_documents
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
UPLOAD_DIR=data/uploads
REPORT_DIR=reports
```

### Frontend Environment (`frontend/.env`)
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Qdrant Setup

The project runs Qdrant inside a Docker container. The host port is configured to `6335` to avoid collisions:
1. Run the container:
   ```bash
   docker run -d `
     --name auditflow-qdrant `
     -p 6335:6333 `
     -v auditflow_qdrant_storage:/qdrant/storage `
     qdrant/qdrant
   ```
2. Verify that the container is running:
   ```bash
   docker ps
   ```
3. To stop or restart:
   ```bash
   docker stop auditflow-qdrant
   docker start auditflow-qdrant
   ```

---

## Neon PostgreSQL Setup

1. Sign up on [Neon Console](https://neon.tech/) and create a PostgreSQL database.
2. Retrieve the database connection URL connection string (make sure SSL Mode is enabled).
3. Insert this connection URL as `DATABASE_URL` in the `backend/.env`.
4. Database tables are generated automatically by FastAPI during server startup using SQLAlchemy metadata.

---

## Backend Setup

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Set up virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **CMD**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the FastAPI development server:
   ```bash
   venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

---

## Frontend Setup

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start Vite dev server:
   ```bash
   npm run dev
   ```
4. Access the interface:
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running the Application

1. **Terminal 1**: Verify Qdrant Docker is running on port `6335`.
2. **Terminal 2**: Start the FastAPI backend on port `8000`.
3. **Terminal 3**: Start the React frontend on port `5173`.
4. Open the frontend URL. The navigation bar features a database connection status indicator that turns green when the health endpoint (`/health`) checks succeed.

---

## API Endpoints

| Tag | Method | Endpoint | Description |
|---|---|---|---|
| **Health** | GET | `/health` | Returns connectivity status for Groq, PostgreSQL, Qdrant, and embeddings. |
| **Document Ingestion** | POST | `/upload` | Ingests policy/regulation documents. |
| **Document Ingestion** | GET | `/documents` | Lists metadata and versions of all uploaded documents. |
| **Document Ingestion** | DELETE | `/documents/{document_id}` | Removes a document from PostgreSQL and deletes its Qdrant vectors. |
| **RAG Retrieval** | POST | `/search` | Queries Qdrant vectors directly. |
| **RAG Retrieval** | POST | `/retrieve` | Returns version-filtered policy/regulation chunks. |
| **Audit Workflow** | POST | `/audit` | Initiates the multi-agent compliance evaluation graph. |
| **Human Review** | GET | `/review/{review_id}` | Retrieves data for a pending manual verification check. |
| **Human Review** | POST | `/review/{review_id}/decision` | Submits reviewer decisions (approve, reject, request evidence). |
| **Reports** | GET | `/reports/{report_id}` | Retrieves the finalized audit report. |
| **Reports** | GET | `/reports/{report_id}/evidence` | Lists RAG evidence provenance references. |
| **Reports** | GET | `/reports/{report_id}/download` | Downloads the compiled audit report as a Markdown document. |

---

## Testing

### Backend Tests
Verify the complete LangGraph, database, and retrieval system using the existing pytest suite (74 passing tests baseline):
```bash
cd backend
venv\Scripts\pytest tests/
```

### Frontend Builds
Confirm compilation parameters and check styling:
```bash
cd frontend
npm run build
```

---

## Example Workflow

1. **Ingestion**: The user uploads `access_control_policy.txt` (Version 2.1.0).
2. **Indexing**: Chunks are generated and stored in Qdrant with document IDs mapped to PostgreSQL metadata.
3. **Audit Submission**: The user submits the compliance audit question: `"Does our access control policy require MFA for AWS administrator privileges?"`
4. **Planning & Retrieval**: The Planner Agent scopes the audit checks. The Retriever fetches relevant chunks from `access_control_policy.txt` (Version 2.1.0) and ISO 27001 standard frameworks.
5. **Evaluation**: Gaps are identified, risk levels calculated, and prioritized remediation actions generated.
6. **Confidence Check**: If confidence is high, the system routes directly to report generation. If low, it triggers a Human Review Request ID.
7. **Resolution**: The reviewer approves the audit, resuming the graph to write the final report to PostgreSQL.
8. **Final Document**: The user opens the report workspace to view finding summaries and downloads the file as a Markdown report.

---

## Error Handling

- **Groq HTTP 429**: Rate limits can block audit completions. If this occurs, the API returns a `400` or `429` status code, and the UI displays a clean error banner rather than crashing or exposing logs.
- **Dependency Failures**: If PostgreSQL or Qdrant connections fail, the health endpoint reflects a disconnected state, and the UI alerts the user that background services are temporarily down.
- **Missing Resources**: Accessing invalid Review IDs or Report IDs triggers custom FastAPI exceptions, which the frontend displays as informative warning cards (e.g. "The requested audit report could not be located").

---

## Security Considerations

- **Server-Side API Keys**: Private keys (`GROQ_API_KEY`, `DATABASE_URL`) are loaded from `backend/.env` and remain hidden on the server.
- **Frontend Isolation**: The React frontend communicates strictly with API controllers. It has no direct database or vector store access.
- **Safe Sandbox Gating**: Mock reviews and mock reports used during UI testing are guarded with `import.meta.env.DEV` to block exposure in production bundles.

---

## Current Implementation Status

### Backend (100% Complete)
- **RAG Ingestion Pipeline**: Ingestion, PyMuPDF parsing, chunking, and embedding.
- **Postgres Checkpointer**: State persistence during multi-agent graph runs.
- **Orchestration Workflow**: Modular planner, compliance checker, risk evaluators, and report compilation nodes.
- **HITL Integration**: Resumable human review decisions.

### Frontend (100% Complete)
- **Document Management**: Listing, uploading, and deleting policies.
- **Audit Workspace**: Interactive query forms, live graph updates, and compliance matrices.
- **Human Review**: Comments and decision forms.
- **Report Workspace**: Executive summaries, findings, checklists, evidence details, and download hooks.

---

## Future Improvements

- **Role-Based Access**: Multi-tenant authorization (RBAC) to isolate workspace documents.
- **Audit History**: Direct listing registry to search past persisted reports.
- **Advanced Rerankers**: Upgraded transformer architectures for denser retrieval relevance.
- **Real-Time Workflows**: WebSockets integration to stream LangGraph execution nodes in real time.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
