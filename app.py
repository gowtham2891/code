import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from datetime import datetime
import time
from dotenv import load_dotenv
import logging
import json


def console_log(event_type: str, user: str, details: str):
    """Log events to console with formatting"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🧙 {user} | {event_type} | {details}")






# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Page configuration
st.set_page_config(
    page_title="Code Wizard",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern styling
st.markdown("""
<style>
    /* Reset and Base Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    /* Theme Variables */
    :root {
        /* Light Theme Colors */
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #22c55e;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --light-bg: #f8fafc;
        --dark-bg: #1a1a1a;
        --light-text: #ffffff;
        --dark-text: #1a1a1a;
        --border-light: #e2e8f0;
        --border-dark: #404040;
        
        /* Spacing */
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        
        /* Transitions */
        --transition-fast: 0.2s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.5s ease;
    }

    /* Dark Mode Variables */
    [data-theme="dark"] {
        --background-color: var(--dark-bg);
        --text-color: var(--light-text);
        --card-bg: #2d2d2d;
        --card-border: var(--border-dark);
        --highlight-bg: #2d3748;
        --code-bg: #2d2d2d;
        --input-bg: #374151;
        --input-text: var(--light-text);
        --shadow-color: rgba(0, 0, 0, 0.3);
    }

    /* Light Mode Variables */
    [data-theme="light"] {
        --background-color: var(--light-bg);
        --text-color: var(--dark-text);
        --card-bg: #ffffff;
        --card-border: var(--border-light);
        --highlight-bg: #e0f2fe;
        --code-bg: #f8fafc;
        --input-bg: #ffffff;
        --input-text: var(--dark-text);
        --shadow-color: rgba(0, 0, 0, 0.1);
    }

    /* Main App Container */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        transition: background-color var(--transition-normal);
    }

    /* Hide Streamlit Default Elements */
    .stApp > header {
        display: none !important;
    }

    /* Welcome Container */
    .welcome-container {
        text-align: center;
        padding: var(--spacing-xl);
        background: linear-gradient(145deg, var(--card-bg), var(--highlight-bg));
        border-radius: 1rem;
        margin-bottom: var(--spacing-xl);
        box-shadow: 0 4px 15px var(--shadow-color);
        animation: slideIn 0.8s ease-out, fadeIn 0.8s ease-out;
        border: 1px solid var(--card-border);
    }

    /* Welcome Title */
    .welcome-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: var(--spacing-md);
        animation: gradientFlow 8s ease infinite;
    }

    /* Stats Cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--spacing-md);
        margin: var(--spacing-lg) 0;
    }

    .stats-card {
        background: var(--card-bg);
        border-radius: 1rem;
        padding: var(--spacing-lg);
        border: 1px solid var(--card-border);
        box-shadow: 0 4px 6px var(--shadow-color);
        transition: all var(--transition-normal);
        animation: slideUp 0.5s ease-out;
    }

    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px var(--shadow-color);
    }

    /* Chat Messages */
    .chat-container {
        margin: var(--spacing-lg) 0;
        animation: fadeIn var(--transition-normal);
    }

    .chat-message {
        padding: var(--spacing-md);
        border-radius: 0.5rem;
        margin-bottom: var(--spacing-md);
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        box-shadow: 0 2px 4px var(--shadow-color);
        animation: slideIn 0.3s ease-out;
    }

    .user-message {
        margin-left: var(--spacing-xl);
        background: var(--highlight-bg);
    }

    .assistant-message {
        margin-right: var(--spacing-xl);
    }

    /* Input Elements */
    .stTextInput input {
        color: var(--input-text);
        background-color: var(--input-bg);
        border: 1px solid var(--card-border);
        border-radius: 0.5rem;
        padding: var(--spacing-sm) var(--spacing-md);
        transition: all var(--transition-normal);
    }

    .stTextInput input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }

    /* Code Area */
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace;
        background-color: var(--code-bg);
        color: var(--text-color);
        border: 1px solid var(--card-border);
        border-radius: 0.5rem;
        padding: var(--spacing-md);
        font-size: 0.9rem;
        line-height: 1.5;
        transition: all var(--transition-normal);
    }

    .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: var(--light-text) !important;
        border: none;
        padding: var(--spacing-sm) var(--spacing-xl);
        border-radius: 0.5rem;
        font-weight: bold;
        transition: all var(--transition-normal);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    .stButton button:active {
        transform: translateY(0);
    }

    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: var(--primary-color);
        transition: width var(--transition-normal);
    }

    /* Tooltips */
    [data-tooltip]:hover::before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: var(--spacing-xs) var(--spacing-sm);
        background: var(--dark-bg);
        color: var(--light-text);
        border-radius: 0.25rem;
        font-size: 0.8rem;
        white-space: nowrap;
        animation: fadeIn 0.2s ease-out;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes gradientFlow {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }

    /* Loading Animation */
    .loading {
        display: inline-block;
        position: relative;
        width: 80px;
        height: 80px;
    }

    .loading div {
        position: absolute;
        border: 4px solid var(--primary-color);
        opacity: 1;
        border-radius: 50%;
        animation: loading 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
    }

    @keyframes loading {
        0% {
            top: 36px;
            left: 36px;
            width: 0;
            height: 0;
            opacity: 1;
        }
        100% {
            top: 0px;
            left: 0px;
            width: 72px;
            height: 72px;
            opacity: 0;
        }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .stats-container {
            grid-template-columns: 1fr;
        }

        .welcome-title {
            font-size: 2rem;
        }

        .chat-message {
            margin-left: var(--spacing-sm);
            margin-right: var(--spacing-sm);
        }
    }

    /* System Dark Mode Detection */
    @media (prefers-color-scheme: dark) {
        :root {
            color-scheme: dark;
        }
    }
