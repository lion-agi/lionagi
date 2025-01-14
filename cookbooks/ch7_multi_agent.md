# LionAGI Cookbook

## Chapter 7: Building a Content Creation System

In previous chapters, you built various assistants. Now we'll explore multi-agent systems by building a content creation system that:
- Plans content strategy
- Creates various content types
- Reviews and edits content
- Manages publication workflow

### Prerequisites
- Completed [Chapter 6](ch6_multi_branch.md)
- Understanding of content creation
- Basic Python knowledge

## Multi-Agent Basics

### Agent Setup
```python
from lionagi import Branch, Model, Session, types
from datetime import datetime
from pathlib import Path
import json

class ContentTeam:
    """Content creation team."""
    def __init__(
        self,
        project_name: str,
        save_dir: str = "content"
    ):
        # Create session
        self.session = Session()
        
        # Create agents
        self.strategist = self.session.new_branch(
            name="Strategist",
            system="""You are a content strategist.
            Plan content strategy.
            Define target audience.
            Set content goals."""
        )
        
        self.writer = self.session.new_branch(
            name="Writer",
            system="""You are a content writer.
            Create engaging content.
            Follow style guides.
            Match audience needs."""
        )
        
        self.editor = self.session.new_branch(
            name="Editor",
            system="""You are a content editor.
            Review content quality.
            Ensure consistency.
            Suggest improvements."""
        )
        
        self.publisher = self.session.new_branch(
            name="Publisher",
            system="""You are a content publisher.
            Format content properly.
            Optimize for platforms.
            Track performance."""
        )
        
        # Configure models
        model = Model(
            provider="openai",
            model="gpt-4",
            temperature=0.7  # More creative
        )
        
        for branch in self.session.branches:
            branch.add_model(model)
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track content
        self.content: dict[str, dict] = {}
        self._load_content()
    
    def _load_content(self):
        """Load saved content."""
        for file in self.save_dir.glob("*.json"):
            with open(file) as f:
                content = json.load(f)
                self.content[content["id"]] = content
    
    async def plan_content(
        self,
        topic: str,
        audience: str,
        goals: list[str]
    ) -> dict:
        """Plan content strategy."""
        try:
            # Get strategy
            strategy = await self.strategist.chat(
                f"""Plan content for:
                Topic: {topic}
                Audience: {audience}
                Goals: {goals}"""
            )
            
            # Get content outline
            outline = await self.writer.chat(
                f"""Create outline based on:
                Strategy: {strategy}
                Topic: {topic}
                Audience: {audience}"""
            )
            
            # Get editorial guidelines
            guidelines = await self.editor.chat(
                f"""Define guidelines for:
                Topic: {topic}
                Audience: {audience}
                Outline: {outline}"""
            )
            
            # Create content plan
            content_id = f"content_{len(self.content)}"
            plan = {
                "id": content_id,
                "topic": topic,
                "audience": audience,
                "goals": goals,
                "strategy": strategy,
                "outline": outline,
                "guidelines": guidelines,
                "status": "planned",
                "timestamp": datetime.now().isoformat()
            }
            
            # Save plan
            self.content[content_id] = plan
            
            return {
                "status": "success",
                "content_id": content_id,
                "plan": plan
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def create_content(
        self,
        content_id: str
    ) -> dict:
        """Create content from plan."""
        if content_id not in self.content:
            return {
                "status": "error",
                "error": f"Unknown content: {content_id}"
            }
        
        try:
            plan = self.content[content_id]
            
            # Create draft
            draft = await self.writer.chat(
                f"""Write content following:
                Topic: {plan['topic']}
                Outline: {plan['outline']}
                Guidelines: {plan['guidelines']}"""
            )
            
            # Review content
            review = await self.editor.chat(
                f"""Review content:
                Draft: {draft}
                Guidelines: {plan['guidelines']}"""
            )
            
            # Get improvements
            if "needs_revision" in review.lower():
                revised = await self.writer.chat(
                    f"""Revise content based on:
                    Draft: {draft}
                    Review: {review}"""
                )
                draft = revised
            
            # Format content
            formatted = await self.publisher.chat(
                f"""Format content for publication:
                Content: {draft}
                Topic: {plan['topic']}
                Audience: {plan['audience']}"""
            )
            
            # Update content
            plan["draft"] = draft
            plan["review"] = review
            plan["content"] = formatted
            plan["status"] = "created"
            plan["updated"] = datetime.now().isoformat()
            
            # Save content
            file_path = self.save_dir / f"{content_id}.json"
            with open(file_path, "w") as f:
                json.dump(plan, f, indent=2)
            
            return {
                "status": "success",
                "content_id": content_id,
                "content": formatted
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def create_article():
    """Demo content creation."""
    # Create team
    team = ContentTeam(
        project_name="Tech Blog",
        save_dir="blog_content"
    )
    
    # Plan content
    plan = await team.plan_content(
        topic="AI Safety",
        audience="Technical professionals",
        goals=[
            "Explain key concepts",
            "Discuss challenges",
            "Provide solutions"
        ]
    )
    print("\nContent Plan:", plan)
    
    # Create content
    if plan["status"] == "success":
        content = await team.create_content(
            plan["content_id"]
        )
        print("\nContent:", content)

# Run creation
asyncio.run(create_article())
```

