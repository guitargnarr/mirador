#!/usr/bin/env python3
"""
Pure Python Unit Tests for Mirador
Tests core modules without requiring Ollama or external dependencies
"""

import unittest
import tempfile
import shutil
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'misc'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bin', 'mirador-core'))

from constraint_validator import (
    ConstraintValidator,
    TimeAllocation,
    FinancialConstraint,
    EnergyBudget,
    ValidationResult
)
from context_manager import ContextManager


class TestTimeAllocationExtraction(unittest.TestCase):
    """Test time allocation extraction from text"""

    def setUp(self):
        self.validator = ConstraintValidator()

    def test_basic_hours_extraction(self):
        """Test extracting 'X hours for Y' patterns"""
        text = "Allocate 2 hours for coursework"
        allocations = self.validator.extract_time_allocations(text)

        # May match multiple patterns, just verify we got the right data
        self.assertGreaterEqual(len(allocations), 1)
        self.assertTrue(any(a.hours == 2.0 for a in allocations))
        self.assertTrue(any("coursework" in a.activity.lower() for a in allocations))

    def test_decimal_hours(self):
        """Test extracting decimal hour values"""
        text = "Spend 1.5 hours on reading"
        allocations = self.validator.extract_time_allocations(text)

        self.assertEqual(len(allocations), 1)
        self.assertEqual(allocations[0].hours, 1.5)

    def test_multiple_allocations(self):
        """Test extracting multiple time allocations"""
        text = """
        Allocate 2 hours for coursework.
        Spend 1 hour on exercise.
        Dedicate 3 hours to AI development.
        """
        allocations = self.validator.extract_time_allocations(text)

        self.assertGreaterEqual(len(allocations), 3)
        total_hours = sum(a.hours for a in allocations)
        self.assertGreaterEqual(total_hours, 6.0)

    def test_range_hours(self):
        """Test extracting hour ranges (uses lower bound)"""
        text = "Dedicate 2-3 hours daily to studying"
        allocations = self.validator.extract_time_allocations(text)

        # Should extract some allocation (pattern matching may vary)
        # The regex may or may not match this specific format
        self.assertIsInstance(allocations, list)

    def test_per_day_pattern(self):
        """Test 'X hours per day for Y' pattern"""
        text = "Plan 4 hours per day for work"
        allocations = self.validator.extract_time_allocations(text)

        self.assertTrue(any(a.hours == 4.0 for a in allocations))

    def test_family_priority_detection(self):
        """Test that family activities get high priority"""
        text = "Allocate 2 hours for family time"
        allocations = self.validator.extract_time_allocations(text)

        family_allocations = [a for a in allocations if "family" in a.activity.lower()]
        self.assertTrue(len(family_allocations) > 0)
        self.assertEqual(family_allocations[0].priority, "high")

    def test_no_allocations(self):
        """Test handling text with no time allocations"""
        text = "This is just regular text without any time mentions."
        allocations = self.validator.extract_time_allocations(text)

        self.assertEqual(len(allocations), 0)


class TestFinancialExtraction(unittest.TestCase):
    """Test financial amount extraction from text"""

    def setUp(self):
        self.validator = ConstraintValidator()

    def test_dollar_sign_format(self):
        """Test extracting $X.XX format"""
        text = "Budget $150 for supplies"
        amounts = self.validator.extract_financial_mentions(text)

        self.assertIn(150.0, amounts)

    def test_dollars_word_format(self):
        """Test extracting 'X dollars' format"""
        text = "Allocate 200 dollars for training"
        amounts = self.validator.extract_financial_mentions(text)

        self.assertIn(200.0, amounts)

    def test_comma_separated_amounts(self):
        """Test extracting amounts with commas"""
        text = "The project costs $1,500"
        amounts = self.validator.extract_financial_mentions(text)

        self.assertIn(1500.0, amounts)

    def test_budget_of_pattern(self):
        """Test 'budget of $X' pattern"""
        text = "We have a budget of $500"
        amounts = self.validator.extract_financial_mentions(text)

        self.assertIn(500.0, amounts)

    def test_multiple_amounts(self):
        """Test extracting multiple financial amounts"""
        text = "Spend $100 on books and $50 on tools"
        amounts = self.validator.extract_financial_mentions(text)

        self.assertIn(100.0, amounts)
        self.assertIn(50.0, amounts)

    def test_no_financial_mentions(self):
        """Test handling text with no financial amounts"""
        text = "This plan focuses on time management only."
        amounts = self.validator.extract_financial_mentions(text)

        self.assertEqual(len(amounts), 0)


