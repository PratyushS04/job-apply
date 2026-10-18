# Pratyush Shendre - Master Resume

## Contact

- **Email:** pshendre6604@gmail.com
- **Phone:** +91-9975080249
- **Location:** India
- **LinkedIn:** [LinkedIn](https://www.linkedin.com/in/pratyush-shendre-2256a7223/)
- **GitHub:** [GitHub](https://github.com/PratyushS04)

## Summary

Software Development Engineer with experience in Java and Spring modernization, application security, Kubernetes-based delivery, and generative AI products. Builds backend automation and context-aware AI systems using Python, Java, Azure AI Foundry, RAG, MCP, and modern cloud tooling.

## Experience

### Software Development Engineer - Amadeus Software Labs

**August 2025 - Present**

Internal review note: The candidate confirmed a separate Amadeus internship from January through July 2025. ContX AI, Pod Brain, and the separate AI-assisted developer portal prototype belong to this full-time role only. Recheck the timing of other undated Amadeus achievements before placing them in a new application resume.

- Investigated and fixed application-security issues identified through Black Duck, Checkmarx, and penetration testing.
- Built ContX AI, a context-aware campaign-design application that turns natural-language briefs and GMS guest, property, booking, audience, and brand context into personalized content for email, messaging, Google Ads, and Meta Ads using Python, React, Azure AI Foundry, MJML, and REST APIs.
- Implemented audience-specific variants, property-level personalization, prompt-based editing, marketing compliance controls, and manual export, with guardrails to avoid storing PII or fabricating property information.
- Built a working prototype of the ContX AI Pod Brain, a curated project-knowledge layer for AI development agents; designed source linkage, ownership, approval states, indexing, and lifecycle metadata for its knowledge assets.
- Built a working prototype of an AI-assisted internal developer portal to bring engineering knowledge and tools into one interface.
- Ran hands-on evaluations of language models and multi-agent workflows for personalized marketing copy, structured email content, image generation, and output validation.
- Engineered and deployed a Meta-RAG framework for the Loyalty Portal chatbot, implementing multi-stage contextual validation to minimize LLM hallucinations and improve response grounding.
- Developed a custom Model Context Protocol server for Black Duck, enabling LLMs to query vulnerability metadata, analyze project risks, and generate real-time remediation strategies through a chat-based interface.
- Independently developed an end-to-end security tool using Black Duck API v2 to automate container image downloads and vulnerability scanning, reducing manual work for security developers by 40%.
- Architected a proof of concept for agentic AI-assisted Java Spring migration using OpenRewrite recipes and the GitHub Copilot Agent SDK to automate legacy-code modernization and reduce manual migration effort.
- Applied AI-assisted development across four Java modernization initiatives covering Java 17, Spring 6, Spring Boot 3, and Core and Loyalty dependency upgrades.
- Resolved a customer-reported stability defect in the sync-currency-exchange-rates service, improving the reliability of currency exchange-rate synchronization.
- Supported the AKS regression program and DE93897 through testing, issue investigation, deployment validation, reverts, and redeployments.
- Designed and documented the GMS AI Skills Toolkit to automate Rally, Jenkins, Kubernetes, and knowledge-retrieval workflows.
- Developed and demonstrated practical MCP and GitHub Copilot Skills use cases during GMS IP Weeks 26.1 and 26.2, showing how AI-assisted workflows can improve developer productivity.
- Strengthened engineering documentation by creating detailed Rally notes, research findings, and implementation analyses for previously undocumented or under-documented GMS areas.
- Advanced internal innovation efforts by drafting three Lift proposals, contributing to the Internship Idea Program, and presenting an AI-based Hotel Receptionist concept to the GMS initiative group.

### Software Development Intern - Amadeus Software Labs

**January 2025 - July 2025**

- Built Python workflows to extract and prepare iHotelier shopping, availability, and promotion data from Splunk and SQL sources for Power BI reporting.
- Migrated dashboard inputs from Excel to CSV, developed Power BI visuals and interactive Top-N property filters, and optimized DAX queries.
- Published the dashboards in the iHotelier workspace, checked data and visuals during QA, and documented the extraction and reporting workflows.

Internal selection notes (exclude from submitted resumes): The candidate confirmed that the portal/AI hub prototype belongs to the full-time role and that iHotelier dashboard work was during this internship. They personally worked on all listed Python/Splunk, SQL, CSV, Power BI/DAX, Top-N, publishing, QA, and documentation tasks. Overlap with the existing HIT project and performance metrics still need confirmation. The candidate explicitly denied implementing RAG ingestion from Jira, Confluence, or PDFs during this internship.

### AI-ML Virtual Intern - AWS Academy

**May 2023 - July 2023** | Virtual

- Developed foundational knowledge of AWS cloud infrastructure and its use in machine learning, including forecasting, computer vision, and natural language processing.
- Implemented end-to-end machine learning pipelines with Amazon SageMaker covering problem formulation, data collection, feature engineering, model training, deployment, and evaluation.
- Used Amazon Rekognition, Forecast, and Lex to build practical image and video analysis, forecasting, and natural language processing solutions.

### Android Developer - Gear To Care

**September 2022 - December 2022** | Nagpur, India

- Integrated Razorpay to facilitate seamless in-app transactions and improve the user payment experience.
- Implemented Firebase Authentication protocols to secure application access and user data.
- Designed and deployed instant and scheduled Firebase notifications, improving response time by 30%.

## Projects

The internal projects below are associated with the Amadeus role. The GMS, Black Duck, reporting, and automation entries came from the candidate's earlier project write-up; the ContX AI Pod Brain entry follows the candidate's 2026-10-17 confirmations. Approximate years appear only where previously authorized. Treat related components as one project story when tailoring; do not duplicate existing Experience achievements. Status and review notes below are for internal selection, not application copy.

### ContX AI — Pod Brain and AI Evaluation

**Working prototype; dates not supplied** | Internal Amadeus work

Built a curated knowledge-layer prototype for AI development agents and ran hands-on evaluations of generative AI workflows for hospitality marketing.

- Built a working prototype of the ContX AI Pod Brain, a curated project-knowledge layer for AI development agents.
- Designed source linkage, ownership, approval states, indexing, and lifecycle metadata for the knowledge assets.
- Explored automated ingestion and summarization of project artifacts to keep agent context current.
- Ran hands-on evaluations of language models and multi-agent workflows for personalized marketing copy, structured email content, image generation, and output validation.

Internal selection notes (exclude from submitted resumes): The candidate confirmed this belongs to the August 2025–present full-time role, not the preceding internship. They also confirmed the prototype and hands-on evaluations. Production deployment, benchmark results, model training, detailed data-integration ownership, and a separate GenAI Engineer title are not established. Avoid duplicating these bullets under Experience and Projects in a one-page resume.

### GMS Knowledge Bot - Meta-RAG Question Answering System

**2025; built with a two-LLM Meta-RAG structure** | Python, LangChain, Azure OpenAI, ChromaDB, Streamlit, RAG, Meta-RAG, Prompt Engineering

An internal knowledge assistant for the Guest Management Solution product suite, using intent classification to adapt document retrieval and answer generation.

- Built a knowledge assistant that classifies questions by intent and adjusts retrieval depth, generation settings, token budget, and prompts for each query.
- Implemented retrieval and generation with LangChain, Azure OpenAI, and ChromaDB, using 1,000-character chunks with a 200-character overlap.
- Built a Streamlit interface showing routing decisions, answers, execution logs, and session query history.
- Implemented an HTTP client layer for the corporate network environment and documented architecture, setup, and troubleshooting.

Internal selection notes (exclude from submitted resumes): Candidate clarified that this is distinct from the Loyalty Portal chatbot and uses a two-LLM Meta-RAG structure. Source does not provide evaluation results supporting claims of novelty, measurable relevance improvement, or deterministic answers. Documentation page count is unspecified. Exact model deployments can be retained from the source if needed; do not imply every model supports every generation parameter.

### GMS Documentation Ingestion Pipeline

**2025; built, with 86 normalized documents reported** | Python, Requests, BeautifulSoup, Web Scraping, JSON, Data Processing

The documentation ingestion component of the GMS Knowledge Bot, converting online help content into structured data for retrieval.

- Mapped a help portal's hash-based navigation to static content URLs and built a Python scraper for product documentation.
- Preserved tables as structured records and added breadcrumb and parent-category metadata to retain context during retrieval.
- Produced 86 normalized documents and versioned JSON datasets for vector-store ingestion.
- Built normalization, schema-correction, and token-accounting utilities to inspect data quality and embedding inputs.

Internal selection notes (exclude from submitted resumes): Treat as a component of the GMS Knowledge Bot when selecting resume content, rather than counting the same delivery twice. The supplied count is 86 normalized documents, not necessarily 86 source pages or vector chunks.

### Black Duck Container Image Security Scanner

**2025; built and packaged** | Python, Azure Container Registry, Podman, Black Duck, REST APIs, Tkinter, PyInstaller, Microsoft Teams Webhooks

Internal container vulnerability-scanning tooling with a Windows desktop interface, command-line tools, and programmatic access.

- Automated image retrieval from Azure Container Registry, export with Podman, and scan submission and result polling through Black Duck REST APIs.
- Built a Tkinter interface for scanning registry images or existing image archives, with live progress output.
- Integrated Teams notifications with scan status, vulnerability summaries, and links to detailed results.
- Packaged the scanner as a Windows executable with PyInstaller and provided CLI tools and a programmatic interface.

Internal selection notes (exclude from submitted resumes): Likely overlaps with the existing Black Duck API v2 security-automation achievement; confirm before duplicating it in Experience and Projects. This source supplies no time-saving measurements. Do not automatically attach the existing 40% figure without confirming that it describes this tool. Credential caching is described but its storage security is unspecified; do not claim encrypted or secure caching.

### iHotelier Data-Driven Reporting Platform (HIT)

**2025; built** | Python, Splunk, SQL, Multiprocessing, PlantUML

An internal reporting system combining application telemetry and database data for monthly, weekly, and promotional hospitality reports.

- Built reporting workflows combining Splunk application logs and SQL data to report request volumes, hotel and source traffic, rate and inventory updates, and response times.
- Ran independent queries concurrently using Python multiprocessing, with structured logging and progress reporting.
- Separated query execution from report formatting through a pluggable writer interface.
- Documented the system with PlantUML sequence diagrams and provided a batch runner for stakeholders to trigger reports.

Internal selection notes (exclude from submitted resumes): Query count and before/after runtime are missing; do not add a speedup percentage or claim a quantified reduction. The source describes both scheduled and on-demand reporting; confirm scheduling implementation if highlighting scheduled operation. The candidate is unsure whether the internship Power BI dashboard and this HIT platform are the same project; do not merge or count them separately until clarified.

### AI-Powered Social Engagement Bot - Futurize Innovation POC

**2025; proof of concept** | Python, Azure OpenAI, REST APIs, X/Twitter API

An internal proof of concept using Azure OpenAI to generate replies to X/Twitter mentions, with persistent interaction state and adaptive polling.

- Built a proof of concept that monitors mentions, generates replies within platform character limits, and persists reply state across restarts.
- Implemented adaptive polling with exponential backoff and configurable interval bounds to handle API rate limits.
- Refactored the bot into modules for inference, API transport, configuration, persistence, logging, and orchestration, with separate AI and TLS test harnesses.
- Moved credentials into environment configuration and addressed certificate-chain issues in the corporate network.

Internal selection notes (exclude from submitted resumes): Persistent state supports duplicate prevention but does not establish an exactly-once guarantee under all failures. No load or duration measurements were provided; omit 'at scale', guaranteed quota compliance, and unsupported production-reliability claims.

### Infrastructure Configuration Automation

**2026; scaffold, YAML modification logic incomplete** | Python, PyGithub, GitPython, GitHub, Kubernetes, Helm

An unfinished Python scaffold for applying Kubernetes/Helm configuration changes across GitHub repositories.

- Started a Python scaffold for coordinating GitHub repository changes using PyGithub and GitPython.
- Outlined a workflow for branch creation and pull requests around Helm configuration updates; YAML modification logic remains unfinished.

Internal selection notes (exclude from submitted resumes): Source implementation caveat contradicts its opening completed-rollout description. Preserve scaffold status. Do not claim completed configuration changes, rollout, idempotency, or validated failure isolation without implementation evidence. Normally omit from a space-constrained resume unless unfinished tooling is directly relevant and clearly labeled.

### Black Duck Report Retrieval Utility

**2025; built** | Python, Black Duck, REST APIs, CLI Development

A companion CLI utility for inspecting report status and downloading completed Black Duck report artifacts.

- Built a CLI that retrieves report metadata and distinguishes in-progress, failed, and completed Black Duck reports before downloading artifacts.
- Added timestamped output names, local metadata records, and authentication through configuration files or direct parameters.

Internal selection notes (exclude from submitted resumes): Use as supporting depth for Black Duck tooling rather than a separate headline project when space is limited.

### Crowd Detection & Management System

**2023** | Python, YOLOv8, OpenCV, Computer Vision, Telegram API

- Collected and labeled data for the crowd-detection pipeline.
- Used YOLOv8 and computer vision algorithms to detect crowd density with 80% accuracy.
- Implemented a real-time Telegram bot alert system for crowd management.

### MediInfo

**2024** | OCR, Large Language Models

- Built a medication identification and treatment-guidance system.
- Extracted prescription text using OCR and analyzed medicine names with large language models.
- Designed the system to streamline medication identification for healthcare professionals and provide patients with treatment guidance.

### Red Light Violation Detection

**2024** | Python, Computer Vision, TensorFlow, YOLOv8, Convolutional Neural Networks

- Designed and implemented a system for detecting vehicles that violate traffic signals.
- Focused the system on accurately identifying traffic-signal violations to support improved road safety.

## Education

### Bachelor of Technology - RCOEM Nagpur

**Computer Science and Engineering (Artificial Intelligence and Machine Learning)**  
**August 2021 - July 2025** | CGPA: 8.23/10

Relevant coursework: Data Structures and Algorithms (Java), Design and Analysis of Algorithms (Java), Object-Oriented Programming (Java), Computer Networks, Operating Systems, Database Management Systems, Machine Learning, Deep Learning (Python), Neural Networks, Natural Language Processing, and Digital Image Processing.

## Skills

- **Languages:** Java, Python, Go, C, SQL, Shell scripting
- **Frameworks:** TensorFlow, Spring, Spring Boot, React, LangChain, Streamlit, Tkinter
- **Tools:** Git, GitHub, Docker, Podman, Kubernetes, Helm, Jenkins, Kafka, Argo CD, Power BI, DAX, OpenCV, OCR, YOLOv8, Black Duck, Checkmarx, OpenRewrite, GitHub Copilot Agent SDK, Requests, BeautifulSoup, Splunk, PyInstaller, PlantUML, MJML
- **Platforms:** Linux, Azure, Azure Kubernetes Service, AWS, Amazon SageMaker, Amazon Rekognition, Amazon Forecast, Amazon Lex, Firebase, Razorpay, Android, Azure OpenAI, Azure AI Foundry, Azure Container Registry
- **Databases:** SQL, PostgreSQL, Couchbase, NoSQL, ChromaDB
- **Areas:** Backend Development, Microservices, Client-Server Development, REST API Integration, CI/CD, System Design, Design Patterns, SOLID Principles, Object-Oriented Programming, Data Structures and Algorithms, Operating Systems, Computer Networking, Database Management Systems, Debugging, Code Review, Cybersecurity, Application Security, AI-driven Automation, AI-assisted Software Modernization, Generative AI, RAG, Meta-RAG, Large Language Models, Model Context Protocol, Prompt Engineering, Context-aware Personalization, Agentic AI, Knowledge Engineering, LLM Evaluation, Vulnerability Management, Container Security, Machine Learning, Deep Learning, Computer Vision, Natural Language Processing, Convolutional Neural Networks, Web Scraping, Multiprocessing, Vector Databases

## Certifications and Achievements

- Claude Certified Architect, Foundations - Anthropic
- GATE Qualified (2023)
- Technical Club Member: Led the planning and execution of multiple technical events, contributing to the growth of the college's tech community.
- Solved over 1,000 LeetCode problems, demonstrating sustained practice in data structures, algorithms, and problem solving.