## Advanced Workflows

### Content Pipeline
```python
from enum import Enum
from typing import List, Dict, Any

class ContentType(Enum):
    ARTICLE = "article"
    VIDEO = "video"
    SOCIAL = "social"
    EMAIL = "email"

class ContentPipeline:
    """Advanced content pipeline."""
    def __init__(
        self,
        project_name: str,
        save_dir: str = "content"
    ):
        # Create team
        self.team = ContentTeam(
            project_name=project_name,
            save_dir=save_dir
        )
        
        # Add coordinator
        self.coordinator = self.team.session.new_branch(
            name="Coordinator",
            system="""You are a content coordinator.
            Manage content pipeline.
            Coordinate team efforts.
            Ensure quality delivery."""
        )
        
        # Configure model
        self.coordinator.add_model(self.team.writer.model)
        
        # Track workflows
        self.workflows: Dict[str, List[dict]] = {}
    
    async def create_workflow(
        self,
        topic: str,
        types: List[ContentType]
    ) -> dict:
        """Create content workflow."""
        try:
            # Plan workflow
            workflow_id = f"workflow_{len(self.workflows)}"
            
            # Get coordinator plan
            plan = await self.coordinator.chat(
                f"""Plan content workflow for:
                Topic: {topic}
                Content Types: {[t.value for t in types]}
                
                Consider:
                1. Content dependencies
                2. Team coordination
                3. Quality checks
                4. Timeline"""
            )
            
            # Create content items
            items = []
            for type_ in types:
                # Plan content
                result = await self.team.plan_content(
                    topic=topic,
                    audience=f"{type_.value} audience",
                    goals=[
                        f"Create {type_.value} content",
                        "Engage audience",
                        "Drive action"
                    ]
                )
                
                if result["status"] == "success":
                    items.append({
                        "type": type_.value,
                        "content_id": result["content_id"],
                        "plan": result["plan"]
                    })
            
            # Record workflow
            workflow = {
                "id": workflow_id,
                "topic": topic,
                "types": [t.value for t in types],
                "plan": plan,
                "items": items,
                "status": "planned",
                "timestamp": datetime.now().isoformat()
            }
            
            self.workflows[workflow_id] = workflow
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow": workflow
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_workflow(
        self,
        workflow_id: str
    ) -> dict:
        """Execute content workflow."""
        if workflow_id not in self.workflows:
            return {
                "status": "error",
                "error": f"Unknown workflow: {workflow_id}"
            }
        
        try:
            workflow = self.workflows[workflow_id]
            results = []
            
            # Create each content item
            for item in workflow["items"]:
                result = await self.team.create_content(
                    item["content_id"]
                )
                
                results.append({
                    "type": item["type"],
                    "result": result
                })
            
            # Update workflow
            workflow["results"] = results
            workflow["status"] = "completed"
            workflow["completed"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "results": results
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def run_workflow():
    """Demo content workflow."""
    # Create pipeline
    pipeline = ContentPipeline(
        project_name="Product Launch",
        save_dir="launch_content"
    )
    
    # Create workflow
    workflow = await pipeline.create_workflow(
        topic="New AI Feature",
        types=[
            ContentType.ARTICLE,
            ContentType.VIDEO,
            ContentType.SOCIAL
        ]
    )
    print("\nWorkflow:", workflow)
    
    # Execute workflow
    if workflow["status"] == "success":
        results = await pipeline.execute_workflow(
            workflow["workflow_id"]
        )
        print("\nResults:", results)

# Run workflow
asyncio.run(run_workflow())
```

## Real-World Example

