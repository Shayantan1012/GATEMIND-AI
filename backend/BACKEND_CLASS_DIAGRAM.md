# GATEMIND AI Backend Class Diagram

This document reflects the backend currently implemented under `backend/app`.
It separates the full design into renderable Mermaid class diagrams so that the
relationships remain readable.

## Relationship Legend

- `*--` composition: the owner contains and controls the child lifecycle.
- `o--` aggregation: the class is wired with and uses a collaborator.
- `-->` association: a persistent domain relationship or reference.
- `..>` dependency: creates, calls, serializes, or otherwise depends on.
- `..|>` interface realization.
- `--|>` inheritance.

## 1. Domain Model

```mermaid
classDiagram
direction LR

class User {
  +str user_id
  +str full_name
  +str email
  +str password_hash
  +str mobile_number
  +Branch branch
  +int target_gate_year
  +bool is_email_verified
  +AccountStatus account_status
  +UserProfile user_profile
  +List~Session~ sessions
  +to_dict() dict
  +from_dict(data) User$
  +activate() void
}

class UserProfile {
  +str profile_id
  +List~str~ preferred_subjects
  +str profile_image
  +str headline
  +str bio
  +str college_name
  +int current_semester
  +int graduation_year
  +float daily_study_goal_hours
  +int weekly_mock_test_goal
  +int exam_goal_score
  +int total_mock_tests
  +List~str~ weak_subjects
  +List~str~ strong_subjects
  +dict subject_performance
  +float overall_progress
  +float performance_percentage
  +float preparation_progress
  +List~dict~ mock_test_history
  +to_dict() dict
  +from_dict(data) UserProfile$
}

class Admin {
  +str admin_id
  +str full_name
  +str email
  +str password_hash
  +str phone_number
  +AdminRole role
  +str employee_id
  +str job_title
  +str department
  +bool is_verified
  +AccountStatus account_status
  +List~Session~ sessions
  +datetime created_at
  +user_id str
  +to_dict() dict
  +from_dict(data) Admin$
  +create(data, password_hash) Admin$
}

class Session {
  +str session_id
  +str access_token
  +str refresh_token
  +datetime login_time
  +datetime expiry_time
  +bool is_active
  +to_dict() dict
  +from_dict(data) Session$
  +is_expired() bool
}

class Question {
  +str question_id
  +QuestionType question_type
  +str prompt
  +str subject
  +float marks
  +float negative_marks
  +object correct_answer
  +List~str~ options
  +str explanation
  +str source
  +str created_by
  +datetime created_at
  +to_dict() dict
  +public_dict() dict
  +from_dict(data) Question$
}

class MockTest {
  +str mock_test_id
  +str title
  +List~str~ question_ids
  +int duration_minutes
  +str created_by
  +bool is_published
  +str description
  +datetime created_at
  +to_dict() dict
  +from_dict(data) MockTest$
  +create(data, created_by) MockTest$
}

class PerformanceRecord {
  +str performance_id
  +str user_id
  +str mock_test_id
  +float score
  +float total_marks
  +int correct_count
  +int incorrect_count
  +int unanswered_count
  +dict subject_breakdown
  +List~dict~ answers
  +str mock_test_title
  +int time_taken_seconds
  +datetime attempted_at
  +percentage float
  +to_dict() dict
  +create(kwargs) PerformanceRecord$
}

class Citation {
  +str document_id
  +str source
  +int page_no
  +str chunk_id
  +to_dict() dict
}

class RAGResponse {
  +str answer
  +List~Citation~ citations
  +str query_type
  +datetime created_at
  +to_dict() dict
}

class AccountStatus {
  <<enumeration>>
  ACTIVE
  PENDING_VERIFICATION
  BLOCKED
  DEACTIVATED
  OTHER
}

class AdminRole {
  <<enumeration>>
  SUPER_ADMIN
  CONTENT_ADMIN
  MOCKTEST_ADMIN
  ANALYTICS_ADMIN
  SUPPORT_ADMIN
}

class Branch {
  <<enumeration>>
  CSE
  ECE
  EE
  ME
  CE
  OTHER
}

class QuestionType {
  <<enumeration>>
  MCQ
  MSQ
  NAT
}

class QueryType {
  <<enumeration>>
  TEXT
  IMAGE
  HYBRID
}

User *-- "0..1" UserProfile
User *-- "0..*" Session
Admin *-- "0..*" Session
User --> Branch
User --> AccountStatus
Admin --> AdminRole
Admin --> AccountStatus
Question --> QuestionType
MockTest --> "1..*" Question : question_ids
PerformanceRecord --> User : user_id
PerformanceRecord --> MockTest : mock_test_id
RAGResponse *-- "0..*" Citation
RAGResponse ..> QueryType : query_type string defaults to TEXT
```

