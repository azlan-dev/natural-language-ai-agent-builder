# 🏗️ Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                      (Streamlit Web App)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Natural    │  │   Template   │  │     View     │     │
│  │   Language   │  │     Mode     │  │  Generated   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     CORE APPLICATION                         │
│                   (src/ Python Modules)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │          Agent Generator (agent_generator.py)      │    │
│  │  • Orchestrates agent creation                     │    │
│  │  • Validates configurations                        │    │
│  │  • Manages refinement loop                         │    │
│  └──────────┬─────────────────────────┬─────────────┘    │
│             │                         │                     │
│             ▼                         ▼                     │
│  ┌──────────────────┐     ┌─────────────────────┐         │
│  │   LLM Client     │     │   Block Manager     │         │
│  │ (llm_client.py)  │     │   (blocks.py)       │         │
│  │                  │     │                     │         │
│  │ • OpenAI GPT-4   │     │ • Tool definitions  │         │
│  │ • Google Gemini  │     │ • Capability search │         │
│  │ • Provider       │     │ • Schema validation │         │
│  │   abstraction    │     │                     │         │
│  └──────────────────┘     └─────────────────────┘         │
│             │                         │                     │
│             └──────────┬──────────────┘                     │
│                        │                                     │
│                        ▼                                     │
│  ┌─────────────────────────────────────────────┐           │
│  │      Template Manager (templates.py)        │           │
│  │  • Pre-built agent patterns                 │           │
│  │  • Keyword matching                         │           │
│  │  • Template customization                   │           │
│  └─────────────────────────────────────────────┘           │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA & CONFIGURATION                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   blocks.    │  │  templates.  │  │  generated_  │     │
│  │     json     │  │     json     │  │   agents/    │     │
│  │              │  │              │  │              │     │
│  │ • Tool defs  │  │ • Agent      │  │ • Saved      │     │
│  │ • Schemas    │  │   templates  │  │   agents     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. User Interface Layer (app.py)

**Responsibilities:**
- Render web interface
- Handle user interactions
- Display agent configurations
- Manage session state
- Provide real-time feedback

**Key Features:**
- Multi-mode interface
- Real-time validation display
- JSON preview and export
- Agent history tracking
- Responsive design

**Dependencies:**
- Streamlit
- Agent Generator
- Block Manager
- Template Manager

---

### 2. Agent Generator (agent_generator.py)

**Responsibilities:**
- Orchestrate agent creation process
- Interface with LLM for generation
- Validate agent configurations
- Manage refinement iterations
- Save/load agents

**Key Classes:**

#### `AgentGenerator`
```python
class AgentGenerator:
    def __init__(self)
    def generate_from_description(description: str) -> Dict
    def generate_from_template(template_id: str) -> Dict
    def refine_agent(config: Dict, refinement: str) -> Dict
    def validate_agent(config: Dict) -> List[str]
    def save_agent(agent_data: Dict) -> Path
```

**Validation Schema:**
```python
AGENT_SCHEMA = {
    "type": "object",
    "required": ["name", "description", "systemPrompt", "tasks"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "systemPrompt": {"type": "string"},
        "tasks": {"type": "array"},
        "memory": {"type": "object"}
    }
}
```

---

### 3. LLM Client (llm_client.py)

**Responsibilities:**
- Abstract LLM provider differences
- Format prompts for agent generation
- Handle API communication
- Manage provider-specific configurations

**Key Classes:**

#### `LLMClient`
```python
class LLMClient:
    def __init__(provider: Optional[str])
    def _initialize_llm() -> BaseChatModel
    def generate_agent(description: str, blocks_summary: str) -> str
    def refine_agent(config: str, refinement: str) -> str
```

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Google (Gemini Pro)
- Extensible for more

**System Prompt Template:**
```python
"""
You are an expert AutoGPT agent architect.
Generate complete agent.json with:
- Subtasks
- Memory configuration
- System prompt
- Tool selection

Available Tools:
{blocks_summary}

Output Format: JSON only
"""
```

---

### 4. Block Manager (blocks.py)

**Responsibilities:**
- Load and manage tool/block definitions
- Search blocks by capabilities
- Validate block usage
- Provide block summaries for LLM

**Key Classes:**

