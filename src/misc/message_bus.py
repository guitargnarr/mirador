#!/usr/bin/env python3
"""
Mirador Mesfamily_member Bus

This module implements the core messaging infrastructure for bidirectional
communication between specialists in the Mirador AI Framework.
"""

import os
import json
import uuid
import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from datetime import datetime
from collections import defaultdict
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(mesfamily_member)s'
)
logger = logging.getLogger("mirador-mesfamily_member-bus")

class Mesfamily_memberBus:
    """
    Central component that manages communication between specialists.
    
    The Mesfamily_memberBus handles routing, tracking, and coordination of mesfamily_members
    between specialists in the Mirador framework, enabling bidirectional
    communication.
    """
    
    def __init__(self, session_id: str = None, session_dir: str = None):
        """
        Initialize the mesfamily_member bus.
        
        Args:
            session_id: Unique identifier for this session. If None, one will be generated.
            session_dir: Directory to store session data. If None, uses default location.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.session_dir = session_dir or os.path.join(
            os.path.expanduser("~/ai_framework_git/outputs/sessions"), 
            f"session_{self.session_id}"
        )
        
        # Create session directory structure
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(os.path.join(self.session_dir, "mesfamily_members"), exist_ok=True)
        os.makedirs(os.path.join(self.session_dir, "queue"), exist_ok=True)
        
        # Initialize state
        self.mesfamily_members: List[Dict[str, Any]] = []
        self.mesfamily_member_graph: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        self.query_cache: Dict[str, Dict[str, Any]] = {}
        
        # Circular dependency detection
        self.active_queries: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)
        
        # Mesfamily_member interceptors for user intervention
        self.interceptors: List[Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]] = []
        
        # Threading lock for thread safety
        self.lock = threading.Lock()
        
        logger.info(f"Mesfamily_memberBus initialized with session ID: {self.session_id}")
        logger.info(f"Session directory: {self.session_dir}")
    
    def register_interceptor(
        self, 
        interceptor: Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]
    ) -> None:
        """
        Register a mesfamily_member interceptor function.
        
        Args:
            interceptor: Function that takes a mesfamily_member and returns a modified mesfamily_member
                         or None to reject the mesfamily_member
        """
        self.interceptors.append(interceptor)
        logger.info(f"Registered mesfamily_member interceptor: {interceptor.__qualname__}")
    
    def create_mesfamily_member(
        self, 
        mesfamily_member_type: str,
        source_specialist: str,
        target_specialist: str,
        content: Dict[str, Any],
        priority: int = 3,
        timeout_ms: int = 30000,
        parent_mesfamily_member_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a properly formatted mesfamily_member.
        
        Args:
            mesfamily_member_type: Type of mesfamily_member (query, response, notification)
            source_specialist: Specialist sending the mesfamily_member
            target_specialist: Specialist receiving the mesfamily_member
            content: Mesfamily_member content with query type, text, and context
            priority: Mesfamily_member priority (1-5, with 1 being highest)
            timeout_ms: Timeout in milliseconds
            parent_mesfamily_member_id: ID of the parent mesfamily_member, if this is a response
            
        Returns:
            Complete mesfamily_member dictionary
        """
        mesfamily_member_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        mesfamily_member = {
            "mesfamily_member_id": mesfamily_member_id,
            "mesfamily_member_type": mesfamily_member_type,
            "source_specialist": source_specialist,
            "target_specialist": target_specialist,
            "content": content,
            "metadata": {
                "timestamp": timestamp,
                "priority": priority,
                "timeout_ms": timeout_ms,
                "session_id": self.session_id
            }
        }
        
        if parent_mesfamily_member_id:
            mesfamily_member["metadata"]["parent_mesfamily_member_id"] = parent_mesfamily_member_id
            
        return mesfamily_member
    
    def route_mesfamily_member(self, mesfamily_member: Dict[str, Any]) -> Optional[str]:
        """
        Route a mesfamily_member between specialists.
        
        Args:
            mesfamily_member: Complete mesfamily_member dictionary to route
            
        Returns:
            Mesfamily_member ID of the routed mesfamily_member, or None if mesfamily_member was rejected by an interceptor
        """
        with self.lock:
            # Process through interceptors first
            modified_mesfamily_member = mesfamily_member
            for interceptor in self.interceptors:
                try:
                    result = interceptor(modified_mesfamily_member)
                    if result is None:
                        # Mesfamily_member rejected by interceptor
                        logger.info(f"Mesfamily_member {modified_mesfamily_member['mesfamily_member_id']} rejected by interceptor {interceptor.__qualname__}")
                        return None
                    modified_mesfamily_member = result
                except Exception as e:
                    logger.error(f"Error in interceptor {interceptor.__qualname__}: {e}")
                    # Continue processing with unmodified mesfamily_member in case of interceptor error
            
            # Proceed with the potentially modified mesfamily_member
            mesfamily_member = modified_mesfamily_member
            
            # Store mesfamily_member in memory
            self.mesfamily_members.append(mesfamily_member)
            
            # Update mesfamily_member graph
            source = mesfamily_member["source_specialist"]
            target = mesfamily_member["target_specialist"]
            mesfamily_member_id = mesfamily_member["mesfamily_member_id"]
            self.mesfamily_member_graph[source][target].append(mesfamily_member_id)
            
            # Store mesfamily_member on disk
            mesfamily_member_path = os.path.join(
                self.session_dir, 
                "mesfamily_members", 
                f"{mesfamily_member_id}.json"
            )
            with open(mesfamily_member_path, "w") as f:
                json.dump(mesfamily_member, f, indent=2)
            
            # Queue mesfamily_member for processing
            queue_path = os.path.join(
                self.session_dir,
                "queue",
                f"{target}_{mesfamily_member_id}.json"
            )
            with open(queue_path, "w") as f:
                json.dump(mesfamily_member, f, indent=2)
            
            # Add to active queries if this is a query
            if mesfamily_member["mesfamily_member_type"] == "query":
                query_pair = (source, target)
                query_text = mesfamily_member["content"].get("query", "")
                query_key = f"{source}:{target}:{query_text}"
                self.active_queries[query_key].add(query_pair)
                
                # Check for circular dependencies
                if self._check_circular_dependency(source, target):
                    logger.warning(f"Circular dependency detected: {source} → {target}")
                    # Create a notification about the circular dependency
                    self._create_circular_dependency_notification(mesfamily_member)
            
            logger.info(f"Routed mesfamily_member: {mesfamily_member_id} from {source} to {target}")
            return mesfamily_member_id
    
    def get_pending_mesfamily_members(self, specialist: str) -> List[Dict[str, Any]]:
        """
        Get all pending mesfamily_members for a specialist.
        
        Args:
            specialist: Name of the specialist to get mesfamily_members for
            
        Returns:
            List of pending mesfamily_members
        """
        with self.lock:
            # Read from queue directory
            queue_dir = os.path.join(self.session_dir, "queue")
            specialist_mesfamily_members = []
            
            for filename in os.listdir(queue_dir):
                if filename.startswith(f"{specialist}_"):
                    mesfamily_member_path = os.path.join(queue_dir, filename)
                    try:
                        with open(mesfamily_member_path, "r") as f:
                            mesfamily_member = json.load(f)
                            specialist_mesfamily_members.append(mesfamily_member)
                    except Exception as e:
                        logger.error(f"Error reading mesfamily_member {filename}: {e}")
            
            # Sort by priority
            specialist_mesfamily_members.sort(key=lambda m: m["metadata"].get("priority", 3))
            
            return specialist_mesfamily_members
    
    def mark_mesfamily_member_processed(self, mesfamily_member_id: str) -> None:
        """
        Mark a mesfamily_member as processed and remove it from the queue.
        
        Args:
            mesfamily_member_id: ID of the mesfamily_member to mark as processed
        """
        with self.lock:
            # Find the mesfamily_member
            mesfamily_member = None
            for m in self.mesfamily_members:
                if m["mesfamily_member_id"] == mesfamily_member_id:
                    mesfamily_member = m
                    break
            
            if not mesfamily_member:
                logger.warning(f"Mesfamily_member {mesfamily_member_id} not found")
                return
            
            # Remove from queue
            target = mesfamily_member["target_specialist"]
            queue_path = os.path.join(
                self.session_dir,
                "queue",
                f"{target}_{mesfamily_member_id}.json"
            )
            
            if os.path.exists(queue_path):
                os.remove(queue_path)
                logger.info(f"Removed {mesfamily_member_id} from queue")
            
            # Update metadata to mark as processed
            mesfamily_member["metadata"]["processed"] = True
            mesfamily_member["metadata"]["processed_timestamp"] = datetime.now().isoformat()
            
            # Update mesfamily_member on disk
            mesfamily_member_path = os.path.join(
                self.session_dir, 
                "mesfamily_members", 
                f"{mesfamily_member_id}.json"
            )
            with open(mesfamily_member_path, "w") as f:
                json.dump(mesfamily_member, f, indent=2)
    
    def send_query(
        self,
        source_specialist: str,
        target_specialist: str,
        query: str,
        query_type: str = "clarification",
        context: Optional[str] = None,
        priority: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Send a query from one specialist to another.
        
        Args:
            source_specialist: Specialist sending the query
            target_specialist: Specialist receiving the query
            query: The actual question or request
            query_type: Type of query (clarification, elaboration, collaboration)
            context: Additional context for the query
            priority: Query priority (1-5, with 1 being highest)
            
        Returns:
            The created and routed mesfamily_member, or None if mesfamily_member was rejected by an interceptor
        """
        # Create content
        content = {
            "query_type": query_type,
            "query": query
        }
        
        if context:
            content["context"] = context
        
        # Create and route mesfamily_member
        mesfamily_member = self.create_mesfamily_member(
            mesfamily_member_type="query",
            source_specialist=source_specialist,
            target_specialist=target_specialist,
            content=content,
            priority=priority
        )
        
        mesfamily_member_id = self.route_mesfamily_member(mesfamily_member)
        if mesfamily_member_id is None:
            # Mesfamily_member was rejected by an interceptor
            return None
            
        return mesfamily_member
    
    def send_response(
        self,
        source_specialist: str,
        target_specialist: str,
        query_mesfamily_member_id: str,
        response: str,
        priority: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Send a response to a query.
        
        Args:
            source_specialist: Specialist sending the response
            target_specialist: Specialist receiving the response
            query_mesfamily_member_id: ID of the query being responded to
            response: The actual response text
            priority: Response priority (1-5, with 1 being highest)
            
        Returns:
            The created and routed mesfamily_member, or None if mesfamily_member was rejected by an interceptor
        """
        # Create content
        content = {
            "response": response
        }
        
        # Create and route mesfamily_member
        mesfamily_member = self.create_mesfamily_member(
            mesfamily_member_type="response",
            source_specialist=source_specialist,
            target_specialist=target_specialist,
            content=content,
            priority=priority,
            parent_mesfamily_member_id=query_mesfamily_member_id
        )
        
        mesfamily_member_id = self.route_mesfamily_member(mesfamily_member)
        if mesfamily_member_id is None:
            # Mesfamily_member was rejected by an interceptor
            return None
        
        # Update query cache
        query_mesfamily_member = self.get_mesfamily_member(query_mesfamily_member_id)
        if query_mesfamily_member:
            query_text = query_mesfamily_member["content"].get("query", "")
            cache_key = f"{query_mesfamily_member['source_specialist']}:{query_text}"
            self.query_cache[cache_key] = mesfamily_member
            
            # Remove from active queries
            query_key = f"{target_specialist}:{source_specialist}:{query_text}"
            if query_key in self.active_queries:
                query_pair = (target_specialist, source_specialist)
                self.active_queries[query_key].discard(query_pair)
        
        return mesfamily_member
    
    def extract_queries_from_text(self, specialist: str, text: str) -> List[Dict[str, Any]]:
        """
        Extract queries from specialist output text.
        
        Args:
            specialist: The specialist who generated the text
            text: Text to extract queries from
            
        Returns:
            List of extracted query dictionaries
        """
        queries = []
        
        # Look for query tags in the format:
        # <query specialist="name">query text</query>
        import re
        query_pattern = r'<query\s+specialist=["\']([^"\']+)["\']>(.*?)</query>'
        matches = re.finditer(query_pattern, text, re.DOTALL)
        
        for match in matches:
            target = match.group(1).strip()
            query_text = match.group(2).strip()
            
            # Create a query mesfamily_member
            query = {
                "target_specialist": target,
                "query": query_text,
                "source_specialist": specialist
            }
            queries.append(query)
        
        return queries
    
    def process_specialist_output(
        self, 
        specialist: str, 
        output: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process specialist output, extracting and routing any queries.
        
        Args:
            specialist: The specialist who generated the output
            output: The raw output text
            
        Returns:
            Tuple of (cleaned output, list of routed queries)
        """
        # Extract queries
        extracted_queries = self.extract_queries_from_text(specialist, output)
        
        # Route each query
        routed_queries = []
        for query in extracted_queries:
            mesfamily_member = self.send_query(
                source_specialist=specialist,
                target_specialist=query["target_specialist"],
                query=query["query"]
            )
            if mesfamily_member is not None:  # Only add if not rejected by an interceptor
                routed_queries.append(mesfamily_member)
        
        # Clean output by removing query tags
        cleaned_output = output
        if extracted_queries:
            import re
            query_pattern = r'<query\s+specialist=["\']([^"\']+)["\']>(.*?)</query>'
            cleaned_output = re.sub(query_pattern, '', cleaned_output, flags=re.DOTALL)
            # Clean up any double newlines
            cleaned_output = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_output)
        
        return cleaned_output, routed_queries
    
    def get_mesfamily_member(self, mesfamily_member_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a mesfamily_member by ID.
        
        Args:
            mesfamily_member_id: ID of the mesfamily_member to retrieve
            
        Returns:
            The mesfamily_member dictionary, or None if not found
        """
        # Check in-memory cache first
        for mesfamily_member in self.mesfamily_members:
            if mesfamily_member["mesfamily_member_id"] == mesfamily_member_id:
                return mesfamily_member
        
        # If not in memory, try to load from disk
        mesfamily_member_path = os.path.join(
            self.session_dir, 
            "mesfamily_members", 
            f"{mesfamily_member_id}.json"
        )
        
        if os.path.exists(mesfamily_member_path):
            try:
                with open(mesfamily_member_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading mesfamily_member {mesfamily_member_id}: {e}")
                
        return None
    
    def get_session_graph(self) -> Dict[str, Any]:
        """
        Get a complete graph of the session's mesfamily_member flow.
        
        Returns:
            Dictionary with session graph data
        """
        nodes = set()
        edges = []
        
        # Add all specialists as nodes
        for source in self.mesfamily_member_graph:
            nodes.add(source)
            for target in self.mesfamily_member_graph[source]:
                nodes.add(target)
                # Add edges for all mesfamily_members
                for mesfamily_member_id in self.mesfamily_member_graph[source][target]:
                    mesfamily_member = self.get_mesfamily_member(mesfamily_member_id)
                    if mesfamily_member:
                        edges.append({
                            "source": source,
                            "target": target,
                            "mesfamily_member_id": mesfamily_member_id,
                            "mesfamily_member_type": mesfamily_member["mesfamily_member_type"],
                            "timestamp": mesfamily_member["metadata"]["timestamp"]
                        })
        
        # Create graph
        graph = {
            "session_id": self.session_id,
            "nodes": list(nodes),
            "edges": edges,
            "timestamp": datetime.now().isoformat()
        }
        
        return graph
    
    def save_session_graph(self) -> str:
        """
        Save the session graph to disk.
        
        Returns:
            Path to the saved graph file
        """
        graph = self.get_session_graph()
        graph_path = os.path.join(self.session_dir, "session_graph.json")
        
        with open(graph_path, "w") as f:
            json.dump(graph, f, indent=2)
            
        logger.info(f"Saved session graph to {graph_path}")
        return graph_path
    
    def _check_circular_dependency(self, source: str, target: str) -> bool:
        """
        Check if adding a query from source to target would create a circular dependency.
        
        Args:
            source: Source specialist
            target: Target specialist
            
        Returns:
            True if circular dependency would be created, False otherwise
        """
        # Simple check for direct circular dependency
        if target in self.mesfamily_member_graph and source in self.mesfamily_member_graph[target]:
            active_targets = set()
            for key, pairs in self.active_queries.items():
                for s, t in pairs:
                    if s == target:
                        active_targets.add(t)
            
            if source in active_targets:
                return True
        
        # TODO: Implement deeper circular dependency checking
        return False
    
    def _create_circular_dependency_notification(self, mesfamily_member: Dict[str, Any]) -> None:
        """
        Create a notification for a circular dependency.
        
        Args:
            mesfamily_member: The mesfamily_member that would create a circular dependency
        """
        source = mesfamily_member["source_specialist"]
        target = mesfamily_member["target_specialist"]
        
        # Create notification mesfamily_member
        notification = self.create_mesfamily_member(
            mesfamily_member_type="notification",
            source_specialist="mesfamily_member_bus",
            target_specialist=source,
            content={
                "notification_type": "circular_dependency",
                "mesfamily_member": f"Circular dependency detected between {source} and {target}",
                "original_query": mesfamily_member["content"].get("query", ""),
                "recommendation": "Try reformulating your query or requesting information from a different specialist"
            },
            priority=1
        )
        
        self.route_mesfamily_member(notification)


# Unit tests
if __name__ == "__main__":
    import shutil
    import tempfile
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    
    try:
        # Initialize mesfamily_member bus
        bus = Mesfamily_memberBus(session_id="test_session", session_dir=test_dir)
        
        # Test query and response flow
        query = bus.send_query(
            source_specialist="code_reviewer_fix",
            target_specialist="master_coder",
            query="What's the best way to implement authentication in Python?",
            query_type="collaboration"
        )
        
        # Check that the query was created
        assert query is not None
        assert query["mesfamily_member_type"] == "query"
        assert query["source_specialist"] == "code_reviewer_fix"
        assert query["target_specialist"] == "master_coder"
        
        # Get pending mesfamily_members
        pending = bus.get_pending_mesfamily_members("master_coder")
        assert len(pending) == 1
        assert pending[0]["mesfamily_member_id"] == query["mesfamily_member_id"]
        
        # Send response
        response = bus.send_response(
            source_specialist="master_coder",
            target_specialist="code_reviewer_fix",
            query_mesfamily_member_id=query["mesfamily_member_id"],
            response="I recommend using JWT tokens with proper expiration and refresh mechanism."
        )
        
        # Check that the response was created
        assert response is not None
        assert response["mesfamily_member_type"] == "response"
        assert response["source_specialist"] == "master_coder"
        assert response["target_specialist"] == "code_reviewer_fix"
        
        # Test interceptors
        class TestInterceptorState:
            def __init__(self):
                self.intercepted = False
                
        interceptor_state = TestInterceptorState()
        
        def test_interceptor(mesfamily_member):
            # For testing purposes, we'll reject any mesfamily_member to the security_expert
            if mesfamily_member["target_specialist"] == "security_expert":
                interceptor_state.intercepted = True
                return None  # Reject mesfamily_member
            return mesfamily_member  # Allow mesfamily_member to proceed
        
        # Register interceptor
        bus.register_interceptor(test_interceptor)
        
        # Test query extraction
        text = """Here's my initial review of the code:

The authentication function seems weak. 

<query specialist="security_expert">
What are the best practices for secure password storage?
</query>

I think we should also consider rate limiting.

<query specialist="master_coder">
Can you provide an example of rate limiting in Python?
</query>

Overall, the code needs significant security improvements."""

        cleaned, queries = bus.process_specialist_output("code_reviewer_fix", text)
        
        # Check that the queries were extracted and intercepted correctly
        assert len(queries) == 1  # Only one query should have passed through
        assert queries[0]["target_specialist"] == "master_coder"
        assert interceptor_state.intercepted == True  # Security query should have been intercepted
        
        # Check that the cleaned output doesn't contain query tags
        assert "<query" not in cleaned
        assert "</query>" not in cleaned
        
        # Test interceptor that modifies mesfamily_members
        bus.interceptors.clear()  # Clear existing interceptors
        
        def modifying_interceptor(mesfamily_member):
            if mesfamily_member["mesfamily_member_type"] == "query":
                # Add a flag to the content
                mesfamily_member["content"]["intercepted"] = True
            return mesfamily_member
        
        bus.register_interceptor(modifying_interceptor)
        
        modified_query = bus.send_query(
            source_specialist="security_expert",
            target_specialist="master_coder",
            query="Is this code secure?"
        )
        
        # Check that the interceptor modified the mesfamily_member
        assert modified_query is not None
        assert modified_query["content"].get("intercepted") == True
        
        # Mark mesfamily_members as processed
        bus.mark_mesfamily_member_processed(query["mesfamily_member_id"])
        
        # Save session graph
        graph_path = bus.save_session_graph()
        assert os.path.exists(graph_path)
        
        print("All tests passed!")
        
    finally:
        # Clean up
        shutil.rmtree(test_dir)