## 2. Authentication, User, and Admin Services

```mermaid
classDiagram
direction LR

class UserRepository {
  <<interface>>
  +save(user)
  +find_by_email(email)
  +find_by_id(user_id)
  +update(user)
  +delete(user_id)
  +exists_by_email(email)
  +find_all(limit, skip)
  +count()
}

class MongoUserRepository {
  +collection
  +save(user) User
  +find_by_email(email) User
  +find_by_id(user_id) User
  +update(user) User
  +delete(user_id) bool
  +exists_by_email(email) bool
  +find_by_refresh_token(token) User
  +find_all(limit, skip) List~User~
  +count() int
}

class InMemoryUserRepository {
  -dict _users_by_id
  -dict _email_index
  +save(user)
  +find_by_email(email)
  +find_by_id(user_id)
  +update(user)
  +delete(user_id)
  +exists_by_email(email)
  +find_by_refresh_token(token)
  +find_all(limit, skip)
  +count()
}

class MongoAdminRepository {
  +collection
  +save(admin)
  +update(admin)
  +find_by_id(admin_id)
  +find_by_email(email)
  +find_by_refresh_token(token)
  +find_all(limit)
  +exists_by_email(email)
  +exists_by_employee_id(employee_id)
  +count()
  +delete_by_id(admin_id)
}

class MongoAuditRepository {
  +collection
  +save(event)
}

class AuthenticationService {
  +dict pending_users
  +register_user(data) Tuple~User,str~
  +authenticate_user(email, password) dict
  +logout_user(refresh_token) bool
  +forgot_password(email) str
  +reset_password(otp, new_password) bool
  +verify_otp(otp) User
  +refresh_token(refresh_token) str
}

class UserService {
  +get_user_profile(user_id)
  +update_profile(user_id, data)
  +update_profile_image(user_id, image_url)
  +change_password(user_id, old_password, new_password) bool
  +get_preparation_progress(user_id) dict
  +get_mock_test_history(user_id) list
}

class AdminAuthService {
  +register(data)
  -_generate_employee_id(role)
  +login(email, password)
  +logout(refresh_token)
}

class AdminDashboardService {
  +summary()
  +users_overview(limit, skip)
}

class AuditLogger {
  +log(actor_id, action, details)
}

class StorageMaintenanceService {
  +Path upload_folder
  +clear_logs_and_uploaded_documents()
}

class PasswordService {
  +hash_password(password) str
  +verify_password(raw, hashed) bool
  +validate_password_strength(password) bool
}

class JWTService {
  +str secret_key
  +str algorithm
  +generate_access_token(user, subject_type, role) str
  +generate_refresh_token(user, subject_type, role) str
  +validate_token(token) dict
  +extract_user_id(token) str
  +extract_subject(token) dict
  +refresh_token(refresh_token) str
}

class CheckEmail {
  +contains_necessary_character(email) bool$
}

class OTPVerificationService {
  -dict _otps
  +send_otp(user) str
  +verify_otp(otp) str
}

class SMSNotificationService {
  +send_sms(to_number, body) bool
  +send_otp_sms(to_number, otp) bool
  +send_reset_password_sms(to_number, otp) bool
}

class VerificationStrategy {
  <<interface>>
  +send_verification(user)
  +verify(token)
}

class EmailVerificationService {
  -dict _tokens
  -dict _otps
  +send_verification(user)
  +verify(token)
  +generate_email_token(user)
  +verify_email_token(token)
  +send_otp(user)
  +verify_otp(otp)
}

class EmailNotificationService {
  +send_email(to_email, subject, body) bool
  +send_otp_email(to_email, otp) bool
  +send_verification_email(to_email, link) bool
  +send_reset_password_email(to_email, link) bool
}

MongoUserRepository ..|> UserRepository
InMemoryUserRepository ..|> UserRepository
AuthenticationService o-- UserRepository
AuthenticationService o-- PasswordService
AuthenticationService o-- JWTService
AuthenticationService o-- OTPVerificationService : runtime verification
AuthenticationService ..> CheckEmail
AuthenticationService ..> User : creates and authenticates
AuthenticationService ..> UserProfile : creates
AuthenticationService ..> Session : creates
UserService o-- UserRepository
UserService o-- PasswordService
AdminAuthService o-- MongoAdminRepository
AdminAuthService o-- PasswordService
AdminAuthService o-- JWTService
AdminAuthService o-- AuditLogger
AdminAuthService ..> Admin : creates
AuditLogger o-- MongoAuditRepository
AdminDashboardService o-- MongoUserRepository
AdminDashboardService o-- MongoAdminRepository
AdminDashboardService o-- MongoQuestionRepository
AdminDashboardService o-- MongoPerformanceRepository
AdminDashboardService o-- MongoRAGRepository
OTPVerificationService o-- SMSNotificationService
EmailVerificationService ..|> VerificationStrategy
EmailVerificationService o-- EmailNotificationService

class MongoQuestionRepository
class MongoPerformanceRepository
class MongoRAGRepository
class User
class UserProfile
class Session
class Admin
```

