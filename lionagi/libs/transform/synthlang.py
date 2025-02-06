# synthlang.py
"""
SynthLang translator and system prompt generator.
We incorporate the simpler framework approach (a list of frameworks to enable),
and rely on a chosen template from the included FRAMEWORK_TEMPLATES.
We also integrate optional perplexity compression from `compress_perplexity.py`.
"""
# For the optional compression step:
from timeit import default_timer as timer
from typing import Literal

from lionagi.session.branch import Branch
from lionagi.settings import Settings

from .perplexity import compress_text, iModel

########################################################################
# 1) Template Data
#    Each item is a dictionary capturing your multi-line text blocks.
########################################################################

group_theory = {
    "title": "Group Theory Analysis",
    "domain": "mathematics",
    "category": "Abstract Algebra",
    "overview": "Investigation of algebraic structures using group theory and ring theory.",
    "content": """# Structures
Let G be a group with operation •
Let H be a subgroup of G
Let N be a normal subgroup of G

# Properties
P(x): "x is a homomorphism"
Q(x): "x preserves group structure"
R(x): "x maps to kernel"

# Objectives
1. Prove fundamental homomorphism theorem
2. Show group action properties
3. Analyze quotient groups
""",
}

category_theory = {
    "title": "Category Theory Concepts",
    "domain": "mathematics",
    "category": "Category Theory",
    "overview": "Abstract mathematical framework dealing with relationships between structures.",
    "content": """# Basic Definitions
C = (Ob(C), hom(C), ∘)
F: C → D (Functor)
...
""",
}

complex_analysis = {
    "title": "Complex Analysis Foundations",
    "domain": "mathematics",
    "category": "Complex Analysis",
    "overview": "Advanced study of complex functions, including integration and residue theory.",
    "content": """# Complex Integration
∮ f(z)dz = 2πi∑Res(f,ak)
...
""",
}

math_logic = {
    "title": "Mathematical Logic Foundations",
    "domain": "mathematics",
    "category": "Mathematical Logic",
    "overview": "Exploration of fundamental mathematical logic concepts.",
    "content": """# Sets and Axioms
Let A be the set of all propositions.
...
""",
}

number_theory = {
    "title": "Number Theory Principles",
    "domain": "mathematics",
    "category": "Number Theory",
    "overview": "Study of integers, prime numbers, and arithmetic functions.",
    "content": """# Congruence Relations
a ≡ b (mod n)
...
""",
}

set_theory = {
    "title": "Set Theory Foundations",
    "domain": "mathematics",
    "category": "Set Theory",
    "overview": "Exploration of fundamental set theory concepts and operations.",
    "content": """# Basic Definitions
Let U be the universal set
...
""",
}

symbolic_systems = {
    "title": "Symbolic Systems Analysis",
    "domain": "computer-science",
    "category": "Symbolic Systems",
    "overview": "Analysis of symbolic computation in AI and formal languages.",
    "content": """# Core Concepts
Let Σ be a finite alphabet
...
""",
}

symbolic_exploration_system_supression = {
    "title": "Systematic Suppression Exploration",
    "domain": "societal",
    "category": "Real-World Simulations",
    "overview": "Analysis of suppression mechanisms using symbolic logic.",
    "content": """# Sets and Categories
Let U be the set of actions representing policies ...
""",
}

topology_fundamentals = {
    "title": "Topology Fundamentals",
    "domain": "mathematics",
    "category": "Topology",
    "overview": "Study of geometric properties under continuous deformations.",
    "content": """# Open Sets
(X,τ) topological space
...
""",
}

FRAMEWORK_TEMPLATES = {
    "group_theory": group_theory,
    "category_theory": category_theory,
    "complex_analysis": complex_analysis,
    "math_logic": math_logic,
    "number_theory": number_theory,
    "set_theory": set_theory,
    "symbolic_systems": symbolic_systems,
    "symbolic_exploration_system_supression": symbolic_exploration_system_supression,
    "topology_fundamentals": topology_fundamentals,
}


