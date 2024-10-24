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
