# System Updates and Bug Fixes

## Date: 2025-12-10

### Overview
This document outlines all the bug fixes and improvements made to the TCIS Academic Report Generation System.

---

## 1. Fixed Exam Score Calculation Display (70% Issue)

### Problem
The system was displaying the full exam score in the end-of-term report template, but the exam score should be displayed as 70% of the entered value to match the grading calculation formula (CA 30% + Exam 70%).

### Solution
- **File Modified**: `reports/views.py` (lines 1875-1879)
  - Added logic to calculate and attach `exam_score_display` (70% of exam_score) to each score object before passing to the template

- **File Modified**: `templates/generated_report.html` (line 272)
  - Changed from `{{ item.exam_score }}` to `{{ item.exam_score_display|floatformat:2 }}`
  - Removed client-side JavaScript calculation (lines 417-430) that was previously doing this on the frontend

### Impact
Now when a teacher enters an exam score of 85, the report will correctly display 59.50 (70% of 85) in the Exam column, which matches the calculation used for the total score.

---

## 2. Restricted Academic and Behavioural Comments to Class Advisors Only

### Problem
Any teacher could add Academic and Behavioural comments to student reports, but these comments should only be added by Class Advisors (Head Class Teachers).

### Solution
- **File Modified**: `reports/views.py` (lines 1820-1825)
  - Added authorization check in the `generate_report` function to verify that only users with `is_head_class_teacher=True` can add comments
  - Returns error message: "Only Class Advisors (Head Class Teachers) are authorized to add Academic and Behavioural Comments."

- **File Modified**: `static/js/report.js` (lines 8, 15-19)
  - Added frontend validation to check `is_head_class_teacher` status before allowing report generation
  - Displays error message if non-Class Advisor attempts to generate a report

- **File Modified**: `templates/dashboard.html` (line 21)
  - Added hidden input field to pass `is_head_class_teacher` status to JavaScript

### Impact
- Backend: Server-side validation prevents unauthorized comment submission
- Frontend: Non-Class Advisors see an error message if they attempt to generate reports
- Database: Only Class Advisors can save Academic and Behavioural comments to the database

---

## 3. Fixed Score Filtering Inconsistencies

### Problem
Some report generation and viewing functions were fetching all scores for a student in a term, regardless of whether the subjects were actually assigned to that student. This could lead to including scores for subjects the student is not taking.

### Solution
- **File Modified**: `reports/views.py` (multiple locations)
  - Updated all report generation functions to filter scores by `subject__in=student.subjects.all()`
  - Applied to the following functions:
    1. `generate_midterm_report` (lines 1939-1943)
    2. `generate_mock_report` (lines ~2080-2084)
    3. `generate_progressive_test_one_report` (lines ~2235-2239)
    4. `generate_progressive_test_two_report` (lines ~2378-2382)
    5. `view_midterm_report` (lines 899-903)
    6. `view_mock_report` (lines 994-998)
    7. `view_progressive_test_score_one_report` (lines 1090-1094)
    8. `view_progressive_test_score_two_report` (lines 1186-1190)
    9. `view_progressive_test_score_three_report` (lines 1282-1286)

### Before:
```python
scores = Score.objects.filter(student=student, term=term).distinct('subject')
```

### After:
```python
scores = Score.objects.filter(
    student=student,
    term=term,
    subject__in=student.subjects.all()
).distinct('subject')
```

### Impact
- Reports now only display scores for subjects that are actually assigned to each student
- GPA calculations are now accurate and only include relevant subjects
- Prevents data inconsistencies and incorrect report generation

---

## 4. GPA Calculation Consistency

### Problem
While investigating, confirmed that GPA calculations were working correctly but needed to ensure consistency across all report types.

### Verification
- **End-of-Term Reports**: Use `calculate_gpa()` from `reports/utils.py` which calculates GPA based on total_score (CA 30% + Exam 70%)
- **Midterm Reports**: Calculate GPA based on midterm_score only
- **Mock Reports**: Calculate GPA based on mock_score only
- **Progressive Test Reports**: Calculate GPA based on progressive_test_1/2/3_score

All calculations follow the same grading scale:
- A* (95-100%): 4.00 GPA
- A (80-94%): 3.67 GPA
- B+ (75-79%): 3.33 GPA
- B (70-74%): 3.00 GPA
- C+ (65-69%): 2.67 GPA
- C (60-64%): 2.33 GPA
- D (50-59%): 2.00 GPA
- E (45-49%): 1.67 GPA
- F (35-44%): 1.00 GPA
- Ungraded (0-34%): 0.00 GPA

### Impact
All report types now consistently filter scores by student subjects before calculating GPAs, ensuring accurate GPA representation.

---

## Summary of Files Modified

1. `reports/views.py` - Multiple functions updated
2. `templates/generated_report.html` - Fixed exam score display
3. `static/js/report.js` - Added Class Advisor authorization check
4. `templates/dashboard.html` - Added hidden input for authorization status

## Testing Recommendations

1. **Exam Score Display**:
   - Enter an exam score (e.g., 85) for a student
   - Generate the end-of-term report
   - Verify the Exam column shows 59.50 (70% of 85)
   - Verify the Total score is correctly calculated as CA + 59.50

2. **Class Advisor Authorization**:
   - Login as a non-Class Advisor teacher
   - Attempt to generate a report with comments
   - Verify error message appears both on frontend and backend
   - Login as a Class Advisor
   - Verify report generation with comments works

3. **Score Filtering**:
   - Create a student with specific subjects assigned
   - Add scores for both assigned and non-assigned subjects
   - Generate all report types (end-of-term, midterm, mock, progressive tests)
   - Verify only scores for assigned subjects appear in reports
   - Verify GPA calculations reflect only assigned subjects

---

## Notes

- All changes are backward compatible
- No database migrations required
- Existing reports in the database are not affected
- All changes apply to new report generation going forward

---

## System Stability

All fixes have been implemented without disrupting the existing system functionality. The report generation system continues to work as before, but with these critical improvements:
- Accurate exam score display (70%)
- Proper authorization for comment entry
- Consistent and accurate score filtering across all report types
