# Bidirectional Communication System Design

This document outlines the design for implementing bidirectional communication between specialists in the Mirador AI Framework.

## 1. Overview

### Current Limitations
The current implementation uses a sequential, unidirectional flow where:
- Each specialist receives input only from the previous specialist
- No mechanism exists for specialists to request clarification
- Information is lost if not explicitly carried forward
- Specialists cannot collaborate on specific sub-problems

### Vision
Transform Mirador from a pipeline to a collaborative multi-agent system where:
- Specialists can query each other for specific information
- Information flows can be bidirectional when needed
- The system becomes more than the sum of its parts through emergent collaboration
- Complex problems can be decomposed and solved collaboratively

## 2. Architecture

### Core Components

#### 2.1 Mesfamily_member Bus
A central component that manages communication between specialists:
- Routes queries and responses between specialists
- Maintains a history of interactions
- Prevents infinite loops and deadlocks
- Provides observability for debugging

#### 2.2 Specialist Interface
Extended specialist interface that supports:
- Ability to generate queries to other specialists
- Ability to receive and respond to queries
- Context awareness of available specialists
- Standardized query/response format

#### 2.3 Chain Coordinator
Enhanced chain execution system that:
- Orchestrates the overall flow while allowing side communications
- Manages specialist state throughout execution
- Provides hooks for user intervention
- Tracks execution graph instead of just a linear sequence

#### 2.4 Query Protocol
A standardized format for inter-specialist communication:
- Query type (clarification, elaboration, collaboration)
- Target specialist(s)
- Context and specific question
- Expected response format
- Priority and timeout parameters

## 3. Implementation Strategy

### Phase 1: Foundation (Weeks 1-2)

1. **Core Mesfamily_member Protocol**
   - Design the JSON schema for specialist mesfamily_members
   - Implement basic mesfamily_member routing functionality
   - Create serialization/deserialization utilities

2. **Specialist Query Generation**
   - Enhance specialist prompts to support query generation
   - Implement parsing logic to extract queries from specialist responses
   - Create a simple query validation system

3. **Basic Mesfamily_member Bus**
   - Implement initial mesfamily_member routing system
   - Add simple state tracking for mesfamily_members
   - Create basic observability for debugging

### Phase 2: Core Functionality (Weeks 3-4)

1. **Enhanced Chain Execution**
   - Refactor chain execution to support non-linear flows
   - Add support for side-channel communications
   - Implement state management for specialists

2. **Query Handling Logic**
   - Create specialist query handlers
   - Implement response generation and routing
   - Add logic to prevent circular dependencies

3. **Visualization Extensions**
   - Extend the progress visualization to show communication flows
   - Add query/response visualizations to summaries
   - Create debugging tools for mesfamily_member flows

### Phase 3: User Integration & Refinement (Weeks 5-6)

1. **User Intervention Points**
   - Add user decision points at key communication junctures
   - Implement configuration options for automatic vs. manual routing
   - Create intuitive UI for query/response monitoring and intervention

2. **Advanced Routing & Optimization**
   - Implement priority-based mesfamily_member routing
   - Add caching for repeated queries
   - Create specialized routing patterns for common workflows

3. **Testing & Tuning**
   - Create comprehensive test suite for bidirectional flows
   - Benchmark performance impacts and optimize
   - Refine specialist prompts for effective communication

## 4. Technical Design

### Mesfamily_member Format
```json
{
  "mesfamily_member_id": "uuid-string",
  "mesfamily_member_type": "query|response|notification",
  "source_specialist": "specialist_name",
  "target_specialist": "specialist_name",
  "content": {
    "query_type": "clarification|elaboration|collaboration",
    "query": "Specific question text",
    "context": "Relevant context for the query"
  },
  "metadata": {
    "timestamp": "ISO timestamp",
    "priority": 1-5,
    "timeout_ms": 30000,
    "parent_mesfamily_member_id": "uuid-string-of-parent-mesfamily_member"
  }
}
```

### Execution Flow
1. Chain is initialized with specialists
2. First specialist processes initial prompt
3. During processing, any specialist can:
   - Generate a response to pass forward (standard flow)
   - Generate queries to other specialists (new capability)
   - Receive and process queries from other specialists (new capability)
4. Chain coordinator manages the flow, ensuring forward progress
5. Final output is generated when all necessary processing is complete

### Storage & State Management
- In-memory mesfamily_member store during execution
- Persistent storage of interaction graphs for review and reuse
- Atomic specialist state snapshots for reliability
- Query/response cache for efficiency

## 5. Implementation Details

