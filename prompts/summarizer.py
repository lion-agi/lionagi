system_Summarizer = """
You are a dedicated summarizer specializing in research and analytical tasks. 
Your primary objective is to distill the given data in accordance with the user's 
defined goals. Only include synthesized, directly relevant information from the 
supplied material. Omit additional comments or sections.
"""

Summarize_person = {
    "Task Name": "Summarize a Professional Profile",
    "Provided Resources": """
    Comprehensive details about the individual's career, academic accomplishments, 
    and other relevant facets.
    """,
    "Task Description": """
    Generate a concise paragraph that distills the individual's career trajectory, 
    accomplishments, and standout qualifications.
    """,
    "Task Purpose/Objectives": """
    To create a synthesized profile that acts as a quick reference for essential 
    attributes and career milestones, useful for further investigation or contextualization.
    """,
    "Task Requirements": """
    The summary must include the following elements, if available:
    - Name
    - Current Role
    - Employer
    - Duties
    - Milestones
    - Education
    - Honors
    - Prior Positions
    - Significant Interests
    """,
    "Task Deliverables": """
    Produce a summary comprising 70-200 words that encapsulates relevant aspects 
    for immediate or future reference.
    """,
    "Deliverable Format": """
    [Person_Name] serves as [Current_Role] at [Employer], tasked with 
    [Duties]. Recognized for [Milestones], they earned their degree(s) from 
    [Education]. Previous roles were at [Prior_Positions]. Awards include [Honors]. 
    Interests encompass [Significant_Interests].
    """
}

Summarize_company = {
    "Task Name": "Distill a Company Profile",
    "Provided Resources": """
    Information from the company's official webpage, its brief description, and 
    other relevant data points.
    """,
    "Task Description": """
    Compile a succinct paragraph that delineates the company's primary focus, 
    market engagement, and unique selling propositions.
    """,
    "Task Purpose/Objectives": """
    To draft a concise summary that unambiguously identifies the company, aiding 
    in additional research or risk assessment.
    """,
    "Task Requirements": """
    The summary should include the following aspects, if obtainable:
    - Company Name
    - Sector
    - Core Offerings
    - Business Focus
    - Location
    - Scale (Employees or Turnover)
    - Founders
    - Major Backers
    - Strategic Alliances
    - Main Rivals
    - Significant Achievements
    """,
    "Task Deliverables": """
    Deliver a summary ranging between 70-200 words that is either immediately 
    useful or holds potential for future relevance.
    """,
    "Deliverable Format": """
    [Company_Name] is engaged in the [Sector] industry, known for 
    [Core_Offerings]. Located in [Location], it scales at [Scale]. Founded by 
    [Founders], it has attracted investment from [Major_Backers]. Collaborations 
    exist with [Strategic_Alliances], while primary competitors include [Main_Rivals]. 
    Noteworthy achievements encompass [Significant_Achievements].
    """
}
