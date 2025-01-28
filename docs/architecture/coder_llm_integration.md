# LLM Integration for Coder Tools

## Overview

This document describes how our coder tools integrate with Large Language Models (LLMs) for code analysis, generation, and modification. The integration provides:

1. Structured prompting for code operations
2. Context management for multi-file changes
3. Response parsing and validation
4. Error recovery and refinement loops

## Core Components

### 1. Code Analysis Prompts

```python
class CodeAnalysisPrompt:
    """Base prompt templates for code analysis"""
    
    FILE_ANALYSIS = """
    Analyze the following code:
    {code}
    
    Focus on:
    1. Structure and patterns
    2. Error handling and edge cases
    3. Performance considerations
    4. Security implications
    """
    
    CHANGE_PROPOSAL = """
    Propose changes to implement:
    {instruction}
    
    Current code:
    {code}
    
    Consider:
    1. Minimal necessary changes
    2. Maintaining existing patterns
    3. Error handling
    4. Tests needed
    """
    
    REVIEW_CHANGES = """
    Review the proposed changes:
    {diff}
    
    Original context:
    {original}
    
    Verify:
    1. Correctness
    2. Completeness
    3. Side effects
    4. Testing needs
    """
```

### 2. Response Models

```python
class CodeAnalysis(BaseModel):
    """Structured code analysis response"""
    patterns: List[str] = Field(..., description="Identified code patterns")
    risks: List[str] = Field(..., description="Potential risks or issues")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    dependencies: List[str] = Field(..., description="Identified dependencies")

class ChangeProposal(BaseModel):
    """Proposed code changes"""
    changes: List[Dict[str, str]] = Field(..., description="File changes")
    reasoning: str = Field(..., description="Change justification")
    tests: List[str] = Field(..., description="Required tests")
    risks: List[str] = Field(..., description="Potential risks")

class ReviewFeedback(BaseModel):
    """Code review feedback"""
    approved: bool = Field(..., description="Whether changes are approved")
    issues: List[str] = Field(..., description="Identified issues")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    required_changes: List[str] = Field(..., description="Required changes")
```

### 3. LLM Integration Manager

```python
class CoderLLMManager:
    """
    Manages LLM interactions for code operations
    
    Features:
    - Context management
    - Prompt construction
    - Response parsing
    - Error recovery
    """
    
    async def analyze_code(
        self,
        files: List[str],
        instruction: Optional[str] = None
    ) -> CodeAnalysis:
        """Analyze code files"""
        
    async def propose_changes(
        self,
        instruction: str,
        files: List[str]
    ) -> ChangeProposal:
        """Generate change proposal"""
        
    async def review_changes(
        self,
        diff: str,
        original_files: List[str]
    ) -> ReviewFeedback:
        """Review proposed changes"""
```

## Integration Workflows

### 1. Aider Integration

```python
class AiderLLMWorkflow:
    """
    Aider-specific LLM workflow
    
    Features:
    - CLI interaction parsing
    - Context preservation
    - Change tracking
    """
    
    async def process_instruction(
        self,
        instruction: str,
        files: List[str]
    ) -> Changes:
        # 1. Analyze current code
        analysis = await self.llm.analyze_code(files)
        
        # 2. Generate proposal
        proposal = await self.llm.propose_changes(instruction, files)
        
        # 3. Apply changes in sandbox
        changes = await self.sandbox.apply_changes(proposal.changes)
        
        # 4. Review results
        review = await self.llm.review_changes(changes.diff, files)
        
        # 5. Refine if needed
        if not review.approved:
            return await self.refine_changes(review, files)
            
        return changes
```

### 2. Direct Diff Workflow

```python
class DiffLLMWorkflow:
    """
    Direct diff modification workflow
    
    Features:
    - Targeted file changes
    - Context-aware modifications
    - Validation checks
    """
    
    async def generate_diff(
        self,
        instruction: str,
        file_path: str
    ) -> str:
        # 1. Analyze target file
        analysis = await self.llm.analyze_code([file_path])
        
        # 2. Generate specific changes
        proposal = await self.llm.propose_changes(
            instruction,
            [file_path]
        )
        
        # 3. Create and validate diff
        diff = self.create_diff(
            original=self.read_file(file_path),
            changes=proposal.changes
        )
        
        # 4. Review diff
        review = await self.llm.review_changes(diff, [file_path])
        
        # 5. Refine if needed
        if not review.approved:
            return await self.refine_diff(review, file_path)
            
        return diff
```

### 3. Fuzzy Finding Integration

```python
class FinderLLMWorkflow:
    """
    Code finding with LLM assistance
    
    Features:
    - Semantic search
    - Pattern matching
    - Result ranking
    """
    
    async def find_matches(
        self,
        pattern: str,
        files: List[str],
        threshold: float
    ) -> List[Match]:
        # 1. Analyze search context
        analysis = await self.llm.analyze_code(files)
        
        # 2. Generate search patterns
        patterns = await self.llm.expand_search_pattern(pattern)
        
        # 3. Find matches
        matches = []
        for p in patterns:
            matches.extend(
                self.fuzzy_find(p, files, threshold)
            )
            
        # 4. Rank and filter results
        ranked = await self.llm.rank_matches(matches, pattern)
        
        return ranked
```

## Response Processing

### 1. Validation Pipeline

```python
async def validate_changes(
    changes: ChangeProposal,
    context: Dict[str, Any]
) -> bool:
    """
    Validate proposed changes through multiple steps
    """
    # 1. Basic validation
    if not changes.validate_schema():
        return False
        
    # 2. Context validation
    if not await validate_context(changes, context):
        return False
        
    # 3. Safety checks
    if not await validate_safety(changes):
        return False
        
    # 4. Integration validation
    if not await validate_integration(changes):
        return False
        
    return True
```

### 2. Error Recovery

```python
async def recover_from_error(
    error: Error,
    context: Dict[str, Any]
) -> Optional[Solution]:
    """
    Attempt to recover from errors with LLM assistance
    """
    # 1. Analyze error
    analysis = await llm.analyze_error(error)
    
    # 2. Generate recovery plan
    plan = await llm.generate_recovery(analysis)
    
    # 3. Attempt recovery
    for step in plan.steps:
        if await attempt_recovery(step):
            return step.solution
            
    return None
```

## Best Practices

1. Context Management:
- Maintain file state
- Track dependencies
- Preserve history

2. Prompt Engineering:
- Clear instructions
- Relevant context
- Consistent format

3. Validation:
- Schema validation
- Context validation
- Integration testing

4. Error Handling:
- Graceful degradation
- Recovery attempts
- Clear feedback

5. Performance:
- Batch operations
- Cache context
- Reuse results

This integration system provides a robust framework for combining LLM capabilities with our coder tools while maintaining safety and reliability.