`MongoUserRepository` is the runtime adapter. `InMemoryUserRepository`,
`EmailVerificationService`, and `EmailNotificationService` are implemented
alternatives but are not wired by `create_app`.

## 3. Mock-Test Subsystem

```mermaid
classDiagram
direction LR

class QuestionFactory {
  <<factory>>
  +create(data, created_by) Question$
}

class EvaluationStrategy {
  <<strategy>>
  +is_correct(expected, actual) bool
}

class MCQEvaluationStrategy {
  +is_correct(expected, actual) bool
}

class MSQEvaluationStrategy {
  +is_correct(expected, actual) bool
}

class NATEvaluationStrategy {
  +is_correct(expected, actual) bool
}

class QuestionEvaluator {
  +dict strategies
  +evaluate(question, actual_answer) dict
}

class QuestionBankService {
  +create_question(data, admin_id)
  +list_questions(subject)
  +create_mock_test(data, admin_id)
  +list_mock_tests()
  +update_mock_test(mock_test_id, data, admin_id)
  +publish_mock_test(mock_test_id)
  +delete_mock_test(mock_test_id)
  +get_mock_test_questions(mock_test) list
}

class MockTestService {
  +list_available()
  +get_test(mock_test_id)
  +submit(user_id, mock_test_id, answers, time_taken_seconds)
  +history(user_id)
}

class PerformanceAnalyzer {
  +analyze(results) dict
}

class PersonalizedRAGUpdater {
  +update(user_id, record)
}

class MongoQuestionRepository {
  +questions
  +mock_tests
  +save_question(question)
  +find_question(question_id)
  +delete_question(question_id)
  +find_questions(question_ids, subject)
  +save_mock_test(test)
  +find_mock_test(test_id)
  +delete_mock_test(test_id)
  +list_mock_tests(published_only)
  +count_questions()
  +count_mock_tests()
}

class MongoPerformanceRepository {
  +collection
  +save(record)
  +find_by_user(user_id, limit)
  +aggregate_user(user_id)
  +count()
}

class UserRepository {
  <<interface>>
}

class Question
class MockTest
class PerformanceRecord
class UserProfile

MCQEvaluationStrategy ..|> EvaluationStrategy
MSQEvaluationStrategy ..|> EvaluationStrategy
NATEvaluationStrategy ..|> EvaluationStrategy
QuestionEvaluator *-- MCQEvaluationStrategy
QuestionEvaluator *-- MSQEvaluationStrategy
QuestionEvaluator *-- NATEvaluationStrategy
QuestionEvaluator ..> Question
QuestionFactory ..> Question : creates
QuestionBankService o-- MongoQuestionRepository
QuestionBankService ..> QuestionFactory
QuestionBankService ..> MockTest : creates and manages
MockTestService o-- MongoQuestionRepository
MockTestService o-- MongoPerformanceRepository
MockTestService o-- QuestionEvaluator
MockTestService o-- PerformanceAnalyzer
MockTestService o-- PersonalizedRAGUpdater
MockTestService ..> PerformanceRecord : creates
PersonalizedRAGUpdater o-- UserRepository
PersonalizedRAGUpdater ..> UserProfile : observer-style update
MongoQuestionRepository ..> Question : persists
MongoQuestionRepository ..> MockTest : persists
MongoPerformanceRepository ..> PerformanceRecord : persists
```

