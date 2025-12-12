# Mirador Chain Inputs Guide

**Created:** 2025-12-11
**Status:** Production-Ready Demo Inputs
**Validated:** Security Audit chain successfully executed

---

## Success Record: Security Audit Chain

**Date:** 2025-12-11 ~22:30 EST
**Chain:** `security_audit` (4 personas)
**Input:** SQL injection vulnerable login function

### Results

| Persona | Tokens | Time | Output Quality |
|---------|--------|------|----------------|
| master_coder | 368 | 189s | Identified 3 critical issues, provided secure implementation |
| code_reviewer | 547 | 312s | Detailed review with error handling additions |
| cross_model_synthesizer | 343 | 226s | Pattern synthesis, consolidated bcrypt solution |
| **Total** | **1,258** | **~12 min** | **Accurate security analysis** |

### Validation
- SQL Injection: Correctly identified (CVSS 9.8)
- Plain text passwords: Correctly identified
- Session issues: Correctly identified
- Recommendations: Industry standard (parameterized queries, bcrypt, Flask-Login)
- Minor code bug in synthesizer output (expected - requires human review)

---

## Chain Types and Recommended Inputs

### 1. Quick Review
**Personas:** master_coder, code_reviewer, cross_model_synthesizer
**Best for:** Fast feedback on code snippets
**Time:** ~8-12 minutes

**Recommended Input:**
```python
def calculate_discount(price, user_type):
    if user_type == "premium":
        return price * 0.8
    elif user_type == "member":
        return price * 0.9
    else:
        return price

# Ufamily_member
final_price = calculate_discount(100, user_input)
```

**Expected Analysis:**
- Input validation missing
- Magic numbers should be constants
- Could use enum for user types
- No error handling for negative prices

---

### 2. Security Audit
**Personas:** security_expert, code_reviewer, cross_model_synthesizer, self_reflection_guardian
**Best for:** Vulnerability detection, compliance review
**Time:** ~12-15 minutes

**Recommended Input (VALIDATED):**
```python
def login(username, password):
    query = f"SELECT * FROM users WHERE name='{username}' AND pwd='{password}'"
    result = db.execute(query)
    if result:
        session['user'] = username
        return redirect('/dashboard')
    return "Login failed"
```

**Alternative Inputs:**

**API Key Exposure:**
```python
import requests

API_KEY = "sk-proj-abc123xyz789"

def fetch_data(endpoint):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get(f"https://api.example.com/{endpoint}", headers=headers)
```

**File Path Traversal:**
```python
def get_user_file(filename):
    filepath = f"/var/uploads/{filename}"
    with open(filepath, 'r') as f:
        return f.read()
```

**XSS Vulnerability:**
```python
from flask import request, render_template_string

@app.route('/search')
def search():
    query = request.args.get('q', '')
    return render_template_string(f"<h1>Results for: {query}</h1>")
```

---

### 3. Code Review
**Personas:** master_coder, code_reviewer, test_architect, feedback_loop_optimizer
**Best for:** Comprehensive code quality analysis
**Time:** ~15-20 minutes

**Recommended Input:**
```python
class UserManager:
    def __init__(self):
        self.users = []
        self.db = Database()

    def add_user(self, name, email, age):
        user = {"name": name, "email": email, "age": age}
        self.users.append(user)
        self.db.insert("users", user)
        self.send_welcome_email(email)
        self.log_action("user_created", name)
        return user

    def get_user(self, name):
        for user in self.users:
            if user["name"] == name:
                return user
        return self.db.query("SELECT * FROM users WHERE name = ?", name)

    def delete_user(self, name):
        self.users = [u for u in self.users if u["name"] != name]
        self.db.delete("users", {"name": name})
```

**Expected Analysis:**
- Single Responsibility Principle violation
- In-memory/database sync issues
- Missing error handling
- No input validation
- Tight coupling to Database class
- Missing type hints
- No transaction handling

---

### 4. Architecture
**Personas:** master_coder, api_designer, database_architect, devops_engineer
**Best for:** System design review, scalability analysis
**Time:** ~15-20 minutes

**Recommended Input:**
```
System: E-commerce platform

Current Architecture:
- Monolithic Django application
- Single PostgreSQL database
- File uploads stored locally
- Session-based authentication
- Synchronous order processing
- Single server deployment

Requirements:
- Support 10,000 concurrent users
- 99.9% uptime SLA
- Multi-region deployment
- Real-time inventory updates
- Mobile app support planned

What architectural changes are needed?
```

**Alternative Input (Microservices):**
```
We have these microservices:
- user-service (Node.js, MongoDB)
- order-service (Python, PostgreSQL)
- inventory-service (Go, Redis)
- notification-service (Python, RabbitMQ)

Problems:
1. Services directly call each other via HTTP
2. No service discovery
3. Distributed transactions failing
4. Log aggregation is manual

How should we improve this architecture?
```

---

### 5. Business Analysis
**Personas:** business_analyst, project_manager, ux_analyst
**Best for:** Requirements analysis, feature planning
**Time:** ~10-15 minutes

**Recommended Input:**
```
Feature Request: User Dashboard Redesign

Current State:
- Dashboard shows 15 widgets
- Users complain it's overwhelming
- 40% of users never scroll below fold
- Mobile experience is poor
- Average session time: 2 minutes

Business Goals:
- Increase user engagement by 25%
- Reduce support tickets about navigation
- Improve mobile conversion rate

User Feedback:
"I can't find what I need"
"Too much information at once"
"Works terribly on my phone"

What should we prioritize?
```

