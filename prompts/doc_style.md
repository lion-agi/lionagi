Use this as the single source of truth for any project contributor writing or updating documentation.

Table of Contents
	1.	General Principles
	2.	Tone & Wording
	3.	Documentation Format & Organization
	4.	Docstring Conventions
	•	4.1. High-Level Python Docstring Standards
	•	4.2. NumPy/Pandas Style Docstring Format
	•	4.3. Examples of Method & Class Docstrings
	5.	Cross-References & Linking
	6.	Styling & Layout
	•	6.1. Page Layout & Margins
	•	6.2. Fonts & Color
	•	6.3. Headings & Hierarchy
	7.	Content Structure
	•	7.1. Module-Level Documentation
	•	7.2. Class & Function Documentation
	•	7.3. Inline Explanations & Code Blocks
	8.	Consistent Language & Terminology
	9.	Handling Errors, Exceptions, & Edge Cases
	10.	Examples & Sample Outputs
	11.	Release Notes & Changelog
	12.	Concluding Notes

1. General Principles
	1.	Consistency: All documentation (docstrings, reST files, Markdown guides) should follow the conventions in this guide. This ensures that docs are easy to navigate and maintain.
	2.	Clarity: Prioritize clarity over brevity. Write in plain, understandable English, especially for public-facing references.
	3.	Accuracy: Keep descriptions accurate and up to date with code changes. Avoid speculation or unverified examples.
	4.	Conciseness: Although clarity is important, docstrings and references should not be overly wordy. Avoid duplicating content unnecessarily; cross-reference instead.
	5.	Professional Tone: Use a neutral, instructional, and professional voice. Avoid slang or overly informal language.

2. Tone & Wording
	•	Tone:
	•	Aim for a direct and guiding tone, as if you are instructing a fellow engineer or data scientist.
	•	Avoid casual phrases like “just do X.” Instead, use more precise language such as “use the X function to achieve …”.
	•	Wording:
	•	Use active voice whenever possible (e.g., “Call validate() to check input” rather than “validate() is called to check input”).
	•	Prefer short sentences. Complex constructs can be broken up to improve readability.
	•	Avoid ambiguous pronouns (“it,” “this,” “that”) without clear references.
	•	Jargon:
	•	Introduce specialized terms or acronyms only if necessary.
	•	Provide a succinct definition the first time a new term appears.

3. Documentation Format & Organization

We rely on reStructuredText (reST) for Sphinx-generated documentation. Some sections (like READMEs or tutorials) may use Markdown.
	•	Module Docs: Each module should have a top-level docstring or an accompanying .rst file explaining its purpose, main classes/functions, and usage context.
	•	Class Docs: Each class should have a docstring describing its purpose, attributes, and how it typically interacts with other classes.
	•	Function/Method Docs: Each should explain the parameters, return values, raised exceptions, and usage examples where relevant.

To keep these consistent, we use Google style docstrings for functions and classes.

4. Docstring Conventions

