#!/usr/bin/env python3
"""
Mirador Integration Test for User Intervention

This script tests the integration between InterventionManager and Mesfamily_memberBus
to verify that user intervention points work correctly with the bidirectional
communication system.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from core.mesfamily_member_bus import Mesfamily_memberBus
from core.intervention_manager import InterventionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(mesfamily_member)s'
)
logger = logging.getLogger("mirador-integration-test")

class InterventionTesterThread(threading.Thread):
    """Thread class to test interventions without blocking the main thread."""
    
    def __init__(self, manager: InterventionManager, mesfamily_member: Dict[str, Any]):
        """
        Initialize the tester thread.
        
        Args:
            manager: The intervention manager to test
            mesfamily_member: The test mesfamily_member to use
        """
        super().__init__()
        self.manager = manager
        self.mesfamily_member = mesfamily_member
        self.result = None
        
    def run(self):
        """Run the test."""
        # Use programmatic intervention handling
        pending = self.manager.get_pending_interventions()
        if pending:
            intervention_id = pending[0]["id"]
            
            # Simulate user approved
            time.sleep(1)  # Delay to simulate user thinking
            self.manager.handle_intervention(intervention_id, "approve")
            
            logger.info(f"Successfully handled intervention {intervention_id}")

def test_intervention_integration():
    """
    Test the integration between InterventionManager and Mesfamily_memberBus
    using programmatic intervention.
    """
    logger.info("Starting intervention integration test")
    
    # Create mesfamily_member bus
    bus = Mesfamily_memberBus(session_id="integration_test")
    
    # Create intervention manager with CLI mode disabled
    manager = InterventionManager(bus, cli_mode=False)
    
    # Create a test mesfamily_member
    test_mesfamily_member = {
        "mesfamily_member_id": "test-id-" + str(int(time.time())),
        "mesfamily_member_type": "query", 
        "source_specialist": "test_specialist",
        "target_specialist": "security_expert",
        "content": {
            "query_type": "clarification",
            "query": "Is this password hashing secure?",
            "context": "Testing intervention integration"
        },
        "metadata": {
            "priority": 1,
            "timestamp": datetime.now().isoformat(),
            "session_id": "integration_test"
        }
    }
    
    # Configure intervention to always require intervention for security_expert
    manager.config = {
        "enabled": True,
        "intervention_types": {
            "query": {
                "enabled": True,
                "priority_threshold": 3,
                "auto_approve_specialists": [],
                "always_intervene_specialists": ["security_expert"]
            }
        }
    }
    
    # Start handler thread
    handler = InterventionTesterThread(manager, test_mesfamily_member)
    handler.start()
    
    # Route the mesfamily_member (this will be intercepted)
    mesfamily_member_id = bus.route_mesfamily_member(test_mesfamily_member)
    
    # Wait for handler to complete
    handler.join(timeout=5)
    
    # Verify mesfamily_member was routed after intervention
    assert mesfamily_member_id is not None, "Mesfamily_member should have been routed after intervention"
    logger.info(f"Mesfamily_member {mesfamily_member_id} was successfully routed after intervention")
    
    # Test intervention rejection
    # Configure a new interceptor that always rejects
    bus.interceptors.clear()
    
    def rejection_interceptor(mesfamily_member: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Test interceptor that always rejects mesfamily_members."""
        if mesfamily_member["target_specialist"] == "security_expert":
            logger.info(f"Rejection interceptor rejecting mesfamily_member to {mesfamily_member['target_specialist']}")
            return None
        return mesfamily_member
    
    # Register the new interceptor
    bus.register_interceptor(rejection_interceptor)
    
    # Try to route another mesfamily_member
    another_mesfamily_member = test_mesfamily_member.copy()
    another_mesfamily_member["mesfamily_member_id"] = "test-id-" + str(int(time.time()))
    
    # This should be rejected
    rejected_id = bus.route_mesfamily_member(another_mesfamily_member)
    
    # Verify mesfamily_member was rejected
    assert rejected_id is None, "Mesfamily_member should have been rejected by interceptor"
    logger.info("Mesfamily_member was successfully rejected by interceptor")
    
    # Test mesfamily_member modification
    bus.interceptors.clear()
    
    def modification_interceptor(mesfamily_member: Dict[str, Any]) -> Dict[str, Any]:
        """Test interceptor that modifies mesfamily_members."""
        if mesfamily_member["mesfamily_member_type"] == "query":
            # Add a flag to the content
            mesfamily_member["content"]["modified_by_interceptor"] = True
            logger.info(f"Modification interceptor modifying mesfamily_member {mesfamily_member['mesfamily_member_id']}")
        return mesfamily_member
    
    # Register the new interceptor
    bus.register_interceptor(modification_interceptor)
    
    # Route another mesfamily_member
    modified_mesfamily_member = test_mesfamily_member.copy()
    modified_mesfamily_member["mesfamily_member_id"] = "test-id-" + str(int(time.time()))
    
    # This should be modified
    modified_id = bus.route_mesfamily_member(modified_mesfamily_member)
    
    # Verify mesfamily_member was modified
    assert modified_id is not None, "Mesfamily_member should have been routed"
    
    # Get the mesfamily_member and check if it was modified
    stored_mesfamily_member = bus.get_mesfamily_member(modified_id)
    assert stored_mesfamily_member is not None, "Mesfamily_member should be stored"
    assert stored_mesfamily_member["content"].get("modified_by_interceptor") is True, "Mesfamily_member should have been modified"
    
    logger.info("Mesfamily_member was successfully modified by interceptor")
    logger.info("All integration tests passed!")

if __name__ == "__main__":
    test_intervention_integration()