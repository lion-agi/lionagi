# LionAGI Cookbook

## Chapter 5: Building a Travel Planner

In previous chapters, you built various assistants. Now we'll explore ReAct (Reasoning + Action) by building a travel planner that:
- Plans complex itineraries
- Checks availability
- Optimizes schedules
- Handles constraints

### Prerequisites
- Completed [Chapter 4](ch4_structured_forms.md)
- Understanding of async/await
- Basic Python knowledge

## ReAct Basics

### Simple Planning
```python
from lionagi import Branch, Model, Tool, Form, types
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import Field

# Define tools
def check_flights(
    origin: str,
    destination: str,
    date: str
) -> dict:
    """Check flight availability."""
    # Simulated API call
    return {
        "available": True,
        "flights": [
            {
                "id": "F123",
                "departure": "09:00",
                "arrival": "11:00",
                "price": 299
            },
            {
                "id": "F456",
                "departure": "14:00",
                "arrival": "16:00",
                "price": 349
            }
        ]
    }

def check_hotels(
    city: str,
    check_in: str,
    check_out: str
) -> dict:
    """Check hotel availability."""
    # Simulated API call
    return {
        "available": True,
        "hotels": [
            {
                "id": "H123",
                "name": "City Center Hotel",
                "price": 199,
                "rating": 4.5
            },
            {
                "id": "H456",
                "name": "Beach Resort",
                "price": 299,
                "rating": 4.8
            }
        ]
    }

def check_activities(
    city: str,
    date: str
) -> dict:
    """Check available activities."""
    # Simulated API call
    return {
        "available": True,
        "activities": [
            {
                "id": "A123",
                "name": "City Tour",
                "duration": 3,
                "price": 49
            },
            {
                "id": "A456",
                "name": "Museum Visit",
                "duration": 2,
                "price": 29
            }
        ]
    }

# Create tools
tools = [
    Tool(func=check_flights),
    Tool(func=check_hotels),
    Tool(func=check_activities)
]
```

### ReAct Planning
```python
class TravelPlanner:
    """Travel planner with ReAct."""
    def __init__(
        self,
        name: str = "TravelPlanner",
        model: str = "gpt-4"
    ):
        # Create planner
        self.planner = Branch(
            name=name,
            system="""You are a travel planner.
            Help plan trips efficiently.
            Consider budget and preferences.
            Optimize schedules carefully."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model=model,
            temperature=0.3  # More precise
        )
        self.planner.add_model(self.model)
        
        # Add tools
        for tool in tools:
            self.planner.add_tool(tool)
    
    async def plan_trip(
        self,
        request: dict
    ) -> dict:
        """Plan trip using ReAct."""
        try:
            # Start planning
            plan = await self.planner.ReAct(
                instruct={
                    "task": "Plan optimal trip",
                    "request": request
                },
                tools=True,  # Allow tool usage
                max_steps=10  # Limit steps
            )
            
            return {
                "status": "success",
                "plan": plan
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def optimize_schedule(
        self,
        plan: dict
    ) -> dict:
        """Optimize trip schedule."""
        try:
            # Optimize plan
            optimized = await self.planner.ReAct(
                instruct={
                    "task": "Optimize schedule",
                    "plan": plan
                },
                tools=True,
                max_steps=5
            )
            
            return {
                "status": "success",
                "schedule": optimized
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def plan_vacation():
    """Demo travel planning."""
    # Create planner
    planner = TravelPlanner()
    
    # Plan trip
    request = {
        "origin": "New York",
        "destination": "Paris",
        "dates": {
            "departure": "2024-06-01",
            "return": "2024-06-07"
        },
        "budget": 3000,
        "preferences": {
            "hotel_rating": 4,
            "activities": ["culture", "food"]
        }
    }
    
    # Get plan
    result = await planner.plan_trip(request)
    print("\nInitial Plan:", result)
    
    # Optimize if successful
    if result["status"] == "success":
        optimized = await planner.optimize_schedule(
            result["plan"]
        )
        print("\nOptimized Schedule:", optimized)

# Run planner
asyncio.run(plan_vacation())
```

## Advanced Planning