## 4. RAG Subsystem

```mermaid
classDiagram
direction LR

class IndexingPipeline {
  <<template>>
  +execute(file_path, uploaded_by, metadata) dict
  +parse(file_path)*
  +process(documents)*
  +store(document_id, file_path, uploaded_by, chunks, metadata)*
}

class LangChainIndexingPipeline {
  +parse(file_path)
  +process(documents)
  +store(document_id, file_path, uploaded_by, chunks, metadata)
}

class DocumentParser {
  <<interface>>
  +parse(file_path) List~Document~
}

class PDFDocumentParser {
  +parse(file_path) List~Document~
}

class TextDocumentParser {
  +parse(file_path) List~Document~
}

class ImageDocumentParser {
  +parse(file_path) List~Document~
}

class DocumentParserFactory {
  <<factory>>
  +dict PARSERS
  +create(file_path) DocumentParser$
}

class ChunkingStrategy {
  <<strategy>>
  +split(documents) List~Document~
}

class RecursiveChunkingStrategy {
  +splitter
  +split(documents) List~Document~
}

class EmbeddingFactory {
  <<factory>>
  +create(config) Embeddings$
}

class LocalHashEmbeddings {
  +int dimensions
  +embed_documents(texts) List~Vector~
  +embed_query(text) Vector
}

class VectorStoreAdapter {
  <<adapter interface>>
  +add(chunks) int
  +search(query_vector, top_k, filters, query_text) List~dict~
}

class MongoVectorStoreAdapter {
  +add(chunks) int
  +search(query_vector, top_k, filters, query_text) List~dict~
}

class Retriever {
  <<interface>>
  +retrieve(query, filters) List~dict~
}

class HybridRetriever {
  +int top_k
  +retrieve(query, filters) List~dict~
}

class HybridReranker {
  +rerank(documents) List~dict~
}

class ContextBuilder {
  <<builder>>
  +build(documents, learning_profile) str
}

class LLMServiceFactory {
  <<factory>>
  +create(config) LLMService$
}

class LLMService {
  +model
  +generate(system_prompt, context, query) str
}

class GroqLLMService {
  +model
  +generate(system_prompt, context, query) str
}

class RAGChatService {
  +str SYSTEM_PROMPT
  +int top_k
  +create_conversation(user_id, title) dict
  +ask(user_id, query, filters, conversation_id) Tuple~RAGResponse,dict~
  +conversations(user_id) List~dict~
  +history(user_id, conversation_id) List~dict~
  +delete_conversation(user_id, conversation_id) bool
}

class MongoRAGRepository {
  +documents
  +chunks
  +chats
  +conversations
  +save_document(document)
  +save_chunks(chunks)
  +list_chunks(filters)
  +list_documents(limit)
  +list_documents_by_uploader(uploaded_by, limit)
  +find_documents_by_ids(document_ids)
  +find_document(document_id)
  +delete_document(document_id)
  +save_chat(chat)
  +list_chats(user_id, conversation_id, limit)
  +save_conversation(conversation)
  +find_conversation(conversation_id, user_id)
  +list_conversations(user_id, limit)
  +delete_conversation(conversation_id, user_id)
  +count_documents()
}

class UserRepository {
  <<interface>>
}

class RAGResponse
class Citation

LangChainIndexingPipeline --|> IndexingPipeline
PDFDocumentParser ..|> DocumentParser
TextDocumentParser ..|> DocumentParser
ImageDocumentParser ..|> DocumentParser
RecursiveChunkingStrategy ..|> ChunkingStrategy
MongoVectorStoreAdapter ..|> VectorStoreAdapter
HybridRetriever ..|> Retriever

DocumentParserFactory ..> PDFDocumentParser : creates
DocumentParserFactory ..> TextDocumentParser : creates
DocumentParserFactory ..> ImageDocumentParser : creates
EmbeddingFactory ..> LocalHashEmbeddings : fallback
EmbeddingFactory ..> OpenAIEmbeddings : when OPENAI_API_KEY exists
EmbeddingFactory ..> HuggingFaceEmbeddings : when HUGGINGFACE_API_KEY exists
LLMServiceFactory ..> GroqLLMService : when GROQ_API_KEY exists
LLMServiceFactory ..> LLMService : fallback or OpenAI

LangChainIndexingPipeline o-- MongoRAGRepository
LangChainIndexingPipeline o-- VectorStoreAdapter
LangChainIndexingPipeline o-- Embeddings
LangChainIndexingPipeline o-- DocumentParserFactory
LangChainIndexingPipeline o-- ChunkingStrategy
MongoVectorStoreAdapter o-- MongoRAGRepository
HybridRetriever o-- VectorStoreAdapter
HybridRetriever o-- Embeddings

RAGChatService o-- MongoRAGRepository
RAGChatService o-- Retriever
RAGChatService o-- HybridReranker
RAGChatService o-- ContextBuilder
RAGChatService o-- LLMService
RAGChatService o-- UserRepository
RAGChatService ..> RAGResponse : creates
RAGChatService ..> Citation : creates

class Embeddings {
  <<external interface>>
}
class OpenAIEmbeddings {
  <<external>>
}
class HuggingFaceEmbeddings {
  <<external>>
}
LocalHashEmbeddings ..|> Embeddings
OpenAIEmbeddings ..|> Embeddings
HuggingFaceEmbeddings ..|> Embeddings
```

