import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from datetime import datetime
import time
from dotenv import load_dotenv


def log_interaction(event_type: str, details: str):
    """Simple console logging for user interactions"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {event_type}: {details}")

def log_event(event_type: str, content: str, metadata: dict = None):
    """Structured logging function for all events"""
    try:
        log_data = {
            'event_type': event_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        logger.info(json.dumps(log_data))
    except Exception as e:
        logger.error(f"Logging error: {str(e)}")


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
        --card-bg: #ffffff;
        --text-color: #1a1a1a;
        
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

    /* Animation Keyframes */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    @keyframes glowPulse {
        0% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.2); }
        50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }
        100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.2); }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
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

    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Hide Streamlit Default Elements */
    .stApp > header {
        display: none !important;
    }

    /* Welcome Container */
    .welcome-container {
        text-align: center;
        padding: var(--spacing-xl);
        background: linear-gradient(145deg, var(--card-bg), var(--light-bg));
        border-radius: 1rem;
        margin-bottom: var(--spacing-xl);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        animation: scaleIn 0.6s ease-out, glowPulse 3s infinite;
        border: 1px solid var(--border-light);
    }

    /* Welcome Title */
    .welcome-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: var(--spacing-md);
        animation: float 3s ease-in-out infinite, gradientFlow 8s ease infinite;
    }

    /* Chat Messages */
    .stChatMessage {
        padding: var(--spacing-md);
        border-radius: 0.5rem;
        margin-bottom: var(--spacing-md);
        background: var(--card-bg);
        border: 1px solid var(--border-light);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .stChatMessage.user {
        animation: slideInRight 0.5s ease-out;
        margin-left: var(--spacing-xl);
        background: var(--light-bg);
    }

    .stChatMessage.assistant {
        animation: slideInLeft 0.5s ease-out;
        margin-right: var(--spacing-xl);
    }

    /* Input Elements */
    .stTextInput input, .stTextArea textarea {
        color: var(--text-color);
        background-color: var(--card-bg);
        border: 1px solid var(--border-light);
        border-radius: 0.5rem;
        padding: var(--spacing-sm) var(--spacing-md);
        transition: all var(--transition-normal);
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        transform: scale(1.01);
    }

    /* Code Area */
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        line-height: 1.5;
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
        animation: scaleIn 0.5s ease-out;
    }

    .stButton button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    .stButton button:active {
        transform: translateY(0) scale(0.98);
    }

    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: var(--primary-color);
        transition: width var(--transition-normal);
    }

    /* Loading Spinner */
    .stSpinner {
        animation: spin 1s linear infinite;
        border: 4px solid var(--border-light);
        border-top: 4px solid var(--primary-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--light-bg), var(--card-bg));
        border-right: 1px solid var(--border-light);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .welcome-title {
            font-size: 2rem;
        }

        .stChatMessage {
            margin-left: var(--spacing-sm);
            margin-right: var(--spacing-sm);
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

def log_user_action(action_type: str, details: dict = None):
    """Log user actions with additional details"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "user": st.session_state.user_name,
        "action": action_type,
        "session_id": st.session_state.get("session_id", "unknown"),
        "details": details or {}
    }
    logging.info(json.dumps(log_data))

def init_session_state():
    """Initialize all session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'code_submitted' not in st.session_state:
        st.session_state.code_submitted = False
    if 'current_code' not in st.session_state:
        st.session_state.current_code = ""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'is_code_context' not in st.session_state:
        st.session_state.is_code_context = True
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    if 'code_analyses' not in st.session_state:
        st.session_state.code_analyses = 0


def show_welcome_screen():
    """Display welcome screen with enhanced animations"""
    st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">🪄 Welcome to Code Wizard</h1>
            <p style="font-size: 1.2rem;">Your magical companion for code analysis</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("welcome_form"):
        name = st.text_input("🧙‍♂️ What's your name?", placeholder="Enter your name...")
        submitted = st.form_submit_button("✨ Begin Your Journey", use_container_width=True)
        
        if submitted and name.strip():
            st.session_state.user_name = name
            log_interaction("login", f"New user: {name}")
            st.success(f"Welcome, {name}! 🌟")
            time.sleep(1)
            st.rerun()
            



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
    """Analyze code using the Groq LLM"""
    try:
        if query is None:
            prompt_template = """
            Analyze this code:
            ```
            {code}
            ```
            Provide a detailed analysis including:
            1. 🎯 Overview
            2. 🔍 Key components
            3. 💡 Concepts used
            4. ⚡ Performance notes
            5. ✨ Potential improvements
            """
            log_interaction("code_analysis", "Initial code analysis requested")
        else:
            prompt_template = """
            Code:
            ```
            {code}
            ```
            Question: {query}
            Provide a focused answer with relevant examples.
            """
            log_interaction("question", f"User asked: {query}")
        
        return get_llm_response(prompt_template, code=code, query=query)
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None


def render_code_analysis_section():
    """Render code analysis section"""
    st.markdown("### 📝 Let's analyze your code!")
    code_input = st.text_area(
        "Enter your code",
        height=300,
        placeholder="Paste your code here! 🚀",
        label_visibility="collapsed"
    )
    
    if st.button("🔍 Analyze Code", type="primary", use_container_width=True) and code_input.strip():
        st.session_state.current_code = code_input
        with st.spinner("🤖 Analyzing..."):
            explanation = analyze_code(code_input)
            if explanation:
                st.session_state.code_submitted = True
                st.session_state.messages.extend([
                    {"role": "user", "content": "Please analyze this code."},
                    {"role": "assistant", "content": explanation}
                ])
                st.rerun()


def render_chat_interface():
    """Render chat interface"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("💭 Ask about the code..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("🤔 Thinking..."):
            response = analyze_code(st.session_state.current_code, prompt)
            if response:
                st.session_state.messages.append({
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
    """Main application logic"""
    init_session_state()
    
    if not st.session_state.user_name:
        show_welcome_screen()
        return

    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="welcome-title">Hello, {st.session_state.user_name}! 🌟</h1>
            <p style="font-size: 1.2rem;">Let's make some coding magic! ✨</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.code_submitted:
        render_code_analysis_section()
    else:
        render_chat_interface()
    
    # Simple sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Options")
        if st.button("🗑️ Clear Chat"):
            log_interaction("clear_chat", f"Chat cleared by {st.session_state.user_name}")
            st.session_state.messages = []
            st.session_state.code_submitted = False
            st.session_state.current_code = ""
            st.rerun()

if __name__ == "__main__":
    main()
