"""Deterministic, explainable recommendation logic.

This module does not decide or predict government approval. It reports profile-fit
signals plus documented checks and unknowns from the locally captured scheme record.
"""
from __future__ import annotations

from typing import Any

ACRES_PER_HECTARE = 2.47105


def _path(data: dict[str, Any], path: str) -> Any:
    value: Any = data
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def profile_completeness(profile: dict[str, Any]) -> dict[str, Any]:
    checks = [
        ("district", bool(profile.get("district"))),
        ("taluka", bool(profile.get("taluka"))),
        ("village", bool(profile.get("village"))),
        ("land", isinstance(profile.get("land_area_acres"), (int, float)) and profile.get("land_area_acres", 0) > 0),
        ("crop", bool(profile.get("crop"))),
        ("farmer_category", bool(profile.get("farmer_category"))),
        ("irrigation", profile.get("irrigation") in ("yes", "no")),
        ("aadhaar", isinstance(profile.get("aadhaar_present"), bool)),
        ("land_7_12", profile.get("documents", {}).get("land_7_12") in ("available", "needs_verification")),
        ("land_8a", profile.get("documents", {}).get("land_8a") in ("available", "needs_verification")),
    ]
    total = len(checks)
    done = sum(1 for _, is_done in checks if is_done)
    missing = [key for key, is_done in checks if not is_done]
    return {"percent": round(done * 100 / total), "complete": done, "total": total, "missing": missing}


