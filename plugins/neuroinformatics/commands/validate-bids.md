---
description: Validate a BIDS dataset and fix common issues
argument-hint: <dataset-path>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# BIDS Validation

Validate a BIDS dataset and provide fixes for any issues found.

## Process

### 1. Locate Dataset
!echo "Dataset: $ARGUMENTS"
!ls "$ARGUMENTS/dataset_description.json" 2>/dev/null || echo "No dataset_description.json found"

### 2. Run Validation
Invoke the bids-validator agent to autonomously validate, diagnose, and fix issues.

### 3. Report
Present validation results with fixes applied and remaining issues.
