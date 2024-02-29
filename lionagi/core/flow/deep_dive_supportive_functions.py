
# Supportive Functions for DeepDive Method

def GenerateInitialQuery(topic):
    """
    Constructs the initial query based on the specified topic.
    
    Args:
        topic (str): The topic to explore in depth.
        
    Returns:
        str: The initial query tailored for the deep dive into the topic.
    """
    return f"Tell me more about {topic}."

def GenerateFollowUpQuery(response, depth):
    """
    Creates a follow-up query based on the previous response and the exploration depth.
    
    Args:
        response (str): The LLM's last response.
        depth (int): The current depth of exploration.
        
    Returns:
        str: The follow-up query to delve deeper into the topic.
    """
    return f"Can you provide more detailed information on this aspect: {response}? Depth: {depth}"

def FurtherExplorationNeeded(response):
    """
    Determines if further exploration is needed based on the LLM's response.
    
    Args:
        response (str): The LLM's last response.
        
    Returns:
        bool: True if further exploration is needed, False otherwise.
    """
    # Example condition, can be replaced with more complex logic
    return "more to explore" in response

def SummarizeFindings(response):
    """
    Summarizes the findings from the deep dive exploration.
    
    Args:
        response (str): The aggregated responses from the deep dive.
        
    Returns:
        str: A summary of the key findings.
    """
    return f"Summary of findings: {response}"
