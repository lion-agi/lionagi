# LionAGI Cookbook

## Chapter 4: Building a Survey System

In previous chapters, you built assistants for research, customer service, and data processing. Now we'll explore forms by building a survey system that:
- Collects structured feedback
- Validates responses
- Generates insights
- Handles data export

### Prerequisites
- Completed [Chapter 3](ch3_internal_tools.md)
- Understanding of data validation
- Basic Python knowledge

## Form Basics

### Simple Form
```python
from lionagi import Branch, Model, Form, types
from pydantic import Field
from typing import List, Optional
from enum import Enum

# Define rating scale
class Rating(str, Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

# Create feedback form
class FeedbackForm(Form):
    """Product feedback form."""
    # User info
    name: str = Field(
        description="User's full name"
    )
    email: str = Field(
        description="User's email",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    )
    
    # Product feedback
    product: str = Field(
        description="Product name"
    )
    rating: Rating = Field(
        description="Product rating"
    )
    comments: Optional[str] = Field(
        description="Additional comments",
        default=None
    )
    
    # Metadata
    would_recommend: bool = Field(
        description="Would recommend to others",
        default=True
    )
    
    class Config:
        """Form configuration."""
        title = "Product Feedback"
        description = "Share your product experience"

# Usage
form = FeedbackForm(
    name="Alice Smith",
    email="alice@example.com",
    product="AI Assistant",
    rating=Rating.EXCELLENT,
    comments="Very helpful!",
    would_recommend=True
)

print("Valid form:", form.model_dump())
```

### Form Validation
```python
from datetime import datetime
from typing import Dict, Any

class SurveyForm(Form):
    """Advanced survey form with validation."""
    # Response metadata
    response_id: str = Field(
        description="Unique response ID"
    )
    timestamp: datetime = Field(
        description="Response time",
        default_factory=datetime.now
    )
    
    # Survey questions
    answers: Dict[str, Any] = Field(
        description="Question answers"
    )
    
    # Custom validation
    @validator("answers")
    def validate_answers(cls, v):
        """Validate survey answers."""
        required = {
            "q1": str,  # Text response
            "q2": int,  # Rating 1-5
            "q3": bool  # Yes/No
        }
        
        # Check required questions
        for q, type_ in required.items():
            if q not in v:
                raise ValueError(f"Missing answer: {q}")
            
            if not isinstance(v[q], type_):
                raise ValueError(
                    f"Invalid type for {q}: "
                    f"expected {type_.__name__}"
                )
            
            # Validate rating range
            if q == "q2" and not 1 <= v[q] <= 5:
                raise ValueError(
                    "Rating must be between 1 and 5"
                )
        
        return v
```

## Form Management

