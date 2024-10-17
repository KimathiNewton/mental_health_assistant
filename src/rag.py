import json
from time import time
from groq import Groq
from dotenv import load_dotenv
import os
import ingest
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# Load the search index
try:
    index = ingest.load_index()
except Exception as e:
    logger.error(f"Failed to load index: {e}")
    raise

if index is None:
    raise ValueError("Search index could not be loaded")

def search(query):
    try:
        results = index.search(
            query=query,
            num_results=10
        )
        return results
    except Exception as e:
        logger.error(f"Error in search function: {e}")
        return []

prompt_template = """ 
You are an expert mental health assistant specialized in providing detailed and accurate answers based on the given context. Answer the QUESTION based on the CONTEXT from our mental health database. Use only the facts from the CONTEXT when answering the QUESTION.

Here is the context:

Context: {context}

Please answer the following question based on the provided context:

Question: {question}

Provide a detailed and informative response. Ensure that your answer is clear, concise, and directly addresses the question while being relevant to the context provided.

Your response should be in plain text and should not include any code blocks or extra formatting.

Answer:
""".strip()

entry_template = """ 
questions={Questions}
answers={Answers}
""".strip()

def build_prompt(query, search_results):
    context = ""
    for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt, model="mixtral-8x7b-32768"):
    start_time = time()
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    end_time = time()
    response_time = end_time - start_time

    return answer, token_stats, response_time    

def evaluate_relevance(question, answer, model='mixtral-8x7b-32768'):
    eval_prompt = f"""
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:
Question: {question}
Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

"Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
"Explanation": "[Provide a brief explanation for your evaluation]"
""".strip()

    evaluation, tokens, _ = llm(eval_prompt, model)
    
    try:
        json_eval = json.loads(evaluation)
        relevance = json_eval['Relevance'].upper()  # Ensure it's uppercase
        if relevance not in ["NON_RELEVANT", "PARTLY_RELEVANT", "RELEVANT"]:
            logger.warning(f"Unexpected relevance value: {relevance}. Defaulting to PARTLY_RELEVANT.")
            relevance = "PARTLY_RELEVANT"
        return relevance, json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        logger.error(f"Failed to parse evaluation JSON: {evaluation}")
        return "PARTLY_RELEVANT", "Failed to parse evaluation", tokens


def rag(query, model="mixtral-8x7b-32768"):
    t0 = time()

    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model=model)

    relevance, explanation, eval_tokens = evaluate_relevance(query, answer, model=model)
    
    t1 = time()
    took = t1 - t0

    answer_data = {
        'answer': answer,
        'model_used': model,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
    }

    return answer_data