import json
import unittest
from pathlib import Path

from backend.database import DEFAULT_PROFILE
from backend.eligibility import evaluate_scheme, generate_recommendations, profile_completeness

SCHEMES = json.loads((Path(__file__).parent / "data" / "schemes.json").read_text(encoding="utf-8"))


class EligibilityEngineTests(unittest.TestCase):
    def setUp(self):
        self.profile = json.loads(json.dumps(DEFAULT_PROFILE))

    def test_demo_profile_completeness_is_honest_about_missing_village(self):
        result = profile_completeness(self.profile)
        self.assertEqual(result["percent"], 90)
        self.assertIn("village", result["missing"])

    def test_recommendation_order_is_deterministic_and_explainable(self):
        first = generate_recommendations(SCHEMES, self.profile)
        second = generate_recommendations(SCHEMES, self.profile)
        self.assertEqual([r["slug"] for r in first], [r["slug"] for r in second])
        self.assertGreaterEqual(first[0]["evaluation"]["profile_match"], first[-1]["evaluation"]["profile_match"])
        self.assertTrue(all("profile_match" in item["evaluation"] for item in first))

    def test_profile_match_is_not_called_eligibility(self):
        scheme = next(s for s in SCHEMES if s["slug"] == "pmksy-micro-irrigation")
        result = evaluate_scheme(scheme, self.profile)
        self.assertEqual(result["status"], "POTENTIAL_FIT")
        self.assertNotIn("ELIGIBLE", result["status"])
        self.assertIn("not an official eligibility decision", result["evaluated_note"])

    def test_recommendation_explains_profile_signals_separately_from_conditions(self):
        scheme = next(s for s in SCHEMES if s["slug"] == "pmksy-micro-irrigation")
        result = evaluate_scheme(scheme, self.profile)
        self.assertTrue(any("selected irrigation" in reason for reason in result["match_reasons"]))
        self.assertTrue(any("5-hectare" in reason for reason in result["match_reasons"]))
        self.assertTrue(any(item["id"] == "prior_benefit" for item in result["missing_information"]))

    def test_unknown_micro_conditions_remain_unknown(self):
        scheme = next(s for s in SCHEMES if s["slug"] == "pmksy-micro-irrigation")
        result = evaluate_scheme(scheme, self.profile)
        unknown_ids = {item["id"] for item in result["missing_information"]}
        self.assertIn("electricity", unknown_ids)
        self.assertIn("prior_benefit", unknown_ids)

    def test_area_limit_overage_is_review_not_automatic_rejection(self):
        scheme = next(s for s in SCHEMES if s["slug"] == "pmksy-micro-irrigation")
        profile = {**self.profile, "land_area_acres": 20.0}
        result = evaluate_scheme(scheme, profile)
        cap = next(item for item in result["checks"] if item["id"] == "area_limit")
        self.assertEqual(cap["status"], "review")
        self.assertEqual(result["status"], "POTENTIAL_FIT")

    def test_document_availability_is_self_reported_and_not_validated(self):
        scheme = next(s for s in SCHEMES if s["slug"] == "pmksy-micro-irrigation")
        result = evaluate_scheme(scheme, self.profile)
        self.assertEqual(result["documents_available"], 2)
        land = next(item for item in result["documents"] if item["id"] == "land_7_12")
        self.assertEqual(land["state"], "self_reported_available")
        passed_land = next(item for item in result["checks"] if item["id"] == "land_7_12")
        self.assertIn("not checked", passed_land["explanation"])

    def test_sc_st_certificate_is_conditional(self):
        scheme = next(s for s in SCHEMES if s["slug"] == "mission-integrated-horticulture-development")
        open_profile = {**self.profile, "social_category": "open"}
        result = evaluate_scheme(scheme, open_profile)
        check = next(item for item in result["checks"] if item["id"] == "social_certificate")
        self.assertEqual(check["status"], "not_applicable")
        sc_profile = {**self.profile, "social_category": "sc"}
        result_sc = evaluate_scheme(scheme, sc_profile)
        check_sc = next(item for item in result_sc["checks"] if item["id"] == "social_certificate")
        self.assertEqual(check_sc["status"], "missing")


if __name__ == "__main__":
    unittest.main()
