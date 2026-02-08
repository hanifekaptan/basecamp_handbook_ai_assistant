# API Usage Examples

Practical examples of using the Basecamp Handbook RAG API in various scenarios and languages.

## Quick Start Examples

### Python

#### Basic Question

```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={"question": "What is the vacation policy?"}
)

data = response.json()
print(f"Answer: {data['answer']}\n")
print(f"Sources: {len(data['sources'])} documents")
```

#### Streaming Response

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ask/stream",
    json={"question": "What are the company values?"},
    stream=True
)

print("Answer: ", end='', flush=True)
for line in response.iter_lines():
    if line:
        token = line.decode('utf-8').replace('data: ', '')
        print(token, end='', flush=True)
print()
```

---

### JavaScript / Node.js

#### Basic Question (async/await)

```javascript
const axios = require('axios');

async function askQuestion(question) {
    const response = await axios.post('http://localhost:8000/api/v1/ask', {
        question: question
    });
    
    return response.data;
}

// Usage
askQuestion("What health insurance is offered?")
    .then(data => {
        console.log('Answer:', data.answer);
        console.log('Sources:', data.sources.length);
    });
```

#### Streaming Response (fetch API)

```javascript
async function askStreaming(question) {
    const response = await fetch('http://localhost:8000/api/v1/ask/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        process.stdout.write(chunk.replace(/^data: /gm, ''));
    }
}

askStreaming("What are the company values?");
```

---

### cURL

#### Basic Question

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the vacation policy?"}'
```

#### With Pretty Printing (using jq)

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the vacation policy?"}' \
  | jq '.'
```

#### Extract Only Answer

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the vacation policy?"}' \
  | jq -r '.answer'
```

#### Streaming

```bash
curl -X POST http://localhost:8000/api/v1/ask/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -N \
  -d '{"question": "What are the benefits?"}'
```

---

## Common Use Cases

### 1. Employee Onboarding Bot

```python
"""
Interactive onboarding assistant
"""
import requests

class OnboardingBot:
    def __init__(self, api_url="http://localhost:8000/api/v1"):
        self.api_url = api_url
    
    def ask(self, question):
        """Ask a question for new employees"""
        response = requests.post(
            f"{self.api_url}/ask",
            json={"question": question}
        )
        return response.json()
    
    def get_onboarding_info(self):
        """Get common onboarding questions answered"""
        questions = [
            "What do I need to do on my first day?",
            "What benefits am I eligible for?",
            "How do I set up my work equipment?",
            "What are the company values?"
        ]
        
        answers = {}
        for question in questions:
            result = self.ask(question)
            answers[question] = result['answer']
        
        return answers

# Usage
bot = OnboardingBot()
onboarding_info = bot.get_onboarding_info()

for question, answer in onboarding_info.items():
    print(f"\nQ: {question}")
    print(f"A: {answer}\n")
    print("-" * 80)
```

### 2. Slack Bot Integration

```python
"""
Slack bot that answers handbook questions
"""
from slack_bolt import App
import requests

app = App(token="xoxb-your-token")

@app.message("ask:")
def handle_handbook_question(message, say):
    # Extract question from message
    question = message['text'].replace('ask:', '').strip()
    
    # Query RAG API
    response = requests.post(
        "http://localhost:8000/api/v1/ask",
        json={"question": question}
    )
    
    data = response.json()
    
    # Format response for Slack
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Answer:*\n{data['answer']}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📚 Sources: {len(data['sources'])} documents"
                }
            ]
        }
    ]
    
    say(blocks=blocks)

# Start bot
if __name__ == "__main__":
    app.start(port=3000)
```

**Usage in Slack**:
```
ask: What is the vacation policy?
```

### 3. CLI Tool

```python
"""
Command-line handbook search tool
"""
import click
import requests
from rich.console import Console
from rich.markdown import Markdown

console = Console()

@click.command()
@click.argument('question')
@click.option('--stream', is_flag=True, help='Stream the response')
def ask(question, stream):
    """Ask a question about the Basecamp handbook"""
    
    if stream:
        # Streaming mode
        response = requests.post(
            "http://localhost:8000/api/v1/ask/stream",
            json={"question": question},
            stream=True
        )
        
        console.print(f"\n[bold]Question:[/bold] {question}\n")
        console.print("[bold]Answer:[/bold] ", end='')
        
        for line in response.iter_lines():
            if line:
                token = line.decode('utf-8').replace('data: ', '')
                console.print(token, end='')
        console.print("\n")
    else:
        # Normal mode
        response = requests.post(
            "http://localhost:8000/api/v1/ask",
            json={"question": question}
        )
        
        data = response.json()
        
        console.print(f"\n[bold]Question:[/bold] {question}\n")
        console.print(Markdown(f"**Answer:**\n{data['answer']}"))
        console.print(f"\n[dim]Sources: {len(data['sources'])} documents[/dim]\n")

if __name__ == '__main__':
    ask()
```

**Usage**:
```bash
# Install dependencies
pip install click rich

# Ask a question
python handbook_cli.py "What is the vacation policy?"

# With streaming
python handbook_cli.py "What are the benefits?" --stream
```

### 4. Web Dashboard (Flask)

