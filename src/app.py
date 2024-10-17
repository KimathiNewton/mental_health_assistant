import streamlit as st
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import rag
from db import (
    save_conversation,
    save_feedback,
    get_recent_conversations,
    get_feedback_stats,
    init_db,
    verify_conversation_saved
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tz = ZoneInfo("Europe/Berlin")

def print_log(message):
    print(message, flush=True)

def main():
    print_log("Starting the Mental Health Assistant application")
    st.title("Mental Health Assistant")

    # Initialize the database
    init_db()

    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID: {st.session_state.conversation_id}")
    if "count" not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")
    if "feedback_given" not in st.session_state:
        st.session_state.feedback_given = False
    if "past_questions" not in st.session_state:
        st.session_state.past_questions = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # Stores the questions and answers for display
    if "clear_chat" not in st.session_state:
        st.session_state.clear_chat = False

    # Session state for user input
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""  # This will control the text input field value

    # Check if we need to clear the chat
    if st.session_state.clear_chat:
        st.session_state.chat_history = []
        st.session_state.clear_chat = False

    # Model selection
    model_choice = st.selectbox(
        "Select a model:",
        ["gemma2-9b-it", "llama-3.1-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"],
    )
    print_log(f"User selected model: {model_choice}")

    # User input text box
    user_input = st.text_input("Ask a question about mental health:", value=st.session_state.user_input)

    if "last_conversation_id" not in st.session_state:
        st.session_state.last_conversation_id = None

    if st.button("Ask"):
        logger.debug(f"Ask button pressed. User input: {user_input}")

        # Check if input is valid
        if user_input.strip() == "":
            st.warning("Please enter a question before asking.")
        elif user_input in st.session_state.past_questions:
            st.warning("You've already asked this question.")
        else:
            # Proceed with getting an answer from the assistant
            print_log(f"User asked: '{user_input}'")
            with st.spinner("Processing..."):
                print_log(f"Getting answer from assistant using {model_choice} model")
                start_time = time.time()
                answer_data = rag.rag(user_input, model=model_choice)
                end_time = time.time()
                print_log(f"Answer received in {end_time - start_time:.2f} seconds")
                st.success("Completed!")
                st.write(answer_data["answer"])

                # Store the conversation in chat history
                st.session_state.chat_history.append({
                "question": user_input,
                "answer": answer_data["answer"],
                "relevance": answer_data["relevance"],
                "model": answer_data["model_used"]})

                # Display monitoring information
                st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
                st.write(f"Relevance: {answer_data['relevance']}")
                st.write(f"Model used: {answer_data['model_used']}")
                st.write(f"Total tokens: {answer_data['total_tokens']}")

                # Save conversation to database
                logger.debug(f"Attempting to save conversation: {st.session_state.conversation_id}")
                save_conversation(st.session_state.conversation_id, user_input, answer_data)
                logger.debug(f"Conversation saved. Verifying...")
                verify_conversation_saved(st.session_state.conversation_id)



                # Update the last_conversation_id and reset feedback
                st.session_state.last_conversation_id = st.session_state.conversation_id
                st.session_state.conversation_id = str(uuid.uuid4())  # New conversation ID for the next question
                st.session_state.feedback_given = False  # Reset feedback state
                st.session_state.past_questions.append(user_input)  # Add the question to past questions

                # Clear the input field by resetting session state variable
                st.session_state.user_input = ""  # Reset input for next question

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+1"):
            if st.session_state.last_conversation_id and not st.session_state.feedback_given:
                save_feedback(st.session_state.last_conversation_id, 1)
                st.success("Positive feedback saved!")
                st.session_state.feedback_given = True  # Mark feedback as given
                st.session_state.last_conversation_id = None  # Clear last conversation
                st.session_state.clear_chat = True  # Set flag to clear chat on next rerun
                st.rerun()  # Rerun the app to refresh the UI
            elif st.session_state.feedback_given:
                st.warning("Feedback has already been provided for this conversation.")
            else:
                st.warning("No conversation to provide feedback for.")
    with col2:
        if st.button("-1"):
            if st.session_state.last_conversation_id and not st.session_state.feedback_given:
                save_feedback(st.session_state.last_conversation_id, -1)
                st.success("Negative feedback saved!")
                st.session_state.feedback_given = True  # Mark feedback as given
                st.session_state.last_conversation_id = None  # Clear last conversation
                st.session_state.clear_chat = True  # Set flag to clear chat on next rerun
                st.rerun()  # Rerun the app to refresh the UI
            elif st.session_state.feedback_given:
                st.warning("Feedback has already been provided for this conversation.")
            else:
                st.warning("No conversation to provide feedback for.")

    # Display feedback status
    if st.session_state.feedback_given:
        st.info("Feedback has already been provided for this conversation.")
    else:
        st.info("You can provide feedback for the current conversation.")

    # Display chat history
    if st.session_state.chat_history:
        st.subheader("Chat History")
        for chat in st.session_state.chat_history:
            st.write(f"**Q:** {chat['question']}")
            st.write(f"**A:** {chat['answer']}")
            st.write(f"*Relevance: {chat['relevance']}, Model: {chat['model']}*")
            st.write("---")

    # Display recent conversations
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance:",
        ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]
    )
    recent_conversations = get_recent_conversations(
        limit=3,
        relevance=relevance_filter if relevance_filter != "All" else None
    )
    for conv in recent_conversations:
        st.write(f"Q: {conv['question']}")
        st.write(f"A: {conv['answer']}")
        st.write(f"Relevance: {conv['relevance']}")
        st.write(f"Model: {conv['model_used']}")
        st.write("---")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up']}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down']}")

    # Generate a new conversation ID for the next question
    st.session_state.conversation_id = str(uuid.uuid4())

print_log("Streamlit app loop completed")

if __name__ == "__main__":
    print_log("Mental Health Assistant application started")
    main()