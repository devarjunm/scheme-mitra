import json
import unittest
from pathlib import Path

from backend.api.schemes import _assistant_reply
from backend.database import DEFAULT_PROFILE
from backend.eligibility import evaluate_scheme

SCHEMES = json.loads((Path(__file__).parent / "data" / "schemes.json").read_text(encoding="utf-8"))


class GroundedAssistantTests(unittest.TestCase):
    def setUp(self):
        self.catalog = []

    def test_scheme_explanation_disclaims_eligibility_and_links_source(self):
        scheme = dict(next(s for s in SCHEMES if s["slug"] == "pmksy-micro-irrigation"))
        scheme["evaluation"] = evaluate_scheme(scheme, DEFAULT_PROFILE)
        result = _assistant_reply("Why did this match my profile?", "en", scheme, DEFAULT_PROFILE, [scheme])
        self.assertEqual(result["grounding"], "local_official_source_summary")
        self.assertEqual(result["ai_provider"], "not_configured")
        self.assertIn("not eligibility or approval", result["answer"])
        self.assertEqual(result["source_url"], scheme["source_url"])

    def test_general_profile_question_uses_profile_data_not_hallucination(self):
        result = _assistant_reply("What is missing from my profile?", "en", None, DEFAULT_PROFILE, [])
        self.assertEqual(result["grounding"], "local_profile_data")
        self.assertIn("village", result["answer"])
        self.assertIn("90%", result["answer"])

    def test_unverified_general_question_declines(self):
        result = _assistant_reply("Will my application be approved tomorrow?", "en", None, DEFAULT_PROFILE, [])
        self.assertEqual(result["grounding"], "no_verified_answer")
        self.assertIn("could not verify", result["answer"])

    def test_marathi_profile_and_match_messages_respect_selected_language(self):
        profile = _assistant_reply("माझ्या प्रोफाइलमध्ये काय कमी आहे?", "mr", None, DEFAULT_PROFILE, [])
        self.assertIn("तुमची प्रोफाइल माहिती", profile["answer"])
        self.assertIn("गाव", profile["answer"])
        scheme = dict(next(s for s in SCHEMES if s["slug"] == "pmksy-micro-irrigation"))
        scheme["evaluation"] = evaluate_scheme(scheme, DEFAULT_PROFILE)
        explanation = _assistant_reply("हे का जुळले?", "mr", scheme, DEFAULT_PROFILE, [scheme])
        self.assertIn("पात्रता किंवा मंजुरी नाही", explanation["answer"])
        self.assertIn("जुळण्याची कारणे", explanation["answer"])


if __name__ == "__main__":
    unittest.main()