```python
"""
Simple web dashboard for handbook Q&A
"""
from flask import Flask, render_template, request, jsonify, stream_with_context, Response
import requests

app = Flask(__name__)
RAG_API = "http://localhost:8000/api/v1"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    
    response = requests.post(
        f"{RAG_API}/ask",
        json={"question": question}
    )
    
    return jsonify(response.json())

@app.route('/stream', methods=['POST'])
def stream():
    data = request.json
    question = data.get('question')
    
    def generate():
        response = requests.post(
            f"{RAG_API}/ask/stream",
            json={"question": question},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                yield line.decode('utf-8') + '\n'
    
    return Response(stream_with_context(generate()), 
                    mimetype='text/event-stream')

@app.route('/health')
def health():
    response = requests.get(f"{RAG_API}/health")
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Template (templates/index.html)**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Handbook Q&A</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        #question { width: 100%; padding: 10px; font-size: 16px; }
        #answer { margin-top: 20px; padding: 20px; background: #f5f5f5; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>📚 Basecamp Handbook Q&A</h1>
    
    <input type="text" id="question" placeholder="Ask a question...">
    <button onclick="askQuestion()">Ask</button>
    
    <div id="answer"></div>
    
    <script>
        async function askQuestion() {
            const question = document.getElementById('question').value;
            const answerDiv = document.getElementById('answer');
            
            answerDiv.innerHTML = 'Loading...';
            
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: question})
            });
            
            const data = await response.json();
            answerDiv.innerHTML = `
                <strong>Answer:</strong><br>
                ${data.answer}<br><br>
                <small>Sources: ${data.sources.length} documents</small>
            `;
        }
    </script>
</body>
</html>
```

### 5. Batch Processing

```python
"""
Process multiple questions in batch
"""
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def ask_question(question):
    """Ask a single question"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/ask",
            json={"question": question},
            timeout=30
        )
        return {
            "question": question,
            "answer": response.json()['answer'],
            "status": "success"
        }
    except Exception as e:
        return {
            "question": question,
            "answer": None,
            "status": f"error: {str(e)}"
        }

def batch_ask(questions, max_workers=5):
    """Process questions in parallel"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(ask_question, q): q for q in questions}
        
        for future in as_completed(futures):
            results.append(future.result())
    
    return results

# Example usage
questions = [
    "What is the vacation policy?",
    "What health insurance is offered?",
    "How does 401(k) matching work?",
    "What are the remote work guidelines?",
    "What is the code of conduct?"
]

results = batch_ask(questions, max_workers=3)

# Save to CSV
df = pd.DataFrame(results)
df.to_csv('handbook_qa.csv', index=False)

print(f"Processed {len(results)} questions")
print(f"Success: {sum(1 for r in results if r['status'] == 'success')}")
```

---

## Error Handling

### Python: Robust Error Handling

```python
import requests
from typing import Optional, Dict, Any

class HandbookAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def ask(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Ask a question with comprehensive error handling
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                json={"question": question},
                timeout=30
            )
            
            # Check HTTP status
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error = response.json()
                print(f"❌ Invalid request: {error['detail']['message']}")
            elif response.status_code == 503:
                print("❌ Service unavailable. Is Ollama running?")
            else:
                print(f"❌ Unexpected error: {response.status_code}")
            
            return None
            
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Is the server running?")
            return None
        except requests.exceptions.Timeout:
            print("❌ Request timed out. Try again.")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return None
    
    def check_health(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data['status'] == 'healthy' and data['ollama_available']
            return False
        except:
            return False

# Usage
api = HandbookAPI()

# Check health first
if not api.check_health():
    print("⚠️  API is not healthy. Please check:")
    print("  1. Is the backend running? (python backend/main.py)")
    print("  2. Is Ollama running? (ollama serve)")
    exit(1)

# Ask question
result = api.ask("What is the vacation policy?")
if result:
    print(f"✅ Answer: {result['answer']}")
```

---

## Performance Optimization

### Caching Results

```python
"""
Cache responses to avoid redundant API calls
"""
import requests
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def ask_cached(question: str) -> dict:
    """
    Cached version of ask - won't make API call if question was asked before
    """
    response = requests.post(
        "http://localhost:8000/api/v1/ask",
        json={"question": question}
    )
    return response.json()

# Usage
result1 = ask_cached("What is vacation policy?")  # API call
result2 = ask_cached("What is vacation policy?")  # Cached (no API call)
```

### Rate Limiting

```python
"""
Implement client-side rate limiting
"""
import time
import requests
from collections import deque

class RateLimitedAPI:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def _check_rate_limit(self):
        """Enforce rate limit"""
        now = time.time()
        
        # Remove old requests outside time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        # Check if limit exceeded
        if len(self.requests) >= self.max_requests:
            sleep_time = self.requests[0] + self.time_window - now
            if sleep_time > 0:
                print(f"Rate limit reached. Waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                self._check_rate_limit()
        
        self.requests.append(now)
    
    def ask(self, question):
        """Ask with rate limiting"""
        self._check_rate_limit()
        
        response = requests.post(
            "http://localhost:8000/api/v1/ask",
            json={"question": question}
        )
        return response.json()

# Usage (max 10 requests per minute)
api = RateLimitedAPI(max_requests=10, time_window=60)

for i in range(20):
    result = api.ask(f"Question {i}")
    print(f"Processed question {i}")
```

---

## Next Steps

- [API Endpoints](endpoints.md) - Complete endpoint reference
- [API Schemas](schemas.md) - Detailed data models
- [Getting Started](../getting-started.md) - Installation and setup

---

**Example Categories**:

- ✅ Quick Start (Python, JavaScript, cURL)
- ✅ Use Cases (Onboarding, Slack, CLI, Dashboard, Batch)
- ✅ Error Handling
- ✅ Performance Optimization (Caching, Rate Limiting)
