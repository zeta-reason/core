"""Tests for core metrics functions."""

import math
import pytest

from zeta_reason.metrics import (
    accuracy,
    brier_score,
    expected_calibration_error,
    self_consistency_entropy,
    unsupported_step_rate,
)


class TestAccuracy:
    """Tests for accuracy metric."""

    def test_perfect_accuracy(self):
        """Test perfect accuracy (all correct)."""
        predictions = ["42", "100", "abc"]
        targets = ["42", "100", "abc"]
        assert accuracy(predictions, targets) == 1.0

    def test_zero_accuracy(self):
        """Test zero accuracy (all incorrect)."""
        predictions = ["wrong", "bad", "nope"]
        targets = ["42", "100", "abc"]
        assert accuracy(predictions, targets) == 0.0

    def test_partial_accuracy(self):
        """Test partial accuracy."""
        predictions = ["42", "wrong", "abc"]
        targets = ["42", "100", "abc"]
        assert accuracy(predictions, targets) == pytest.approx(2/3)

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        predictions = ["ABC", "xyz"]
        targets = ["abc", "XYZ"]
        assert accuracy(predictions, targets) == 1.0

    def test_whitespace_handling(self):
        """Test whitespace stripping."""
        predictions = ["  42  ", "abc"]
        targets = ["42", "  abc  "]
        assert accuracy(predictions, targets) == 1.0

    def test_empty_lists(self):
        """Test empty input lists."""
        assert accuracy([], []) == 0.0

    def test_mismatched_lengths(self):
        """Test mismatched list lengths."""
        predictions = ["42", "100"]
        targets = ["42"]
        assert accuracy(predictions, targets) == 0.0


class TestBrierScore:
    """Tests for Brier score metric."""

    def test_perfect_calibration(self):
        """Test perfect calibration (prob matches outcome)."""
        probs = [1.0, 1.0, 0.0, 0.0]
        targets = [1, 1, 0, 0]
        assert brier_score(probs, targets) == 0.0

    def test_worst_calibration(self):
        """Test worst calibration (opposite predictions)."""
        probs = [1.0, 1.0]
        targets = [0, 0]
        assert brier_score(probs, targets) == 1.0

    def test_uncertain_predictions(self):
        """Test uncertain predictions (0.5 probability)."""
        probs = [0.5, 0.5, 0.5, 0.5]
        targets = [1, 0, 1, 0]
        assert brier_score(probs, targets) == 0.25

    def test_empty_lists(self):
        """Test empty input lists."""
        assert brier_score([], []) == 1.0


class TestExpectedCalibrationError:
    """Tests for Expected Calibration Error metric."""

    def test_perfect_calibration(self):
        """Test perfectly calibrated predictions."""
        # All predictions at 100% confidence are correct
        probs = [1.0, 1.0, 1.0, 1.0]
        targets = [1, 1, 1, 1]
        assert expected_calibration_error(probs, targets) == 0.0

    def test_miscalibration(self):
        """Test miscalibrated predictions."""
        # 100% confident but all wrong
        probs = [1.0, 1.0, 1.0, 1.0]
        targets = [0, 0, 0, 0]
        assert expected_calibration_error(probs, targets) == 1.0

    def test_partial_calibration(self):
        """Test partial calibration."""
        # 100% confident, 50% correct
        probs = [1.0, 1.0, 1.0, 1.0]
        targets = [1, 0, 1, 0]
        # ECE should be |1.0 - 0.5| = 0.5
        assert expected_calibration_error(probs, targets) == pytest.approx(0.5)

    def test_empty_lists(self):
        """Test empty input lists."""
        assert expected_calibration_error([], []) == 1.0


class TestSelfConsistencyEntropy:
    """Tests for Self-Consistency Entropy metric."""

    def test_perfect_consistency(self):
        """Test perfect consistency (all same answer)."""
        answer_counts = {"42": 10}
        assert self_consistency_entropy(answer_counts) == 0.0

    def test_uniform_distribution(self):
        """Test uniform distribution (maximum entropy)."""
        # 2 answers with equal counts: H = -0.5*ln(0.5) - 0.5*ln(0.5) = ln(2)
        answer_counts = {"a": 5, "b": 5}
        expected = math.log(2)
        assert self_consistency_entropy(answer_counts) == pytest.approx(expected)

    def test_skewed_distribution(self):
        """Test skewed distribution."""
        answer_counts = {"42": 9, "41": 1}
        # Entropy should be > 0 but < ln(2)
        entropy = self_consistency_entropy(answer_counts)
        assert 0 < entropy < math.log(2)

    def test_empty_dict(self):
        """Test empty answer distribution."""
        assert self_consistency_entropy({}) == 0.0

    def test_zero_counts(self):
        """Test distribution with zero total count."""
        answer_counts = {"a": 0, "b": 0}
        assert self_consistency_entropy(answer_counts) == 0.0


class TestUnsupportedStepRate:
    """Tests for Unsupported Step Rate metric."""

    def test_correct_answer(self):
        """Test correct answer (should return 0.0)."""
        cot_text = "Let me solve: 2+2=4"
        final_answer = "4"
        target = "4"
        assert unsupported_step_rate(cot_text, final_answer, target) == 0.0

    def test_incorrect_answer(self):
        """Test incorrect answer (should return 1.0)."""
        cot_text = "Let me solve: 2+2=5"
        final_answer = "5"
        target = "4"
        assert unsupported_step_rate(cot_text, final_answer, target) == 1.0

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        cot_text = "The answer is ABC"
        final_answer = "ABC"
        target = "abc"
        assert unsupported_step_rate(cot_text, final_answer, target) == 0.0

    def test_whitespace_handling(self):
        """Test whitespace handling."""
        cot_text = "  The answer is 42  "
        final_answer = "  42  "
        target = "42"
        assert unsupported_step_rate(cot_text, final_answer, target) == 0.0