### Bash Implementation
```bash
# Mesfamily_member routing function
route_mesfamily_member() {
  local source=$1
  local target=$2
  local mesfamily_member_type=$3
  local content=$4
  
  # Create mesfamily_member JSON
  mesfamily_member=$(jq -n \
    --arg id "$(uuidgen)" \
    --arg type "$mesfamily_member_type" \
    --arg source "$source" \
    --arg target "$target" \
    --argjson content "$content" \
    '{mesfamily_member_id: $id, mesfamily_member_type: $type, source_specialist: $source, target_specialist: $target, content: $content, metadata: {timestamp: now|tostring}}')
  
  # Store in mesfamily_member history
  echo "$mesfamily_member" >> "$SESSION_DIR/mesfamily_members.jsonl"
  
  # Queue for processing
  echo "$mesfamily_member" > "$SESSION_DIR/queue/${target}_${mesfamily_member_id}.json"
}

# Specialist query function
specialist_query() {
  local specialist=$1
  local query_prompt=$2
  
  # Add query capability to prompt
  prompt="${query_prompt}

If you need information from another specialist, you can ask by formatting your response like this:
<query specialist=\"specialist_name\">
Your specific question here
</query>

Continue with your normal response after any queries."

  # Process with model
  response=$(query_model "$specialist" "$prompt")
  
  # Extract and process any queries
  extract_and_process_queries "$specialist" "$response"
  
  # Return the cleaned response
  clean_response "$response"
}
```

### Python Implementation
```python
class Mesfamily_memberBus:
    def __init__(self):
        self.mesfamily_members = []
        self.mesfamily_member_graph = {}
        self.query_cache = {}
        
    def route_mesfamily_member(self, mesfamily_member):
        """Route a mesfamily_member between specialists"""
        self.mesfamily_members.append(mesfamily_member)
        
        # Update mesfamily_member graph
        source = mesfamily_member["source_specialist"]
        target = mesfamily_member["target_specialist"]
        if source not in self.mesfamily_member_graph:
            self.mesfamily_member_graph[source] = {}
        if target not in self.mesfamily_member_graph[source]:
            self.mesfamily_member_graph[source][target] = []
        self.mesfamily_member_graph[source][target].append(mesfamily_member["mesfamily_member_id"])
        
        # Handle mesfamily_member based on type
        if mesfamily_member["mesfamily_member_type"] == "query":
            return self._handle_query(mesfamily_member)
        elif mesfamily_member["mesfamily_member_type"] == "response":
            return self._handle_response(mesfamily_member)
        
    def _handle_query(self, mesfamily_member):
        """Process a query mesfamily_member"""
        # Check cache
        cache_key = f"{mesfamily_member['source_specialist']}:{mesfamily_member['content']['query']}"
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
            
        # Route to target specialist
        target_specialist = mesfamily_member["target_specialist"]
        # Processing logic here
        
    def _handle_response(self, mesfamily_member):
        """Process a response mesfamily_member"""
        # Update cache
        query_id = mesfamily_member["metadata"]["parent_mesfamily_member_id"]
        query_mesfamily_member = self._get_mesfamily_member(query_id)
        cache_key = f"{query_mesfamily_member['source_specialist']}:{query_mesfamily_member['content']['query']}"
        self.query_cache[cache_key] = mesfamily_member
        
        # Notify waiting specialist
```

## 6. Integration Points

### Chain Execution Integration
- Modify chain runners to initialize mesfamily_member bus
- Update specialist execution to support query generation
- Add hooks for mesfamily_member routing and coordination
- Extend visualization to show communication flows

### User Interface Integration
- Add configuration options for bidirectional communication
- Create visualization for query/response flows
- Add user intervention points at communication junctions
- Extend summary output to include communication graphs

### API Integration
- Extend API to expose communication capabilities
- Add endpoints for monitoring and controlling mesfamily_member flow
- Provide webhooks for external integration
- Create documentation for API ufamily_member

## 7. Testing Strategy

### Unit Tests
- Mesfamily_member format validation
- Routing logic correctness
- Query extraction accuracy
- Loop prevention mechanisms

### Integration Tests
- End-to-end specialist communication
- Chain execution with side communications
- Performance under different communication patterns
- Error handling and recovery

### Acceptance Tests
- Solve problems requiring collaboration
- Measure improvement over sequential chains
- Verify user intervention capabilities
- Validate visualization accuracy

## 8. Success Metrics

The bidirectional communication system will be considered successful if it:

1. Enables specialists to resolve ambiguities that would otherwise persist
2. Shows measurable improvement in output quality for complex tasks
3. Maintains reasonable performance despite increased complexity
4. Creates opportunities for emergent collaborative behaviors
5. Provides clear visibility into the communication process
6. Supports meaningful user intervention at key points

## 9. Future Extensions

Once the core bidirectional communication system is implemented, it can be extended with:

1. **Specialized Collaborative Patterns**
   - Consensus building across multiple specialists
   - Divide-and-conquer for complex problems
   - Iterative refinement cycles

2. **Learning & Adaptation**
   - Record successful communication patterns
   - Optimize routing based on historical effectiveness
   - Suggest specialist combinations based on problem type

3. **External Integrations**
   - Allow external tools/APIs as communication participants
   - Enable cross-session specialist collaboration
   - Support human-in-the-loop expert collaboration