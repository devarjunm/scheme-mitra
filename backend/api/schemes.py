from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, func, Integer, select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..dependencies import current_user
from ..eligibility import evaluate_scheme, generate_recommendations, profile_completeness
from ..models import Application, ApplicationStatusHistory, AnalyticsEvent, Feedback, FarmerProfile, FarmerDocument, FarmerLand, FarmerCrop, PilotSurvey, RecommendationSnapshot, SavedScheme, Scheme, User
from ..schemas import ApplicationCreate, ApplicationUpdate, AssistantQuestion, FeedbackCreate, PilotSurveyCreate
from ..services.farmers import profile_dict
from ..services.recommendations import scheme_payload, visible_schemes
from .common import application_payload, record_event, require_scheme

router = APIRouter(prefix="/api/v1", tags=["schemes and action"])


def _ranked(db: Session, user: User) -> list[dict[str, Any]]:
    return generate_recommendations(visible_schemes(db, user), profile_dict(db, user))


@router.get("/schemes")
def list_schemes(q: str = Query(default="", max_length=120), category: str = Query(default="", max_length=80),
                 db: Session = Depends(get_db), user: User = Depends(current_user)):
    records = _ranked(db, user)
    q_norm = q.casefold().strip()
    if q_norm:
        records = [row for row in records if q_norm in " ".join(str(row.get(k, "")) for k in ("name", "name_mr", "summary", "benefit_summary", "department", "category")).casefold()]
    if category:
        records = [row for row in records if row.get("category") == category]
    return {"schemes": records, "count": len(records)}