class TestMetricsV2:
    """Tests for v0.2 metric functions."""

    def test_usr_v0_perfect(self):
        """Test USR_v0 with all correct answers."""
        from zeta_reason.metrics.core import usr_v0

        preds = ["42", "hello", "world"]
        targets = ["42", "hello", "world"]
        result = usr_v0(preds, targets)
        assert result == 0.0

    def test_usr_v0_all_wrong(self):
        """Test USR_v0 with all wrong answers."""
        from zeta_reason.metrics.core import usr_v0

        preds = ["42", "hello", "world"]
        targets = ["43", "hi", "earth"]
        result = usr_v0(preds, targets)
        assert result == 1.0

    def test_usr_v0_partial(self):
        """Test USR_v0 with partial correctness."""
        from zeta_reason.metrics.core import usr_v0

        preds = ["42", "hello", "world"]
        targets = ["42", "hi", "world"]
        result = usr_v0(preds, targets)
        assert abs(result - (1.0 / 3.0)) < 0.001

    def test_sce_v0_single_answer(self):
        """Test SCE_v0 with all same answers (entropy=0)."""
        from zeta_reason.metrics.core import sce_v0

        preds = ["42", "42", "42", "42"]
        result = sce_v0(preds)
        assert result == 0.0

    def test_sce_v0_diverse(self):
        """Test SCE_v0 with diverse answers."""
        from zeta_reason.metrics.core import sce_v0
        import math

        preds = ["a", "b", "c", "d"]
        result = sce_v0(preds)
        # Should be log(4) = 1.386...
        expected = math.log(4)
        assert abs(result - expected) < 0.001

    def test_sce_v0_empty(self):
        """Test SCE_v0 with empty list."""
        from zeta_reason.metrics.core import sce_v0

        result = sce_v0([])
        assert result is None

    def test_mean_or_none_with_values(self):
        """Test mean_or_none with valid values."""
        from zeta_reason.metrics.core import mean_or_none

        values = [1.0, 2.0, 3.0, 4.0]
        result = mean_or_none(values)
        assert result == 2.5

    def test_mean_or_none_with_nones(self):
        """Test mean_or_none filtering None values."""
        from zeta_reason.metrics.core import mean_or_none

        values = [1.0, None, 3.0, None, 5.0]
        result = mean_or_none(values)
        assert result == 3.0

    def test_mean_or_none_all_none(self):
        """Test mean_or_none with all None."""
        from zeta_reason.metrics.core import mean_or_none

        values = [None, None, None]
        result = mean_or_none(values)
        assert result is None

    def test_self_correction_rate_all_true(self):
        """Test self_correction_rate with all corrections."""
        from zeta_reason.metrics.core import self_correction_rate

        flags = [True, True, True]
        result = self_correction_rate(flags)
        assert result == 1.0

    def test_self_correction_rate_partial(self):
        """Test self_correction_rate with partial corrections."""
        from zeta_reason.metrics.core import self_correction_rate

        flags = [True, False, True, False]
        result = self_correction_rate(flags)
        assert result == 0.5

    def test_self_correction_rate_with_nones(self):
        """Test self_correction_rate filtering None values."""
        from zeta_reason.metrics.core import self_correction_rate

        flags = [True, None, False, None, True]
        result = self_correction_rate(flags)
        assert result == (2.0 / 3.0)

    def test_latency_p95_basic(self):
        """Test latency_p95 with basic list."""
        from zeta_reason.metrics.core import latency_p95

        latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        result = latency_p95(latencies)
        # P95 of 10 values should be index 9 (ceiling of 0.95*10 - 1)
        assert result == 100.0

    def test_latency_p95_with_nones(self):
        """Test latency_p95 filtering None values."""
        from zeta_reason.metrics.core import latency_p95

        latencies = [10.0, None, 30.0, None, 50.0]
        result = latency_p95(latencies)
        # P95 of [10, 30, 50] should be 50.0
        assert result == 50.0

    def test_brier_score_v2_with_values(self):
        """Test brier_score_v2 with valid probabilities."""
        from zeta_reason.metrics.core import brier_score_v2

        probs = [0.9, 0.8, 0.1]
        correct = [True, True, False]
        result = brier_score_v2(probs, correct)
        # (0.9-1)^2 + (0.8-1)^2 + (0.1-0)^2 = 0.01 + 0.04 + 0.01 = 0.06
        # Mean = 0.06 / 3 = 0.02
        assert abs(result - 0.02) < 0.001

    def test_brier_score_v2_all_none(self):
        """Test brier_score_v2 with all None probabilities."""
        from zeta_reason.metrics.core import brier_score_v2

        probs = [None, None, None]
        correct = [True, False, True]
        result = brier_score_v2(probs, correct)
        assert result is None

    def test_ece_v2_with_values(self):
        """Test expected_calibration_error_v2 with valid probabilities."""
        from zeta_reason.metrics.core import expected_calibration_error_v2

        probs = [0.9, 0.8, 0.7, 0.6]
        correct = [True, True, False, False]
        result = expected_calibration_error_v2(probs, correct)
        # Should compute ECE across bins
        assert result is not None
        assert 0.0 <= result <= 1.0

    def test_ece_v2_all_none(self):
        """Test expected_calibration_error_v2 with all None probabilities."""
        from zeta_reason.metrics.core import expected_calibration_error_v2

        probs = [None, None, None]
        correct = [True, False, True]
        result = expected_calibration_error_v2(probs, correct)
        assert result is None