########################################################################
# 2) Framework Definitions (Simplified)
########################################################################

# Instead of a complex dict with "selectedGlyphs", let's do a simpler approach:
# We define each "framework" by name, description, and glyphs. The user can pick them by name.
FRAMEWORK_OPTIONS = {
    "math": {
        "name": "Mathematical Framework",
        "description": "Offers a suite of math glyphs and notation rules.",
        "glyphs": [
            {
                "symbol": "↹",
                "name": "Focus/Filter",
                "description": "Used for focusing instructions",
            },
            {
                "symbol": "Σ",
                "name": "Summarize",
                "description": "Condense large sets of data",
            },
            {
                "symbol": "⊕",
                "name": "Combine/Merge",
                "description": "Merge multiple data sources",
            },
            {
                "symbol": "•",
                "name": "Group Operation",
                "description": "Binary operation in group theory",
            },
        ],
    },
    "optim": {
        "name": "Optimization Framework",
        "description": "Compression and optimization for code/math expressions.",
        "glyphs": [
            {
                "symbol": "IF",
                "name": "Conditional Operator",
                "description": "Represents branching logic",
            }
        ],
    },
    "custom_algebra": {
        "name": "Custom Algebraic Framework",
        "description": "Extra rules for ring, group, field expansions.",
        "glyphs": [
            {
                "symbol": "∞",
                "name": "Infinite Operator",
                "description": "Represents unbounded algebraic ops",
            }
        ],
    },
}

########################################################################
# 3) SynthLang Base Prompt
########################################################################

BASE_PROMPT = """You are a SynthLang translator. You convert standard text into SynthLang format with these rules:

[Framework Integration]
- Use relevant framework glyphs wherever possible.
- Combine multiple frameworks if requested.

[Grammar Rules]
1) Task Glyphs:
   - ↹ (Focus/Filter) for main tasks
   - Σ (Summarize) for condensing info
   - ⊕ (Combine) for merging data
   - ? (Query) for clarifications
   - IF for conditionals

2) Subject Markers:
   - Use • before datasets (e.g., •myData)
   - Use 花 for abstract concepts
   - Use 山 for hierarchical structures

3) Modifiers:
   - ^format(type) for output format
   - ^n for importance level
   - ^lang for language
   - ^t{n} for time constraints

4) Flow Control:
   - [p=n] for priority
   - -> for sequential
   - + for parallel
   - | for alternatives

[Output Style]
- Maximize compression by removing articles & filler
- Use glyphs for repeated phrases
- Preserve semantic meaning
"""


########################################################################
# 4) Utility to build the "Active Frameworks" block
########################################################################


def build_frameworks_text(frameworks: list[str]) -> str:
    """
    Takes a list of framework keys (e.g. ["math", "optim"]) and returns
    a textual block describing them.
    """
    lines = []
    if not frameworks:
        frameworks = FRAMEWORK_OPTIONS.keys()

    for fw_key in frameworks:
        fw = FRAMEWORK_OPTIONS.get(fw_key, None)
        if fw:
            lines.append(f"{fw['name']}: {fw['description']}")
            lines.append("Glyphs:")
            for g in fw["glyphs"]:
                lines.append(
                    f"  {g['symbol']} -> {g['name']} ({g['description']})"
                )
            lines.append("")
    return "\n".join(lines).strip()


########################################################################
# 5) Main: create the SynthLang prompt
########################################################################