**Alternative Input (Product Launch):**
```
New Product: AI-Powered Code Review Tool

Target Market:
- Small development teams (5-20 developers)
- Companies without dedicated security teams
- Startups moving fast with limited resources

Competitors:
- SonarQube (enterprise, complex setup)
- CodeClimate (subscription expensive)
- GitHub Copilot (different focus)

Our Differentiators:
- Local execution (data never leaves)
- One-time purchase option
- Simple setup (<5 minutes)

What's our go-to-market strategy?
```

---

### 6. Meta-Cognitive Only
**Personas:** cross_model_synthesizer, feedback_loop_optimizer, self_reflection_guardian
**Best for:** Improving existing analysis, finding blindspots
**Time:** ~10-12 minutes

**Recommended Input:**
```
Previous Analysis Output:

The application has a SQL injection vulnerability in the login function.
We recommend using parameterized queries.

The password storage is insecure - use bcrypt.

Session management needs improvement.

---

Please analyze this security assessment for:
1. Missing considerations
2. Priority ordering
3. Implementation complexity
4. Potential blindspots
```

**Alternative Input (Synthesis):**
```
Team Discussion Summary:

Developer A: "We should rewrite in Rust for performance"
Developer B: "The bottleneck is the database, not the code"
Developer C: "We need better caching first"
PM: "Users are complaining about slow page loads"

Current metrics:
- API response time: 200ms average
- Database queries: 50ms average
- Frontend render: 800ms average

Synthesize these perspectives and identify the real issue.
```

---

### 7. Full 16-Persona
**Personas:** All 16 personas in sequence
**Best for:** Comprehensive analysis of complex problems
**Time:** ~45-60 minutes

**Recommended Input:**
```
Project: Healthcare Patient Portal

Context:
We're building a patient portal for a hospital network.
Patients will access medical records, schedule appointments,
mesfamily_member doctors, and view test results.

Technical Stack (proposed):
- React frontend
- Node.js API
- PostgreSQL database
- AWS deployment

Constraints:
- HIPAA compliance required
- Must integrate with existing EMR (Epic)
- 500,000 potential users
- Launch in 6 months
- Budget: $500k

Please provide comprehensive analysis covering:
- Architecture recommendations
- Security requirements
- Development approach
- Risk assessment
- Timeline feasibility
```

**This input will exercise all 16 personas:**
- Development: master_coder, code_reviewer, debug_specialist, test_architect
- Security: security_expert, performance_optimizer
- Architecture: api_designer, database_architect, devops_engineer
- Business: ux_analyst, business_analyst, project_manager
- Creative: documentation_writer
- Meta: cross_model_synthesizer, feedback_loop_optimizer, self_reflection_guardian

---

## Input Design Principles

### What Makes a Good Mirador Input

1. **Specific Context** - Include relevant details (language, framework, constraints)
2. **Clear Problem** - State what needs analysis
3. **Appropriate Scope** - Match input complexity to chain type
4. **Realistic Code** - Use production-like examples, not toy code

### Input Length Guidelines

| Chain Type | Recommended Input Size |
|------------|----------------------|
| Quick Review | 10-30 lines of code |
| Security Audit | 10-50 lines with vulnerabilities |
| Code Review | 30-100 lines of a module |
| Architecture | 100-300 words describing system |
| Business Analysis | 100-200 words with metrics |
| Meta-Cognitive | Previous analysis + questions |
| Full 16-Persona | 200-500 words comprehensive brief |

### Avoid

- Extremely long inputs (>500 lines) - split into multiple chains
- Vague requests ("review this code") - be specific
- No context ("fix this") - provide background
- Multiple unrelated concerns - focus each chain

---

## Demo Script for Portfolio

### 60-Second Demo
1. Show landing page hero
2. Click "Connect" to localhost:5001
3. Select "Quick Review"
4. Paste discount function
5. Execute - show streaming output
6. Point to meta-cognitive synthesis

### 5-Minute Demo
1. Landing page overview
2. Connect to local API
3. Run Security Audit with SQL injection code
4. Show each persona's output streaming
5. Highlight vulnerability detection accuracy
6. Show meta-cognitive synthesis
7. Discuss local execution / HIPAA benefit

### Technical Deep Dive (15 min)
1. Architecture diagram walkthrough
2. Live Security Audit demo
3. Explain context accumulation
4. Show API endpoints via curl
5. Run Architecture chain
6. Discuss research alignment
7. Show GitHub source

---

## Performance Expectations

| Chain | Personas | Cold Start | Warm |
|-------|----------|------------|------|
| Quick Review | 3 | ~12 min | ~5 min |
| Security Audit | 4 | ~15 min | ~8 min |
| Code Review | 4 | ~15 min | ~8 min |
| Architecture | 4 | ~15 min | ~8 min |
| Business Analysis | 3 | ~12 min | ~5 min |
| Meta-Cognitive | 3 | ~12 min | ~5 min |
| Full 16-Persona | 16 | ~60 min | ~30 min |

*Times based on llama3.2:latest on Apple Silicon. Faster models (mistral:7b) reduce times significantly.*

---

## Next Steps

1. [ ] Test each chain type with recommended inputs
2. [ ] Record demo videos for portfolio
3. [ ] Add "Copy Input" buttons to landing page
4. [ ] Create preset inputs in UI dropdown
5. [ ] Optimize timeout handling for better UX
