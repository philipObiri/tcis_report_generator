from decimal import Decimal

def calculate_continuous_assessment(class_work, pt1, pt2, midterm, grading_system='standard'):
    """
    Calculate continuous assessment based on the grading system.

    Parameters:
    class_work (Decimal): Classwork score (0-100 as percentage)
    pt1 (Decimal): Progressive Test 1 score (0-100 as percentage)
    pt2 (Decimal): Progressive Test 2 score (0-100 as percentage)
    midterm (Decimal): Midterm score (0-100 as percentage)
    grading_system (str): 'standard' or 'cambridge'

    Returns:
    Decimal: Continuous assessment score (0-30% of total grade)
    """
    class_work = Decimal(str(class_work))
    pt1 = Decimal(str(pt1))
    pt2 = Decimal(str(pt2))
    midterm = Decimal(str(midterm))

    if grading_system == 'cambridge':
        # Cambridge Grading System with Progressive Test 2 included
        # Weights scaled to total 30% CA:
        # - Classwork & Homework: 3.75% (originally 5%, scaled by 0.75)
        # - Progressive Test 1: 7.5% (originally 10%, scaled by 0.75)
        # - Progressive Test 2: 7.5% (originally 10%, scaled by 0.75)
        # - Midterm: 11.25% (originally 15%, scaled by 0.75)
        continuous_assessment = (
            (class_work * Decimal('0.0375')) +      # 3.75%
            (pt1 * Decimal('0.075')) +              # 7.5%
            (pt2 * Decimal('0.075')) +              # 7.5%
            (midterm * Decimal('0.1125'))           # 11.25%
        )
    else:
        # Standard Grading System
        # All four components equally weighted
        total_score = class_work + pt1 + pt2 + midterm
        normalized = (total_score / Decimal('400')) * Decimal('100')
        continuous_assessment = normalized * Decimal('0.30')

    return continuous_assessment

def calculate_gpa(scores):
    """
    Calculate the final GPA from a list of Score instances, with each score's GPA 
    calculated based on predefined grade ranges as per the new table.

    Parameters:
    scores (list): List of Score instances

    Returns:
    float: The final GPA calculated from the scores
    """
    from reports.models import Score  # Importing here to avoid circular import

    def get_gpa_from_score(score):
        """
        Return GPA based on the given score, according to the new grading table.
        """
        if score >= 95 and score <= 100:
            return 4.00  # A* (Distinction)
        elif score >= 80 and score < 95:
            return 3.67  # A (Excellent)
        elif score >= 75 and score < 80:
            return 3.33  # B+ (Very Good)
        elif score >= 70 and score < 75:
            return 3.00  # B (Good)
        elif score >= 65 and score < 70:
            return 2.67  # C+ (Average)
        elif score >= 60 and score < 65:
            return 2.33  # C (Pass)
        elif score >= 50 and score < 60:
            return 2.00  # D (Credit)
        elif score >= 45 and score < 50:
            return 1.67  # E (Failed)
        elif score >= 35 and score < 45:
            return 1.00  # F (Failed)
        else:
            return 0.00  # Ungraded (0% - 34%)

    total_points = 0
    total_subjects = len(scores)

    if total_subjects == 0:
        print("No scores available to calculate GPA.")
        return 0.0

    # Iterate through the list of scores and calculate total GPA points
    for score in scores:
        try:
            # Handle both Score instances and numeric values
            if isinstance(score, Score):
                # It's a Score object, use total_score
                total_score = float(score.total_score)
            elif isinstance(score, (int, float, Decimal)):
                # It's a numeric value (for midterm, mock, progressive tests)
                total_score = float(score)
            else:
                # Invalid input
                print(f"Invalid score type encountered: {type(score)}. Defaulting to 0.0")
                total_score = 0.0

            # Get GPA for the current score
            gpa = get_gpa_from_score(total_score)
            total_points += gpa  # Add the GPA to the total points

        except Exception as e:
            print(f"Error processing score {score}: {e}")
            total_points += 0  # Add 0 if there's an error with the score

    # Calculate final GPA by averaging total points and round it to 2 decimal places
    final_gpa = round(total_points / total_subjects, 2) if total_subjects > 0 else 0.0
    print(f"Final GPA: {final_gpa}")
    return final_gpa