</style>

<script>
    // Dark Mode Detection and Handling
    function setTheme() {
        const darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.body.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    }

    // Initial theme setting
    setTheme();

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setTheme);
</script>
""", unsafe_allow_html=True)



def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'code_submitted' not in st.session_state:
        st.session_state.code_submitted = False
    if 'current_code' not in st.session_state:
        st.session_state.current_code = ""
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    if 'code_analyses' not in st.session_state:
        st.session_state.code_analyses = 0
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()


def show_welcome_screen():
    """Display an engaging welcome screen"""
    st.markdown("""
        <div class="welcome-container">
            <h1 style="font-size: 2.5rem;">✨ Welcome to Code Wizard ✨</h1>
            <p style="font-size: 1.2rem;">Your magical companion for code enhancement!</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("welcome_form"):
        name = st.text_input(
            "🧙‍♂️ What shall we call you, fellow coder?",
            placeholder="Enter your magical name..."
        )
        submitted = st.form_submit_button("🌟 Begin Your Coding Adventure", use_container_width=True)
        
        if submitted and len(name.strip()) >= 2:
            st.session_state.user_name = name
            console_log("LOGIN", name, "New user joined")
            st.balloons()
            st.success(f"Welcome to the coding realm, {name}! 🌟")
            time.sleep(1)
            st.rerun()
        elif submitted:
            st.warning("🪄 A wizard needs a proper name (at least 2 characters)!")


def show_stats():
    """Display user stats with animations"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="stats-card">
                <h3>⏱️ Session Duration</h3>
                <p>{} minutes</p>
            </div>
        """.format(int((datetime.now() - st.session_state.session_start).total_seconds() / 60)), 
        unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stats-card">
                <h3>❓ Questions Asked</h3>
                <p>{}</p>
            </div>
        """.format(st.session_state.questions_asked), 
        unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stats-card">
                <h3>🔍 Code Analyses</h3>
                <p>{}</p>
            </div>
        """.format(st.session_state.code_analyses), 
        unsafe_allow_html=True)


def get_llm_response(prompt_template: str, **kwargs) -> str:
    """Get response from LLM using the new LangChain syntax"""
    if not GROQ_API_KEY:
        st.error("⚠️ GROQ_API_KEY not found. Please set it in your environment variables.")
        st.stop()
    
    try:
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="mixtral-8x7b-32768",
            temperature=0.7
        )
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm  # New syntax replacing LLMChain
        
        response = chain.invoke(kwargs)
        return response.content
    except Exception as e:
        st.error(f"Error in LLM processing: {str(e)}")
        return None

