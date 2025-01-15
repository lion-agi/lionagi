# LionAGI Cookbook

## Chapter 6: Building a Development Team

In previous chapters, you built various assistants. Now we'll explore multi-branch operations by building a software development team that:
- Coordinates development tasks
- Reviews code changes
- Manages documentation
- Handles team communication

### Prerequisites
- Completed [Chapter 5](ch5_react.md)
- Understanding of software development
- Basic Python knowledge

## Multi-Branch Basics

### Team Setup
```python
from lionagi import Branch, Model, Session, types
from datetime import datetime
from pathlib import Path
import json

class DevTeam:
    """Development team with specialized roles."""
    def __init__(
        self,
        project_name: str,
        save_dir: str = "team_logs"
    ):
        # Create session
        self.session = Session()
        
        # Create team members
        self.architect = self.session.new_branch(
            name="Architect",
            system="""You are a software architect.
            Design system architecture.
            Review technical decisions.
            Ensure code quality."""
        )
        
        self.developer = self.session.new_branch(
            name="Developer",
            system="""You are a senior developer.
            Write clean, efficient code.
            Follow best practices.
            Handle implementation details."""
        )
        
        self.reviewer = self.session.new_branch(
            name="Reviewer",
            system="""You are a code reviewer.
            Check code quality.
            Find potential issues.
            Suggest improvements."""
        )
        
        # Configure models
        model = Model(
            provider="openai",
            model="gpt-4",
            temperature=0.3
        )
        
        for branch in self.session.branches:
            branch.add_model(model)
        
        # Setup logging
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Project info
        self.project = {
            "name": project_name,
            "tasks": {},
            "reviews": {},
            "decisions": {}
        }
    
    async def design_feature(
        self,
        feature: dict
    ) -> dict:
        """Design new feature."""
        try:
            # Get architecture design
            design = await self.architect.chat(
                f"""Design feature: {feature['name']}
                Requirements: {feature['requirements']}
                Constraints: {feature['constraints']}"""
            )
            
            # Get implementation plan
            plan = await self.developer.chat(
                f"""Review design: {design}
                Provide implementation plan."""
            )
            
            # Get review criteria
            criteria = await self.reviewer.chat(
                f"""Review design: {design}
                Plan: {plan}
                Define review criteria."""
            )
            
            # Save task
            task = {
                "feature": feature,
                "design": design,
                "plan": plan,
                "criteria": criteria,
                "status": "designed",
                "timestamp": datetime.now().isoformat()
            }
            
            task_id = f"task_{len(self.project['tasks'])}"
            self.project["tasks"][task_id] = task
            
            return {
                "status": "success",
                "task_id": task_id,
                "task": task
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def implement_task(
        self,
        task_id: str,
        code: str
    ) -> dict:
        """Implement task with code."""
        if task_id not in self.project["tasks"]:
            return {
                "status": "error",
                "error": f"Unknown task: {task_id}"
            }
        
        try:
            task = self.project["tasks"][task_id]
            
            # Review implementation
            review = await self.reviewer.chat(
                f"""Review code: {code}
                Design: {task['design']}
                Criteria: {task['criteria']}"""
            )
            
            # Get architect feedback
            feedback = await self.architect.chat(
                f"""Review implementation: {code}
                Design: {task['design']}
                Review: {review}"""
            )
            
            # Update task
            task["code"] = code
            task["review"] = review
            task["feedback"] = feedback
            task["status"] = "implemented"
            task["updated"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "task_id": task_id,
                "review": review,
                "feedback": feedback
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def develop_feature():
    """Demo team development."""
    # Create team
    team = DevTeam(
        project_name="AI Assistant",
        save_dir="assistant_dev"
    )
    
    # Design feature
    feature = {
        "name": "Smart Search",
        "requirements": [
            "Search multiple sources",
            "Rank results by relevance",
            "Cache common queries"
        ],
        "constraints": [
            "Response time < 1s",
            "Memory usage < 100MB"
        ]
    }
    
    # Get design
    result = await team.design_feature(feature)
    print("\nDesign:", result)
    
    # Implement if successful
    if result["status"] == "success":
        code = """
        class SmartSearch:
            def __init__(self):
                self.cache = {}
            
            async def search(
                self,
                query: str
            ) -> list[dict]:
                if query in self.cache:
                    return self.cache[query]
                
                results = []
                for source in self.sources:
                    data = await source.search(query)
                    results.extend(data)
                
                ranked = self.rank_results(results)
                self.cache[query] = ranked
                return ranked
        """
        
        review = await team.implement_task(
            result["task_id"],
            code
        )
        print("\nReview:", review)

# Run development
asyncio.run(develop_feature())
```

