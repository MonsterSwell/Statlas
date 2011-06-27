from markupfield import MarkupField, MarkupContent, MarkupInput

import markdown

class MarkdownInput(MarkupInput):
    """Input field for MarkDown content"""
    pass

class MarkdownField(MarkupField):
    """TextField that automatically buffers the content that has been processed by markdown."""
    def process_markup(self, value):
        return markdown.markdown(value)
    
    markupInputClass = MarkdownInput
  
class MarkdownContent(MarkupContent):
    """Markdown content."""
    def __init__(self, raw, rendered = None):
        super(MarkdownContent, self).__init__(raw, markdown.markdown, rendered)
        
HAS_SOUTH = True
try:
    from south.modelsinspector import add_introspection_rules
except ImportError as exp:
    HAS_SOUTH = False

if HAS_SOUTH:
    add_introspection_rules(
        patterns = [r'^fluxbase\.fields.\markdownfield\.MarkdownField$']
    )