def analyze_code(code: str, query: str = None) -> str:
    """Analyze code using Groq LLM"""
    try:
        llm = ChatGroq(
            groq_api_key=st.secrets["GROQ_API_KEY"],
            model_name="mixtral-8x7b-32768",
            temperature=0.7
        )
        
        if query is None:
            prompt = ChatPromptTemplate.from_template("""
                As a friendly coding wizard, analyze this code:
                
                ```
                {code}
                ```
                
                Provide an engaging analysis with:
                1. 🎯 What's the code's purpose?
                2. 🔍 Key magical components
                3. 💫 Cool programming concepts
                4. ⚡ Performance insights
                5. 🛡️ Security considerations
                6. ✨ Enhancement suggestions
                
                Make it fun and clear, like explaining to a fellow wizard!
            """)
        else:
            prompt = ChatPromptTemplate.from_template("""
                Regarding this code:
                ```
                {code}
                ```
                Question: {query}
                
                Provide a clear, wizard-friendly answer with relevant examples! ✨
            """)
        
        chain = prompt | llm
        response = chain.invoke({"code": code, "query": query} if query else {"code": code})
        console_log("ANALYSIS", st.session_state.user_name, 
                   "Follow-up question" if query else "Initial analysis")
        return response.content
    except Exception as e:
        console_log("ERROR", st.session_state.user_name, f"Analysis error: {str(e)}")
        st.error("🔮 Oops! The magic went wrong. Please try again!")
        return None


def render_code_analysis_section():
    """Render the code analysis section of the app"""
    st.markdown("### 📝 Let's analyze your code!")
    code_input = st.text_area(
        "Enter your code",
        height=300,
        placeholder="Paste your code here and let's make it better together! 🚀",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze Code", type="primary", use_container_width=True) and code_input.strip():
            log_user_action("submit_code", {"code_length": len(code_input)})
            st.session_state.current_code = code_input
            with st.spinner("🤖 Analyzing your code..."):
                explanation = analyze_code(code_input, is_initial_analysis=True)
                if explanation:
                    st.session_state.code_submitted = True
                    st.session_state.messages.extend([
                        {"role": "user", "content": "Please analyze this code."},
                        {"role": "assistant", "content": explanation}
                    ])
                    st.session_state.conversation_history.extend(st.session_state.messages[-2:])
                    st.session_state.code_analyses += 1
                    st.rerun()

def render_chat_interface():
    """Render the chat interface section"""
    with st.expander("📄 View Current Code", expanded=False):
        st.code(st.session_state.current_code, language="python")
        if st.button("📝 Submit New Code"):
            st.session_state.code_submitted = False
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    
    if prompt := st.chat_input("💭 Ask me anything about the code..."):
        log_user_action("chat_message", {"message": prompt})
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.questions_asked += 1
        
        with st.spinner("🤔 Thinking..."):
            response = analyze_code(
                st.session_state.current_code, 
                prompt, 
                is_initial_analysis=False
            ) if st.session_state.is_code_context else get_llm_response(
                "Answer this programming question:\nQuestion: {query}\n\n"
                "Provide a clear, comprehensive answer with examples where applicable.\n"
                "Use emojis and formatting to make the explanation engaging.",
                query=prompt
            )
            
            if response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()

def render_sidebar():
    """Render the sidebar section"""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.session_state.is_code_context = st.checkbox(
            "Code-specific questions",
            value=st.session_state.is_code_context,
            help="Toggle between code-specific and general programming questions"
        )
    
        if st.button("🗑️ Clear Chat") and st.session_state.messages:
            log_user_action("clear_chat")
            st.session_state.messages = []
            st.session_state.code_submitted = False
            st.session_state.current_code = ""
            st.session_state.conversation_history = []
            st.success("✨ Chat cleared!")
            st.rerun()

def main():
    """Main application logic."""
    init_session_state()
    
    if not st.session_state.user_name:
        show_welcome_screen()
        return
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="welcome-title">Hello, {st.session_state.user_name}! 🌟</h1>
            <p style="font-size: 1.2rem; color: #4b5563;">Ready to make some coding magic? ✨</p>
        </div>
    """, unsafe_allow_html=True)
    
    show_user_stats()
    
    if not st.session_state.code_submitted:
        render_code_analysis_section()
    else:
        render_chat_interface()
    
    render_sidebar()

if __name__ == "__main__":
    main()
