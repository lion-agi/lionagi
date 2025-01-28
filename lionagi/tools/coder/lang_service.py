"""
Language service for code analysis and manipulation.
Provides syntax parsing, linting, and semantic analysis.
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field


class SymbolKind(str, Enum):
    """Symbol types in code."""

    FILE = "file"
    MODULE = "module"
    NAMESPACE = "namespace"
    PACKAGE = "package"
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    VARIABLE = "variable"
    CONSTANT = "constant"
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    KEY = "key"
    NULL = "null"
    IMPORT = "import"
    TYPE = "type"
    PARAMETER = "parameter"


class DiagnosticSeverity(str, Enum):
    """Severity levels for diagnostics."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class Position(BaseModel):
    """
    Position in source code.

    Attributes:
        line: Zero-based line number
        character: Zero-based character offset
    """

    line: int = Field(..., ge=0)
    character: int = Field(..., ge=0)


class Range(BaseModel):
    """
    Range in source code.

    Attributes:
        start: Start position
        end: End position
    """

    start: Position
    end: Position


class Location(BaseModel):
    """
    Location in source code.

    Attributes:
        uri: Source file URI
        range: Position range
    """

    uri: str
    range: Range


class Diagnostic(BaseModel):
    """
    Code diagnostic (error, warning, etc).

    Attributes:
        range: Affected code range
        severity: Issue severity
        code: Error code
        source: Diagnostic source
        message: Description
    """

    range: Range
    severity: DiagnosticSeverity
    code: Optional[str] = None
    source: str
    message: str


class Symbol(BaseModel):
    """
    Code symbol information.

    Attributes:
        name: Symbol name
        kind: Symbol type
        range: Symbol range in code
        location: Symbol definition location
        container: Container symbol name
    """

    name: str
    kind: SymbolKind
    range: Range
    location: Location
    container: Optional[str] = None


class LanguageService:
    """
    Code analysis service with support for multiple languages.

    Features:
    - Syntax parsing
    - Linting
    - Symbol lookup
    - Type checking
    - Cross-references
    """

    def __init__(self):
        self._parsers: Dict[str, Any] = {}
        self._symbol_cache: Dict[str, List[Symbol]] = {}
        self._diagnostic_cache: Dict[str, List[Diagnostic]] = {}

    def register_parser(self, language: str, parser: Any) -> None:
        """Register parser for language."""
        self._parsers[language] = parser

    async def parse_file(
        self, path: Path, language: Optional[str] = None
    ) -> Any:
        """
        Parse source file.

        Args:
            path: Source file path
            language: Optional language override

        Returns:
            AST or parse tree
        """
        if not language:
            language = self._detect_language(path)

        parser = self._get_parser(language)
        return await parser.parse_file(path)

    async def parse_text(self, text: str, language: str) -> Any:
        """
        Parse source text.

        Args:
            text: Source code text
            language: Source language

        Returns:
            AST or parse tree
        """
        parser = self._get_parser(language)
        return await parser.parse_text(text)

    async def get_symbols(
        self, path: Path, refresh: bool = False
    ) -> List[Symbol]:
        """
        Get symbols defined in file.

        Args:
            path: Source file path
            refresh: Force cache refresh

        Returns:
            List of symbols
        """
        uri = str(path)
        if uri in self._symbol_cache and not refresh:
            return self._symbol_cache[uri]

        language = self._detect_language(path)
        parser = self._get_parser(language)

        symbols = await parser.get_symbols(path)
        self._symbol_cache[uri] = symbols
        return symbols

    async def get_diagnostics(
        self, path: Path, refresh: bool = False
    ) -> List[Diagnostic]:
        """
        Get diagnostics for file.

        Args:
            path: Source file path
            refresh: Force cache refresh

        Returns:
            List of diagnostics
        """
        uri = str(path)
        if uri in self._diagnostic_cache and not refresh:
            return self._diagnostic_cache[uri]

        language = self._detect_language(path)
        parser = self._get_parser(language)

        diagnostics = await parser.get_diagnostics(path)
        self._diagnostic_cache[uri] = diagnostics
        return diagnostics

    async def find_references(
        self, path: Path, position: Position
    ) -> List[Location]:
        """
        Find symbol references.

        Args:
            path: Source file path
            position: Symbol position

        Returns:
            List of reference locations
        """
        language = self._detect_language(path)
        parser = self._get_parser(language)
        return await parser.find_references(path, position)

    async def get_definition(
        self, path: Path, position: Position
    ) -> Optional[Location]:
        """
        Get symbol definition.

        Args:
            path: Source file path
            position: Symbol position

        Returns:
            Symbol definition location
        """
        language = self._detect_language(path)
        parser = self._get_parser(language)
        return await parser.get_definition(path, position)

    async def get_hover(self, path: Path, position: Position) -> Optional[str]:
        """
        Get hover information.

        Args:
            path: Source file path
            position: Hover position

        Returns:
            Hover text if available
        """
        language = self._detect_language(path)
        parser = self._get_parser(language)
        return await parser.get_hover(path, position)

    def _detect_language(self, path: Path) -> str:
        """Detect language from file extension."""
        ext = path.suffix.lower()
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".cs": "csharp",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".m": "objective-c",
            ".mm": "objective-c",
        }
        return ext_to_lang.get(ext, "text")

    def _get_parser(self, language: str) -> Any:
        """Get parser for language."""
        if language not in self._parsers:
            raise ValueError(f"No parser registered for {language}")
        return self._parsers[language]