def create_synthlang_system_prompt(
    template_name: Literal[
        "group_theory",
        "category_theory",
        "complex_analysis",
        "math_logic",
        "number_theory",
        "set_theory",
        "symbolic_systems",
        "symbolic_exploration_system_supression",
        "topology_fundamentals",
    ],
    frameworks: list[str],
    additional_text: str = "",
) -> str:
    """
    Merges:
    - BASE_PROMPT
    - "Active Frameworks" block (from frameworks list)
    - The chosen template (from FRAMEWORK_TEMPLATES)
    - plus additional text if desired
    """
    template_block = FRAMEWORK_TEMPLATES[template_name]
    frameworks_text = build_frameworks_text(frameworks)

    # We show the user the "domain", "category", etc. from the template
    template_details = (
        f"Title: {template_block['title']}\n"
        f"Domain: {template_block['domain']}\n"
        f"Category: {template_block['category']}\n"
        f"Overview: {template_block['overview']}\n"
        "Excerpt:\n"
        f"{template_block['content']}\n"
    )

    prompt = (
        f"{BASE_PROMPT}\n\n"
        "[Active Frameworks]\n"
        f"{frameworks_text}\n\n"
        "[Template]\n"
        f"{template_details}\n"
    )

    if additional_text.strip():
        prompt += f"\n[Additional]\n{additional_text.strip()}\n"

    # Usually you might want the entire final text to be the system instruction:
    return prompt


########################################################################
# 6) Translate text into SynthLang format
########################################################################


# TODO: refactor using SynthLang package
async def translate_to_synthlang(
    text: str,
    template_name: str = "symbolic_systems",
    frameworks: list[str] = None,
    compress: bool = False,
    chat_model: iModel = None,
    compress_model: iModel = None,
    compression_ratio: float = 0.2,
    compress_kwargs=None,
    verbose: bool = True,
    branch: Branch = None,
    **kwargs,
) -> str:
    """
    Optionally compress the input text using perplexity, then build a final
    "SynthLang" style system prompt that includes frameworks, templates, etc.

    :param text: The original text to be translated/compressed
    :param template_name: Key in FRAMEWORK_TEMPLATES
    :param frameworks: e.g. ["math", "optim"] to enable these frameworks
    :param compress: If True, uses perplexity-based compression
    :param chat_model: The model for perplexity compression
    :param compression_ratio: float ratio of final token usage
    :param compress_kwargs: Additional arguments to pass to compression
    :return: A string in SynthLang style
    """
    from .synthlang import create_synthlang_system_prompt

    start = timer()
    chat_model = chat_model or iModel(**Settings.iModel.CHAT)
    if compress:
        text = await compress_text(
            text,
            chat_model=compress_model or chat_model,
            target_ratio=compression_ratio,
            **(compress_kwargs or {}),
        )

    # Build final system prompt
    final_prompt = create_synthlang_system_prompt(
        template_name=template_name,
        frameworks=frameworks,
    )

    sys1 = None
    sys2 = final_prompt
    if branch and branch.system:
        sys1 = branch.system
        branch.msgs.add_message(system=sys2)

    else:
        branch = Branch(system=final_prompt, chat_model=chat_model)

    from lionagi.service.endpoints.token_calculator import TokenCalculator

    calculator = TokenCalculator()

    len_tokens = calculator.tokenize(text, return_tokens=False)

    kwargs["guidance"] = (
        "Following SynthLang, translate the provided text into SynthLang syntax. "
        "Shrink the token size by 60-85%. Return only the translated text.\n\n"
        + kwargs.get("guidance", "")
    )

    out = await branch.chat(
        instruction=f"Converts the given text into SynthLang's hyper-efficient format.",
        context="Text to convert:\n\n" + text,
        **kwargs,
    )
    if sys1:
        branch.msgs.add_message(system=sys1)

    len_ = calculator.tokenize(out, return_tokens=False)
    if verbose:
        msg = ""
        msg += f"Compression Method: SynthLang\n"
        msg += f"Compressed Token number: {len_}\n"
        msg += f"Token Compression Ratio: {len_ / len_tokens:.1%}\n"
        msg += f"Compression Time: {timer() - start:.03f} seconds\n"
        msg += f"Compression Model: {branch.chat_model.model_name}\n"
        print(msg)

    return out
