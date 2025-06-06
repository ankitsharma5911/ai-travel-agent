import streamlit as st
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)
from prompt_template import SYSTEM_PROMPT_TEMPLATE
from dotenv import load_dotenv
import os
load_dotenv()

GROQ_API = os.getenv("GROQ_API")


st.title("🌍 Sofia - Your AI Travel Planner")
st.caption("✈️ Personalized Travel Itineraries, Activity Suggestions, and Expert Guidance")


# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    selected_model = st.selectbox(
        "Choose Model",
        ["gemma2-9b-it", "llama-3.3-70b-versatile","llama3-70b-8192","mixtral-8x7b-32768"],
        index=0
    )
    st.divider()
    st.markdown("### Model Capabilities")
    st.markdown("""
    ### ✈️ **AI Travel Planner**
    ---

    **Capabilities:**  
    - 🔍 **Input Refinement:** Gathers essential details — budget, duration, destination, preferences, and more.  
    - 🏞️ **Personalized Suggestions:** Curates top attractions, hidden gems, and activity ideas using web search tools.  
    - 📅 **Day-by-Day Itinerary:** Generates coherent, practical travel plans tailored to user preferences.  
    - 🤝 **Conversational Flow:** Asks follow-up questions to clarify missing or vague details.  
    - 🏨 **Accommodation & Dining:** Recommends stays and food options aligned with user needs.  
    - ♿ **Accessibility:** Considers mobility concerns and accessibility requirements.  
    - 🔄 **Flexible & Engaging:** Offers optional activities and alternative plans.  

    ---
    """)
    st.divider()
    st.markdown("Built with [Groq](https://groq.com/) | [LangChain](https://python.langchain.com/)")


# Initialize the Groq client
groq_client = ChatGroq(
    groq_api_key=GROQ_API,
    model_name=selected_model,
    temperature=0.3
)

# System prompt configuration
system_prompt = SystemMessagePromptTemplate.from_template(
SYSTEM_PROMPT_TEMPLATE
)

# Session state management
if "message_log" not in st.session_state:
    # Initialize message log if not present
    st.session_state.message_log = []

# Chat container
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
# Chat input and processing
user_query = st.chat_input("Type your coding question here...")

# Invocation of the AI engine
def generate_ai_response(prompt_chain):
    processing_pipeline = prompt_chain | groq_client | StrOutputParser()
    return processing_pipeline.invoke({})

def build_prompt_chain():
    prompt_sequence = [system_prompt]
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    return ChatPromptTemplate.from_messages(prompt_sequence)

if user_query:
    # Add user message to log
    st.session_state.message_log.append({"role": "user", "content": user_query})
    
    # Generate AI response
    with st.spinner("🧠 Processing..."):
        prompt_chain = build_prompt_chain()
        ai_response = generate_ai_response(prompt_chain)
    
    # Add AI response to log
    st.session_state.message_log.append({"role": "ai", "content": ai_response})
    
    # Rerun to update chat display
    st.rerun()
