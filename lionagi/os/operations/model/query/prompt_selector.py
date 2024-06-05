from typing import Any, Dict, List, Optional

DEFAULT_TEXT_QA_PROMPT = "Provide a detailed answer to the following question based on the given context."
CHAT_TEXT_QA_PROMPT = "In a conversational style, answer the following question using the provided context."

DEFAULT_TREE_SUMMARIZE_PROMPT = "Summarize the key points and themes from the provided hierarchical information."
CHAT_TREE_SUMMARIZE_PROMPT = "Provide a conversational summary of the main points and themes from the hierarchical context."

DEFAULT_REFINE_PROMPT = "Refine the following content to improve clarity and detail."
CHAT_REFINE_PROMPT = "In a conversational manner, refine the provided content for better clarity and detail."

DEFAULT_REFINE_TABLE_CONTEXT_PROMPT = "Refine the content within the table context to ensure accuracy and clarity."
CHAT_REFINE_TABLE_CONTEXT_PROMPT = "In a conversational style, refine the content within the table context for better clarity and accuracy."

default_text_qa_conditionals = [(is_chat_model, CHAT_TEXT_QA_PROMPT)]

DEFAULT_TEXT_QA_PROMPT_SEL = SelectorPromptTemplate(
    default_template=DEFAULT_TEXT_QA_PROMPT,
    conditionals=default_text_qa_conditionals,
)

default_tree_summarize_conditionals = [(is_chat_model, CHAT_TREE_SUMMARIZE_PROMPT)]

DEFAULT_TREE_SUMMARIZE_PROMPT_SEL = SelectorPromptTemplate(
    default_template=DEFAULT_TREE_SUMMARIZE_PROMPT,
    conditionals=default_tree_summarize_conditionals,
)

default_refine_conditionals = [(is_chat_model, CHAT_REFINE_PROMPT)]

DEFAULT_REFINE_PROMPT_SEL = SelectorPromptTemplate(
    default_template=DEFAULT_REFINE_PROMPT,
    conditionals=default_refine_conditionals,
)

default_refine_table_conditionals = [(is_chat_model, CHAT_REFINE_TABLE_CONTEXT_PROMPT)]

DEFAULT_REFINE_TABLE_CONTEXT_PROMPT_SEL = SelectorPromptTemplate(
    default_template=DEFAULT_REFINE_TABLE_CONTEXT_PROMPT,
    conditionals=default_refine_table_conditionals,
)