## Advanced Collaboration

### Team Communication
```python
from enum import Enum
from typing import List, Dict, Any

class MessageType(Enum):
    QUESTION = "question"
    FEEDBACK = "feedback"
    DECISION = "decision"
    UPDATE = "update"

class DevTeamPlus:
    """Advanced development team."""
    def __init__(
        self,
        project_name: str,
        save_dir: str = "team_logs"
    ):
        # Create base team
        self.team = DevTeam(
            project_name=project_name,
            save_dir=save_dir
        )
        
        # Add tech lead
        self.tech_lead = self.team.session.new_branch(
            name="TechLead",
            system="""You are a technical lead.
            Guide technical decisions.
            Coordinate team efforts.
            Ensure project success."""
        )
        
        # Configure model
        self.tech_lead.add_model(self.team.developer.model)
        
        # Track discussions
        self.discussions: Dict[str, List[dict]] = {}
    
    async def discuss_issue(
        self,
        topic: str,
        context: dict
    ) -> dict:
        """Team discussion on issue."""
        try:
            # Start discussion
            if topic not in self.discussions:
                self.discussions[topic] = []
            
            # Get tech lead view
            lead_view = await self.tech_lead.chat(
                f"""Analyze issue: {topic}
                Context: {context}"""
            )
            
            # Get architect input
            arch_input = await self.team.architect.chat(
                f"""Review issue: {topic}
                Context: {context}
                Tech Lead view: {lead_view}"""
            )
            
            # Get developer perspective
            dev_input = await self.team.developer.chat(
                f"""Consider issue: {topic}
                Context: {context}
                Architect input: {arch_input}"""
            )
            
            # Synthesize discussion
            synthesis = await self.tech_lead.chat(
                f"""Synthesize discussion:
                Topic: {topic}
                Tech Lead: {lead_view}
                Architect: {arch_input}
                Developer: {dev_input}"""
            )
            
            # Record discussion
            discussion = {
                "topic": topic,
                "context": context,
                "views": {
                    "tech_lead": lead_view,
                    "architect": arch_input,
                    "developer": dev_input
                },
                "synthesis": synthesis,
                "timestamp": datetime.now().isoformat()
            }
            
            self.discussions[topic].append(discussion)
            
            return {
                "status": "success",
                "discussion": discussion
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def make_decision(
        self,
        topic: str,
        options: List[dict]
    ) -> dict:
        """Make team decision."""
        try:
            # Get tech lead analysis
            lead_analysis = await self.tech_lead.chat(
                f"""Analyze options for: {topic}
                Options: {options}"""
            )
            
            # Get architect review
            arch_review = await self.team.architect.chat(
                f"""Review options for: {topic}
                Options: {options}
                Tech Lead analysis: {lead_analysis}"""
            )
            
            # Get developer input
            dev_input = await self.team.developer.chat(
                f"""Consider options for: {topic}
                Options: {options}
                Architect review: {arch_review}"""
            )
            
            # Make decision
            decision = await self.tech_lead.chat(
                f"""Make decision for: {topic}
                Options: {options}
                Team input:
                - Tech Lead: {lead_analysis}
                - Architect: {arch_review}
                - Developer: {dev_input}"""
            )
            
            # Record decision
            record = {
                "topic": topic,
                "options": options,
                "analysis": {
                    "tech_lead": lead_analysis,
                    "architect": arch_review,
                    "developer": dev_input
                },
                "decision": decision,
                "timestamp": datetime.now().isoformat()
            }
            
            self.team.project["decisions"][topic] = record
            
            return {
                "status": "success",
                "decision": record
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def team_collaboration():
    """Demo team collaboration."""
    # Create team
    team = DevTeamPlus(
        project_name="AI Platform",
        save_dir="platform_dev"
    )
    
    # Discuss architecture
    issue = {
        "type": "architecture",
        "component": "data pipeline",
        "concerns": [
            "scalability",
            "reliability",
            "maintainability"
        ]
    }
    
    discussion = await team.discuss_issue(
        "pipeline_architecture",
        issue
    )
    print("\nDiscussion:", discussion)
    
    # Make decision
    if discussion["status"] == "success":
        options = [
            {
                "name": "microservices",
                "pros": [
                    "scalable",
                    "flexible"
                ],
                "cons": [
                    "complex",
                    "overhead"
                ]
            },
            {
                "name": "monolithic",
                "pros": [
                    "simple",
                    "consistent"
                ],
                "cons": [
                    "less scalable",
                    "tight coupling"
                ]
            }
        ]
        
        decision = await team.make_decision(
            "architecture_choice",
            options
        )
        print("\nDecision:", decision)

# Run collaboration
asyncio.run(team_collaboration())
```

