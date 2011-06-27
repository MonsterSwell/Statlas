
"""
Django-config settings loader.
"""

import os

CONFIG_IDENTIFIER = os.getenv("CONFIG_IDENTIFIER")


# Import defaults
from config.base import *

# Import overrides
overrides = __import__(
    "config." + CONFIG_IDENTIFIER,
    globals(),
    locals(),
    ["config"]
)

# Apply imported overrides
for attribute in dir(overrides):
    # We only want to import settings (which have to be variables in ALLCAPS)
    if attribute.isupper():
        # Update our scope with the imported variables. We use globals() instead of locals()
        # Because locals() is readonly and it returns a copy of itself upon assignment.
        globals()[attribute] = getattr(overrides, attribute)

