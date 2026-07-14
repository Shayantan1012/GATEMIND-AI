# GATEMIND-AI: Functional and Non-Functional Requirements

## 1. Document Information

| Field | Value |
|---|---|
| Project | GATEMIND-AI |
| Document type | Software Requirements Specification (SRS) summary |
| Product type | AI-powered GATE preparation and assessment platform |
| Primary users | GATE aspirants and platform administrators |
| Author | Shayantan Biswas |
| Repository | [Shayantan1012/GATEMIND-AI](https://github.com/Shayantan1012/GATEMIND-AI) |
| Version | 1.0 |

## 2. Purpose and Scope

GATEMIND-AI is a full-stack learning platform designed to help GATE aspirants prepare through mock examinations, performance analysis, document-based doubt solving, and personalized AI assistance.

The system allows students to:

- Create and securely manage accounts
- Attempt GATE-oriented mock tests
- Track subject-wise strengths, weaknesses, and preparation progress
- Upload study materials and ask questions about them
- Receive retrieval-grounded answers with citations
- Maintain separate, persistent AI conversations

The system allows administrators to:

- Manage staff, students, questions, and mock tests
- Publish tests and inspect platform analytics
- Upload and manage educational documents
- Monitor user activity and performance
- Perform controlled platform-maintenance operations

This document aligns the original project specification with the current repository. Capabilities that are not fully implemented are retained as planned requirements and clearly marked.

## 3. Requirement Conventions

### Priority

| Priority | Meaning |
|---|---|
| Must | Required for the core product to operate |
| Should | Important, but the first release can operate without it |
| Could | Desirable enhancement |

### Implementation status

| Status | Meaning |
|---|---|
| Implemented | Present in the current project |
| Partial | Present with limitations or incomplete coverage |
| Planned | Included in product scope but not currently complete |

## 4. Actors

| Actor | Description |
|---|---|
| Student | A registered GATE aspirant using mock tests, analytics, document upload, and AI chat |
| Administrator | Authorized platform operator managing users, content, tests, and analytics |
| Super administrator | Administrator with authority to manage staff and sensitive maintenance operations |
| AI provider | Configured OpenAI, Groq, Hugging Face, or local fallback service |
| Notification provider | SMS or email service used for OTP and account notifications |
| Database | MongoDB persistence layer for users, questions, tests, RAG content, and history |

## 5. Functional Requirements

### 5.1 User Account and Authentication

#### FR-AUTH-01: Student registration

| Attribute | Requirement |
|---|---|
| Description | The system shall allow a new student to create an account. |
| Input | Full name, email, password, mobile number, branch, and target GATE year |
| Validation | Mandatory fields, valid email format, password strength, supported branch, and non-duplicate email |
| Priority | Must |
| Status | Implemented |

Acceptance criteria:

- Registration is rejected when a required field is missing.
- Email addresses are normalized before duplicate checking.
- Passwords must contain at least eight characters, including letters and numbers.
- Passwords are hashed before persistence.
- The account is not activated until OTP verification succeeds.

#### FR-AUTH-02: OTP verification

The system shall generate and deliver an OTP during registration and shall activate the account only after successful OTP verification.

- Priority: Must
- Status: Implemented
- OTP preview may be enabled only in development environments.
- Expired or invalid OTPs shall be rejected.

#### FR-AUTH-03: Student login

The system shall authenticate active students using email and password and return an access token and refresh token after successful authentication.

- Priority: Must
- Status: Implemented
- Invalid credentials shall return a generic authentication error.
- Blocked or deactivated accounts shall not be allowed to log in.

#### FR-AUTH-04: Token refresh

The system shall accept a valid refresh token and issue a new access token.

- Priority: Must
- Status: Implemented
- Access tokens expire after 30 minutes.
- Refresh tokens expire after seven days.
- An access token shall not be accepted as a refresh token.

#### FR-AUTH-05: Logout

The system shall allow a student to log out by invalidating the matching active refresh-token session.

- Priority: Must
- Status: Implemented

#### FR-AUTH-06: Password recovery

The system shall support password recovery through OTP verification.

- Priority: Must
- Status: Implemented
- The response shall not disclose whether an arbitrary email address exists.
- The new password shall satisfy the configured password policy.

### 5.2 User Profile and Progress

#### FR-USER-01: View and update profile

The system shall allow authenticated students to view and update permitted profile fields.

- Priority: Must
- Status: Implemented

#### FR-USER-02: Change password

The system shall allow an authenticated student to change their password after validating the request.

- Priority: Must
- Status: Implemented

#### FR-USER-03: Profile image

The system shall allow a student to upload and associate a profile image with their account.

- Priority: Should
- Status: Implemented

#### FR-USER-04: Preparation progress

The system shall present the student's preparation percentage, mock-test count, preferred subjects, weak subjects, strong subjects, and subject-level performance.

- Priority: Must
- Status: Implemented

#### FR-USER-05: Test history

The system shall allow a student to view previous mock-test attempts and results.

- Priority: Must
- Status: Implemented

### 5.3 Document and Image Upload

#### FR-DOC-01: Supported uploads

The system shall accept study material in the following formats:

- PDF
- TXT and Markdown
- CSV and JSON
- PNG
- JPG and JPEG
- WebP

- Priority: Must
- Status: Implemented

#### FR-DOC-02: Upload validation

The system shall reject unsupported formats, missing files, unauthorized uploads, and requests exceeding the configured maximum size.

- Priority: Must
- Status: Implemented
- Default maximum request size: 25 MiB

#### FR-DOC-03: Text extraction

The system shall select an appropriate parser and extract text and source metadata from every supported document.

- Priority: Must
- Status: Implemented

#### FR-DOC-04: Optical character recognition

The system shall extract text from supported images when Pillow and Tesseract OCR are available.

- Priority: Should
- Status: Partial
- The deployment environment must explicitly install and configure the OCR dependencies.

#### FR-DOC-05: Student document ownership

The system shall associate student uploads with the authenticated student and shall prevent one student from querying another student's private attachments.

- Priority: Must
- Status: Implemented

#### FR-DOC-06: Upload limit per chat request

The chat composer shall allow a student to upload a maximum of five files in one operation.

- Priority: Should
- Status: Implemented

### 5.4 RAG Document Indexing

#### FR-RAG-01: Chunking

The system shall divide extracted content into overlapping chunks before embedding.

- Priority: Must
- Status: Implemented
- Default chunk size: 900
- Default overlap: 150

#### FR-RAG-02: Embedding generation

The system shall generate a vector representation for each chunk using the configured embedding provider.

- Priority: Must
- Status: Implemented
- The system shall provide a deterministic local fallback when external credentials are unavailable.

#### FR-RAG-03: Indexed storage

The system shall store each chunk together with its embedding, document identifier, source, page information when available, owner, and other retrieval metadata.

- Priority: Must
- Status: Implemented

#### FR-RAG-04: Re-indexing and deletion

Authorized users shall be able to list and delete indexed documents. Deleting a document shall also make its chunks unavailable for retrieval.

- Priority: Must
- Status: Implemented

#### FR-RAG-05: Branch and metadata indexing

The system should support branch-wise and metadata-based classification of administrator-provided materials.

- Priority: Should
- Status: Partial

### 5.5 Intelligent Chatbot

#### FR-CHAT-01: Context-grounded question answering

The system shall accept a student question, retrieve relevant context, and generate an answer grounded in the supplied context.

- Priority: Must
- Status: Implemented

#### FR-CHAT-02: Hybrid retrieval

The system shall combine semantic similarity and lexical term overlap when ranking candidate chunks.

- Priority: Must
- Status: Implemented
- Current weighting: 75% semantic score and 25% lexical score
- The system retrieves additional candidates before reranking and returns the configured top-k results.

#### FR-CHAT-03: Retrieval filters

The student shall be able to restrict a question to selected documents. The backend shall validate ownership before applying document filters.

- Priority: Must
- Status: Implemented

#### FR-CHAT-04: Citations

Every grounded answer shall include citations identifying the retrieved document, source, page number when available, and chunk.

- Priority: Must
- Status: Implemented

#### FR-CHAT-05: Conversation management

The system shall allow students to:

- Create a conversation
- List their conversations
- View messages in a conversation
- Continue a conversation using recent history
- Delete a conversation

- Priority: Must
- Status: Implemented

#### FR-CHAT-06: Context retention

The system shall provide a bounded amount of recent conversation history to the model for follow-up questions.

- Priority: Must
- Status: Implemented
- The current service loads recent messages and includes up to the last six exchanges in model context.

#### FR-CHAT-07: Answer styles

The chatbot should respond to requests for short answers, detailed explanations, step-by-step solutions, formulas, and numerical reasoning when the retrieved evidence is sufficient.

- Priority: Should
- Status: Partial
- Answer style is currently guided by the user's natural-language instruction rather than a dedicated mode selector.

#### FR-CHAT-08: Hallucination control

The chatbot shall be instructed to use only retrieved context, mention uncertainty, and refer to citations.

- Priority: Must
- Status: Implemented

#### FR-CHAT-09: AI question generation

The system should generate topic- and difficulty-based MCQ, MSQ, and NAT practice questions from approved materials.

- Priority: Should
- Status: Planned

### 5.6 Question Bank and Mock Tests

#### FR-TEST-01: Question management

Authorized administrators shall be able to create and list question-bank entries with their type, subject, answer, marks, and evaluation data.

- Priority: Must
- Status: Implemented

#### FR-TEST-02: Supported question types

The system shall support the GATE-relevant question types used by its evaluation strategies, including MCQ, MSQ, and NAT where configured.

- Priority: Must
- Status: Implemented

#### FR-TEST-03: Mock-test management

Administrators shall be able to create, list, update, delete, and publish mock tests.

- Priority: Must
- Status: Implemented

#### FR-TEST-04: Published-test access

Students shall be able to list and retrieve tests that are available for participation.

- Priority: Must
- Status: Implemented

#### FR-TEST-05: Test submission and evaluation

Students shall be able to submit answers and elapsed time. The system shall evaluate the answers using the strategy for each question type.

- Priority: Must
- Status: Implemented

#### FR-TEST-06: Result storage

The system shall store the test score, awarded marks, correctness, unanswered questions, time taken, and subject-wise breakdown.

- Priority: Must
- Status: Implemented

#### FR-TEST-07: Negative marking

The evaluation system shall apply the configured negative-marking rule to incorrect answers where applicable.

- Priority: Must
- Status: Implemented

### 5.7 Personalization and Analytics

#### FR-PERS-01: Subject-wise analysis

After a test submission, the system shall calculate subject-level score, total marks, correct answers, incorrect answers, unanswered questions, and percentage.

- Priority: Must
- Status: Implemented

#### FR-PERS-02: Learning-profile update

The system shall update the student's performance profile after mock-test evaluation.

- Priority: Must
- Status: Implemented

#### FR-PERS-03: Personalized RAG context

The chatbot shall receive relevant profile information, including weak and strong subjects, so it can adapt explanations to the student.

- Priority: Should
- Status: Implemented

#### FR-PERS-04: Recommendation system

The system should recommend weak topics, relevant previous-year questions, important subjects, and practice material based on student performance.

- Priority: Should
- Status: Partial

#### FR-PERS-05: Progress dashboard

The system shall display completed tests, preparation progress, performance statistics, weak subjects, strong subjects, and subject-level results.

- Priority: Must
- Status: Implemented

#### FR-PERS-06: Bookmarking

Students should be able to bookmark questions, notes, chatbot answers, and mock-test questions for later revision.

- Priority: Could
- Status: Planned

### 5.8 Administration

#### FR-ADMIN-01: Administrator authentication

The system shall provide separate administrator registration, login, logout, access-token refresh, and authorization workflows.

- Priority: Must
- Status: Implemented

#### FR-ADMIN-02: Secure administrator bootstrap

The first administrator may initialize the platform. Later administrator registrations shall require the configured bootstrap token or authorization from a privileged administrator.

- Priority: Must
- Status: Implemented

#### FR-ADMIN-03: Staff management

Authorized administrators shall be able to create, list, and remove administrator staff according to role permissions.

- Priority: Must
- Status: Implemented

#### FR-ADMIN-04: User monitoring

Administrators shall be able to view user information and platform-level user statistics without receiving plaintext passwords or secret tokens.

- Priority: Must
- Status: Implemented

#### FR-ADMIN-05: Dashboard analytics

The admin dashboard shall summarize users, administrators, questions, tests, performance records, and indexed documents.

- Priority: Must
- Status: Implemented

#### FR-ADMIN-06: Educational-content management

Administrators shall be able to upload, list, and delete GATE notes, previous-year questions, expert material, and other approved documents used by retrieval.

- Priority: Must
- Status: Implemented

#### FR-ADMIN-07: Audit logging

Sensitive administrator operations shall generate audit records containing the actor, action, relevant target, and time.

- Priority: Should
- Status: Implemented

#### FR-ADMIN-08: Storage maintenance

Only an authorized administrator shall be able to initiate controlled cleanup of generated logs, test output, and managed storage.

- Priority: Should
- Status: Implemented

## 6. Non-Functional Requirements

### 6.1 Performance

| ID | Requirement | Target/measurement |
|---|---|---|
| NFR-PERF-01 | Standard API operations should respond quickly under normal load. | 95th percentile below 1 second, excluding uploads and AI calls |
| NFR-PERF-02 | RAG responses should be delivered within an acceptable interactive interval. | Target 3-5 seconds when providers and document volume permit; otherwise show progress or stream output |
| NFR-PERF-03 | Document ingestion shall not block unrelated requests for long-running files. | Move large extraction and embedding jobs to a background queue in scaled deployment |
| NFR-PERF-04 | Retrieval shall return only the configured number of final chunks. | Default top-k: 5 |
| NFR-PERF-05 | File requests shall be bounded. | Default maximum: 25 MiB |

### 6.2 Scalability

| ID | Requirement |
|---|---|
| NFR-SCALE-01 | The service shall support horizontal scaling without relying on process-local user state. |
| NFR-SCALE-02 | OTP and pending-registration state should be moved to Redis or another shared TTL store before multiple Gunicorn workers or backend instances are enabled. |
| NFR-SCALE-03 | Retrieval should migrate from in-process scoring of all candidates to an indexed vector-search service as the corpus grows. |
| NFR-SCALE-04 | Uploaded files should migrate to durable object storage for multi-instance deployment. |
| NFR-SCALE-05 | The modular architecture shall allow authentication, ingestion, RAG, testing, and analytics to be separated into services when operational scale requires it. |

### 6.3 Security

| ID | Requirement |
|---|---|
| NFR-SEC-01 | Passwords shall be stored only as secure hashes. |
| NFR-SEC-02 | Protected endpoints shall validate token signature, expiration, token type, subject type, and required role. |
| NFR-SEC-03 | Production shall reject default JWT secrets, mock databases, and localhost-only database configuration. |
| NFR-SEC-04 | All production traffic shall use HTTPS. |
| NFR-SEC-05 | CORS shall permit only explicitly configured frontend origins. |
| NFR-SEC-06 | Uploaded filenames and content shall be validated and stored outside directly executable locations. |
| NFR-SEC-07 | Student document access shall be scoped by authenticated ownership. |
| NFR-SEC-08 | OTPs shall expire, have attempt limits, and be stored in hashed form in a shared production store. |
| NFR-SEC-09 | Authentication and AI endpoints should implement per-user/IP rate limiting. |
| NFR-SEC-10 | Secrets shall be stored in environment variables or a managed secret store and never committed. |
| NFR-SEC-11 | AI input shall be treated as untrusted and protected against prompt injection and unintended data disclosure. |
| NFR-SEC-12 | Rendered AI Markdown shall be sanitized to reduce XSS risk. |

MongoDB is used rather than SQL; therefore the relevant injection risk is NoSQL/operator injection. Repository queries must not accept arbitrary client-supplied MongoDB operators.

### 6.4 Reliability and Recovery

| ID | Requirement |
|---|---|
| NFR-REL-01 | The production container shall expose a health endpoint and automated health check. |
| NFR-REL-02 | Service errors shall return a consistent JSON response without leaking stack traces or secrets. |
| NFR-REL-03 | MongoDB data shall be backed up regularly with a tested restoration procedure. |
| NFR-REL-04 | Uploaded documents shall persist across container replacement. |
| NFR-REL-05 | External AI or notification failure shall be handled without corrupting application state. |
| NFR-REL-06 | Long-running ingestion should be retryable and idempotent. |
| NFR-REL-07 | Logs shall include enough context to diagnose a failure without containing passwords, tokens, OTPs, or API keys. |

### 6.5 Availability

| ID | Requirement |
|---|---|
| NFR-AVL-01 | The production platform should be accessible continuously except during planned maintenance. |
| NFR-AVL-02 | A production service-level objective should target at least 99.5% monthly availability. |
| NFR-AVL-03 | Deployment shall perform health verification before being considered successful. |
| NFR-AVL-04 | Future zero-downtime deployment shall retain the previous healthy version until the new version passes readiness checks. |

### 6.6 Usability and Accessibility

| ID | Requirement |
|---|---|
| NFR-USE-01 | Navigation shall be understandable to a first-time GATE aspirant without training. |
| NFR-USE-02 | The interface shall be responsive across desktop, tablet, and mobile viewports. |
| NFR-USE-03 | Forms shall provide clear validation and recovery messages. |
| NFR-USE-04 | Long AI or upload operations shall show progress and shall not appear frozen. |
| NFR-USE-05 | Interactive controls shall support keyboard navigation, visible focus, and meaningful accessible labels. |
| NFR-USE-06 | Color shall not be the sole method of communicating correctness, failure, or status. |

### 6.7 Maintainability

| ID | Requirement |
|---|---|
| NFR-MAIN-01 | HTTP controllers, domain services, repositories, models, schemas, and utilities shall remain separated. |
| NFR-MAIN-02 | New parsers, embedding providers, retrievers, and evaluators should be introduced through existing abstractions and factories. |
| NFR-MAIN-03 | Configuration shall be environment-based and shall not require source-code edits between environments. |
| NFR-MAIN-04 | Public API behavior and setup procedures shall be documented. |
| NFR-MAIN-05 | Reusable frontend behavior shall be implemented as focused components or centralized service functions. |
| NFR-MAIN-06 | Code changes shall pass automated tests before production deployment. |

### 6.8 Testability and Quality

| ID | Requirement |
|---|---|
| NFR-TEST-01 | Business services shall receive repositories and external services through dependency injection. |
| NFR-TEST-02 | Tests shall run without a production database through MongoMock or an isolated test database. |
| NFR-TEST-03 | Authentication tests shall cover invalid credentials, expiration, authorization, OTP failure, and logout. |
| NFR-TEST-04 | RAG tests shall separately validate ingestion, retrieval, ownership filters, citation generation, and LLM integration. |
| NFR-TEST-05 | Critical user flows shall have integration tests. |
| NFR-TEST-06 | Production releases should include frontend and end-to-end smoke testing. |

### 6.9 Compatibility

The latest stable versions of the following platforms should be supported:

- Google Chrome
- Microsoft Edge
- Mozilla Firefox
- Chromium-based Android browsers
- Mobile Safari

The backend shall run in a Linux container, while local development should remain possible on Windows, Linux, and macOS.

### 6.10 AI Quality and Safety

| ID | Requirement | Suggested validation |
|---|---|---|
| NFR-AI-01 | Answers shall be grounded in retrieved evidence. | Faithfulness evaluation on a curated GATE question set |
| NFR-AI-02 | Citations shall reference chunks that support the answer. | Manual and automated citation precision |
| NFR-AI-03 | Retrieval shall surface relevant material within top-k results. | Precision@K, Recall@K, and Mean Reciprocal Rank |
| NFR-AI-04 | The assistant shall state uncertainty when evidence is missing or conflicting. | Unsupported-question test set |
| NFR-AI-05 | Conversation context shall remain bounded. | Token-budget and latency monitoring |
| NFR-AI-06 | Student-specific information shall not leak between accounts. | Multi-user isolation tests |
| NFR-AI-07 | Changing the embedding model shall trigger controlled re-indexing. | Embedding-version compatibility checks |
| NFR-AI-08 | OCR quality shall be measurable. | Character/word error rate on representative notes |

### 6.11 Observability

| ID | Requirement |
|---|---|
| NFR-OBS-01 | The system shall log request failures, deployment failures, ingestion failures, and AI provider errors. |
| NFR-OBS-02 | Production monitoring should track request latency, error rate, uptime, database health, RAG latency, retrieval volume, and LLM usage. |
| NFR-OBS-03 | Alerts should be configured for health-check failure, high error rate, resource exhaustion, and database unavailability. |
| NFR-OBS-04 | Logs and metrics shall exclude credentials and sensitive authentication data. |

### 6.12 Privacy and Data Retention

| ID | Requirement |
|---|---|
| NFR-PRIV-01 | The system shall collect only data necessary for account, assessment, personalization, and support features. |
| NFR-PRIV-02 | Users shall not access another user's private profile, conversations, test history, or documents. |
| NFR-PRIV-03 | A retention policy shall define how long chats, uploaded files, audit logs, and inactive accounts are stored. |
| NFR-PRIV-04 | Account deletion should remove or anonymize associated personal data according to the retention policy. |

## 7. External Interface Requirements

### 7.1 User interface

- React-based responsive web application
- Separate student and administrator experiences
- Clear status feedback for authentication, upload, evaluation, and chat operations
- Markdown, code, table, and mathematical-expression rendering

### 7.2 Backend interface

- JSON REST API under `/api`
- Multipart form requests for file uploads
- Bearer-token authorization for protected endpoints
- Consistent success and error response structures

### 7.3 External services

- MongoDB or MongoDB Atlas
- Optional OpenAI, Groq, and Hugging Face services
- Optional Twilio SMS delivery
- Optional SMTP email delivery
- Optional Tesseract OCR
- Vercel for frontend hosting
- AWS EC2 and Docker for backend hosting

## 8. Constraints and Assumptions

- The current Mongo vector adapter scores candidate chunks in application code; this is suitable for small datasets but not a large production corpus.
- The similarity implementation assumes normalized embeddings when using a dot product as cosine similarity.
- Pending registrations and OTP state are currently process-local. A backend restart can invalidate pending verification.
- The production Docker configuration currently uses one Gunicorn worker to avoid inconsistent process-local state.
- OCR depends on optional system packages that are not guaranteed by Python dependencies alone.
- Response time depends on document size, corpus size, selected AI provider, network conditions, and provider availability.
- HTTPS, a reverse proxy, production secret management, rate limiting, and backup automation must be configured before handling real users.

## 9. Recommended Release Scope

### Release 1: Core platform

- Authentication and user profiles
- Admin and question-bank management
- Mock tests and performance analysis
- Document ingestion and hybrid RAG
- Conversation history and citations
- Docker/EC2 backend and Vercel frontend

### Release 2: Production hardening

- Redis-backed OTP and rate limiting
- MongoDB Atlas Vector Search
- Object storage for uploads
- HTTPS reverse proxy
- Monitoring, alerts, backups, and recovery testing
- Expanded frontend and end-to-end testing

### Release 3: Learning intelligence

- AI-generated MCQ, MSQ, and NAT practice sets
- Explicit answer-mode selection
- Advanced recommendations
- Bookmarking and revision collections
- Cross-encoder reranking
- Formal RAG and OCR evaluation dashboards

## 10. Requirement Traceability Summary

| Product area | Implemented | Partial | Planned |
|---|---:|---:|---:|
| Authentication and sessions | Yes | - | - |
| User profiles and progress | Yes | - | - |
| Document upload and parsing | Yes | OCR environment | - |
| RAG retrieval and citations | Yes | Large-scale vector search | - |
| Conversation management | Yes | Answer-mode controls | - |
| Mock tests and analytics | Yes | Recommendations | AI-generated tests |
| Administration | Yes | Branch-specific indexing | - |
| Personalization | Yes | Advanced recommendations | Bookmarking |
| Deployment | Yes | Production hardening | Multi-instance scaling |

---

This requirements document should be updated whenever product behavior, release scope, security controls, or measurable service targets change.
