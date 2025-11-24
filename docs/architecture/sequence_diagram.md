# Sequence Diagrams

## 1. Data Pipeline & Analysis (Background Process)
This process runs periodically (e.g., weekly) to fetch new research papers, analyze them with LLM, and store them.

```mermaid
sequenceDiagram
    participant Scheduler
    participant Crawler as CrawlerService
    participant LLM as LLMService (GPT/Claude)
    participant VDB as VectorDB (Chroma)
    participant DB as Database

    Note over Scheduler, DB: Weekly Data Pipeline

    Scheduler->>Crawler: Trigger Crawl Job (Target Universities)
    activate Crawler
    Crawler->>Crawler: Fetch Web Pages (Playwright)
    Crawler->>Crawler: Parse & Clean Text
    Crawler-->>Scheduler: Return Raw Data List
    deactivate Crawler

    loop For each Paper
        Scheduler->>LLM: Request Analysis (Summary + Career + Action)
        activate LLM
        LLM->>LLM: Generate Content (System Prompt)
        LLM-->>Scheduler: Return Structured JSON
        deactivate LLM

        Scheduler->>VDB: Generate & Store Embeddings
        Scheduler->>DB: Store Structured Data (Paper + Analysis)
    end
```

## 2. User Service & Report Delivery
This process handles user registration and the delivery of personalized reports.

```mermaid
sequenceDiagram
    participant Student as Student (User)
    participant Parent as Parent (User)
    participant API as API Server (FastAPI)
    participant DB as Database
    participant VDB as VectorDB (Chroma)
    participant Noti as NotificationService (Kakao/Notion)

    %% User Registration
    Student->>API: Register / Update Interests (e.g., "AI", "Bio")
    API->>DB: Save User Profile
    API-->>Student: Confirmation

    %% Report Generation (Triggered or On-Demand)
    Note over API, Noti: Personalized Report Generation

    API->>DB: Get User Interests
    API->>VDB: Search Relevant Papers (Cosine Similarity)
    VDB-->>API: Return Top N Papers
    
    API->>DB: Fetch "Plan B" Papers (Theme Cluster)
    DB-->>API: Return Similar Theme Papers

    API->>API: Assemble Report (Student View + Parent Guide)

    par Delivery
        API->>Noti: Send Report Link to Student (Kakao/Notion)
        Noti-->>Student: Notification
    and
        API->>Noti: Send Conversation Guide to Parent
        Noti-->>Parent: Notification
    end
```
