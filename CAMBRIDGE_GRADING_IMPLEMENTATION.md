# Cambridge Grading System Implementation

## Overview

The TCIS Academic Report Generator now supports **two grading systems**:
1. **Standard Grading System** (default, existing)
2. **Cambridge Grading System** (new)

This implementation allows subjects to use different grading systems simultaneously, with automatic calculation of continuous assessment based on the selected system.

---

## Key Changes Made

### 1. Database Model Updates

#### Subject Model (`reports/models.py:51-70`)
- Added `grading_system` field with choices: `'standard'` or `'cambridge'`
- Default: `'standard'` (maintains backward compatibility)
- Allows per-subject grading system configuration

#### Score Model (`reports/models.py:123-162`)
- Updated `save()` method to detect subject's grading system
- Implements dual calculation logic:
  - **Standard**: Equal weighting of all CA components
  - **Cambridge**: Weighted components with scaled percentages

---

## Cambridge Grading System Specifications

### Component Weights (Scaled to 30% Total CA)

Based on your requirement to include Progressive Test 2 and maintain CA = 30%, the weights are:

| Component            | Original Weight | Scaled Weight | Score Input Range |
|----------------------|-----------------|---------------|-------------------|
| Classwork & Homework | 5%              | 3.75%         | 0-100% (as percentage) |
| Progressive Test 1   | 10%             | 7.5%          | 0-100% (as percentage) |
| Progressive Test 2   | 10%             | 7.5%          | 0-100% (as percentage) |
| Midterm Test         | 15%             | 11.25%        | 0-100% (as percentage) |
| **Total CA**         | **40%**         | **30%**       |                   |

### Calculation Formula

```
CA = (Classwork × 0.0375) + (PT1 × 0.075) + (PT2 × 0.075) + (Midterm × 0.1125)
```

### Final Grade

```
Total Score = CA (30%) + Exam (70%)
```

---

## Example Calculation

### Input Scores (as percentages):
- Classwork: 80%
- Progressive Test 1: 70%
- Progressive Test 2: 75%
- Midterm: 76%
- Final Exam: 85%

### Cambridge Calculation:
```
CA = (80 × 0.0375) + (70 × 0.075) + (75 × 0.075) + (76 × 0.1125)
CA = 3.00 + 5.25 + 5.625 + 8.55
CA = 22.425 (out of 30%)

Exam Contribution = 85 × 0.70 = 59.50

Total Score = 22.425 + 59.50 = 81.925
Rounded Total = 82

Grade = A (80-94 range)
```

---

## How to Use

### For Administrators

1. **Configure Subject Grading System:**
   - Go to Django Admin: `/admin/reports/subject/`
   - Edit a subject
   - Select "Grading System": Choose "Standard" or "Cambridge"
   - Save

2. **View Grading System in Scores:**
   - Go to Django Admin: `/admin/reports/score/`
   - New column "Grading System" shows which system applies
   - Filter scores by grading system

### For Teachers

**No change in score entry process:**
- Continue entering scores as percentages (0-100)
- The system automatically applies the correct calculation based on the subject's configuration
- Teachers don't need to know which grading system is being used

### For Students/Parents

**Reports now show:**
- Which grading system was used for each subject
- Cambridge subjects are highlighted in blue on reports
- Continuous Assessment (30%) is calculated correctly per system
- Final grades remain the same format (A*, A, B+, etc.)

---

## Files Modified

### Core Logic
1. `reports/models.py`
   - Subject model: Added `grading_system` field
   - Score model: Updated `save()` with dual calculation logic

2. `reports/forms.py`
   - ScoreForm: Removed duplicate calculation logic
   - Calculations now handled by model

3. `reports/utils.py`
   - Added `calculate_continuous_assessment()` utility function
   - Centralized calculation logic for reusability

### Admin Interface
4. `reports/admin.py`
   - SubjectAdmin: Shows grading system, added filter
   - ScoreAdmin: Shows grading system, made CA/total/grade readonly

### Templates
5. `templates/generated_report.html`
   - Added "Grading System" column to score table
   - Cambridge subjects highlighted in blue

### Database
6. `reports/migrations/0032_subject_grading_system.py`
   - Migration to add grading_system field
   - Applied successfully

### Testing
7. `test_cambridge_grading.py` (NEW)
   - Comprehensive test suite
   - Validates calculations for both systems
   - Tests edge cases

