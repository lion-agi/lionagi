# initial step in analyzing code files
# read in chunks of original file and return preliminary analysis 

_system = """
act like a professional python3 engineer with extensive knowledge in machine learning, large language model and computer science. Perform to the best of your ability to help the user in analyzing python codes. Note the task is multi-stage, user will give detailed instructions on how to proceed. The overall objective is to understand and process individual files effectively for further analysis, derive a summary, and create an algorithm design based on the file's content.
"""

# sequential run 1
_initial = {
    "Task Name": "File Reading and Initial Understanding",
    "Task Objective": "",
    "Task Description": """
        Given this file, gather the necessary information,
        try to understand its purpose. Provide a concise and on point description.
    """,
    "Task Deliverable": "A brief note no more than 50 words, on the essence of the file such as concepts, designs, relations.",
    "Provided Resources": """
        - python codes in a file, or parts of a file
    """
    }


# sequential run 2
_summarize = {
    "Task Name": "Generating File Summary", 
    "Task Objective": "to generate a concise yet informationally comprehensive summary",
    "Task Requirements": """
    Given the new understanding, create a summary that should include the following elements, if available:
        - file name or unique identifier
        - purpose / relationship to other files
        - imports
        - functions
        - classes
        - logic and purpose
        - data structures
        - algorithms
    """,
    "Task Deliverable": "Only the summary itself, no more than 1000 chracaters.",
    }


# sequential run 3
_design = {
    "Task Name": "Algorithm Design",
    "Task Objective": "to design an algorithm that can perform the same task as the file",
    "Task Description": "Based on the file's content and its summary, propose an algorithmic design or strategy to address the relevant challenges or tasks.",
    "Task Deliverable": "A detailed algorithmic design that should contain sufficient details or strategy that can perform the same task as the file. The design should not exceed 300 words if appropriate. Write a highly practically modularized design in a way that it can be understood clearly by user. The design can be but ideally better to be non-specific to any particular programming language. If need to, concisely and informationally articulate on the design and reasoning behind. list the assumptions made in the design.",
    }


# inidividual run
_validate = {
    "Task Name": "Output Validation",
    "Task Objective": "to validate the outputs of the file summary, and the algorithm design",
    "Task Description": "Cross-check the proposed algorithm design with the file's content and summary. Highlight any discrepancies or areas of improvement.",
    "Provied Resources": """
    - python codes in individual files
    - file summary
    - algorithm design
    """,
    "Task Deliverable": "A concise yet practically detailed note on the proposed algorithm design and its validation.",
    }


# sequential run 4
_output = {
    "Task Name": "Final output: check and polish",
    "Provided Resources": "another assistant comments",
    "Task Objective": "generate a final output that can be best used by the user as well as further analysis.",
    "Task Desription": "think about the comments on areas worthy of improvements, integrates the feedback thoughtfuly, concisely and informationally improve your work as appropriate",
    "Task Delievrable": "Final output of summaries and algorithm design that is directly useable to user, no comments from assistant needed. No more than 2500 chracaters.",
    "Task Format": """
    ### This is chunk_id of file_name
    ### final summary: the improved summary of the file
    ### final algorithm design: the improved algorithm design
    """
    }


FileAnalyzerPrompt ={
    "Prompt Name": "FileAnalyzer",
    "system": _system,
    "initial": _initial,
    "summarize": _summarize,
    "design": _design,
    "validate": _validate,
    "output": _output,  
}