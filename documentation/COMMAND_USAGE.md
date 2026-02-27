# Management Command: Recalculate All Scores

## Quick Start Guide

### What This Command Does
Automatically recalculates ALL scores and GPAs for EVERY student in your system:
- ✅ Applies the 70% exam score calculation to all existing records
- ✅ Updates total scores and grades for all students
- ✅ Recalculates GPAs across all report types (End of Term, Midterm, Mock, Progressive Tests)
- ✅ Fixes any data inconsistencies
- ✅ Saves all changes to the database

---

## How to Use

### Option 1: Preview Changes (Safe - No Changes Saved)
```bash
python manage.py recalculate_scores --dry-run
```
Use this to see what will change before actually saving anything.

### Option 2: Apply Changes (Updates Database)
```bash
python manage.py recalculate_scores
```
This will recalculate and save all changes for every student.

---

## When to Run This Command

### ✅ YOU SHOULD RUN THIS NOW
Since we just fixed the 70% exam score calculation, you should run this command to update all existing student records.

**Recommended Steps:**
1. First, run with `--dry-run` to preview:
   ```bash
   python manage.py recalculate_scores --dry-run
   ```

2. Then run without the flag to apply changes:
   ```bash
   python manage.py recalculate_scores
   ```

### Future Use Cases
- After importing scores from external systems
- At the end of each term (maintenance)
- When you notice data inconsistencies
- Before generating final report cards

---

## What You'll See

The command shows detailed progress:

```
======================================================================
LIVE MODE - All changes will be saved to database
======================================================================

Step 1: Recalculating all exam scores and totals...
  Progress: 100/200 scores processed (50.0%)
  Progress: 200/200 scores processed (100.0%)
✓ Recalculated 200 scores

Step 2: Recalculating Academic Report GPAs (End of Term)...
  Updated: John Doe - Term 1 (GPA: 3.45 → 3.52)
✓ Updated 50 Academic Reports

Step 3: Recalculating Midterm Report GPAs...
✓ Updated 40 Midterm Reports

Step 4: Recalculating Mock Report GPAs...
✓ Updated 30 Mock Reports

Step 5: Recalculating Progressive Test 1 GPAs...
✓ Updated 35 Progressive Test 1 Reports

Step 6: Recalculating Progressive Test 2 GPAs...
✓ Updated 35 Progressive Test 2 Reports

======================================================================
RECALCULATION COMPLETE
======================================================================

Total Students in System: 50
Individual Scores Recalculated: 200
Academic Reports (End of Term) Updated: 50
Midterm Reports Updated: 40
Mock Reports Updated: 30
Progressive Test 1 Reports Updated: 35
Progressive Test 2 Reports Updated: 95

All changes have been saved to the database!
```

---

## Safety Features

✅ **Transaction Safety**: If anything goes wrong, all changes are automatically rolled back

✅ **Dry Run Mode**: Preview changes before applying them

✅ **Progress Tracking**: See real-time progress as the command runs

✅ **Change Logging**: See which GPAs changed and by how much

---

## Examples

### Example 1: Preview What Will Change
```bash
python manage.py recalculate_scores --dry-run
```
**Result**: Shows you all changes but doesn't save anything

### Example 2: Apply Changes to Live Database
```bash
python manage.py recalculate_scores
```
**Result**: Recalculates and saves everything

---

## File Locations

The management command files are located at:
```
reports/
  management/
    __init__.py
    commands/
      __init__.py
      recalculate_scores.py  ← Main command file
      README.md              ← Detailed documentation
```

---

## Troubleshooting

### "Unknown command: 'recalculate_scores'"
**Solution**: Make sure the files are in the correct location (see above)

### Command takes too long
**Normal**: For 100+ students, this can take a few minutes. Be patient!

### Errors during execution
**Solution**: All changes are rolled back automatically. Check your database connection and try again.

---

## Need More Help?

📖 **Detailed Documentation**: See `reports/management/commands/README.md`

📋 **All Updates**: See `Updates.md` in the project root

---

## Summary

✅ **Created**: Management command to recalculate all scores
✅ **Updates**: Every student's scores, totals, grades, and GPAs
✅ **Covers**: All report types (End of Term, Midterm, Mock, Progressive Tests)
✅ **Safe**: Includes dry-run mode and transaction safety
✅ **Ready**: Run it now to fix all existing data!

**Run this command now:**
```bash
# First preview
python manage.py recalculate_scores --dry-run

# Then apply
python manage.py recalculate_scores
```