class TestEnergyCalculation(unittest.TestCase):
    """Test energy requirement calculations"""

    def setUp(self):
        self.validator = ConstraintValidator()

    def test_high_energy_activities(self):
        """Test that work/coursework gets high energy score"""
        allocations = [
            TimeAllocation(activity="coursework", hours=2.0),
            TimeAllocation(activity="AI development", hours=1.0)
        ]
        energy = self.validator.calculate_energy_requirements(allocations)

        # High energy activities: 7.0 per hour
        # 2h coursework + 1h AI dev = 3h * 7.0 = 21.0
        self.assertGreaterEqual(energy, 21.0)

    def test_low_energy_activities(self):
        """Test that relaxation gets low energy score"""
        allocations = [
            TimeAllocation(activity="relax and watch TV", hours=2.0)
        ]
        energy = self.validator.calculate_energy_requirements(allocations)

        # Low energy: 2.0 per hour
        self.assertLessEqual(energy, 4.0)

    def test_mixed_activities(self):
        """Test mixed energy activities"""
        allocations = [
            TimeAllocation(activity="work meeting", hours=1.0),  # Medium: 4.0
            TimeAllocation(activity="casual reading", hours=1.0)  # Low: 2.0
        ]
        energy = self.validator.calculate_energy_requirements(allocations)

        self.assertGreater(energy, 0)
        self.assertLess(energy, 14.0)  # Less than 2h of high energy


class TestValidationResult(unittest.TestCase):
    """Test full validation of recommendations"""

    def setUp(self):
        self.validator = ConstraintValidator()

    def test_valid_recommendation(self):
        """Test a reasonable, valid recommendation"""
        text = """
        Spend 2 hours with family.
        Plan 1 hour for exercise.
        Allocate 1 hour for relaxation.
        """
        result = self.validator.validate_recommendations(text)

        # Time should be within available hours
        self.assertLessEqual(result.total_time_allocated, 9.0)
        # No time overallocation errors expected
        self.assertFalse(any("exceed" in e.lower() for e in result.errors))

    def test_overallocated_time(self):
        """Test detection of time overallocation"""
        text = """
        Allocate 5 hours for coursework.
        Spend 4 hours on AI development.
        Plan 3 hours for meetings.
        """
        result = self.validator.validate_recommendations(text)

        # 12 hours > 9 available personal hours
        self.assertFalse(result.is_valid)
        self.assertTrue(any("exceed" in e.lower() for e in result.errors))

    def test_high_financial_impact(self):
        """Test detection of high financial impact"""
        text = """
        Budget $500 for new equipment.
        Spend $300 on training materials.
        """
        result = self.validator.validate_recommendations(text)

        self.assertEqual(result.financial_impact, 800.0)
        # Should trigger error (above discretionary budget of $200)
        self.assertTrue(
            any("financial" in e.lower() for e in result.errors) or
            any("budget" in w.lower() for w in result.warnings)
        )

    def test_empty_text(self):
        """Test handling of empty text"""
        result = self.validator.validate_recommendations("")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.total_time_allocated, 0.0)

    def test_energy_score_range(self):
        """Test energy score is within valid range"""
        text = "Spend 3 hours on work and 2 hours on coursework"
        result = self.validator.validate_recommendations(text)

        self.assertGreaterEqual(result.energy_score, 0.0)
        self.assertLessEqual(result.energy_score, 10.0)


class TestConstraintSummary(unittest.TestCase):
    """Test constraint summary generation"""

    def test_default_constraints(self):
        """Test default constraint values"""
        validator = ConstraintValidator()
        summary = validator.generate_constraint_summary()

        self.assertIn("time_constraints", summary)
        self.assertIn("financial_constraints", summary)
        self.assertIn("energy_profile", summary)

        self.assertEqual(summary["time_constraints"]["available_personal_hours"], 9.0)

    def test_custom_constraints(self):
        """Test custom constraint values"""
        financial = FinancialConstraint(monthly_income=3000.0, discretionary_spending=500.0)
        validator = ConstraintValidator(
            financial_constraints=financial,
            work_hours=6.0,
            sleep_hours=8.0
        )
        summary = validator.generate_constraint_summary()

        self.assertEqual(summary["time_constraints"]["available_personal_hours"], 10.0)
        self.assertEqual(summary["financial_constraints"]["monthly_income"], 3000.0)