@router.get("/schemes/{slug}")
def get_scheme(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    scheme = require_scheme(db, slug, user)
    payload = scheme_payload(scheme)
    evaluation = evaluate_scheme(payload, profile_dict(db, user))
    saved = db.scalar(select(SavedScheme.id).where(SavedScheme.user_id == user.id, SavedScheme.scheme_id == scheme.id)) is not None
    record_event(db, user.id, "scheme_viewed", {"scheme_slug": slug})
    db.commit()
    return {"scheme": payload, "evaluation": evaluation, "saved": saved}


@router.get("/recommendations")
def read_recommendations(db: Session = Depends(get_db), user: User = Depends(current_user)):
    result = _ranked(db, user)
    profile = profile_dict(db, user)
    return {"recommendations": result, "profile_completeness": profile_completeness(profile)}


@router.post("/recommendations/generate")
def generate_and_store_recommendations(db: Session = Depends(get_db), user: User = Depends(current_user)):
    results = _ranked(db, user)
    for item in results:
        scheme = db.scalar(select(Scheme).where(Scheme.slug == item["slug"]))
        if scheme:
            db.add(RecommendationSnapshot(user_id=user.id, scheme_id=scheme.id,
                profile_match=item["evaluation"]["profile_match"],
                eligibility_status=item["evaluation"]["status"], result_json=item["evaluation"]))
    record_event(db, user.id, "recommendations_generated", {"count": len(results)})
    db.commit()
    return {"recommendations": results, "profile_completeness": profile_completeness(profile_dict(db, user))}


@router.post("/eligibility/evaluate/{scheme_slug}")
def evaluate_eligibility(scheme_slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    scheme = require_scheme(db, scheme_slug, user)
    return {"scheme_slug": scheme_slug, "result": evaluate_scheme(scheme_payload(scheme), profile_dict(db, user))}


@router.get("/eligibility/{scheme_slug}")
def read_eligibility(scheme_slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    scheme = require_scheme(db, scheme_slug, user)
    return {"scheme_slug": scheme_slug, "result": evaluate_scheme(scheme_payload(scheme), profile_dict(db, user))}


@router.get("/saved")
def saved_schemes(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(SavedScheme).options(joinedload(SavedScheme.scheme)).where(SavedScheme.user_id == user.id).order_by(SavedScheme.saved_at.desc())).all()
    profile = profile_dict(db, user)
    saved = []
    for row in rows:
        item = scheme_payload(row.scheme)
        item["saved_at"] = row.saved_at.isoformat()
        item["evaluation"] = evaluate_scheme(item, profile)
        saved.append(item)
    return {"saved": saved}


@router.post("/saved/{slug}", status_code=status.HTTP_201_CREATED)
def save_scheme(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    scheme = require_scheme(db, slug, user)
    existing = db.scalar(select(SavedScheme).where(SavedScheme.user_id == user.id, SavedScheme.scheme_id == scheme.id))
    if existing is None:
        db.add(SavedScheme(user_id=user.id, scheme_id=scheme.id))
    record_event(db, user.id, "scheme_saved", {"scheme_slug": slug})
    db.commit()
    return {"saved": True, "scheme_slug": slug}


@router.delete("/saved/{slug}")
def unsave_scheme(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    scheme = require_scheme(db, slug, user)
    existing = db.scalar(select(SavedScheme).where(SavedScheme.user_id == user.id, SavedScheme.scheme_id == scheme.id))
    if existing:
        db.delete(existing)
    record_event(db, user.id, "scheme_unsaved", {"scheme_slug": slug})
    db.commit()
    return {"saved": False, "scheme_slug": slug}


@router.get("/applications")
def list_applications(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(Application).options(joinedload(Application.scheme)).where(Application.user_id == user.id).order_by(Application.updated_at.desc())).all()
    return {"applications": [application_payload(row) for row in rows]}


@router.post("/applications", status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    scheme = require_scheme(db, payload.scheme_slug, user)
    item = Application(user_id=user.id, scheme_id=scheme.id, reference=payload.reference, applied_on=payload.applied_on,
                       status=payload.status, notes=payload.notes, status_source="USER_ENTERED")
    db.add(item)
    db.flush()
    db.add(ApplicationStatusHistory(application_id=item.id, old_status="", new_status=payload.status, status_source="USER_ENTERED"))
    record_event(db, user.id, "application_created", {"scheme_slug": scheme.slug, "status": payload.status})
    db.commit()
    db.refresh(item)
    return {"application": application_payload(item), "status_source": "USER_ENTERED"}


@router.get("/applications/{application_id}")
def get_application(application_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Application).options(joinedload(Application.scheme)).where(Application.id == application_id, Application.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=404, detail="Application record not found.")
    return {"application": application_payload(item), "history": [{"old_status": row.old_status, "new_status": row.new_status, "status_source": row.status_source, "created_at": row.created_at.isoformat()} for row in item.history]}


@router.put("/applications/{application_id}")
def update_application(application_id: str, payload: ApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Application).options(joinedload(Application.scheme)).where(Application.id == application_id, Application.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=404, detail="Application record not found.")
    data = payload.model_dump(exclude_unset=True)
    old_status = item.status
    for key, value in data.items():
        setattr(item, key, value)
    if item.status != old_status:
        db.add(ApplicationStatusHistory(application_id=item.id, old_status=old_status, new_status=item.status, status_source="USER_ENTERED"))
    item.status_source = "USER_ENTERED"
    record_event(db, user.id, "application_updated", {"status": item.status})
    db.commit()
    db.refresh(item)
    return {"application": application_payload(item), "status_source": "USER_ENTERED"}


def _assistant_reply(question: str, language: str, scheme: dict | None, profile: dict, catalog: list[dict]) -> dict:
    q = question.casefold()
    lang = language if language in {"en", "mr", "hi"} else "en"
    portal = "https://mahadbt.maharashtra.gov.in/Farmer/"
    if not scheme and any(word in q for word in ("profile", "missing", "complete", "माहिती", "प्रोफ़ाइल", "प्रोफाइल", "अपूर्ण", "कमी", "जानकारी")):
        missing = profile_completeness(profile)
        labels = {
            "en": {"district":"district", "taluka":"taluka", "village":"village", "land":"land area", "crop":"crop", "farmer_category":"farm size category", "irrigation":"irrigation", "aadhaar":"Aadhaar availability", "land_7_12":"7/12 status", "land_8a":"8-A status"},
            "mr": {"district":"जिल्हा", "taluka":"तालुका", "village":"गाव", "land":"जमिनीचे क्षेत्र", "crop":"पीक", "farmer_category":"शेतजमिनीचा गट", "irrigation":"सिंचन", "aadhaar":"आधार उपलब्धता", "land_7_12":"७/१२ स्थिती", "land_8a":"८-अ स्थिती"},
            "hi": {"district":"जिला", "taluka":"तालुका", "village":"गाँव", "land":"भूमि क्षेत्र", "crop":"फसल", "farmer_category":"भूमि श्रेणी", "irrigation":"सिंचाई", "aadhaar":"आधार उपलब्धता", "land_7_12":"7/12 स्थिति", "land_8a":"8-A स्थिति"},
        }[lang]
        fields = ", ".join(labels.get(key, key) for key in missing["missing"])
        if lang == "mr":
            answer = f"तुमची प्रोफाइल माहिती {missing['percent']}% पूर्ण आहे. अजून भरायची माहिती: {fields or 'काही नाही'}. फक्त योजनेसाठी आवश्यक माहिती भरा; खरी ओळखपत्रे किंवा कागदपत्रे येथे देऊ नका."
        elif lang == "hi":
            answer = f"आपकी प्रोफ़ाइल {missing['percent']}% पूरी है। अभी जोड़ने की जानकारी: {fields or 'कोई नहीं'}। केवल योजना के लिए आवश्यक जानकारी दें; असली पहचान विवरण या दस्तावेज़ यहाँ न डालें।"
        else:
            answer = f"Your profile is {missing['percent']}% complete. Still to add: {fields or 'nothing'}. Only add information relevant to a scheme; do not enter identity numbers or real document files."
        return {"answer": answer, "source_name": "Scheme Mitra profile checklist", "source_url": portal, "grounding": "local_profile_data", "ai_provider": "not_configured"}
    if not scheme:
        hits = catalog
        if any(word in q for word in ("irrigation", "सिंचन", "सिंचाई")):
            hits = [item for item in catalog if item.get("category") == "Irrigation"] or catalog
        if not hits:
            answer = {"mr":"सध्या उपलब्ध योजना नोंदीतून मी याची पडताळणी करू शकत नाही. कृपया अधिकृत स्रोत तपासा.", "hi":"उपलब्ध योजना रिकॉर्ड से इसकी पुष्टि नहीं कर सकता। कृपया आधिकारिक स्रोत देखें।", "en":"I could not verify this from the currently published scheme catalog. Please check the official source."}[lang]
            return {"answer": answer, "source_name": "MahaDBT Farmer Portal", "source_url": portal, "grounding": "no_verified_answer", "ai_provider": "not_configured"}
        options = "\n".join(f"• {item.get('name_mr') if lang == 'mr' and item.get('name_mr') else item['name']} — profile match {item['evaluation']['profile_match']}/100" for item in hits[:3])
        intro = {"mr":"उपलब्ध डेमो नोंदीत पाहण्यासारखे पर्याय:", "hi":"उपलब्ध डेमो रिकॉर्ड में देखने योग्य विकल्प:", "en":"From the available catalog, these are options to review:"}[lang]
        caveat = {"mr":"ही पूर्ण यादी नाही. प्रोफाइल जुळवणी ही सरकारी पात्रता किंवा मंजुरी नाही.", "hi":"यह पूरी सूची नहीं है। प्रोफ़ाइल मिलान सरकारी पात्रता या मंज़ूरी नहीं है।", "en":"This is not a complete catalog or an eligibility/approval decision."}[lang]
        return {"answer": intro + "\n\n" + options + "\n\n" + caveat, "source_name": "MahaDBT Farmer Portal", "source_url": hits[0]["source_url"], "grounding": "local_scheme_catalog", "ai_provider": "not_configured"}
    evaluation = scheme["evaluation"]
    if any(word in q for word in ("why", "eligible", "match", "पात्र", "क्यों", "कसे", "जुळ", "मिलान")):
        matched = "; ".join(evaluation.get("match_reasons", [])[:3])
        unknown = "; ".join(check["label"] for check in evaluation.get("missing_information", [])[:4])
        title = scheme.get("name_mr") if lang == "mr" and scheme.get("name_mr") else scheme["name"]
        if lang == "mr":
            answer = f"{title} साठी प्रोफाइल जुळवणी {evaluation['profile_match']}/100 आहे. हा फक्त प्रोफाइल-जुळवणी संकेत आहे; पात्रता किंवा मंजुरी नाही.\n\nजुळण्याची कारणे (स्रोत नोंदीतील मजकूर): {matched or 'नोंदलेली माहिती मर्यादित आहे'}.\n\nअधिकृत अटी तपासा: {unknown or 'निवडलेल्या घटकाच्या सर्व अटी'}. अंतिम पात्रता संबंधित विभाग ठरवतो."
        elif lang == "hi":
            answer = f"{title} के लिए प्रोफ़ाइल मिलान {evaluation['profile_match']}/100 है। यह केवल प्रोफ़ाइल-मिलान संकेत है; पात्रता या मंज़ूरी नहीं।\n\nमिलान के कारण (स्रोत रिकॉर्ड का पाठ): {matched or 'दर्ज जानकारी सीमित है'}।\n\nआधिकारिक शर्तें जाँचें: {unknown or 'चुने गए घटक की सभी शर्तें'}। अंतिम पात्रता संबंधित विभाग तय करता है।"
        else:
            answer = f"{title} has a profile match of {evaluation['profile_match']}/100. This is profile overlap only, not eligibility or approval.\n\nWhy it appears (captured rule notes): {matched or 'available profile signals are limited'}.\n\nStill to confirm: {unknown or 'the complete official component conditions'}. Final eligibility is decided by the department."
    elif any(word in q for word in ("document", "paper", "कागद", "दस्तावेज", "कागजात")):
        docs = evaluation.get("documents", [])
        status_words = {
            "en": {"self_reported_available":"self-reported available", "not_yet_required":"not yet required", "not_yet_issued":"issued through the official process", "needs_verification":"needs verification", "not_provided":"not marked available"},
            "mr": {"self_reported_available":"स्वतः उपलब्ध असल्याचे नोंदवले", "not_yet_required":"अजून आवश्यक नाही", "not_yet_issued":"अधिकृत प्रक्रियेतून मिळेल", "needs_verification":"पडताळणी आवश्यक", "not_provided":"उपलब्ध म्हणून नोंद नाही"},
            "hi": {"self_reported_available":"स्वयं उपलब्ध बताया", "not_yet_required":"अभी आवश्यक नहीं", "not_yet_issued":"आधिकारिक प्रक्रिया से मिलेगा", "needs_verification":"सत्यापन आवश्यक", "not_provided":"उपलब्ध दर्ज नहीं"},
        }[lang]
        items = "\n".join(f"• {x['label']} — {status_words.get(x['state'], x['state'])}" for x in docs)
        intro = {"mr":"स्रोत पृष्ठावर दिलेली कागदपत्रे; स्थिती स्वतः नोंदवलेली आहे आणि फाइल तपासलेली नाही:", "hi":"स्रोत पृष्ठ पर दिए दस्तावेज़; स्थिति स्वयं बताई गई है और कोई फ़ाइल जाँची नहीं गई:", "en":"The source page lists these items; checklist states are self-reported and no files are validated:"}[lang]
        answer = intro + "\n\n" + items
    elif any(word in q for word in ("apply", "where", "अर्ज", "कुठे", "आवेदन", "कहाँ")):
        lead = {"mr":"योजना मित्र अर्ज पाठवत नाही. अधिकृत पोर्टलवर पुढे जा:", "hi":"योजना मित्र आवेदन जमा नहीं करता। आधिकारिक पोर्टल पर आगे बढ़ें:", "en":"Scheme Mitra does not submit applications. Continue on the official portal:"}[lang]
        answer = lead + " " + scheme.get("application_url", "")
    elif any(word in q for word in ("benefit", "amount", "लाभ", "अनुदान", "रक्कम")):
        caveat = {"mr":"अंतिम लाभ सध्याच्या अधिकृत अटी आणि मंजुरीवर अवलंबून आहे.", "hi":"अंतिम लाभ वर्तमान आधिकारिक शर्तों और मंज़ूरी पर निर्भर है।", "en":"Final benefit depends on current official conditions and approval."}[lang]
        answer = scheme.get("benefit_summary", "No verified benefit summary is available.") + " " + caveat
    else:
        closing = {"mr":"स्रोत नोंदीत नसलेली अट अधिकृत पृष्ठावर तपासा.", "hi":"स्रोत रिकॉर्ड में न दी गई शर्त आधिकारिक पृष्ठ पर जाँचें।", "en":"If a fact is not in the captured page summary, verify it on the official source."}[lang]
        answer = scheme.get("summary", "") + "\n\n" + closing
    return {"answer": answer, "source_name": scheme["source_name"], "source_url": scheme["source_url"], "grounding": "local_official_source_summary", "ai_provider": "not_configured"}


@router.post("/assistant/question")
def ask_assistant(payload: AssistantQuestion, db: Session = Depends(get_db), user: User = Depends(current_user)):
    catalog = _ranked(db, user)
    selected = None
    if payload.scheme_slug:
        scheme_row = require_scheme(db, payload.scheme_slug, user)
        selected = scheme_payload(scheme_row)
        selected["evaluation"] = evaluate_scheme(selected, profile_dict(db, user))
    response = _assistant_reply(payload.question, payload.language, selected, profile_dict(db, user), catalog)
    record_event(db, user.id, "assistant_question", {"scheme_slug": payload.scheme_slug or "", "grounding": response["grounding"]})
    db.commit()
    return response


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    scheme_id = None
    if payload.scheme_slug:
        scheme_id = require_scheme(db, payload.scheme_slug, user).id
    db.add(Feedback(user_id=user.id, scheme_id=scheme_id, useful=payload.useful, reason=payload.reason))
    record_event(db, user.id, "feedback_submitted", {"scheme_slug": payload.scheme_slug or "recommendation_set", "useful": payload.useful})
    db.commit()
    return {"saved": True}


@router.post("/recommendation-feedback", status_code=status.HTTP_201_CREATED)
def recommendation_feedback(payload: FeedbackCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    db.add(Feedback(user_id=user.id, scheme_id=None, useful=payload.useful, reason=payload.reason or "recommendation_set"))
    record_event(db, user.id, "feedback_submitted", {"scope": "recommendations", "useful": payload.useful})
    db.commit()
    return {"saved": True, "scope": "recommendations"}


@router.post("/pilot-surveys", status_code=status.HTTP_201_CREATED)
def submit_survey(payload: PilotSurveyCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = PilotSurvey(user_id=user.id, **payload.model_dump())
    db.add(item)
    record_event(db, user.id, "pilot_survey_submitted", {"phase": payload.phase})
    db.commit()
    return {"saved": True, "disclaimer": "A single entry is not representative evidence."}


@router.get("/pilot-metrics")
def read_pilot_metrics(db: Session = Depends(get_db), user: User = Depends(current_user)):
    event_rows = db.execute(select(AnalyticsEvent.event_name, func.count(AnalyticsEvent.id)).where(AnalyticsEvent.user_id == user.id).group_by(AnalyticsEvent.event_name)).all()
    events = {name: count for name, count in event_rows}
    survey_rows = db.execute(select(PilotSurvey.phase, func.count(PilotSurvey.id), func.avg(PilotSurvey.time_minutes)).where(PilotSurvey.user_id == user.id).group_by(PilotSurvey.phase)).all()
    surveys = {phase: {"count": count, "average_time_minutes": round(avg, 1) if avg is not None else None} for phase, count, avg in survey_rows}
    fb = db.execute(select(func.count(Feedback.id), func.sum(cast(Feedback.useful, Integer))).where(Feedback.user_id == user.id)).one()
    return {"events": events, "baseline_surveys": surveys.get("baseline", {"count": 0, "average_time_minutes": None}),
            "post_use_surveys": surveys.get("post_use", {"count": 0, "average_time_minutes": None}),
            "feedback": {"total": fb[0] or 0, "useful": fb[1] or 0},
            "disclaimer": "User-scoped product/demo events only. These are not pilot results or impact claims."}


@router.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(payload: dict, db: Session = Depends(get_db), user: User = Depends(current_user)):
    name = payload.get("event_name") if isinstance(payload, dict) else None
    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    if name != "official_application_click" or not isinstance(metadata, dict) or set(metadata) != {"scheme_slug"}:
        raise HTTPException(status_code=400, detail="Unsupported event.")
    slug = metadata.get("scheme_slug")
    if not isinstance(slug, str) or len(slug) > 140:
        raise HTTPException(status_code=400, detail="Unsupported event.")
    require_scheme(db, slug, user)
    record_event(db, user.id, name, {"scheme_slug": slug})
    db.commit()
    return {"recorded": True}