### Complex Itineraries
```python
class ComplexPlanner:
    """Advanced travel planner."""
    def __init__(
        self,
        name: str = "ComplexPlanner",
        model: str = "gpt-4"
    ):
        # Create planner
        self.planner = Branch(
            name=name,
            system="""You are an advanced travel planner.
            Plan complex multi-city trips.
            Consider all constraints.
            Optimize for experience and budget."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model=model,
            temperature=0.3
        )
        self.planner.add_model(self.model)
        
        # Add tools
        for tool in tools:
            self.planner.add_tool(tool)
    
    async def plan_multi_city(
        self,
        request: dict
    ) -> dict:
        """Plan multi-city trip."""
        try:
            # Initial planning
            initial = await self.planner.ReAct(
                instruct={
                    "task": "Plan multi-city trip",
                    "request": request
                },
                tools=True,
                max_steps=15
            )
            
            # Optimize connections
            optimized = await self.planner.ReAct(
                instruct={
                    "task": "Optimize connections",
                    "plan": initial
                },
                tools=True,
                max_steps=5
            )
            
            # Check feasibility
            feasible = await self.planner.ReAct(
                instruct={
                    "task": "Check feasibility",
                    "plan": optimized
                },
                tools=True,
                max_steps=5
            )
            
            return {
                "status": "success",
                "initial": initial,
                "optimized": optimized,
                "feasible": feasible
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def handle_changes(
        self,
        plan: dict,
        changes: dict
    ) -> dict:
        """Handle itinerary changes."""
        try:
            # Analyze impact
            impact = await self.planner.ReAct(
                instruct={
                    "task": "Analyze changes",
                    "plan": plan,
                    "changes": changes
                },
                tools=True,
                max_steps=5
            )
            
            # Adjust plan
            adjusted = await self.planner.ReAct(
                instruct={
                    "task": "Adjust plan",
                    "plan": plan,
                    "changes": changes,
                    "impact": impact
                },
                tools=True,
                max_steps=10
            )
            
            return {
                "status": "success",
                "impact": impact,
                "adjusted": adjusted
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def plan_europe():
    """Demo complex planning."""
    # Create planner
    planner = ComplexPlanner()
    
    # Plan trip
    request = {
        "cities": [
            "London",
            "Paris",
            "Rome"
        ],
        "dates": {
            "start": "2024-06-01",
            "end": "2024-06-14"
        },
        "budget": 5000,
        "preferences": {
            "pace": "moderate",
            "interests": [
                "history",
                "food",
                "art"
            ],
            "hotel_rating": 4
        }
    }
    
    # Get plan
    result = await planner.plan_multi_city(request)
    print("\nInitial Plan:", result)
    
    # Handle changes
    if result["status"] == "success":
        changes = {
            "skip_city": "Paris",
            "add_city": "Barcelona",
            "extend_stay": {
                "city": "Rome",
                "days": 2
            }
        }
        
        adjusted = await planner.handle_changes(
            result["optimized"],
            changes
        )
        print("\nAdjusted Plan:", adjusted)

# Run planner
asyncio.run(plan_europe())
```

## Real-World Example

