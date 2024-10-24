## Project Overview: Mental Health Assistant RAG
This project, Mental Health Assistant RAG, was developed to support individuals with mental health concerns by implementing a Retrieval-Augmented Generation (RAG) system. The assistant intelligently answers mental health-related queries by integrating a knowledge base and large language models (LLMs). The system is designed to assist with questions about issues such as depression, trauma, stress, grief, and relationships. By leveraging retrieval and generation capabilities, this project offers users accurate, supportive, and personalized responses, making it a valuable tool for mental health guidance and education.

## 🧠 Problem Description
Mental health is a crucial aspect of well-being, affecting millions of people worldwide. However, individuals seeking guidance often face challenges in finding trustworthy, relevant, and personalized information quickly. The complexity and sensitivity of mental health issues, coupled with the vast amount of available resources, make it difficult for people to get timely, accurate advice.

This project aims to address these challenges by developing an intelligent mental health assistant that can handle complex queries and provide contextually relevant and accurate answers. By leveraging RAG techniques, the system combines the reasoning power of LLMs with the precision of curated mental health knowledge, ensuring that users receive personalized support and guidance based on expert sources. This assistant makes mental health resources more accessible and helps reduce the stigma associated with seeking help, offering a bridge between individuals and the mental health care they need.

### **🧬 Technologies and Tools Used**

#### ⚗️ Key Technologies
- **Docker**: Containerizes the application to ensure seamless deployment and consistent execution across various environments, making it easier to manage dependencies and configurations.
- **Grafana**: Provides real-time monitoring and visualization dashboards to track application performance, user interactions, and usage metrics, supporting continuous improvement.
- **Streamlit**: Offers a simple, interactive user interface that allows users to engage with the Mental Health Assistant and ask mental health-related questions.
- **PostgreSQL**: Serves as the relational database for storing user questions, responses, and feedback, ensuring data consistency and scalability.

#### 🧬 LLMs Used
- **gemma2-9b-it**: Used to reformulate user questions, optimizing them for better clarity and understanding by the assistant.
- **llama3-70b-8192**: Powers the retrieval-augmented generation process by handling complex mental health queries and delivering accurate, contextually relevant responses.
- **mixtral-8x7b-32768**: Contributes to processing large volumes of text, refining responses for depth and relevance.
- **Groq**: Integrated into the system to enhance vector processing efficiency during the search and retrieval phase, improving response time.
- **MinSearch**: Provides fast, scalable retrieval of information by managing vector indexing and semantic search, enabling more precise query-to-answer matching.

#### ⚗️ Other Tools Used for Development
- **Pytest**: Used for unit and integration testing to ensure the reliability and robustness of the code.
- **Git**: Version control system for tracking project changes, enabling collaboration, and maintaining code integrity.
- **Visual Studio Code**: IDE used for coding, debugging, and managing the development workflow.
- **Jupyter Notebook**: Utilized for exploratory data analysis, prototyping, and preprocessing, offering an interactive platform for data exploration.

### **🧬 Dataset**
The dataset in this project contains information related to **mental health queries**, structured for use in the knowledge base of the Retrieval-Augmented Generation (RAG) system. The data is stored in the [dataset](dataset/data.csv) directory and serves as the foundation for generating mental health-related responses in areas such as depression, trauma, stress, and relationship issues.

---

### **Backend Files Overview**

The backend of the **Mental Health Assistant** application handles various components of the RAG system, including data ingestion, retrieval, and interaction with the Large Language Models (LLMs). Below is an overview of the key backend files:

#### **1. [app.py](src/app.py)**
- Streamlit app that Processes the user queries by retrieving relevant data from the knowledge base and generating a response using the LLM and gets the user feedback on the responses provided by the assistant to continuously improve the system.


#### **2. [rag.py](src/rag.py)**
- **Core RAG Logic**: Implements the primary logic for the Retrieval-Augmented Generation process.
- **Key Functions**:
  - **Query Minsearch**: Searches for relevant mental health-related documents in the Minsearch knowledge base.
  - **Build Prompts**: Constructs the input prompt for the LLM based on the retrieved documents.
  - **Evaluate Answers**: Assesses the relevance of the AI-generated answers to ensure they are contextually accurate and meaningful.

#### **3. [db.py](src/db.py)**
- **Database Management**: Manages interaction with the **PostgreSQL** database.
- **Key Features**:
  - **Initialize Database Schema**: Creates the necessary database tables to store conversations and user feedback.
  - **Save Conversations**: Stores question-answer pairs and feedback to analyze user interactions over time.


#### **5. [ingest.py](src/ingest.py)**
- **Document Ingestion**: Handles theingestion of the dataset into Minsearch.
- **Key Features**:
  - **Text Cleaning**: Pre-processes and cleans mental health-related documents before indexing.
  - **Document Indexing**: Pushes the cleaned documents into Elasticsearch for later retrieval during RAG queries.


#### **6. init.py**
- **Grafana Setup**: Configures **Grafana** for monitoring the system's performance.
- **Key Features**:
  - **Data Source Configuration**: Sets up PostgreSQL as a data source for tracking system metrics such as query response times, user activity, and feedback analysis.
  - **Dashboard Initialization**: Initializes Grafana dashboards for visualizing key metrics like query efficiency, response accuracy, and feedback trends.

### **6. [Dockerfile](Dockerfile)**
- **Base Image** : Uses python:3.12-slim as the base image for a lightweight container.
- **Working Directory** : Sets the working directory to /app.
- **Pipenv Installation** : Installs pipenv to manage dependencies.
- **Data and Dependency Copying** : Copies the dataset and dependency files into the container.
- **Streamlit Launch**: Specifies the command to run the Streamlit app on port 8501.

### **7. [docker-Compose.yaml](docker-compose.yaml)
- **Service Definitions**: Sets up three services: PostgreSQL, Streamlit, and Grafana.
- **PostgreSQL Configuration**: Defines environment variables for the database setup.
- **Streamlit Configuration**: Builds the Streamlit service using the Dockerfile, specifying dependencies and environment variables.
- **Grafana Configuration**: Sets up Grafana with the necessary environment variables and dependencies.

---

This backend architecture supports the Mental Health Assistant application by efficiently processing user queries, generating contextually relevant mental health responses, and providing insightful metrics for system performance monitoring.