### Survey System
```python
from pathlib import Path
import json
import uuid

class SurveySystem:
    """Complete survey management system."""
    def __init__(
        self,
        name: str = "SurveyBot",
        save_dir: str = "surveys"
    ):
        # Create assistant
        self.assistant = Branch(
            name=name,
            system="""You are a survey assistant.
            Help collect and analyze feedback.
            Validate responses carefully.
            Generate helpful insights."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model="gpt-3.5-turbo",
            temperature=0.3  # More precise
        )
        self.assistant.add_model(self.model)
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track responses
        self.responses: dict[str, dict] = {}
        self._load_responses()
    
    def _load_responses(self):
        """Load saved responses."""
        for file in self.save_dir.glob("*.json"):
            with open(file) as f:
                response = json.load(f)
                self.responses[response["response_id"]] = response
    
    async def collect_response(
        self,
        answers: dict
    ) -> dict:
        """Collect survey response."""
        try:
            # Create response
            response_id = str(uuid.uuid4())
            response = SurveyForm(
                response_id=response_id,
                answers=answers
            )
            
            # Save response
            data = response.model_dump()
            file_path = self.save_dir / f"{response_id}.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            
            # Track response
            self.responses[response_id] = data
            
            return {
                "status": "success",
                "response_id": response_id
            }
        
        except ValueError as e:
            return {
                "status": "error",
                "error": str(e)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def analyze_responses(
        self,
        min_responses: int = 5
    ) -> str:
        """Generate response analysis."""
        if len(self.responses) < min_responses:
            return (
                f"Need at least {min_responses} responses. "
                f"Currently have {len(self.responses)}."
            )
        
        # Prepare data for analysis
        data = list(self.responses.values())
        prompt = f"""
        Analyze these survey responses:
        {json.dumps(data, indent=2)}
        
        Consider:
        - Response patterns
        - Rating distribution
        - Common themes
        - Key insights
        
        Provide:
        1. Summary statistics
        2. Key findings
        3. Recommendations
        """
        
        try:
            return await self.assistant.chat(prompt)
        except Exception as e:
            return f"Error analyzing responses: {str(e)}"
    
    def export_responses(
        self,
        format: str = "json"
    ) -> str:
        """Export responses to file."""
        try:
            # Prepare export
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            filename = f"survey_responses_{timestamp}"
            
            if format == "json":
                # Export as JSON
                file_path = self.save_dir / f"{filename}.json"
                with open(file_path, "w") as f:
                    json.dump(
                        list(self.responses.values()),
                        f,
                        indent=2,
                        default=str
                    )
            
            elif format == "csv":
                # Export as CSV
                import pandas as pd
                file_path = self.save_dir / f"{filename}.csv"
                df = pd.DataFrame(self.responses.values())
                df.to_csv(file_path, index=False)
            
            else:
                return f"Unsupported format: {format}"
            
            return str(file_path)
        
        except Exception as e:
            return f"Export error: {str(e)}"

# Usage
async def run_survey():
    """Demo survey system."""
    # Create system
    system = SurveySystem(
        name="ProductSurvey",
        save_dir="product_feedback"
    )
    
    # Collect responses
    responses = [
        {
            "q1": "Great product, very intuitive",
            "q2": 5,
            "q3": True
        },
        {
            "q1": "Needs more features",
            "q2": 3,
            "q3": True
        },
        {
            "q1": "Too expensive",
            "q2": 2,
            "q3": False
        }
    ]
    
    # Process each response
    for response in responses:
        result = await system.collect_response(response)
        print(f"\nResponse: {result}")
    
    # Generate analysis
    analysis = await system.analyze_responses()
    print(f"\nAnalysis: {analysis}")
    
    # Export data
    export_path = system.export_responses(format="csv")
    print(f"\nExported to: {export_path}")

# Run survey
asyncio.run(run_survey())
```

## Real-World Example