---

## Testing Results

All tests passed successfully:

### Test 1: Cambridge Example (without PT2)
- ✅ Calculation matches expected weighted results
- ✅ Scaled weights maintain 30% CA total

### Test 2: Cambridge with PT2 Included
- ✅ All four components calculated correctly
- ✅ CA = 22.42/30% for sample scores
- ✅ Final grade calculation accurate

### Test 3: Standard vs Cambridge Comparison
- ✅ Both systems produce valid results
- ✅ Difference is minimal for balanced scores
- ✅ Cambridge gives more weight to midterm

### Test 4: Edge Cases
- ✅ Perfect scores (100%) = 30/30 CA
- ✅ Zero scores (0%) = 0/30 CA
- ✅ Mixed scores calculated correctly

---

## Migration Guide

### For Existing Data

1. **All existing subjects default to "Standard" grading system**
   - No change in calculations for existing data
   - Backward compatible

2. **To switch a subject to Cambridge:**
   ```
   1. Go to Admin > Subjects
   2. Edit the subject
   3. Change "Grading System" to "Cambridge Grading System"
   4. Save
   ```

3. **Recalculate existing scores (if needed):**
   ```bash
   python manage.py shell

   from reports.models import Score
   # Get all scores for a specific subject
   scores = Score.objects.filter(subject__name='Mathematics')

   # Trigger recalculation by saving
   for score in scores:
       score.save()
   ```

---

## Comparison: Standard vs Cambridge

| Aspect                  | Standard System           | Cambridge System          |
|-------------------------|---------------------------|---------------------------|
| **Component Weighting** | Equal (all 25% each)      | Weighted (3.75%-11.25%)   |
| **Classwork Weight**    | 25% of CA                 | 12.5% of CA (3.75/30)     |
| **PT1 Weight**          | 25% of CA                 | 25% of CA (7.5/30)        |
| **PT2 Weight**          | 25% of CA                 | 25% of CA (7.5/30)        |
| **Midterm Weight**      | 25% of CA                 | 37.5% of CA (11.25/30)    |
| **Favors**              | Consistent performance    | Strong midterm performers |
| **Total CA**            | 30%                       | 30%                       |
| **Final Exam**          | 70%                       | 70%                       |

---

## Important Notes

### Score Entry
- **All scores are entered as percentages (0-100)**
- Teachers do NOT need to calculate raw scores (e.g., 16/20)
- If using Cambridge max scores (20, 30, 50), convert to percentage first:
  - Classwork: 16/20 = 80% → Enter **80**
  - PT1: 21/30 = 70% → Enter **70**
  - Midterm: 38/50 = 76% → Enter **76**

### Automatic Calculations
- CA, Total Score, and Grade are calculated automatically
- Read-only in admin (cannot be manually edited)
- Recalculated every time a score is saved

### Grading Scale
Both systems use the same grading scale:
- A*: 95-100
- A: 80-94
- B+: 75-79
- B: 70-74
- C+: 65-69
- C: 60-64
- D: 50-59
- E: 45-49
- F: 35-44
- Ungraded: 0-34

---

## Future Enhancements (Optional)

1. **Score Entry Helper:**
   - Add converter tool for raw scores → percentages
   - Show max score hints based on grading system

2. **Bulk Subject Configuration:**
   - Update multiple subjects to Cambridge at once
   - Import/export grading system configurations

3. **Historical Tracking:**
   - Log when grading system changes
   - Maintain calculation audit trail

4. **Custom Weight Configuration:**
   - Allow admin to customize Cambridge weights
   - Store weights in database instead of hardcoding

---

## Support

### For Questions
- Review this document
- Check `test_cambridge_grading.py` for calculation examples
- Inspect `reports/models.py` for implementation details

### For Issues
- Check score calculations in admin interface
- Verify subject grading system is set correctly
- Run test script: `python test_cambridge_grading.py`

---

## Summary

✅ **Implementation Complete**
- Cambridge grading system fully integrated
- Progressive Test 2 included with 7.5% weight
- Total CA maintained at 30%
- Backward compatible with existing data
- Comprehensive testing completed
- Admin interface updated
- Reports show grading system used

The system is ready for production use. Teachers can continue entering scores as before, and the system will automatically apply the correct calculation based on each subject's configured grading system.
