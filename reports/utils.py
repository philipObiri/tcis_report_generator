from decimal import Decimal


# def calculate_gpa(scores):
#     """
#     Calculate the GPA from a list of scores based on fixed grade ranges.
#     The GPA points are assigned as per the following scale:
#     A* 95% - 100% -> GPA: 4.00
#     A 80% - 94% -> GPA: 3.67
#     B+ 75% - 79% -> GPA: 3.33
#     B 70% - 74% -> GPA: 3.00
#     C+ 65% - 69% -> GPA: 2.67
#     C 60% - 64% -> GPA: 2.33
#     D 50% - 59% -> GPA: 2.00
#     E 45% - 49% -> GPA: 1.67
#     F 35% - 44% -> GPA: 1.00
#     Ungraded 0% - 34% -> GPA: 0.00
#     """
#     total_points = 0
#     total_subjects = len(scores)
    
#     if total_subjects == 0:
#         print("No scores available to calculate GPA.")
#         return 0.0

#     # Define GPA mappings for different score ranges
#     def get_gpa_for_score(total_score):
#         if 95 <= total_score <= 100:
#             return 4.00  # A*
#         elif 80 <= total_score < 95:
#             return 3.67  # A
#         elif 75 <= total_score < 80:
#             return 3.33  # B+
#         elif 70 <= total_score < 75:
#             return 3.00  # B
#         elif 65 <= total_score < 70:
#             return 2.67  # C+
#         elif 60 <= total_score < 65:
#             return 2.33  # C
#         elif 50 <= total_score < 60:
#             return 2.00  # D
#         elif 45 <= total_score < 50:
#             return 1.67  # E
#         elif 35 <= total_score < 45:
#             return 1.00  # F
#         else:
#             return 0.00  # Ungraded

#     # Iterate over each score and calculate GPA based on the total_score
#     for score in scores:
#         try:
#             # Get the total score from the Score object
#             total_score = Decimal(score.total_score)

#             # Assign GPA based on total_score using the defined scale
#             gpa = get_gpa_for_score(total_score)

#             # Add the calculated GPA to the total points
#             total_points += gpa

#         except Exception as e:
#             # If there's an error, log it and skip this score
#             print(f"Error calculating GPA for score {score}: {e}")
#             total_points += 0  # Add 0 in case of error

#     # Return the GPA rounded to two decimal places
#     final_gpa = round(total_points / total_subjects, 2) if total_subjects > 0 else 0.0
#     print(f"Final GPA: {final_gpa}")
#     return final_gpa





def calculate_gpa(scores):
    """
    Calculate the final GPA from a list of scores, with each score's GPA calculated
    based on predefined grade ranges.

    Parameters:
    scores (list): List of numerical scores (as floats or integers)

    Returns:
    float: The final GPA calculated from the scores
    """
    def get_gpa_from_score(score):
        """
        Return GPA based on the given score.
        """
        if score >= 95 and score <= 100:
            return 4.00  # A*
        elif score >= 80 and score < 95:
            return 3.67  # A
        elif score >= 75 and score < 80:
            return 3.33  # B+
        elif score >= 70 and score < 75:
            return 3.00  # B
        elif score >= 65 and score < 70:
            return 2.67  # C+
        elif score >= 60 and score < 65:
            return 2.33  # C
        elif score >= 50 and score < 60:
            return 2.00  # D
        elif score >= 45 and score < 50:
            return 1.67  # E
        elif score >= 35 and score < 45:
            return 1.00  # F
        else:
            return 0.00  # Ungraded

    total_points = 0
    total_subjects = len(scores)

    if total_subjects == 0:
        print("No scores available to calculate GPA.")
        return 0.0

    # Iterate through the list of scores and calculate total GPA points
    for score in scores:
        try:
            total_score = Decimal(score)  # Convert score to Decimal for precision
            gpa = get_gpa_from_score(total_score)  # Get GPA for the current score
            total_points += gpa  # Add the GPA to the total points

        except Exception as e:
            print(f"Error processing score {score}: {e}")
            total_points += 0  # Add 0 if there's an error with the score

    # Calculate final GPA by averaging total points and round it to 2 decimal places
    final_gpa = round(total_points / total_subjects, 2) if total_subjects > 0 else 0.0
    print(f"Final GPA: {final_gpa}")
    return final_gpa












