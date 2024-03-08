
# Supportive Functions for StepWise Method

def DetermineNextStep(response, step):
    """
    Decides the next step based on the LLM's response and the current step.
    
    Args:
        response (str): The LLM's response to the previous step.
        step (int): The current step in the progression.
        
    Returns:
        str: The next instruction or query for the StepWise progression.
    """
    # This is a placeholder logic, actual implementation may vary based on response analysis
    return f"Based on your response, what would be the next step after {step}?"

def NextStepAvailable(response):
    """
    Checks if there is more information to be uncovered or more steps to take.
    
    Args:
        response (str): The LLM's latest response.
        
    Returns:
        bool: True if more steps are available, False otherwise.
    """
    # Placeholder logic, actual implementation may depend on analyzing the response
    return "next step available" in response

def FormatFinalResponse(response):
    """
    Formats the final outcome of the StepWise progression into a coherent message.
    
    Args:
        response (str): The final response from the LLM.
        
    Returns:
        str: The formatted final response to be presented in the chat.
    """
    return f"Final step completed. Here's the outcome: {response}"