def _check(check: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    kind = check["kind"]
    field = check.get("field", "")
    value = _path(profile, field)
    result: dict[str, Any] = {"id": check["id"], "label": check["label"], "source_backed": True}

    if kind == "boolean":
        if value is True:
            result.update(status="pass", explanation="Marked present in the demo profile; not document-verified.")
        elif value is False:
            result.update(status="missing", explanation="The profile says this is not present.")
        else:
            result.update(status="unknown", explanation="Not recorded in the profile.")
    elif kind == "document":
        if value == "available":
            result.update(status="pass", explanation="Self-reported available; Scheme Mitra has not checked the document.")
        elif value == "needs_verification":
            result.update(status="unknown", explanation="Marked for verification; validity has not been checked.")
        else:
            result.update(status="missing", explanation="Not marked available in the profile.")
    elif kind == "area_cap":
        acres = profile.get("land_area_acres")
        if not isinstance(acres, (int, float)):
            result.update(status="unknown", explanation="Land area is missing.")
        elif acres <= check["value"]:
            result.update(status="pass", explanation="Entered area is within the 5-hectare limit stated on the source page. The portal may apply the limit to the eligible plot/component.")
        else:
            result.update(status="review", explanation="Entered area exceeds the source page's stated 5-hectare benefit limit; confirm the eligible area with the department.")
    elif kind == "conditional_boolean":
        pump = profile.get("electric_water_pump", "unknown")
        connection = profile.get("permanent_electric_connection", "unknown")
        if pump == "no":
            result.update(status="not_applicable", explanation="Profile says no electric water pump is used; confirm this matches the proposed setup.")
        elif pump == "yes" and connection == "yes":
            result.update(status="pass", explanation="Both fields are self-reported; electricity-bill evidence is still listed separately.")
        elif pump == "yes" and connection == "no":
            result.update(status="missing", explanation="The source page requires a permanent connection when an electric water pump is used.")
        else:
            result.update(status="unknown", explanation="Confirm whether an electric water pump is used and, if so, whether a permanent connection is available.")
    elif kind == "history":
        if value == "none":
            result.update(status="pass", explanation="Profile says no previous benefit for this item/plot; this history has not been verified.")
        elif value in ("unknown", None, ""):
            result.update(status="unknown", explanation="Previous benefit history is not recorded. The official page describes a 7- or 10-year repeat-benefit restriction depending on the year.")
        else:
            result.update(status="review", explanation="A prior benefit is recorded. Confirm the scheme-specific waiting period and survey/item details on the official portal.")
    elif kind == "crop_tag":
        crop = str(value or "").strip().lower()
        allowed = [str(v).lower() for v in check.get("value", [])]
        if crop == "onion" and "onion" in allowed:
            result.update(status="pass", explanation="The source page includes vegetable/horticulture components and onion-storage infrastructure; this is a relevance signal, not a component-level eligibility decision.")
        elif crop and any(token in crop for token in ("vegetable", "horticulture", "fruit")):
            result.update(status="pass", explanation="Crop label appears relevant to the source page's horticulture scope; confirm the selected component.")
        elif crop:
            result.update(status="review", explanation="The crop label did not clearly match the limited source summary; ask the department about the relevant component.")
        else:
            result.update(status="unknown", explanation="Crop is not recorded.")
    elif kind == "conditional_category":
        category = profile.get("social_category", "not_provided")
        if category in ("sc", "st"):
            doc = profile.get("documents", {}).get("caste_certificate")
            if doc == "available":
                result.update(status="pass", explanation="Certificate is self-reported available; it has not been verified.")
            else:
                result.update(status="missing", explanation="The source page lists a caste certificate for SC/ST applicants.")
        elif category in ("open", "obc", "not_applicable"):
            result.update(status="not_applicable", explanation="The source page makes this document conditional for SC/ST applicants.")
        else:
            result.update(status="unknown", explanation="Social category is not recorded. The profile does not ask for it unless a scheme condition needs it.")
    else:
        if value:
            result.update(status="pass", explanation="A value is recorded; verify the selected item/component against the current official rules.")
        else:
            result.update(status="unknown", explanation="This information is not in the profile and must be checked for the chosen component.")
    return result


def _profile_signal_score(scheme: dict[str, Any], profile: dict[str, Any]) -> int:
    """Return an explainable profile-fit score (never approval probability)."""
    state = str(profile.get("state", "")).strip().lower()
    location = 20 if state in ("maharashtra", "mh") else 0

    need = scheme.get("need")
    needs = [str(item).lower() for item in profile.get("support_needs", [])]
    support = 20 if need in needs else 8

    crop = str(profile.get("crop", "")).strip().lower()
    crop_tags = [str(tag).lower() for tag in scheme.get("crop_tags", [])]
    if crop and crop in crop_tags:
        crop_fit = 20
    elif "*" in crop_tags:
        crop_fit = 12
    elif crop and any(tag in crop for tag in crop_tags):
        crop_fit = 16
    else:
        crop_fit = 0

    completeness = profile_completeness(profile)
    profile_coverage = round(15 * completeness["percent"] / 100)

    docs = profile.get("documents", {})
    core_docs = ["land_7_12", "land_8a"]
    ready = sum(1 for doc in core_docs if docs.get(doc) == "available")
    doc_score = ready * 5

    route_score = 10 if scheme.get("source_url") and scheme.get("application_url") else 0
    raw = location + support + crop_fit + profile_coverage + doc_score + route_score
    return max(0, min(100, raw))


def _match_reasons(scheme: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if str(profile.get("state", "")).strip().lower() in ("maharashtra", "mh"):
        reasons.append("Your profile is in Maharashtra, the state covered by this portal record.")
    need = scheme.get("need")
    needs = [str(item).lower() for item in profile.get("support_needs", [])]
    if need in needs:
        need_label = {"irrigation":"irrigation", "horticulture":"horticulture", "machinery":"farm machinery"}.get(need, need)
        reasons.append(f"You selected {need_label} support as a priority.")
    crop = str(profile.get("crop", "")).strip().lower()
    crop_tags = [str(tag).lower() for tag in scheme.get("crop_tags", [])]
    if crop and crop in crop_tags:
        if scheme.get("slug") == "mission-integrated-horticulture-development" and crop == "onion":
            reasons.append("The source page lists horticulture/vegetable activities and onion-storage infrastructure; confirm the specific component.")
        else:
            reasons.append(f"Your crop ({crop}) appears in the scheme's captured crop scope.")
    elif "*" in crop_tags and crop:
        reasons.append("The captured page summary does not make crop a specific matching condition.")
    if scheme.get("slug") == "pmksy-micro-irrigation":
        area = profile.get("land_area_acres")
        if isinstance(area, (int, float)) and area <= 5 * ACRES_PER_HECTARE:
            reasons.append("Your entered area is within the source page's stated 5-hectare benefit limit; confirm the exact eligible plot/component.")
    docs = profile.get("documents", {})
    available_land = [label for key, label in (("land_7_12", "7/12"), ("land_8a", "8-A")) if docs.get(key) == "available"]
    if available_land:
        reasons.append("Land records marked available (self-reported): " + " and ".join(available_land) + ".")
    if not reasons:
        reasons.append("The limited demo catalog has a related Agriculture Department record; more profile information is needed to explain fit.")
    return reasons[:4]


def evaluate_scheme(scheme: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    checks = [_check(item, profile) for item in scheme.get("checks", [])]
    hard_failures = [c for c in checks if c["status"] == "missing"]
    unknowns = [c for c in checks if c["status"] in ("unknown", "review")]
    score = _profile_signal_score(scheme, profile)
    match_reasons = _match_reasons(scheme, profile)

    # Never call a profile "eligible": the available pages and profile do not
    # establish all component-specific, historical, identity, or application facts.
    if score >= 68:
        status = "POTENTIAL_FIT"
        status_label = "Potential fit — confirm conditions"
    else:
        status = "MORE_INFORMATION_NEEDED"
        status_label = "More information needed"

    documents = []
    for item in scheme.get("document_items", []):
        state = profile.get("documents", {}).get(item["id"], "not_provided")
        if state == "available":
            display_state = "self_reported_available"
        elif state == "needs_verification":
            display_state = "needs_verification"
        elif state in ("not_yet_required", "not_yet_issued"):
            display_state = state
        else:
            display_state = "not_provided"
        documents.append({**item, "state": display_state})

    available = sum(1 for item in documents if item["state"] == "self_reported_available")
    return {
        "scheme_slug": scheme["slug"],
        "profile_match": score,
        "status": status,
        "status_label": status_label,
        "match_reasons": match_reasons,
        "passed_rules": [c for c in checks if c["status"] == "pass"],
        "failed_rules": hard_failures,
        "missing_information": unknowns,
        "checks": checks,
        "documents": documents,
        "documents_available": available,
        "documents_total": len(documents),
        "profile_completeness": profile_completeness(profile),
        "evaluated_note": "Based on the information in this demo profile and the captured source summary. This is not an official eligibility decision or approval probability."
    }


def generate_recommendations(schemes: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for scheme in schemes:
        result = evaluate_scheme(scheme, profile)
        output.append({**scheme, "evaluation": result})
    output.sort(key=lambda item: (item["evaluation"]["profile_match"], item["name"]), reverse=True)
    return output
