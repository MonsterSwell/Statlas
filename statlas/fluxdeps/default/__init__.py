"""
    Selection of tags and filters that one usually would want to be accessible.
    In order to ensure that this is in fact the case, add the following code
    to your project (assuming the project is called `project`)::
    
        # Load default tags and filter
        from django.template import add_to_builtins
        add_to_builtins('project.fluxbase.default.templatetags.filters')
"""