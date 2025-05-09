#!/bin/bash
# Wrapper script for multi-tenant KST

# Activate the virtual environment and run KST with any arguments passed
source /Users/robbybarnes/GitHub/kst/venv/bin/activate
/Users/robbybarnes/GitHub/kst/venv/bin/kst "$@"