### Content Marketing System
```python
from lionagi import Branch, Model, Session, types
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json

class Campaign(Form):
    """Content campaign form."""
    name: str = Field(
        description="Campaign name"
    )
    objective: str = Field(
        description="Campaign objective"
    )
    audience: List[str] = Field(
        description="Target audiences"
    )
    channels: List[str] = Field(
        description="Distribution channels"
    )
    timeline: Dict[str, str] = Field(
        description="Campaign timeline"
    )
    budget: float = Field(
        description="Campaign budget",
        ge=0
    )

class ContentMarketing:
    """Complete content marketing system."""
    def __init__(
        self,
        project_name: str,
        save_dir: str = "marketing"
    ):
        # Create pipeline
        self.pipeline = ContentPipeline(
            project_name=project_name,
            save_dir=save_dir
        )
        
        # Track campaigns
        self.campaigns: Dict[str, dict] = {}
        self.workflows: Dict[str, dict] = {}
        self.analytics: Dict[str, dict] = {}
    
    async def create_campaign(
        self,
        request: dict
    ) -> dict:
        """Create content campaign."""
        try:
            # Validate request
            campaign = Campaign(**request)
            
            # Create workflows
            workflows = []
            for channel in campaign.channels:
                # Determine content types
                types = self._get_channel_types(channel)
                
                # Create workflow
                workflow = await self.pipeline.create_workflow(
                    topic=campaign.name,
                    types=types
                )
                
                if workflow["status"] == "success":
                    workflows.append(workflow)
            
            # Record campaign
            record = {
                "campaign": campaign.model_dump(),
                "workflows": workflows,
                "status": "created",
                "timestamp": datetime.now().isoformat()
            }
            
            campaign_id = f"campaign_{len(self.campaigns)}"
            self.campaigns[campaign_id] = record
            
            return {
                "status": "success",
                "campaign_id": campaign_id,
                "campaign": record
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_channel_types(
        self,
        channel: str
    ) -> List[ContentType]:
        """Get content types for channel."""
        types = {
            "blog": [ContentType.ARTICLE],
            "youtube": [ContentType.VIDEO],
            "social": [ContentType.SOCIAL],
            "email": [ContentType.EMAIL]
        }
        return types.get(channel, [])
    
    async def execute_campaign(
        self,
        campaign_id: str
    ) -> dict:
        """Execute content campaign."""
        if campaign_id not in self.campaigns:
            return {
                "status": "error",
                "error": f"Unknown campaign: {campaign_id}"
            }
        
        try:
            campaign = self.campaigns[campaign_id]
            results = []
            
            # Execute each workflow
            for workflow in campaign["workflows"]:
                result = await self.pipeline.execute_workflow(
                    workflow["workflow_id"]
                )
                results.append(result)
            
            # Update campaign
            campaign["results"] = results
            campaign["status"] = "executed"
            campaign["executed"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "campaign_id": campaign_id,
                "results": results
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def analyze_campaign(
        self,
        campaign_id: str
    ) -> dict:
        """Analyze campaign results."""
        if campaign_id not in self.campaigns:
            return {
                "status": "error",
                "error": f"Unknown campaign: {campaign_id}"
            }
        
        try:
            campaign = self.campaigns[campaign_id]
            
            # Get coordinator analysis
            analysis = await self.pipeline.coordinator.chat(
                f"""Analyze campaign results:
                Campaign: {campaign['campaign']}
                Results: {campaign['results']}
                
                Consider:
                1. Content quality
                2. Channel coverage
                3. Timeline adherence
                4. Resource utilization"""
            )
            
            # Record analysis
            self.analytics[campaign_id] = {
                "campaign_id": campaign_id,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "campaign_id": campaign_id,
                "analysis": analysis
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Usage
async def run_campaign():
    """Demo marketing campaign."""
    # Create system
    system = ContentMarketing(
        project_name="Product Marketing",
        save_dir="marketing"
    )
    
    # Create campaign
    request = {
        "name": "AI Product Launch",
        "objective": "Launch new AI feature",
        "audience": [
            "developers",
            "data scientists"
        ],
        "channels": [
            "blog",
            "youtube",
            "social"
        ],
        "timeline": {
            "start": "2024-01-01",
            "end": "2024-01-31"
        },
        "budget": 10000
    }
    
    # Create campaign
    campaign = await system.create_campaign(request)
    print("\nCampaign:", campaign)
    
    # Execute campaign
    if campaign["status"] == "success":
        execution = await system.execute_campaign(
            campaign["campaign_id"]
        )
        print("\nExecution:", execution)
        
        # Analyze results
        if execution["status"] == "success":
            analysis = await system.analyze_campaign(
                campaign["campaign_id"]
            )
            print("\nAnalysis:", analysis)

# Run campaign
asyncio.run(run_campaign())
```

## Best Practices

1. **Agent Design**
   - Define clear roles
   - Enable specialization
   - Coordinate effectively
   - Track progress

2. **Workflow Design**
   - Plan dependencies
   - Handle coordination
   - Ensure quality
   - Monitor execution

3. **System Design**
   - Validate inputs
   - Handle errors
   - Track state
   - Analyze results

## Quick Reference
```python
from lionagi import Branch, Model, Session

# Create session
session = Session()

# Create agents
writer = session.new_branch(
    name="Writer",
    system="You are a writer."
)
editor = session.new_branch(
    name="Editor",
    system="You are an editor."
)

# Configure model
model = Model(provider="openai")
writer.add_model(model)
editor.add_model(model)

# Collaborate
content = await writer.chat("Write article")
feedback = await editor.chat(f"Review: {content}")
```

## Next Steps

You've learned:
- How to create agent teams
- How to manage workflows
- How to coordinate tasks
- How to analyze results

In [Chapter 8](ch8_rate_limiting.md), we'll explore rate limiting and resource management.