### Travel Agency System
```python
from lionagi import Branch, Model, Tool, Form, types
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import Field
import json

class TravelRequest(Form):
    """Travel request form."""
    # Client info
    client_id: str = Field(
        description="Client identifier"
    )
    travelers: int = Field(
        description="Number of travelers",
        ge=1,
        le=10
    )
    
    # Trip details
    cities: List[str] = Field(
        description="Cities to visit",
        min_items=1,
        max_items=5
    )
    dates: Dict[str, str] = Field(
        description="Trip dates"
    )
    
    # Preferences
    budget: float = Field(
        description="Total budget",
        ge=1000
    )
    hotel_rating: int = Field(
        description="Minimum hotel rating",
        ge=1,
        le=5
    )
    interests: List[str] = Field(
        description="Travel interests"
    )
    
    # Constraints
    accessibility: Optional[bool] = Field(
        description="Need accessible options",
        default=False
    )
    dietary: Optional[List[str]] = Field(
        description="Dietary restrictions",
        default_factory=list
    )

class TravelAgency:
    """Complete travel agency system."""
    def __init__(
        self,
        name: str = "TravelAgency",
        save_dir: str = "trips"
    ):
        # Create planner
        self.planner = ComplexPlanner(
            name=name,
            model="gpt-4"
        )
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track trips
        self.trips: dict[str, dict] = {}
        self._load_trips()
    
    def _load_trips(self):
        """Load saved trips."""
        for file in self.save_dir.glob("*.json"):
            with open(file) as f:
                trip = json.load(f)
                self.trips[trip["client_id"]] = trip
    
    async def plan_trip(
        self,
        request: dict
    ) -> dict:
        """Plan client trip."""
        try:
            # Validate request
            req = TravelRequest(**request)
            
            # Plan trip
            plan = await self.planner.plan_multi_city(
                req.model_dump()
            )
            
            if plan["status"] != "success":
                return plan
            
            # Save trip
            trip = {
                "client_id": req.client_id,
                "request": req.model_dump(),
                "plan": plan["optimized"],
                "timestamp": datetime.now().isoformat()
            }
            
            file_path = self.save_dir / f"{req.client_id}.json"
            with open(file_path, "w") as f:
                json.dump(trip, f, indent=2)
            
            # Track trip
            self.trips[req.client_id] = trip
            
            return {
                "status": "success",
                "trip_id": req.client_id,
                "plan": plan["optimized"]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_trip(
        self,
        client_id: str,
        changes: dict
    ) -> dict:
        """Update existing trip."""
        if client_id not in self.trips:
            return {
                "status": "error",
                "error": f"No trip found for: {client_id}"
            }
        
        try:
            # Get current trip
            trip = self.trips[client_id]
            
            # Handle changes
            result = await self.planner.handle_changes(
                trip["plan"],
                changes
            )
            
            if result["status"] != "success":
                return result
            
            # Update trip
            trip["plan"] = result["adjusted"]
            trip["updated"] = datetime.now().isoformat()
            
            # Save changes
            file_path = self.save_dir / f"{client_id}.json"
            with open(file_path, "w") as f:
                json.dump(trip, f, indent=2)
            
            return {
                "status": "success",
                "trip_id": client_id,
                "plan": result["adjusted"]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_trip(
        self,
        client_id: str
    ) -> dict:
        """Get trip details."""
        return self.trips.get(client_id, {
            "error": f"No trip found for: {client_id}"
        })

# Usage
async def run_agency():
    """Demo travel agency."""
    # Create agency
    agency = TravelAgency(
        name="LuxuryTravel",
        save_dir="luxury_trips"
    )
    
    # Plan trip
    request = {
        "client_id": "C123",
        "travelers": 2,
        "cities": ["Paris", "Rome", "Barcelona"],
        "dates": {
            "start": "2024-06-01",
            "end": "2024-06-14"
        },
        "budget": 8000,
        "hotel_rating": 5,
        "interests": ["luxury", "food", "culture"],
        "accessibility": True,
        "dietary": ["vegetarian"]
    }
    
    # Get plan
    result = await agency.plan_trip(request)
    print("\nInitial Plan:", result)
    
    # Update trip
    if result["status"] == "success":
        changes = {
            "extend_stay": {
                "city": "Paris",
                "days": 2
            },
            "upgrade_hotel": {
                "city": "Rome",
                "rating": 5
            }
        }
        
        updated = await agency.update_trip(
            "C123",
            changes
        )
        print("\nUpdated Plan:", updated)
    
    # Get final trip
    trip = agency.get_trip("C123")
    print("\nFinal Trip:", trip)

# Run agency
asyncio.run(run_agency())
```

## Best Practices

1. **ReAct Design**
   - Break down complex tasks
   - Use tools effectively
   - Handle state changes
   - Validate results

2. **Planning Strategy**
   - Consider constraints
   - Optimize schedules
   - Handle changes
   - Validate feasibility

3. **System Design**
   - Validate inputs
   - Store state
   - Handle errors
   - Track changes

## Quick Reference
```python
from lionagi import Branch, Model, Tool

# Create planner
planner = Branch(name="Planner")
model = Model(provider="openai")
planner.add_model(model)

# Add tool
tool = Tool(func=check_availability)
planner.add_tool(tool)

# Use ReAct
result = await planner.ReAct(
    instruct={"task": "Plan trip"},
    tools=True,
    max_steps=5
)
```

## Next Steps

You've learned:
- How to use ReAct
- How to plan complex tasks
- How to handle changes
- How to build real systems

In [Chapter 6](ch6_multi_branch.md), we'll explore multi-branch operations for coordinating multiple AI agents.