## 5. Runtime Composition and HTTP Boundary

```mermaid
classDiagram
direction LR

class ApplicationFactory {
  <<composition root>>
  +create_app(config_class, database) Flask
}

class Config {
  <<configuration>>
  +APP_ENV
  +SECRET_KEY
  +MONGO_URI
  +MONGO_DB_NAME
  +MONGO_USE_MOCK
  +UPLOAD_FOLDER
  +RAG_CHUNK_SIZE
  +RAG_CHUNK_OVERLAP
  +RAG_TOP_K
}

class AuthBlueprint {
  <<Flask Blueprint>>
  +register()
  +login()
  +logout()
  +forgot_password()
  +verify_otp()
  +refresh_token()
  +reset_password()
}

class UserBlueprint {
  <<Flask Blueprint>>
  +get_profile()
  +update_profile()
  +upload_profile_image()
  +change_password()
  +get_progress()
  +get_mock_test_history()
}

class AdminBlueprint {
  <<Flask Blueprint>>
  +register_admin()
  +create_admin_staff()
  +list_admin_staff()
  +delete_admin_staff()
  +login_admin()
  +logout_admin()
  +dashboard()
  +users_overview()
  +question_and_mock_test_routes()
  +rag_document_routes()
  +clear_logs_and_uploaded_documents()
}

class MockTestBlueprint {
  <<Flask Blueprint>>
  +list_mock_tests()
  +get_mock_test()
  +submit_mock_test()
  +performance_history()
}

class RAGBlueprint {
  <<Flask Blueprint>>
  +upload_documents()
  +list_user_documents()
  +chat()
  +conversation_routes()
  +chat_history()
}

class AuthenticationService
class UserService
class AdminAuthService
class AdminDashboardService
class StorageMaintenanceService
class QuestionBankService
class MockTestService
class LangChainIndexingPipeline
class RAGChatService
class JWTService
class MongoUserRepository
class MongoAdminRepository
class MongoQuestionRepository
class MongoPerformanceRepository
class MongoRAGRepository
class MongoAuditRepository

ApplicationFactory ..> Config : loads
ApplicationFactory *-- MongoUserRepository
ApplicationFactory *-- MongoAdminRepository
ApplicationFactory *-- MongoQuestionRepository
ApplicationFactory *-- MongoPerformanceRepository
ApplicationFactory *-- MongoRAGRepository
ApplicationFactory *-- MongoAuditRepository
ApplicationFactory *-- AuthenticationService
ApplicationFactory *-- UserService
ApplicationFactory *-- AdminAuthService
ApplicationFactory *-- AdminDashboardService
ApplicationFactory *-- StorageMaintenanceService
ApplicationFactory *-- QuestionBankService
ApplicationFactory *-- MockTestService
ApplicationFactory *-- LangChainIndexingPipeline
ApplicationFactory *-- RAGChatService
ApplicationFactory *-- JWTService

ApplicationFactory *-- AuthBlueprint : registers /api/auth
ApplicationFactory *-- UserBlueprint : registers /api/users
ApplicationFactory *-- AdminBlueprint : registers /api/admin
ApplicationFactory *-- MockTestBlueprint : registers /api/mock-tests
ApplicationFactory *-- RAGBlueprint : registers /api/rag

AuthBlueprint ..> AuthenticationService
UserBlueprint ..> UserService
AdminBlueprint ..> AdminAuthService
AdminBlueprint ..> AdminDashboardService
AdminBlueprint ..> StorageMaintenanceService
AdminBlueprint ..> QuestionBankService
AdminBlueprint ..> LangChainIndexingPipeline
AdminBlueprint ..> MongoRAGRepository
MockTestBlueprint ..> MockTestService
RAGBlueprint ..> LangChainIndexingPipeline
RAGBlueprint ..> RAGChatService
RAGBlueprint ..> MongoRAGRepository
```