#### `BlockManager`
```python
class BlockManager:
    def __init__(self)
    def _load_blocks()
    def get_all_blocks() -> List[BlockSchema]
    def get_block_by_name(name: str) -> Optional[BlockSchema]
    def search_blocks(keywords: List[str]) -> List[BlockSchema]
    def get_blocks_summary() -> str
```

#### `BlockSchema`
```python
class BlockSchema(BaseModel):
    id: str
    name: str
    description: str
    category: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    capabilities: List[str]
```

**Block Categories:**
- `data_collection` - Web search, API calls
- `generation` - Text, email generation
- `processing` - Summarization, filtering
- `analysis` - Sentiment, trends
- `integration` - Export, scheduling
- `automation` - Workflow triggers

---

### 5. Template Manager (templates.py)

**Responsibilities:**
- Load pre-built agent templates
- Match user intent to templates
- Suggest relevant templates
- Customize template parameters

**Key Classes:**

#### `TemplateManager`
```python
class TemplateManager:
    def __init__(self)
    def _load_templates()
    def get_all_templates() -> List[AgentTemplate]
    def search_templates(query: str) -> List[AgentTemplate]
    def get_template_by_id(id: str) -> Optional[AgentTemplate]
```

#### `AgentTemplate`
```python
class AgentTemplate(BaseModel):
    id: str
    name: str
    description: str
    keywords: List[str]
    agent_config: Dict[str, Any]
```

---

### 6. Configuration (config.py)

**Responsibilities:**
- Load environment variables
- Manage paths
- Validate configuration
- Provide global settings

**Configuration Sources:**
- `.env` file (API keys, provider)
- Environment variables
- Default values

**Key Settings:**
```python
LLM_PROVIDER = "openai" | "google"
OPENAI_API_KEY = "sk-..."
GOOGLE_API_KEY = "..."
OPENAI_MODEL = "gpt-4-turbo-preview"
GOOGLE_MODEL = "gemini-pro"
ENABLE_VECTOR_STORE = true/false
```

---

## Data Flow

### Agent Creation Flow

```
1. User enters description
   ↓
2. UI passes to AgentGenerator.generate_from_description()
   ↓
3. Generator gets blocks summary from BlockManager
   ↓
4. Generator calls LLMClient.generate_agent()
   ↓
5. LLM Client formats prompt and calls LLM API
   ↓
6. LLM returns JSON configuration
   ↓
7. Generator validates with BlockManager
   ↓
8. Generator returns validated agent + metadata
   ↓
9. UI displays agent with validation results
   ↓
10. User can save, download, or refine
```

### Refinement Flow

```
1. User enters refinement request
   ↓
2. UI passes current config + request to Generator
   ↓
3. Generator calls LLMClient.refine_agent()
   ↓
4. LLM modifies configuration
   ↓
5. Generator validates updated config
   ↓
6. UI displays refined agent
```

### Template Flow

```
1. User selects template
   ↓
2. UI passes template_id to Generator
   ↓
3. Generator gets template from TemplateManager
   ↓
4. Generator applies custom parameters (if any)
   ↓
5. Generator validates configuration
   ↓
6. UI displays agent
```

---

## Storage Architecture

### File-Based Storage

```
generated_agents/
├── agent_name_20240115_103000.json
├── sales_assistant_20240115_110000.json
└── research_agent_20240115_113000.json
```

**Agent File Format:**
```json
{
  "agent": {
    "name": "...",
    "description": "...",
    "systemPrompt": "...",
    "tasks": [...],
    "memory": {...}
  },
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "description": "...",
    "provider": "openai"
  }
}
```

**Benefits:**
- ✅ Simple and reliable
- ✅ Human-readable
- ✅ Version control friendly
- ✅ Easy to backup
- ✅ No database required

**Future Enhancement:**
- Vector store for similarity search
- Database backend for scaling
- Cloud storage integration

---

## Security Architecture

### API Key Management

```
Environment (.env)
    ↓
Config Module (config.py)
    ↓
LLM Client (llm_client.py)
    ↓
LLM API (OpenAI/Google)
```

**Security Measures:**
- ✅ `.env` in `.gitignore`
- ✅ No keys in code
- ✅ Environment variable validation
- ✅ Provider abstraction
- ✅ Secure key storage

### Input Validation

```
User Input
    ↓
Streamlit UI (sanitization)
    ↓
Agent Generator (validation)
    ↓
JSON Schema (structure check)
    ↓
Block Manager (tool validation)
    ↓
Validated Agent
```

---

## Extension Points

