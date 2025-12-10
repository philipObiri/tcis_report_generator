# Recalculate Scores Management Command

## Overview
This Django management command recalculates all student scores, exam calculations (70%), total scores, grades, and GPAs for every student in the TCIS Academic Report System.

## Purpose
- Fix existing data after implementing the 70% exam score calculation
- Ensure all GPAs are accurate across all report types
- Update student_scores relationships in all reports
- Maintain data integrity across the system

## Command Syntax

### Preview Changes (Dry Run)
```bash
python manage.py recalculate_scores --dry-run
```
This will show you what changes will be made WITHOUT saving them to the database.

### Apply Changes (Live Mode)
```bash
python manage.py recalculate_scores
```
This will recalculate and SAVE all changes to the database.

## What Gets Recalculated

### 1. Individual Score Records
For every score record in the database:
- **Continuous Assessment**: Recalculated as 30% of normalized CA components
- **Total Score**: Recalculated as CA (30%) + Exam (70%)
- **Grade**: Reassigned based on the new total score
- All changes are saved to the Score table

### 2. End of Term Reports (Academic Reports)
- GPA recalculated using the calculate_gpa() utility
- student_scores many-to-many relationship updated
- Only includes subjects assigned to each student

### 3. Midterm Reports
- GPA recalculated from midterm_score values
- student_scores relationship updated

### 4. Mock Reports
- GPA recalculated from mock_score values
- student_scores relationship updated

### 5. Progressive Test 1 Reports
- GPA recalculated from progressive_test_1_score values
- student_scores relationship updated

### 6. Progressive Test 2 Reports
- GPA recalculated from progressive_test_2_score values
- student_scores relationship updated

## Output Explanation

The command provides detailed output:

```
======================================================================
LIVE MODE - All changes will be saved to database
======================================================================

Step 1: Recalculating all exam scores and totals...
  Progress: 150/500 scores processed (30.0%)
  Progress: 300/500 scores processed (60.0%)
  Progress: 500/500 scores processed (100.0%)
✓ Recalculated 500 scores

Step 2: Recalculating Academic Report GPAs (End of Term)...
  Updated: John Doe - Term 1 (GPA: 3.45 → 3.52)
  Updated: Jane Smith - Term 2 (GPA: 2.89 → 2.95)
✓ Updated 150 Academic Reports

[... steps 3-6 continue ...]

======================================================================
RECALCULATION COMPLETE
======================================================================

Total Students in System: 150
Individual Scores Recalculated: 500
Academic Reports (End of Term) Updated: 150
Midterm Reports Updated: 120
Mock Reports Updated: 80
Progressive Test 1 Reports Updated: 100
Progressive Test 2 Reports Updated: 95

All changes have been saved to the database!
```

## Safety Features

### 1. Dry Run Mode
- Use `--dry-run` flag to preview changes
- No data is modified
- Transaction is rolled back at the end
- Safe to run multiple times

### 2. Transaction Safety
- All operations run within a database transaction
- If any error occurs, ALL changes are rolled back
- Database remains in consistent state

### 3. Progress Tracking
- Real-time progress updates every 50 scores
- See exactly what's being changed
- Monitor for any unexpected behavior

## When to Run This Command

### Required
- **Immediately after deployment** of the 70% exam score fix
- After bulk score imports from external systems

### Recommended
- At the end of each term to ensure data consistency
- Before generating final report cards
- After any major system updates

### Optional
- As part of regular system maintenance
- When investigating data inconsistencies
- Before database backups

## Step-by-Step Usage

### First Time (After Deployment)

1. **Test with Dry Run**:
   ```bash
   python manage.py recalculate_scores --dry-run
   ```
   Review the output to see what will change.

2. **Create Database Backup**:
   ```bash
   # Example for PostgreSQL
   pg_dump your_database > backup_before_recalc.sql

   # Example for SQLite
   cp db.sqlite3 db.sqlite3.backup
   ```

3. **Run Live Mode**:
   ```bash
   python manage.py recalculate_scores
   ```

4. **Verify Results**:
   - Check a few student reports manually
   - Verify GPAs are correct
   - Confirm exam scores display as 70%

### Routine Maintenance

For regular maintenance, dry run is optional:
```bash
python manage.py recalculate_scores
```

## Troubleshooting

### Command Not Found
**Error**: `Unknown command: 'recalculate_scores'`

**Solution**:
- Ensure the management command files are in the correct location:
  ```
  reports/
    management/
      __init__.py
      commands/
        __init__.py
        recalculate_scores.py
  ```
- Verify `reports` is in INSTALLED_APPS in settings.py

### Permission Errors
**Error**: Database permission denied

**Solution**:
- Run with appropriate user permissions
- Check database connection settings

### Out of Memory
**Error**: Memory error with large datasets

**Solution**:
- The command uses select_related() for optimization
- For very large databases (100k+ scores), consider:
  - Running during off-peak hours
  - Increasing server memory
  - Running on a database replica

## Performance

### Expected Duration
- Small system (< 100 students): ~30 seconds
- Medium system (100-500 students): 1-3 minutes
- Large system (500-1000 students): 3-10 minutes
- Very large system (1000+ students): 10+ minutes

### Database Impact
- Read-heavy operation
- Bulk updates at the end
- Uses transactions for safety
- Minimal table locking

## Technical Details

### Database Queries
- Uses select_related() to minimize queries
- Bulk fetching of related objects
- Single transaction for all updates

### Memory Usage
- Processes scores in batches
- Progress updates every 50 records
- Optimized for memory efficiency

### Logging
- All output goes to stdout
- Progress displayed in real-time
- Summary statistics at completion

## Support

For issues or questions:
1. Check the main Updates.md file
2. Review Django logs
3. Verify database connections
4. Test with --dry-run first

## Version History

- **v1.0** (2025-12-10): Initial release
  - Recalculates all scores and GPAs
  - Supports dry-run mode
  - Includes progress tracking and statistics