class PythonParser:
    """Python source code parser."""

    async def parse_file(self, path: Path) -> ast.AST:
        """Parse Python source file."""
        with open(path) as f:
            return ast.parse(f.read(), str(path))

    async def parse_text(self, text: str) -> ast.AST:
        """Parse Python source text."""
        return ast.parse(text)

    async def get_symbols(self, path: Path) -> List[Symbol]:
        """Get Python symbols."""
        tree = await self.parse_file(path)
        visitor = SymbolVisitor(str(path))
        visitor.visit(tree)
        return visitor.symbols

    async def get_diagnostics(self, path: Path) -> List[Diagnostic]:
        """Get Python diagnostics."""
        try:
            await self.parse_file(path)
        except SyntaxError as e:
            # Convert syntax error to diagnostic
            return [
                Diagnostic(
                    range=Range(
                        start=Position(
                            line=e.lineno - 1, character=e.offset - 1
                        ),
                        end=Position(line=e.lineno - 1, character=e.offset),
                    ),
                    severity=DiagnosticSeverity.ERROR,
                    code="SyntaxError",
                    source="python",
                    message=str(e),
                )
            ]
        return []


class SymbolVisitor(ast.NodeVisitor):
    """AST visitor to collect Python symbols."""

    def __init__(self, uri: str):
        self.uri = uri
        self.symbols: List[Symbol] = []
        self.scope_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definition."""
        self.add_symbol(node, SymbolKind.CLASS)
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition."""
        kind = SymbolKind.METHOD if self.scope_stack else SymbolKind.FUNCTION
        self.add_symbol(node, kind)
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def add_symbol(
        self, node: Union[ast.ClassDef, ast.FunctionDef], kind: SymbolKind
    ):
        """Add symbol from AST node."""
        self.symbols.append(
            Symbol(
                name=node.name,
                kind=kind,
                range=Range(
                    start=Position(
                        line=node.lineno - 1, character=node.col_offset
                    ),
                    end=Position(
                        line=node.end_lineno - 1, character=node.end_col_offset
                    ),
                ),
                location=Location(
                    uri=self.uri,
                    range=Range(
                        start=Position(
                            line=node.lineno - 1, character=node.col_offset
                        ),
                        end=Position(
                            line=node.end_lineno - 1,
                            character=node.end_col_offset,
                        ),
                    ),
                ),
                container=self.scope_stack[-1] if self.scope_stack else None,
            )
        )