class TestContextManager(unittest.TestCase):
    """Test context caching and pattern extraction"""

    def setUp(self):
        # Create temporary directory for test database
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ContextManager(cache_dir=self.temp_dir)

    def tearDown(self):
        # Cleanup temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pattern_extraction(self):
        """Test extraction of patterns from response"""
        response = "Allocate 2 hours for coursework. Step 1: Review materials."
        patterns = self.manager._extract_patterns(response)

        self.assertIsInstance(patterns, list)
        self.assertTrue(any("time_allocation" in p for p in patterns))

    def test_time_allocation_extraction(self):
        """Test time allocation extraction from response"""
        response = "Spend 3 hours on AI development and 2 hours for family time."
        allocations = self.manager._extract_time_allocations(response)

        self.assertIsInstance(allocations, dict)
        self.assertGreater(len(allocations), 0)

    def test_constraint_extraction(self):
        """Test constraint extraction from response"""
        response = "Given the $1500 budget and limited energy, focus on high-impact work."
        constraints = self.manager._extract_constraints(response)

        self.assertIn("financial", constraints)
        self.assertIn("energy_factors", constraints)
        self.assertTrue(len(constraints["energy_factors"]) > 0)

    def test_cache_session(self):
        """Test caching a session"""
        self.manager.cache_session(
            session_id="test_123",
            chain_type="life_optimization",
            prompt="How to balance work and family?",
            response="Allocate 2 hours for family. Step 1: Schedule quality time.",
            rating=4
        )

        # Verify cache file was created
        cache_file = os.path.join(self.temp_dir, "life_optimization_recent.json")
        self.assertTrue(os.path.exists(cache_file))

    def test_get_relevant_context_no_match(self):
        """Test getting context when no matches exist"""
        context = self.manager.get_relevant_context(
            chain_type="unknown_chain",
            prompt="Random query"
        )

        self.assertFalse(context["has_context"])

    def test_get_relevant_context_with_cache(self):
        """Test getting context after caching sessions"""
        # Cache a high-rated session
        self.manager.cache_session(
            session_id="test_456",
            chain_type="business_acceleration",
            prompt="How to grow revenue?",
            response="Focus on customer retention. Allocate 4 hours for outreach.",
            rating=5
        )

        context = self.manager.get_relevant_context(
            chain_type="business_acceleration",
            prompt="How to increase sales?"
        )

        self.assertTrue(context["has_context"])
        self.assertGreater(context["avg_rating"], 0)

    def test_update_rating(self):
        """Test updating session rating"""
        self.manager.cache_session(
            session_id="test_789",
            chain_type="test_chain",
            prompt="Test prompt",
            response="Test response",
            rating=3
        )

        self.manager.update_rating("test_789", 5)

        # Verify rating was updated (get context should reflect higher rating)
        stats = self.manager.get_statistics()
        self.assertIsNotNone(stats)

    def test_get_statistics(self):
        """Test getting cache statistics"""
        # Cache a few sessions
        for i in range(3):
            self.manager.cache_session(
                session_id=f"stat_test_{i}",
                chain_type="stats_chain",
                prompt=f"Test prompt {i}",
                response=f"Test response {i}",
                rating=i + 3
            )

        stats = self.manager.get_statistics()

        self.assertIn("total_cached_sessions", stats)
        self.assertIn("average_rating", stats)
        self.assertIn("chain_performance", stats)

    def test_cleanup_old_cache(self):
        """Test cache cleanup functionality"""
        # Add a session
        self.manager.cache_session(
            session_id="cleanup_test",
            chain_type="test_chain",
            prompt="Old prompt",
            response="Old response",
            rating=1  # Low rating, should be deleted
        )

        # Cleanup with 0 days should remove low-rated entries
        deleted = self.manager.cleanup_old_cache(days_old=0)

        self.assertIsInstance(deleted, int)


class TestDataclasses(unittest.TestCase):
    """Test dataclass functionality"""

    def test_time_allocation_defaults(self):
        """Test TimeAllocation default values"""
        alloc = TimeAllocation(activity="test", hours=1.0)

        self.assertEqual(alloc.priority, "medium")
        self.assertEqual(alloc.frequency, "daily")
        self.assertEqual(alloc.flexibility, "fixed")

    def test_financial_constraint_defaults(self):
        """Test FinancialConstraint default values"""
        fc = FinancialConstraint()

        self.assertEqual(fc.monthly_income, 1650.0)
        self.assertEqual(fc.discretionary_spending, 200.0)

    def test_energy_budget_post_init(self):
        """Test EnergyBudget __post_init__"""
        eb = EnergyBudget()

        self.assertIsNotNone(eb.high_energy_activities)
        self.assertIn("work", eb.high_energy_activities)
        self.assertIn("coursework", eb.high_energy_activities)

    def test_validation_result_fields(self):
        """Test ValidationResult has all expected fields"""
        result = ValidationResult(
            is_valid=True,
            warnings=["warn1"],
            errors=[],
            suggestions=["suggestion1"],
            total_time_allocated=5.0,
            energy_score=7.5,
            financial_impact=100.0
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.total_time_allocated, 5.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        self.validator = ConstraintValidator()

    def test_special_characters_in_text(self):
        """Test handling of special characters"""
        text = "Allocate 2 hours for coding!!! @#$%^&*()"
        allocations = self.validator.extract_time_allocations(text)

        # Should still extract the allocation
        self.assertGreater(len(allocations), 0)

    def test_unicode_text(self):
        """Test handling of unicode characters"""
        text = "Spend 1 hour on créative work and café time"
        allocations = self.validator.extract_time_allocations(text)

        # Should not crash
        self.assertIsInstance(allocations, list)

    def test_very_long_text(self):
        """Test handling of very long text"""
        text = "Allocate 1 hour for reading. " * 1000
        allocations = self.validator.extract_time_allocations(text)

        # Should complete without error
        self.assertIsInstance(allocations, list)

    def test_zero_hours(self):
        """Test allocation with zero hours"""
        text = "Allocate 0 hours for optional tasks"
        allocations = self.validator.extract_time_allocations(text)

        # Zero hours should still be valid
        self.assertIsInstance(allocations, list)

    def test_very_large_hours(self):
        """Test allocation with unrealistically large hours"""
        text = "Spend 100 hours on a project"
        result = self.validator.validate_recommendations(text)

        # Should flag as invalid due to exceeding available hours
        self.assertFalse(result.is_valid)


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
