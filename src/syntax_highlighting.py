from idlelib.colorizer import ColorDelegator
from idlelib.percolator import Percolator
import re

# Define syntax highlighting rules for different programming languages
SYNTAX_RULES = {
    "python": {
        "keywords": r'\b(class|def|return|import|from|as|if|else|elif|for|while|try|except|finally|with|yield|lambda|assert|break|continue|del|pass|raise)\b',
        "comments": r'#.*',
        "strings": r'(\".*?\"|\'.*?\')'
    },
    "java": {
        "keywords": r'\b(public|private|protected|class|static|void|int|String|new|return|if|else|for|while|try|catch|finally|import|package|extends|implements|interface)\b',
        "comments": r'(//.*|/\*[\s\S]*?\*/)',
        "strings": r'(\".*?\"|\'.*?\')'
    },
    "javascript": {
        "keywords": r'\b(var|let|const|function|return|if|else|for|while|class|new|import|export|try|catch|finally|async|await|switch|case|default|break|continue)\b',
        "comments": r'(//.*|/\*[\s\S]*?\*/)',
        "strings": r'(\".*?\"|\'.*?\`)'
    },
    "c": {
        "keywords": r'\b(int|char|float|double|void|if|else|for|while|return|switch|case|break|continue|typedef|struct|union|enum|static|const|sizeof|include|define)\b',
        "comments": r'(//.*|/\*[\s\S]*?\*/)',
        "strings": r'(\".*?\"|\'.*?\')'
    },
    "cpp": {
        "keywords": r'\b(class|public|private|protected|virtual|override|new|delete|this|namespace|template|typename|using|auto|static|const|sizeof|return|if|else|for|while|switch|case|break|continue)\b',
        "comments": r'(//.*|/\*[\s\S]*?\*/)',
        "strings": r'(\".*?\"|\'.*?\')'
    }
}

# Mapping file extensions to programming languages
FILE_EXTENSION_MAP = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp"
}

def detect_language(filename):
    """Detect programming language based on file extension."""
    ext = filename.split('.')[-1]
    return FILE_EXTENSION_MAP.get(f".{ext}", "plaintext")  # Default to plaintext if unknown


def apply_syntax_highlighting(text_widget, filename):
    """Apply syntax highlighting based on the detected programming language."""
    language = detect_language(filename)
    rules = SYNTAX_RULES.get(language)

    if not rules:
        return  # No highlighting if language is unknown

    syntax = ColorDelegator()

    # Compile regex patterns for syntax elements
    keyword_pattern = re.compile(rules["keywords"])
    comment_pattern = re.compile(rules["comments"])
    string_pattern = re.compile(rules["strings"])

    # Define syntax colors
    syntax.tagdefs.update({
        'KEYWORD': {'foreground': '#00507F', 'font': 'bold'},
        'COMMENT': {'foreground': 'green'},
        'STRING': {'foreground': '#A65E17'}
    })

    def highlight_text():
        """Apply syntax highlighting on text."""
        text_widget.tag_remove("KEYWORD", "1.0", "end")
        text_widget.tag_remove("COMMENT", "1.0", "end")
        text_widget.tag_remove("STRING", "1.0", "end")

        text_content = text_widget.get("1.0", "end-1c")

        for match in keyword_pattern.finditer(text_content):
            start, end = match.span()
            text_widget.tag_add("KEYWORD", f"1.{start}", f"1.{end}")

        for match in comment_pattern.finditer(text_content):
            start, end = match.span()
            text_widget.tag_add("COMMENT", f"1.{start}", f"1.{end}")

        for match in string_pattern.finditer(text_content):
            start, end = match.span()
            text_widget.tag_add("STRING", f"1.{start}", f"1.{end}")

    Percolator(text_widget).insertfilter(syntax)
    text_widget.bind("<KeyRelease>", lambda e: highlight_text())  # Re-highlight on key press