### Customer Feedback System
```python
from lionagi import Branch, Model, Form, types
from pydantic import Field, validator
from datetime import datetime
from pathlib import Path
import json
import uuid

class ProductFeedback(Form):
    """Comprehensive product feedback form."""
    # Response metadata
    response_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )
    timestamp: datetime = Field(
        default_factory=datetime.now
    )
    
    # User info
    name: str = Field(
        min_length=2,
        max_length=100
    )
    email: str = Field(
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    )
    
    # Product info
    product_id: str
    version: str
    
    # Ratings (1-5)
    ease_of_use: int = Field(ge=1, le=5)
    features: int = Field(ge=1, le=5)
    value: int = Field(ge=1, le=5)
    support: int = Field(ge=1, le=5)
    
    # Feedback
    likes: str = Field(
        min_length=10,
        max_length=1000
    )
    improvements: str = Field(
        min_length=10,
        max_length=1000
    )
    
    # Additional info
    would_recommend: bool
    referral_source: Optional[str] = None
    
    @validator("version")
    def validate_version(cls, v):
        """Validate version format."""
        import re
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(
                "Version must be in format: X.Y.Z"
            )
        return v

class FeedbackSystem:
    """Product feedback management system."""
    def __init__(
        self,
        name: str = "FeedbackBot",
        save_dir: str = "feedback",
        model: str = "gpt-4"
    ):
        # Create assistant
        self.assistant = Branch(
            name=name,
            system="""You are a feedback analyst.
            Help analyze product feedback.
            Identify patterns and insights.
            Suggest actionable improvements."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model=model,
            temperature=0.3
        )
        self.assistant.add_model(self.model)
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track feedback
        self.feedback: dict[str, dict] = {}
        self._load_feedback()
    
    def _load_feedback(self):
        """Load saved feedback."""
        for file in self.save_dir.glob("*.json"):
            with open(file) as f:
                feedback = json.load(f)
                self.feedback[feedback["response_id"]] = feedback
    
    async def collect_feedback(
        self,
        data: dict
    ) -> dict:
        """Collect product feedback."""
        try:
            # Validate feedback
            feedback = ProductFeedback(**data)
            
            # Save feedback
            data = feedback.model_dump()
            file_path = self.save_dir / f"{feedback.response_id}.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            
            # Track feedback
            self.feedback[feedback.response_id] = data
            
            return {
                "status": "success",
                "response_id": feedback.response_id
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def analyze_product(
        self,
        product_id: str
    ) -> dict:
        """Analyze product feedback."""
        # Get product feedback
        feedback = [
            f for f in self.feedback.values()
            if f["product_id"] == product_id
        ]
        
        if not feedback:
            return {
                "error": f"No feedback for product: {product_id}"
            }
        
        # Calculate metrics
        metrics = {
            "total_responses": len(feedback),
            "recommend_rate": sum(
                1 for f in feedback
                if f["would_recommend"]
            ) / len(feedback),
            "avg_ratings": {
                "ease_of_use": sum(
                    f["ease_of_use"] for f in feedback
                ) / len(feedback),
                "features": sum(
                    f["features"] for f in feedback
                ) / len(feedback),
                "value": sum(
                    f["value"] for f in feedback
                ) / len(feedback),
                "support": sum(
                    f["support"] for f in feedback
                ) / len(feedback)
            }
        }
        
        # Get AI analysis
        prompt = f"""
        Analyze this product feedback:
        
        Metrics: {json.dumps(metrics, indent=2)}
        Feedback: {json.dumps(feedback, indent=2)}
        
        Provide:
        1. Key strengths
        2. Areas for improvement
        3. User sentiment
        4. Actionable recommendations
        """
        
        try:
            analysis = await self.assistant.chat(prompt)
            return {
                "metrics": metrics,
                "analysis": analysis
            }
        except Exception as e:
            return {"error": str(e)}
    
    def export_feedback(
        self,
        product_id: str = None,
        format: str = "json"
    ) -> str:
        """Export feedback data."""
        try:
            # Filter feedback
            if product_id:
                data = [
                    f for f in self.feedback.values()
                    if f["product_id"] == product_id
                ]
            else:
                data = list(self.feedback.values())
            
            # Generate filename
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            filename = f"feedback_{timestamp}"
            if product_id:
                filename = f"{product_id}_{filename}"
            
            if format == "json":
                # Export as JSON
                file_path = self.save_dir / f"{filename}.json"
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            
            elif format == "csv":
                # Export as CSV
                import pandas as pd
                file_path = self.save_dir / f"{filename}.csv"
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
            
            else:
                return f"Unsupported format: {format}"
            
            return str(file_path)
        
        except Exception as e:
            return f"Export error: {str(e)}"

# Usage
async def collect_feedback():
    """Demo feedback system."""
    # Create system
    system = FeedbackSystem(
        name="ProductFeedback",
        save_dir="product_feedback"
    )
    
    # Sample feedback
    feedback = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "product_id": "AI-001",
        "version": "1.0.0",
        "ease_of_use": 5,
        "features": 4,
        "value": 4,
        "support": 5,
        "likes": "Very intuitive interface, great features",
        "improvements": "Could use more customization options",
        "would_recommend": True,
        "referral_source": "Friend"
    }
    
    # Collect feedback
    result = await system.collect_feedback(feedback)
    print(f"\nFeedback: {result}")
    
    # Analyze product
    analysis = await system.analyze_product("AI-001")
    print(f"\nAnalysis: {analysis}")
    
    # Export data
    export_path = system.export_feedback(
        product_id="AI-001",
        format="csv"
    )
    print(f"\nExported to: {export_path}")

# Run system
asyncio.run(collect_feedback())
```

## Best Practices

1. **Form Design**
   - Use clear field names
   - Add field validation
   - Include descriptions
   - Handle optional fields

2. **Data Management**
   - Validate inputs
   - Store responses safely
   - Export data cleanly
   - Track metadata

3. **Analysis**
   - Calculate metrics
   - Identify patterns
   - Generate insights
   - Suggest improvements

## Quick Reference
```python
from lionagi import Form, Field

# Create form
class SimpleForm(Form):
    name: str = Field(
        description="User's name"
    )
    age: int = Field(
        ge=0,
        le=120
    )
    email: str = Field(
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    )

# Use form
form = SimpleForm(
    name="Alice",
    age=30,
    email="alice@example.com"
)

# Get data
data = form.model_dump()
```

## Next Steps

You've learned:
- How to create forms
- How to validate data
- How to collect responses
- How to analyze feedback

In [Chapter 5](ch5_react.md), we'll explore ReAct for complex reasoning tasks.