## LLD Concepts Present in the Implementation

| LLD concept | Exact implementation |
| --- | --- |
| Layered architecture | Flask controllers -> application services -> repositories -> MongoDB |
| Dependency injection | `create_app` constructs services and injects collaborators through constructors |
| Repository pattern | `UserRepository`, Mongo repository classes, and `InMemoryUserRepository` |
| Strategy pattern | `EvaluationStrategy` implementations and `ChunkingStrategy` |
| Factory pattern | `QuestionFactory`, `DocumentParserFactory`, `EmbeddingFactory`, `LLMServiceFactory` |
| Adapter pattern | `MongoVectorStoreAdapter` realizes `VectorStoreAdapter`; Mongo repositories adapt persistence |
| Template Method | `IndexingPipeline.execute()` defines parse/process/store; `LangChainIndexingPipeline` implements steps |
| Builder | `ContextBuilder.build()` assembles retrieval context and learning-profile context |
| Observer-style update | `MockTestService.submit()` triggers `PersonalizedRAGUpdater.update()` after saving performance |
| Composition | `User` owns `UserProfile` and `Session`; `Admin` owns `Session`; `RAGResponse` owns citations |
| Role-based access control | `admin_required(*allowed_roles)` validates `AdminRole`; `token_required` validates users |
| Composition Root | `create_app` chooses and wires all runtime implementations into `app.extensions["services"]` |

## Runtime Notes

- The active user repository is `MongoUserRepository`; `InMemoryUserRepository`
  exists but is not selected by `create_app`.
- Authentication currently uses `OTPVerificationService` with
  `SMSNotificationService`. The email verification classes exist but are not
  wired into the runtime graph.
- `EmbeddingFactory` selects OpenAI, Hugging Face, or local deterministic hash
  embeddings from configuration.
- `LLMServiceFactory` selects `GroqLLMService` when `GROQ_API_KEY` exists;
  otherwise it creates `LLMService`, which can use OpenAI when configured or
  return retrieved context without a remote model.
- Files such as `models/enums.py`, `models/rag.py`,
  `repositories/module_repositories.py`, `services/mocktest/evaluation.py`, and
  similar modules are import-only compatibility facades, not additional
  classes.
