"""
Frontend configuration settings.
"""

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_TIMEOUT = 30
STREAM_TIMEOUT = 60

# UI Configuration
PAGE_TITLE = "Basecamp Handbook AI Assistant"
PAGE_ICON = "📚"

# Example Questions
EXAMPLE_QUESTIONS = [
    "What is the vacation policy?",
    "What are the remote work rules?",
    "Is there a moonlighting policy?",
    "How are working hours organized?",
    "What internal communication tools are used?"
]

# CSS Styles
CUSTOM_CSS = """
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    color: #1E3A8A;
    text-align: center;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #6B7280;
    text-align: center;
    margin-bottom: 2rem;
}
.source-card {
    background-color: #F3F4F6;
    border-left: 4px solid #3B82F6;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 0.5rem;
}
.answer-box {
    background-color: #EFF6FF;
    padding: 1.5rem;
    border-radius: 0.5rem;
    border-left: 4px solid #3B82F6;
    margin: 1rem 0;
    color: #1F2937;
    font-size: 1rem;
    line-height: 1.6;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 0.75rem;
    margin: 0.5rem 0;
}
</style>
"""