4.1. High-Level Python Docstring Standards
	•	Adhere to PEP 257 (Python Docstring Conventions).
	•	Triple quotes (""") for docstring blocks, with a one-line summary followed by a blank line, then more detail if needed.
	•	Use Google style for function and class docstrings.

Example minimal docstring:

def my_function(arg1, arg2):
    """One-line summary of what my_function does.

    More descriptive text that covers details such as usage, side effects,
    or other clarifications. If not needed, keep docstring minimal.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value
    """
    pass

4.2. Google Style Docstring Format

For all functions and classes, we use Google style docstrings. The key sections are:
	1.	Short Summary
	2.	Extended Summary (optional)
	3.	Args
	4.	Returns or Yields
	5.	Raises
	6.	Note (optional)
	7.	Examples (optional)

Example:

def compute_stats(data, axis=0):
    """Compute descriptive statistics for the input data.

    This function calculates mean, standard deviation, and optionally 
    other metrics across the specified axis.

    Args:
        data: Input dataset.
        axis: Axis along which the statistics are computed. Defaults to 0.

    Returns:
        Dictionary containing keys 'mean' and 'std', each mapped to floats 
        or arrays of floats (depending on input shape).

    Raises:
        ValueError: If `data` cannot be converted to a numeric array.
    
    Examples:
        >>> import numpy as np
        >>> arr = np.array([[1, 2], [3, 4]])
        >>> compute_stats(arr, axis=1)
        {'mean': array([1.5, 3.5]), 'std': array([0.5, 0.5])}
    """
    pass

4.3. Examples of Method & Class Docstrings

For classes, include:
	•	Short description of the class's purpose.
	•	Attributes: List them in a NumPy-style “Attributes” section or mention in constructor docstring.
	•	Public methods can each follow the format above with “Parameters,” “Returns,” “Raises,” etc.

class DataContainer:
    """
    Stores dataset in memory with lazy-loaded metadata.

    Attributes
    ----------
    data : array-like
        Main dataset array.
    metadata : dict
        Dictionary storing metadata such as column names or data source info.

    Methods
    -------
    load_data(source):
        Reads data from a given source into memory.
    """

    def __init__(self, data, metadata=None):
        """
        Initialize the DataContainer with data and optional metadata.

        Parameters
        ----------
        data : array-like
            The data array to store.
        metadata : dict, optional
            A dictionary providing details about the data.
        """
        self.data = data
        self.metadata = metadata or {}

5. Cross-References & Linking
	•	Use inline cross-references sparingly. For example, in reST:

See also :class:`lionagi.protocols.generic.pile.Pile` for a concurrency-safe collection.


	•	Cross-reference key concepts from other modules or major classes. Avoid linking every mention of a class to avoid clutter. The rule of thumb: link the first mention in a section.
	•	For configuration references, link to relevant sections. For instance, “See Configuration Options_ for advanced usage.”

6. Styling & Layout

6.1. Page Layout & Margins
	•	In Sphinx output:
	•	The default theme margins (Read the Docs or Sphinx default) are sufficient. We do not apply custom margins for standard reST references.
	•	For PDF output, use the default LaTeX margins unless the design team specifies otherwise.

6.2. Fonts & Color
	•	Fonts: Rely on the Sphinx theme defaults (e.g., standard sans-serif for headings, monospace for code blocks). Avoid custom fonts for the official docs.
	•	Colors: Use standard Python/syntax highlighting from Pygments or the theme's built-in styles. Avoid custom color coding in docstrings or references unless absolutely necessary (e.g., emphasis in a table).

6.3. Headings & Hierarchy
	•	Maintain a consistent heading hierarchy in .rst files:
	•	# with overline for the top-level doc title
	•	= characters for major sections
	•	- characters for subsections
	•	~ or ^ for sub-subsections

Example:

======================================
Major Title
======================================

Subsection
----------

Sub-subsection
^^^^^^^^^^^^^^

7. Content Structure

7.1. Module-Level Documentation
	•	At the top of each module's .rst or docstring, explain the purpose of the module, key classes or functions, and a simple usage note.
	•	Provide references to deeper classes or method docs below or cross-reference them.

7.2. Class & Function Documentation
	•	Classes generally get an overview docstring plus separate docstrings on each public method.
	•	Private or “internal” methods (like _helper_function) can have shorter docstrings or remain undocumented if not user-facing.

7.3. Inline Explanations & Code Blocks
	•	Use code blocks for usage samples or short code snippets.
	•	Keep them minimal yet illustrative; do not show massive code if a 3-line snippet suffices.

8. Consistent Language & Terminology
	•	Use the same terms for the same concepts throughout the project. For example:
	•	“metadata,” “configuration,” “manager,” “observer,” etc.
	•	Document these terms in a glossary if needed.
	•	For concurrency or async references, remain consistent with “asynchronous,” “async,” “await,” etc.

9. Handling Errors, Exceptions, & Edge Cases
	•	Document known exceptions in the Raises section of the docstring.
	•	For complex error-handling logic, add a note or short example clarifying the scenario (only if it's highly relevant and can be shown succinctly).

10. Examples & Sample Outputs
	•	Keep examples factual and testable. Avoid showing code that doesn't exist or cannot be inferred from the current context.
	•	If the function is easily tested in a Python shell, provide a short >>> example.
	•	For classes, show minimal usage, focusing on the constructor or key methods.

11. Release Notes & Changelog
	•	Use a separate file such as CHANGELOG.rst or docs/source/release_notes.rst to outline new features, bug fixes, and version changes.
	•	Keep the style consistent with the rest of the docs.
	•	Reference relevant modules or classes using cross-links when describing changes.

12. Concluding Notes
	•	This style guide must be reviewed periodically, especially if new doc generators or new theming options are introduced.
	•	Any major additions to the codebase (e.g., a new “Manager” or “Observer” type) should include docstrings, reST references, and examples consistent with these guidelines.
	•	Contributors should be encouraged to update the docs alongside code changes, ensuring everything stays in sync.

Final Checklist
	1.	Docstrings match the NumPy style (or, if simpler, PEP 257 minimal style).
	2.	Links to relevant classes or modules are included but not overused.
	3.	Examples are valid, minimal, and show typical usage.
	4.	Styling adheres to standard Sphinx theming for consistency (no excessive custom color, fonts, or margin changes).
	5.	Language is clear, direct, and unambiguous.
