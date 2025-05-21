# Mirador User Intervention

This document describes the User Intervention Points feature of the Mirador AI Framework, which allows users to guide and control the bidirectional communication between specialists.

## Overview

The User Intervention Points feature enables human oversight of the bidirectional communication system by intercepting mesfamily_members between specialists and allowing users to approve, modify, or reject them. This creates a true collaborative human-AI system that combines the efficiency of automated specialist communication with human expertise at critical decision points.

## Features

- **Mesfamily_member Interception**: Intercept mesfamily_members between specialists based on configurable rules
- **Rule-Based Filtering**: Configure which mesfamily_members require intervention based on type, priority, and specialists involved
- **Modification Capabilities**: Approve, modify, or reject intercepted mesfamily_members
- **Watch Mode**: Monitor all mesfamily_members without requiring intervention
- **Timeout Handling**: Configure default actions when user intervention times out
- **Learning Model**: The system can learn from past interventions to make better decisions about when to intervene

## Ufamily_member

### Command-Line Interface

The `mirador-intervene` command provides a user-friendly interface for managing interventions:

```bash
# Start intervention mode (connects to most recent session)
./mirador-intervene start

# Start watch mode (just observe mesfamily_members)
./mirador-intervene start --watch

# Connect to a specific session
./mirador-intervene start --session SESSION_ID

# Configure intervention settings
./mirador-intervene config
```

### Intervention Process

When a mesfamily_member requires intervention, you'll see a display like this:

```
============================================================
Query requiring intervention:
From: master_coder
To: security_expert
Type: query

Query Type: clarification
Query:
What's the best password hashing algorithm?

Context:
Building an authentication system
============================================================

Intervention Options:
  (a) Approve - Send mesfamily_member as is
  (m) Modify - Edit mesfamily_member content
  (r) Reject - Prevent mesfamily_member from being sent
  (i) Info - Show more details about the mesfamily_member
  (s) Settings - Adjust intervention settings for this type

Enter choice: 
```

You can then choose to:
- **Approve** the mesfamily_member as is
- **Modify** the mesfamily_member content
- **Reject** the mesfamily_member completely
- **Info** to see more details about the mesfamily_member
- **Settings** to adjust intervention rules for this type of mesfamily_member

### Configuration

You can configure intervention settings using the `mirador-intervene config` command, which provides a menu-based interface to:

- Enable/disable interventions globally
- Toggle watch mode
- Configure default action on timeout
- Set timeout duration
- Configure learning features
- Configure intervention rules for each mesfamily_member type (query, response, notification)
- Set priority thresholds for intervention
- Configure auto-approve and always-intervene specialists

## Architecture

The User Intervention system consists of two main components:

1. **InterventionManager**: Manages the rules, user interfaces, and decision-making for interventions
2. **Mesfamily_memberBus Interceptors**: Allows the InterventionManager to intercept and modify mesfamily_members in the bidirectional communication system

### Intercept Flow

1. A specialist sends a mesfamily_member via the Mesfamily_memberBus
2. The InterventionManager intercepts the mesfamily_member before routing
3. The InterventionManager decides whether intervention is needed based on the configured rules
4. If intervention is needed, the user is prompted for action
5. The mesfamily_member is approved, modified, or rejected based on user input
6. If approved or modified, the mesfamily_member continues to its destination
7. If rejected, the mesfamily_member is discarded

## Configuration File

Intervention settings are stored in `~/ai_framework_git/config/intervention.json` with the following structure:

```json
{
  "enabled": true,
  "intervention_types": {
    "query": {
      "enabled": true,
      "priority_threshold": 3,
      "auto_approve_specialists": [],
      "always_intervene_specialists": ["security_expert"]
    },
    "response": {
      "enabled": true,
      "priority_threshold": 2,
      "auto_approve_specialists": [],
      "always_intervene_specialists": []
    },
    "notification": {
      "enabled": false
    }
  },
  "timeout_seconds": 300,
  "default_action": "approve",
  "watch_mode": false,
  "learning": {
    "enabled": true,
    "min_examples": 5
  }
}
```

## Advanced Ufamily_member

### Programmatic Intervention

For automated or custom intervention interfaces, you can use the programmatic API:

```python
from src.core.mesfamily_member_bus import Mesfamily_memberBus
from src.core.intervention_manager import InterventionManager

# Create mesfamily_member bus and intervention manager
bus = Mesfamily_memberBus(session_id="my_session")
manager = InterventionManager(bus, cli_mode=False)

# Get pending interventions
pending = manager.get_pending_interventions()

# Handle an intervention
if pending:
    # Approve the mesfamily_member
    manager.handle_intervention(pending[0]["id"], "approve")
    
    # Or modify it
    manager.handle_intervention(pending[0]["id"], "modify", modified_mesfamily_member)
    
    # Or reject it
    manager.handle_intervention(pending[0]["id"], "reject")
```

### Customizing the Learning Model

The learning model can be extended by modifying the `_learning_should_intervene` method in the `InterventionManager` class. By default, it tracks intervention history and can be enhanced with more sophisticated ML algorithms.

## Integration with Specialist Handler

To enable user intervention in your specialist workflows, make sure your `SpecialistHandler` is using a `Mesfamily_memberBus` with an associated `InterventionManager`.

Example:

```python
from src.core.mesfamily_member_bus import Mesfamily_memberBus
from src.core.specialist_handler import SpecialistHandler
from src.core.intervention_manager import InterventionManager

# Create components with intervention enabled
bus = Mesfamily_memberBus(session_id="session_123")
intervention = InterventionManager(bus)
handler = SpecialistHandler(mesfamily_member_bus=bus)

# Now use the handler as normal - interventions will be applied automatically
result = handler.run_with_collaboration(
    input_text="My input for the specialist",
    specialist="master_coder",
    specialists_to_collaborate_with=["security_expert", "ux_designer"]
)
```