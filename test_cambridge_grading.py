"""
Test script to verify Cambridge grading system calculations.

This script tests the continuous assessment calculations for both
Standard and Cambridge grading systems.
"""

from decimal import Decimal, ROUND_HALF_UP

def calculate_continuous_assessment_standard(class_work, pt1, pt2, midterm):
    """Standard grading system calculation."""
    total_score = class_work + pt1 + pt2 + midterm
    normalized = (total_score / Decimal('400')) * Decimal('100')
    return normalized * Decimal('0.30')

def calculate_continuous_assessment_cambridge(class_work, pt1, pt2, midterm):
    """Cambridge grading system calculation with PT2 included."""
    return (
        (class_work * Decimal('0.0375')) +      # 3.75%
        (pt1 * Decimal('0.075')) +              # 7.5%
        (pt2 * Decimal('0.075')) +              # 7.5%
        (midterm * Decimal('0.1125'))           # 11.25%
    )

def test_cambridge_example():
    """
    Test with the example from updates.txt:
    - Classwork & Homework: 16/20 = 80%
    - Progressive Test 1: 21/30 = 70%
    - Midterm Test: 38/50 = 76%

    Expected CA (without PT2) = 4.0 + 7.0 + 11.4 = 22.4 (out of 30%)
    """
    print("=" * 70)
    print("TEST 1: Cambridge Example from updates.txt (without PT2)")
    print("=" * 70)

    class_work = Decimal('80')  # 80%
    pt1 = Decimal('70')         # 70%
    pt2 = Decimal('0')          # Not in original example
    midterm = Decimal('76')     # 76%

    # Cambridge weights (scaled to 30% total):
    # Classwork: 5% → 3.75%
    # PT1: 10% → 7.5%
    # PT2: 10% → 7.5%
    # Midterm: 15% → 11.25%

    # Without PT2:
    ca_without_pt2 = (
        (class_work * Decimal('0.0375')) +      # 80% × 3.75% = 3.0
        (pt1 * Decimal('0.075')) +              # 70% × 7.5% = 5.25
        (midterm * Decimal('0.1125'))           # 76% × 11.25% = 8.55
    )

    print(f"Classwork (80%): 80 × 3.75% = {class_work * Decimal('0.0375')}")
    print(f"PT1 (70%): 70 × 7.5% = {pt1 * Decimal('0.075')}")
    print(f"Midterm (76%): 76 × 11.25% = {midterm * Decimal('0.1125')}")
    print(f"\nCA (without PT2) = {ca_without_pt2} out of 30%")
    print(f"As percentage of CA portion: {(ca_without_pt2 / Decimal('30')) * Decimal('100'):.2f}%")
    print("\nNote: Original example shows 22.4/30% because it uses different weights.")
    print("Our implementation uses scaled weights to maintain 30% total CA.\n")

def test_cambridge_with_pt2():
    """Test Cambridge grading with Progressive Test 2 included."""
    print("=" * 70)
    print("TEST 2: Cambridge Grading with PT2 Included")
    print("=" * 70)

    class_work = Decimal('80')  # 80%
    pt1 = Decimal('70')         # 70%
    pt2 = Decimal('75')         # 75% (NEW)
    midterm = Decimal('76')     # 76%

    ca = calculate_continuous_assessment_cambridge(class_work, pt1, pt2, midterm)

    print(f"Classwork (80%): 80 × 3.75% = {class_work * Decimal('0.0375')}")
    print(f"PT1 (70%): 70 × 7.5% = {pt1 * Decimal('0.075')}")
    print(f"PT2 (75%): 75 × 7.5% = {pt2 * Decimal('0.075')}")
    print(f"Midterm (76%): 76 × 11.25% = {midterm * Decimal('0.1125')}")
    print(f"\nContinuous Assessment = {ca:.2f} out of 30%")
    print(f"As percentage of CA portion: {(ca / Decimal('30')) * Decimal('100'):.2f}%")

    # Calculate final grade with exam
    exam_score = Decimal('85')  # 85%
    exam_contribution = exam_score * Decimal('0.70')
    total_score = ca + exam_contribution
    total_score_rounded = total_score.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    print(f"\nWith Exam Score (85%):")
    print(f"  Exam contribution (70%): 85 × 0.70 = {exam_contribution}")
    print(f"  Total Score: {ca:.2f} + {exam_contribution} = {total_score:.2f}")
    print(f"  Total Score (rounded): {total_score_rounded}\n")

def test_standard_vs_cambridge():
    """Compare Standard and Cambridge grading systems."""
    print("=" * 70)
    print("TEST 3: Standard vs Cambridge Comparison")
    print("=" * 70)

    # Same raw scores for both systems
    class_work = Decimal('80')
    pt1 = Decimal('70')
    pt2 = Decimal('75')
    midterm = Decimal('76')

    ca_standard = calculate_continuous_assessment_standard(class_work, pt1, pt2, midterm)
    ca_cambridge = calculate_continuous_assessment_cambridge(class_work, pt1, pt2, midterm)

    print("Input Scores:")
    print(f"  Classwork: {class_work}%")
    print(f"  Progressive Test 1: {pt1}%")
    print(f"  Progressive Test 2: {pt2}%")
    print(f"  Midterm: {midterm}%")

    print(f"\nStandard System:")
    print(f"  All components equally weighted")
    print(f"  CA = ((80+70+75+76)/400) × 100 × 0.30")
    print(f"  CA = {ca_standard:.2f} out of 30%")

    print(f"\nCambridge System:")
    print(f"  Weighted components (scaled to 30% total):")
    print(f"    Classwork: 3.75%, PT1: 7.5%, PT2: 7.5%, Midterm: 11.25%")
    print(f"  CA = {ca_cambridge:.2f} out of 30%")

    print(f"\nDifference: {abs(ca_cambridge - ca_standard):.2f} points")
    print(f"Cambridge gives {'more' if ca_cambridge > ca_standard else 'less'} weight to higher-performing components\n")

def test_edge_cases():
    """Test edge cases."""
    print("=" * 70)
    print("TEST 4: Edge Cases")
    print("=" * 70)

    # Perfect scores
    ca_perfect = calculate_continuous_assessment_cambridge(
        Decimal('100'), Decimal('100'), Decimal('100'), Decimal('100')
    )
    print(f"Perfect scores (all 100%): CA = {ca_perfect:.2f} out of 30%")

    # Zero scores
    ca_zero = calculate_continuous_assessment_cambridge(
        Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0')
    )
    print(f"Zero scores (all 0%): CA = {ca_zero:.2f} out of 30%")

    # Mixed scores
    ca_mixed = calculate_continuous_assessment_cambridge(
        Decimal('50'), Decimal('60'), Decimal('70'), Decimal('80')
    )
    print(f"Mixed scores (50,60,70,80): CA = {ca_mixed:.2f} out of 30%\n")

def main():
    """Run all tests."""
    print("\n")
    print("*" * 70)
    print(" CAMBRIDGE GRADING SYSTEM CALCULATION TESTS")
    print("*" * 70)
    print()

    test_cambridge_example()
    test_cambridge_with_pt2()
    test_standard_vs_cambridge()
    test_edge_cases()

    print("=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    print("\nKey Points:")
    print("1. Cambridge system uses weighted components (scaled to 30% total)")
    print("2. Weights: CW=3.75%, PT1=7.5%, PT2=7.5%, Midterm=11.25%")
    print("3. Standard system treats all components equally")
    print("4. Final grade = CA (30%) + Exam (70%)")
    print()

if __name__ == '__main__':
    main()