## Real-World Example

### Development Process
```python
from lionagi import Branch, Model, Session, types
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json

class Feature(Form):
    """Feature request form."""
    name: str = Field(
        description="Feature name"
    )
    description: str = Field(
        description="Feature description"
    )
    requirements: List[str] = Field(
        description="Feature requirements"
    )
    constraints: List[str] = Field(
        description="Feature constraints"
    )
    priority: str = Field(
        description="Feature priority",
        pattern="^(low|medium|high)$"
    )

class DevProcess:
    """Complete development process."""
    def __init__(
        self,
        project_name: str,
        save_dir: str = "project"
    ):
        # Create team
        self.team = DevTeamPlus(
            project_name=project_name,
            save_dir=save_dir
        )
        
        # Track process
        self.features: Dict[str, dict] = {}
        self.sprints: Dict[str, dict] = {}
        self.releases: Dict[str, dict] = {}
    
    async def add_feature(
        self,
        request: dict
    ) -> dict:
        """Add new feature."""
        try:
            # Validate request
            feature = Feature(**request)
            
            # Design feature
            design = await self.team.design_feature(
                feature.model_dump()
            )
            
            if design["status"] != "success":
                return design
            
            # Discuss implementation
            discussion = await self.team.discuss_issue(
                f"implement_{feature.name}",
                {
                    "feature": feature.model_dump(),
                    "design": design["task"]
                }
            )
            
            # Track feature
            self.features[design["task_id"]] = {
                "feature": feature.model_dump(),
                "design": design["task"],
                "discussion": discussion["discussion"],
                "status": "planned",
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "feature_id": design["task_id"]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def plan_sprint(
        self,
        features: List[str],
        duration: int = 14
    ) -> dict:
        """Plan development sprint."""
        try:
            # Validate features
            invalid = [
                f for f in features
                if f not in self.features
            ]
            if invalid:
                return {
                    "status": "error",
                    "error": f"Unknown features: {invalid}"
                }
            
            # Get sprint features
            sprint_features = [
                self.features[f]
                for f in features
            ]
            
            # Plan sprint
            sprint_id = f"sprint_{len(self.sprints)}"
            sprint = {
                "id": sprint_id,
                "features": features,
                "duration": duration,
                "status": "planned",
                "start": datetime.now().isoformat()
            }
            
            # Get team input
            plan = await self.team.discuss_issue(
                f"sprint_{sprint_id}",
                {
                    "sprint": sprint,
                    "features": sprint_features
                }
            )
            
            # Record sprint
            sprint["plan"] = plan["discussion"]
            self.sprints[sprint_id] = sprint
            
            return {
                "status": "success",
                "sprint_id": sprint_id,
                "sprint": sprint
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def implement_sprint(
        self,
        sprint_id: str
    ) -> dict:
        """Implement sprint features."""
        if sprint_id not in self.sprints:
            return {
                "status": "error",
                "error": f"Unknown sprint: {sprint_id}"
            }
        
        try:
            sprint = self.sprints[sprint_id]
            results = []
            
            # Implement each feature
            for feature_id in sprint["features"]:
                feature = self.features[feature_id]
                
                # Generate code
                code = await self.team.developer.chat(
                    f"""Implement feature:
                    {feature['feature']}
                    Design: {feature['design']}"""
                )
                
                # Review implementation
                review = await self.team.implement_task(
                    feature_id,
                    code
                )
                
                results.append({
                    "feature_id": feature_id,
                    "result": review
                })
            
            # Update sprint
            sprint["results"] = results
            sprint["status"] = "implemented"
            sprint["end"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "sprint_id": sprint_id,
                "results": results
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def run_sprint():
    """Demo development process."""
    # Create process
    process = DevProcess(
        project_name="AI Platform",
        save_dir="platform"
    )
    
    # Add features
    features = [
        {
            "name": "Smart Search",
            "description": "Intelligent search system",
            "requirements": [
                "Multi-source search",
                "Result ranking",
                "Query caching"
            ],
            "constraints": [
                "Response time < 1s",
                "Memory < 100MB"
            ],
            "priority": "high"
        },
        {
            "name": "Data Pipeline",
            "description": "ETL pipeline system",
            "requirements": [
                "Data extraction",
                "Transformation rules",
                "Load validation"
            ],
            "constraints": [
                "Throughput > 1000 rps",
                "Error rate < 0.1%"
            ],
            "priority": "medium"
        }
    ]
    
    # Add each feature
    feature_ids = []
    for feature in features:
        result = await process.add_feature(feature)
        print(f"\nFeature {feature['name']}:", result)
        
        if result["status"] == "success":
            feature_ids.append(result["feature_id"])
    
    # Plan sprint
    if feature_ids:
        sprint = await process.plan_sprint(
            feature_ids,
            duration=14
        )
        print("\nSprint Plan:", sprint)
        
        # Implement sprint
        if sprint["status"] == "success":
            results = await process.implement_sprint(
                sprint["sprint_id"]
            )
            print("\nSprint Results:", results)

# Run process
asyncio.run(run_sprint())
```

## Best Practices

1. **Team Design**
   - Define clear roles
   - Enable communication
   - Track decisions
   - Maintain context

2. **Process Flow**
   - Plan carefully
   - Review thoroughly
   - Document decisions
   - Monitor progress

3. **Collaboration**
   - Share knowledge
   - Coordinate efforts
   - Handle conflicts
   - Maintain quality

## Quick Reference
```python
from lionagi import Branch, Model, Session

# Create session
session = Session()

# Create branches
architect = session.new_branch(
    name="Architect",
    system="You are an architect."
)
developer = session.new_branch(
    name="Developer",
    system="You are a developer."
)

# Configure model
model = Model(provider="openai")
architect.add_model(model)
developer.add_model(model)

# Communicate
await architect.chat("Design system")
await developer.chat("Implement design")
```

## Next Steps

You've learned:
- How to coordinate teams
- How to manage communication
- How to track decisions
- How to handle development

In [Chapter 7](ch7_multi_agent.md), we'll explore multi-agent systems for complex task coordination.
