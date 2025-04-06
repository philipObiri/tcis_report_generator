# from decimal import Decimal

# def calculate_gpa(scores):
#     """
#     Calculate the final GPA from a list of Score instances, with each score's GPA 
#     calculated based on predefined grade ranges.

#     Parameters:
#     scores (list): List of Score instances

#     Returns:
#     float: The final GPA calculated from the scores
#     """
#     from reports.models import Score  # Importing here to avoid circular import

#     def get_gpa_from_score(score):
#         """
#         Return GPA based on the given score.
#         """
#         if score >= 95 and score <= 100:
#             return 4.00  # A*
#         elif score >= 80 and score < 95:
#             return 3.67  # A
#         elif score >= 75 and score < 80:
#             return 3.33  # B+
#         elif score >= 70 and score < 75:
#             return 3.00  # B
#         elif score >= 65 and score < 70:
#             return 2.67  # C+
#         elif score >= 60 and score < 65:
#             return 2.33  # C
#         elif score >= 50 and score < 60:
#             return 2.00  # D
#         elif score >= 45 and score < 50:
#             return 1.67  # E
#         elif score >= 35 and score < 45:
#             return 1.00  # F
#         else:
#             return 0.00  # Ungraded

#     total_points = 0
#     total_subjects = len(scores)

#     if total_subjects == 0:
#         print("No scores available to calculate GPA.")
#         return 0.0

#     # Iterate through the list of scores and calculate total GPA points
#     for score in scores:
#         try:
#             # Ensure the score is a valid Score instance and has a total_score
#             if isinstance(score, Score):
#                 total_score = Decimal(score.total_score)  # Access total_score of the Score instance
#             else:
#                 # If the input is invalid (not a Score instance), set the score to 0.0
#                 print(f"Invalid score encountered: {score}. Defaulting to 0.0")
#                 total_score = Decimal('0.0')

#             # Get GPA for the current score
#             gpa = get_gpa_from_score(total_score)
#             total_points += gpa  # Add the GPA to the total points

#         except Exception as e:
#             print(f"Error processing score {score}: {e}")
#             total_points += 0  # Add 0 if there's an error with the score

#     # Calculate final GPA by averaging total points and round it to 2 decimal places
#     final_gpa = round(total_points / total_subjects, 2) if total_subjects > 0 else 0.0
#     print(f"Final GPA: {final_gpa}")
#     return final_gpa



from decimal import Decimal

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
            # Ensure the score is a valid Score instance and has a total_score
            if isinstance(score, Score):
                total_score = Decimal(score.total_score)  # Access total_score of the Score instance
            else:
                # If the input is invalid (not a Score instance), set the score to 0.0
                print(f"Invalid score encountered: {score}. Defaulting to 0.0")
                total_score = Decimal('0.0')

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
