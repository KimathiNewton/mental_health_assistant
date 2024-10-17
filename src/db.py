import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RUN_TIMEZONE_CHECK = os.getenv('RUN_TIMEZONE_CHECK', '1') == '1'

TZ_INFO = os.getenv("TZ", "Europe/Berlin")
tz = ZoneInfo(TZ_INFO)


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "mental_health"),
            user=os.getenv("POSTGRES_USER", "newton"),
            password=os.getenv("POSTGRES_PASSWORD", "Admin"),
        )
        logger.info("Successfully connected to the database")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise


def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if tables exist
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'conversations')")
            conversations_exists = cur.fetchone()[0]
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'feedback')")
            feedback_exists = cur.fetchone()[0]
            
            if not conversations_exists:
                logger.info("Creating conversations table")
                cur.execute("""
                    CREATE TABLE conversations (
                        id TEXT PRIMARY KEY,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        model_used TEXT NOT NULL,
                        response_time FLOAT NOT NULL,
                        relevance TEXT NOT NULL,
                        relevance_explanation TEXT NOT NULL,
                        prompt_tokens INTEGER NOT NULL,
                        completion_tokens INTEGER NOT NULL,
                        total_tokens INTEGER NOT NULL,
                        eval_prompt_tokens INTEGER NOT NULL,
                        eval_completion_tokens INTEGER NOT NULL,
                        eval_total_tokens INTEGER NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                    )
                """)
            
            if not feedback_exists:
                logger.info("Creating feedback table")
                cur.execute("""
                    CREATE TABLE feedback (
                        id SERIAL PRIMARY KEY,
                        conversation_id TEXT REFERENCES conversations(id),
                        feedback INTEGER NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                    )
                """)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()


def save_conversation(conversation_id, question, answer_data, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            logger.debug(f"Saving conversation: {conversation_id}")
            logger.debug(f"Question: {question}")
            logger.debug(f"Answer data: {answer_data}")
            cur.execute(
                """
                INSERT INTO conversations 
                (id, question, answer, model_used, response_time, relevance, 
                relevance_explanation, prompt_tokens, completion_tokens, total_tokens, 
                eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    question,
                    answer_data["answer"],
                    answer_data["model_used"],
                    answer_data["response_time"],
                    answer_data["relevance"].upper(),  # Ensure it's uppercase
                    answer_data["relevance_explanation"],
                    answer_data["prompt_tokens"],
                    answer_data["completion_tokens"],
                    answer_data["total_tokens"],
                    answer_data["eval_prompt_tokens"],
                    answer_data["eval_completion_tokens"],
                    answer_data["eval_total_tokens"],
                    timestamp
                ),
            )
        conn.commit()
        logger.info(f"Successfully saved conversation: {conversation_id}")
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        conn.rollback()
    finally:
        conn.close()


def save_feedback(conversation_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the conversation exists
            cur.execute("SELECT id FROM conversations WHERE id = %s", (conversation_id,))
            if cur.fetchone() is None:
                logger.warning(f"Attempted to save feedback for non-existent conversation: {conversation_id}")
                return  # Or handle this case as appropriate for your application

            logger.info(f"Attempting to save feedback: conversation_id={conversation_id}, feedback={feedback}, timestamp={timestamp}")
            cur.execute(
                "INSERT INTO feedback (conversation_id, feedback, timestamp) VALUES (%s, %s, %s)",
                (conversation_id, feedback, timestamp),
            )
        conn.commit()
        logger.info(f"Feedback saved successfully for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_recent_conversations(limit=5, relevance=None):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """
            params = []
            if relevance:
                if relevance in ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]:
                    query += " WHERE c.relevance = %s"
                    params.append(relevance)
                else:
                    logger.warning(f"Invalid relevance filter: {relevance}")
            query += " ORDER BY c.timestamp DESC LIMIT %s"
            params.append(limit)

            logger.debug(f"Executing query: {query}")
            logger.debug(f"Query parameters: {params}")
            cur.execute(query, tuple(params))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Error in get_recent_conversations: {e}")
        return []
    finally:
        conn.close()


def get_feedback_stats():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            return cur.fetchone()
    finally:
        conn.close()


def check_timezone():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW timezone;")
            db_timezone = cur.fetchone()[0]
            print(f"Database timezone: {db_timezone}")

            cur.execute("SELECT current_timestamp;")
            db_time_utc = cur.fetchone()[0]
            print(f"Database current time (UTC): {db_time_utc}")

            db_time_local = db_time_utc.astimezone(tz)
            print(f"Database current time ({TZ_INFO}): {db_time_local}")

            py_time = datetime.now(tz)
            print(f"Python current time: {py_time}")

            # Use py_time instead of tz for insertion
            cur.execute("""
                INSERT INTO conversations 
                (id, question, answer, model_used, response_time, relevance, 
                relevance_explanation, prompt_tokens, completion_tokens, total_tokens, 
                eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING timestamp;
            """, 
            ('test', 'test question', 'test answer', 'test model', 0.0, 0.0, 
             'test explanation', 0, 0, 0, 0, 0, 0, 0.0, py_time))

            inserted_time = cur.fetchone()[0]
            print(f"Inserted time (UTC): {inserted_time}")
            print(f"Inserted time ({TZ_INFO}): {inserted_time.astimezone(tz)}")

            cur.execute("SELECT timestamp FROM conversations WHERE id = 'test';")
            selected_time = cur.fetchone()[0]
            print(f"Selected time (UTC): {selected_time}")
            print(f"Selected time ({TZ_INFO}): {selected_time.astimezone(tz)}")

            # Clean up the test entry
            cur.execute("DELETE FROM conversations WHERE id = 'test';")
            conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_conversation_saved(conversation_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM conversations WHERE id = %s", (conversation_id,))
            result = cur.fetchone()
            if result:
                logger.info(f"Verified conversation saved: {conversation_id}")
            else:
                logger.error(f"Failed to verify conversation saved: {conversation_id}")
    except Exception as e:
        logger.error(f"Error verifying conversation: {e}")
    finally:
        conn.close()
def verify_feedback_saved(conversation_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM feedback WHERE conversation_id = %s", (conversation_id,))
            result = cur.fetchone()
            if result:
                logger.info(f"Verified feedback saved for conversation: {conversation_id}")
            else:
                logger.error(f"Failed to verify feedback saved for conversation: {conversation_id}")
    except Exception as e:
        logger.error(f"Error verifying feedback: {e}")
    finally:
        conn.close()


if RUN_TIMEZONE_CHECK:
    check_timezone()