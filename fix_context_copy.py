"""
Fix for Django 4.2.29 + Python 3.14 compatibility issue with Context.__copy__()
This monkey patch addresses the AttributeError when copying RequestContext objects.

Python 3.14 changed how super() objects work - they no longer allow arbitrary 
attribute assignment. Django 4.2.29's Context.__copy__() method tries to do this,
causing: "AttributeError: 'super' object has no attribute 'dicts' and no __dict__"
"""

import sys
from copy import copy as _copy
from django.template.context import BaseContext

# Store the original __copy__ method
_original_copy = BaseContext.__copy__

def _patched_copy(self):
    """
    Patched version of BaseContext.__copy__ that works with Python 3.14
    
    Instead of using super() and setting attributes on it, we create a new 
    instance directly and copy all necessary attributes.
    """
    try:
        # Create a new instance of the same class
        duplicate = self.__class__.__new__(self.__class__)
        
        # Copy the main 'dicts' attribute (core of Context)
        if hasattr(self, 'dicts'):
            duplicate.dicts = self.dicts[:]
        
        # Copy template attribute (required in render method)
        if hasattr(self, 'template'):
            duplicate.template = self.template
        
        # For RequestContext, we need to handle the request and other attrs
        if hasattr(self, '_request'):
            duplicate._request = self._request
        
        # Copy any auth-related attributes and other context attributes
        for attr in ('_auth_user_backend', '_is_auth_request', '_auth_user_id', 
                     '_auth_user_hash', 'user', '_processor_index', 'autoescape', 
                     'use_tz', 'use_l10n', 'use_i18n', 'timezone', 'exception_processor'):
            if hasattr(self, attr):
                try:
                    setattr(duplicate, attr, getattr(self, attr))
                except (AttributeError, TypeError):
                    # Some attributes might not be settable, skip them
                    pass
        
        return duplicate
        
    except Exception as e:
        # Fallback: try the original method if our patch fails
        print(f"Warning: Context copy patch failed ({e}), using original")
        try:
            return _original_copy(self)
        except:
            # Last resort: create a minimal copy
            duplicate = self.__class__.__new__(self.__class__)
            if hasattr(self, 'dicts'):
                duplicate.dicts = self.dicts[:]
            if hasattr(self, 'template'):
                duplicate.template = self.template
            # Try to copy common attributes
            for attr in ('autoescape', 'use_tz', 'use_l10n', 'use_i18n'):
                if hasattr(self, attr):
                    try:
                        setattr(duplicate, attr, getattr(self, attr))
                    except:
                        pass
            return duplicate

# Apply the monkey patch
BaseContext.__copy__ = _patched_copy

print("[OK] Django 4.2.29 + Python 3.14 compatibility patch applied")