### Adding New Blocks

**Where:** `config/blocks.json`

**Steps:**
1. Define block schema
2. Add to `blocks.json`
3. Test with sample agent
4. Document usage

**Example:**
```json
{
  "id": "slack_notify",
  "name": "SlackNotificationBlock",
  "description": "Send notifications to Slack",
  "category": "integration",
  "inputs": {
    "message": {"type": "string", "required": true},
    "channel": {"type": "string", "required": true}
  },
  "outputs": {
    "message_id": {"type": "string"}
  },
  "capabilities": ["slack", "notification", "messaging"]
}
```

### Adding New Templates

**Where:** `config/templates.json`

**Steps:**
1. Create agent configuration
2. Add keywords for matching
3. Test thoroughly
4. Add example

### Adding New LLM Providers

**Where:** `src/llm_client.py`

**Steps:**
1. Install provider's library
2. Add provider initialization
3. Update config.py
4. Update .env.example
5. Test generation
6. Document setup

**Example:**
```python
elif self.provider == "anthropic":
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model="claude-3-opus",
        anthropic_api_key=ANTHROPIC_API_KEY
    )
```

---

## Error Handling

### Validation Errors

```
User Input → Validation → Error Display
                ↓
         Helpful Message
                ↓
         Suggestions
```

**Error Types:**
- Schema validation errors
- Unknown block errors
- Missing input errors
- Reference errors
- API errors

**User Experience:**
- ✅ Clear error messages
- ✅ Actionable suggestions
- ✅ Partial success handling
- ✅ Graceful degradation

### API Errors

```python
try:
    response = llm.invoke(messages)
except Exception as e:
    # Log error
    # Show user-friendly message
    # Suggest alternative provider
    # Enable retry
```

---

## Performance Considerations

### Response Time

**Typical Flow:**
- User input: < 1s
- LLM generation: 3-10s
- Validation: < 1s
- UI update: < 1s

**Total:** ~5-12 seconds

**Optimization:**
- Cached block summaries
- Efficient JSON parsing
- Minimal LLM calls
- Streamlined validation

### Scalability

**Current:**
- File-based storage
- Single-user sessions
- Stateless design

**Future:**
- Database backend
- Multi-user support
- Caching layer
- Load balancing

---

## Testing Architecture

### Unit Tests

```
tests/
├── test_blocks.py          # Block system
├── test_templates.py       # Templates
└── test_agent_generator.py # Generation
```

**Test Coverage:**
- Block loading and search
- Template matching
- Agent validation
- Schema compliance
- Error handling

### Integration Tests

**Mock LLM responses:**
```python
@pytest.mark.skipif(True, reason="Requires API")
def test_full_generation():
    generator = AgentGenerator()
    result = generator.generate_from_description("...")
    assert "agent" in result
```

---

## Deployment Architecture

### Local Development

```
Developer Machine
    ↓
Python 3.8+
    ↓
Streamlit Server (port 8501)
    ↓
Browser (localhost:8501)
```

### Production Options

**Option 1: Streamlit Cloud**
```
GitHub Repo
    ↓
Streamlit Cloud
    ↓
Public URL
```

**Option 2: Docker**
```
Dockerfile
    ↓
Docker Container
    ↓
Cloud Platform (AWS/GCP/Azure)
```

**Option 3: Traditional Server**
```
Application Server
    ↓
Reverse Proxy (nginx)
    ↓
HTTPS
```

---

## Monitoring & Logging

### Current Implementation

**Logging:**
- Error messages to console
- Validation results displayed
- User actions tracked in session

**Future Enhancements:**
- Structured logging
- Performance metrics
- Usage analytics
- Error tracking (Sentry)
- LLM cost tracking

---

## Summary

The architecture is:
- ✅ **Modular** - Clear separation of concerns
- ✅ **Extensible** - Easy to add features
- ✅ **Maintainable** - Well-organized code
- ✅ **Testable** - Unit test coverage
- ✅ **Scalable** - Ready for growth
- ✅ **Secure** - Proper key management
- ✅ **User-Friendly** - Intuitive flow

**Design Principles:**
- Single Responsibility
- Open/Closed
- Dependency Injection
- Separation of Concerns
- DRY (Don't Repeat Yourself)

---

**For more details, see:**
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Technical overview
- [FEATURES.md](FEATURES.md) - Feature documentation
- Source code in `src/` - Implementation details

