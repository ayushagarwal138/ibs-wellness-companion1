#!/usr/bin/env python3
"""
Script to generate a test JWT token for API testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import create_access_token

# Create a token for an existing user
token_data = {
    "sub": "51ddae36-5b4c-4dcb-b6db-9992b5b4de31",  # existing user ID
    "email": "test4@example.com"
}

token = create_access_token(token_data)
print(f"Test token: {token}")