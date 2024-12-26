import re

def escape_markdown(text: str) -> str:
    """
    Escape special characters for Markdown V2 formatting.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

