const API = "/api/v1";
const appState = {
  profile: null,
  user: null,
  completeness: null,
  recommendations: [],
  schemes: [],
  saved: [],
  applications: [],
  activePage: "overview",
  activeFilter: "all",
  search: "",
  selectedScheme: null,
  language: localStorage.getItem("schememitra-language") || "en",
  toastTimer: null
};

const translations = {
  en: {
    taglineShort:"A clearer next step", workspace:"FARMER WORKSPACE", navOverview:"Overview", navFind:"Find schemes", navSaved:"Saved schemes", navApplications:"Applications", navPilot:"Pilot evidence", needHelp:"Need a hand?", askAssistant:"Ask Scheme Mitra", crumbWorkspace:"Farmer workspace", demoWorkspace:"DEMO FARMER WORKSPACE", hello:"Namaskar", homeIntro:"See scheme options that may fit your farm, with the reasons and next steps.", editProfile:"Edit profile", heroKicker:"PERSONALIZED FOR YOUR FARM", heroTitle:"Find support that fits your next step.", heroBody:"A short, explainable shortlist — built from your farm profile and official scheme pages.", findForMe:"Find schemes for me", rulesNote:"Rule-based matching · No AI approval guesses", sourceBacked:"Source-backed", explainable:"and explainable", yourFarm:"YOUR FARM PROFILE", profileCompleteness:"Profile completeness", completeProfile:"Complete profile", ofProfile:"of 10 details added", profileMissingDefault:"Add your village to make local matching clearer.", nextStep:"NEXT STEP", nextStepTitle:"Check your irrigation documents", nextStepBody:"Your profile points to micro-irrigation support. Confirm the pump connection and review the source checklist.", twoLandRecords:"7/12 and 8-A marked available", seeChecklist:"See document checklist", basedOnProfile:"BASED ON YOUR PROFILE", pathsTitle:"A few paths to explore", viewAll:"View all", trustTitle:"Guidance, not a government decision", trustBody:"Scheme Mitra explains a profile match. Final eligibility and approval are decided by the concerned department.", sourceReview:"Source pages checked 07 Oct 2026", findEyebrow:"SCHEME DISCOVERY", findTitle:"Matches for your farm", findIntro:"Ranked by profile fit. Open any result to see the rule checks and what still needs confirmation.", searchPlaceholder:"Search crop, benefit or scheme", filterAll:"All schemes", filterIrrigation:"Irrigation", filterHorticulture:"Horticulture", filterMachinery:"Machinery", resultText:"scheme pathways in this demo catalog", matchKey:"Profile match ≠ approval probability", feedbackQuestion:"Were these recommendations useful?", feedbackSub:"Your response helps us check relevance. It does not change official rules.", yesUseful:"Yes, useful", notYet:"Not yet", yourShortlist:"YOUR SHORTLIST", savedTitle:"Saved schemes", savedIntro:"Keep promising options together while you confirm the details.", noSavedTitle:"Nothing saved yet", noSavedBody:"Save a scheme from your shortlist and it will appear here.", browseSchemes:"Browse schemes", yourRecords:"YOUR RECORDS", applicationsTitle:"Application tracker", applicationsIntro:"Record your own progress. Scheme Mitra does not receive live status from MahaDBT.", addRecord:"Add a record", manualTracker:"Manual tracker only", manualTrackerBody:"Every status below is entered by the farmer and is not verified by a government system.", noAppsTitle:"No application records", noAppsBody:"When you apply through the official portal, you can note your own reference here.", addFirstRecord:"Add your first record", evidenceEyebrow:"SEVA FIRST · FIELD EVIDENCE", pilotTitle:"Measure the service, not the story", pilotIntro:"This panel records demo interactions and survey entries. It does not claim farmer impact.", demoEvents:"Demo events only", demoEventsBody:"Counts below reflect this local app database. They are not field-pilot results or representative survey data.", captureObservation:"CAPTURE AN OBSERVATION", surveyTitle:"Short pilot survey", noPersonalData:"No identity fields", surveyPhase:"Survey phase", baseline:"Before using the tool", postUse:"After using the tool", timeQuestion:"Time to identify a relevant scheme (minutes)", relevantKnown:"Could the farmer name a relevant scheme?", yes:"Yes", no:"No", unsure:"Not recorded", docsKnown:"Could the farmer identify the required documents?", nextStepKnown:"Did the farmer know the next step?", observationNotes:"Observation (optional; no names or sensitive details)", observationPlaceholder:"What caused confusion? What helped?", consentNote:"Use only with informed consent. Enter real field results only after they are actually collected.", saveObservation:"Save observation", savedObservation:"Observation saved.", challengeReadiness:"CHALLENGE READINESS", evidenceNeeded:"Evidence still needed", fieldInterviews:"Farmer interviews", fieldInterviewsBody:"Problem frequency, current process, time spent.", baselinePost:"Before/after baseline", baselinePostBody:"Same task, measured with real participants.", ownerPilot:"Department owner & pilot", ownerPilotBody:"Identify a proposed owner; do not imply a partnership.", costEvidence:"Cost & sustainability", costEvidenceBody:"Estimate unit costs and validate them in a pilot.", openEvidencePlan:"Open evidence plan", footerSources:"Official source pages checked 07 Oct 2026 · No government affiliation claimed", importantNote:"Important note", editYourProfile:"Tell us about your farm", profilePrivacy:"Only use the synthetic demo profile here. The MVP does not need Aadhaar numbers or document uploads.", nameLabel:"Name", districtLabel:"District", talukaLabel:"Taluka", villageLabel:"Village (optional)", landAreaLabel:"How much land do you farm? (acres)", cropLabel:"Main crop", farmerCategory:"Farm size category", socialCategory:"Social category (only when a scheme asks)", irrigationLabel:"Do you have irrigation?", electricPump:"Do you use an electric water pump?", permanentConnection:"Permanent electricity connection?", previousMicro:"Previous micro-irrigation benefit on this plot?", supportNeedLabel:"What support are you looking for? (choose any)", needIrrigation:"Irrigation", needHorticulture:"Horticulture", needMachinery:"Machinery", aadhaarPresence:"Aadhaar is available (do not enter the number)", land712Available:"7/12 extract marked available", land8aAvailable:"8-A extract marked available", selfReportNote:"Checklist states are self-reported only. Do not upload real documents or identifiers in this demo.", cancel:"Cancel", saveProfile:"Save demo profile", manualRecord:"USER-ENTERED RECORD", addApplicationTitle:"Add application record", applicationNote:"This only records what you enter. It does not submit or verify an application.", schemeLabel:"Scheme", statusLabel:"Status", dateLabel:"Application date", referenceLabel:"Reference number (optional)", notesLabel:"Notes (optional)", saveRecord:"Save record", groundedDemo:"GROUNDED DEMO ASSISTANT", assistantTitle:"Ask about a scheme", assistantSub:"Answers use the captured official scheme notes, not a live government API.", askAbout:"Ask about", suggestWhy:"Why did this match?", suggestDocs:"Which documents?", suggestApply:"Where do I apply?", assistantPlaceholder:"Ask a question in English...", assistantDisclaimer:"If a fact is not in the source summary, the assistant will say it cannot verify it. Final decisions belong to the department.", guidanceNotDecision:"Guidance, not a decision", fullDisclaimer:"Scheme Mitra is an independent demo. It is not part of MahaDBT or any government department. The source pages are linked and were checked on 7 October 2026; summaries need human domain review before a live pilot. A profile match is not eligibility or approval. The demo does not submit applications, verify uploaded documents, or receive official application status.", privacyDisclaimer:"This demo stores account email and farm-profile data. Use only fictional or test details. Never enter real Aadhaar or bank details or upload real documents; secure document storage and independent privacy/security review are not in place.", understood:"Understood"
  },
  mr: {
    taglineShort:"पुढचे पाऊल अधिक स्पष्ट", workspace:"शेतकरी कार्यक्षेत्र", navOverview:"आढावा", navFind:"योजना शोधा", navSaved:"जतन केलेल्या योजना", navApplications:"अर्ज नोंदी", navPilot:"पायलट पुरावे", needHelp:"मदत हवी आहे?", askAssistant:"योजना मित्राला विचारा", crumbWorkspace:"शेतकरी कार्यक्षेत्र", demoWorkspace:"डेमो शेतकरी कार्यक्षेत्र", hello:"नमस्कार", homeIntro:"तुमच्या शेतीला लागू पडू शकणाऱ्या योजना, जुळण्याची कारणे आणि पुढची पावले पाहा.", editProfile:"माहिती बदला", heroKicker:"तुमच्या शेतीसाठी वैयक्तिक", heroTitle:"पुढच्या पावलासाठी योग्य मदत शोधा.", heroBody:"तुमच्या शेतीच्या माहितीतून आणि अधिकृत योजना पृष्ठांवरून तयार केलेली समजण्यास सोपी यादी.", findForMe:"माझ्यासाठी योजना शोधा", rulesNote:"नियमांवर आधारित जुळवणी · AI मंजुरीचा अंदाज नाही", sourceBacked:"स्रोतावर आधारित", explainable:"आणि समजावून सांगता येणारे", yourFarm:"तुमच्या शेतीची माहिती", profileCompleteness:"माहितीची पूर्णता", completeProfile:"माहिती पूर्ण करा", ofProfile:"१० पैकी माहिती भरली", profileMissingDefault:"स्थानिक जुळवणीसाठी गावाचे नाव जोडा.", nextStep:"पुढचे पाऊल", nextStepTitle:"सिंचनाची कागदपत्रे तपासा", nextStepBody:"तुमच्या माहितीनुसार सूक्ष्म सिंचन योजना पाहता येईल. पंपाची जोडणी तपासा आणि अधिकृत यादी पाहा.", twoLandRecords:"७/१२ आणि ८-अ उपलब्ध म्हणून नोंद", seeChecklist:"कागदपत्रांची यादी पाहा", basedOnProfile:"तुमच्या माहितीनुसार", pathsTitle:"पाहण्यासारखे काही पर्याय", viewAll:"सर्व पाहा", trustTitle:"माहिती — सरकारी निर्णय नाही", trustBody:"योजना मित्र प्रोफाइल जुळवणी समजावतो. अंतिम पात्रता आणि मंजुरी संबंधित विभाग ठरवतो.", sourceReview:"अधिकृत स्रोत पृष्ठे ७ ऑक्टोबर २०२६ रोजी तपासली", findEyebrow:"योजना शोध", findTitle:"तुमच्या शेतीशी जुळणारे पर्याय", findIntro:"प्रोफाइल जुळवणीनुसार क्रम. नियम आणि अजून तपासायची माहिती पाहण्यासाठी योजना उघडा.", searchPlaceholder:"पीक, लाभ किंवा योजना शोधा", filterAll:"सर्व योजना", filterIrrigation:"सिंचन", filterHorticulture:"फलोत्पादन", filterMachinery:"यंत्रसामग्री", resultText:"डेमो कॅटलॉगमधील योजना पर्याय", matchKey:"प्रोफाइल जुळवणी ≠ मंजुरीची शक्यता", feedbackQuestion:"या सूचना उपयोगी ठरल्या का?", feedbackSub:"तुमचे उत्तर उपयुक्तता तपासण्यास मदत करते; सरकारी नियम बदलत नाहीत.", yesUseful:"हो, उपयोगी", notYet:"अजून नाही", yourShortlist:"तुमची यादी", savedTitle:"जतन केलेल्या योजना", savedIntro:"तपशील तपासत असताना उपयोगी पर्याय एकत्र ठेवा.", noSavedTitle:"अजून काही जतन केलेले नाही", noSavedBody:"यादीतून योजना जतन करा; ती येथे दिसेल.", browseSchemes:"योजना पाहा", yourRecords:"तुमच्या नोंदी", applicationsTitle:"अर्ज नोंदवही", applicationsIntro:"तुमची प्रगती स्वतः नोंदवा. योजना मित्राला महा-डीबीटीची थेट स्थिती मिळत नाही.", addRecord:"नोंद जोडा", manualTracker:"फक्त स्वतःची नोंद", manualTrackerBody:"खालील प्रत्येक स्थिती शेतकऱ्याने भरलेली आहे; सरकारी प्रणालीने पडताळलेली नाही.", noAppsTitle:"अर्जाच्या नोंदी नाहीत", noAppsBody:"अधिकृत पोर्टलवर अर्ज केल्यावर संदर्भ क्रमांकाची स्वतःची नोंद येथे ठेवा.", addFirstRecord:"पहिली नोंद जोडा", evidenceEyebrow:"सेवा प्रथम · प्रत्यक्ष पुरावे", pilotTitle:"कथा नव्हे, सेवेचा परिणाम मोजा", pilotIntro:"येथे डेमो वापर आणि सर्वेक्षण नोंदवले जाते. शेतकऱ्यांवरील परिणामाचा दावा नाही.", demoEvents:"फक्त डेमो वापर", demoEventsBody:"खालील आकडे स्थानिक डेमो डेटाबेसमधील आहेत. ते पायलटचे निकाल किंवा प्रतिनिधिक सर्वेक्षण नाहीत.", captureObservation:"निरीक्षण नोंदवा", surveyTitle:"लहान पायलट सर्वेक्षण", noPersonalData:"ओळख माहिती नाही", surveyPhase:"सर्वेक्षणाची वेळ", baseline:"साधन वापरण्यापूर्वी", postUse:"साधन वापरल्यानंतर", timeQuestion:"योग्य योजना शोधण्यास लागलेला वेळ (मिनिटे)", relevantKnown:"शेतकऱ्याला योग्य योजनेचे नाव सांगता आले का?", yes:"होय", no:"नाही", unsure:"नोंद नाही", docsKnown:"आवश्यक कागदपत्रे ओळखता आली का?", nextStepKnown:"पुढचे पाऊल माहीत होते का?", observationNotes:"निरीक्षण (ऐच्छिक; नावे किंवा संवेदनशील माहिती नको)", observationPlaceholder:"कशामुळे गोंधळ झाला? काय उपयोगी ठरले?", consentNote:"माहितीपूर्ण संमती घेऊनच वापरा. प्रत्यक्ष निकाल प्रत्यक्ष गोळा केल्यानंतरच भरा.", saveObservation:"निरीक्षण जतन करा", savedObservation:"निरीक्षण जतन झाले.", challengeReadiness:"चॅलेंज तयारी", evidenceNeeded:"अजून आवश्यक पुरावे", fieldInterviews:"शेतकरी मुलाखती", fieldInterviewsBody:"समस्या किती वेळा येते, सध्याची पद्धत, लागणारा वेळ.", baselinePost:"वापरापूर्वी/नंतर तुलना", baselinePostBody:"प्रत्यक्ष सहभागींनी तोच प्रश्न सोडवताना मोजमाप.", ownerPilot:"विभागीय मालक व पायलट", ownerPilotBody:"संभाव्य विभाग ओळखा; भागीदारी असल्याचा दावा करू नका.", costEvidence:"खर्च व टिकाव", costEvidenceBody:"प्रति वापरकर्ता खर्चाचा अंदाज घ्या आणि पायलटमध्ये तपासा.", openEvidencePlan:"पुरावा योजना उघडा", footerSources:"अधिकृत पृष्ठे ७ ऑक्टोबर २०२६ रोजी तपासली · सरकारी संलग्नतेचा दावा नाही", importantNote:"महत्त्वाची सूचना", editYourProfile:"तुमच्या शेतीबद्दल सांगा", profilePrivacy:"येथे फक्त बनावट डेमो माहिती वापरा. आधार क्रमांक किंवा कागदपत्रे अपलोड करण्याची गरज नाही.", nameLabel:"नाव", districtLabel:"जिल्हा", talukaLabel:"तालुका", villageLabel:"गाव (ऐच्छिक)", landAreaLabel:"तुमच्याकडे किती जमीन आहे? (एकर)", cropLabel:"मुख्य पीक", farmerCategory:"जमिनीचा प्रकार", socialCategory:"सामाजिक प्रवर्ग (योजनेने विचारल्यासच)", irrigationLabel:"सिंचन आहे का?", electricPump:"वीज पंप वापरता का?", permanentConnection:"कायमची वीज जोडणी आहे का?", previousMicro:"या शेतावर पूर्वी सूक्ष्म सिंचनाचा लाभ घेतला आहे का?", supportNeedLabel:"तुम्हाला कोणत्या मदतीची गरज आहे?", needIrrigation:"सिंचन", needHorticulture:"फलोत्पादन", needMachinery:"यंत्रसामग्री", aadhaarPresence:"आधार उपलब्ध आहे (क्रमांक टाकू नका)", land712Available:"७/१२ उतारा उपलब्ध म्हणून नोंद", land8aAvailable:"८-अ उतारा उपलब्ध म्हणून नोंद", selfReportNote:"कागदपत्रांची स्थिती स्वतः नोंदवलेली आहे. या डेमोमध्ये खरी कागदपत्रे अपलोड करू नका.", cancel:"रद्द करा", saveProfile:"डेमो माहिती जतन करा", manualRecord:"वापरकर्त्याने नोंदवलेले", addApplicationTitle:"अर्जाची नोंद जोडा", applicationNote:"ही फक्त तुमची नोंद आहे. अर्ज पाठवला किंवा पडताळला जात नाही.", schemeLabel:"योजना", statusLabel:"स्थिती", dateLabel:"अर्जाची तारीख", referenceLabel:"संदर्भ क्रमांक (ऐच्छिक)", notesLabel:"टीप (ऐच्छिक)", saveRecord:"नोंद जतन करा", groundedDemo:"स्रोताधारित डेमो सहाय्यक", assistantTitle:"योजनेबद्दल विचारा", assistantSub:"उत्तरे नोंदवलेल्या अधिकृत स्रोतांवर आधारित; थेट सरकारी API नाही.", askAbout:"याबद्दल विचारा", suggestWhy:"हे का जुळले?", suggestDocs:"कागदपत्रे कोणती?", suggestApply:"अर्ज कुठे करायचा?", assistantPlaceholder:"मराठी किंवा इंग्रजीत प्रश्न विचारा...", assistantDisclaimer:"स्रोत नोंदीत माहिती नसेल तर सहाय्यक ते स्पष्ट सांगेल. अंतिम निर्णय विभागाचा आहे.", guidanceNotDecision:"मार्गदर्शन, सरकारी निर्णय नाही", fullDisclaimer:"योजना मित्र हा स्वतंत्र डेमो आहे. तो महा-डीबीटी किंवा कोणत्याही सरकारी विभागाचा भाग नाही. अधिकृत स्रोत पृष्ठे लिंक केली आहेत आणि ७ ऑक्टोबर २०२६ रोजी तपासली; प्रत्यक्ष पायलटपूर्वी तज्ज्ञांकडून नियम तपासणे आवश्यक आहे. प्रोफाइल जुळवणी ही पात्रता किंवा मंजुरी नाही. डेमो अर्ज पाठवत नाही, कागदपत्रे पडताळत नाही आणि अधिकृत स्थिती घेत नाही.", privacyDisclaimer:"या डेमोमध्ये खाते ईमेल आणि शेतीची माहिती साठवली जाते. फक्त काल्पनिक किंवा चाचणी माहिती वापरा. खरा आधार किंवा बँक तपशील टाकू नका; खरी कागदपत्रे अपलोड करू नका. सुरक्षित दस्तऐवज साठवण आणि स्वतंत्र गोपनीयता/सुरक्षा तपासणी झालेली नाही.", understood:"समजले"
  },
  hi: {
    taglineShort:"अगला कदम, अधिक स्पष्ट", workspace:"किसान कार्यक्षेत्र", navOverview:"अवलोकन", navFind:"योजनाएँ खोजें", navSaved:"सहेजी योजनाएँ", navApplications:"आवेदन रिकॉर्ड", navPilot:"पायलट साक्ष्य", needHelp:"मदद चाहिए?", askAssistant:"योजना मित्र से पूछें", crumbWorkspace:"किसान कार्यक्षेत्र", demoWorkspace:"डेमो किसान कार्यक्षेत्र", hello:"नमस्कार", homeIntro:"अपने खेत से मेल खा सकने वाली योजनाएँ, कारण और अगले कदम देखें।", editProfile:"प्रोफ़ाइल बदलें", heroKicker:"आपके खेत के लिए व्यक्तिगत", heroTitle:"अगले कदम के लिए सही सहायता खोजें।", heroBody:"आपकी खेती की जानकारी और आधिकारिक योजना पृष्ठों से बनी समझने योग्य सूची।", findForMe:"मेरे लिए योजनाएँ खोजें", rulesNote:"नियम-आधारित मिलान · AI मंज़ूरी का अनुमान नहीं", sourceBacked:"स्रोत-आधारित", explainable:"और समझने योग्य", yourFarm:"आपकी खेती की जानकारी", profileCompleteness:"प्रोफ़ाइल पूर्णता", completeProfile:"प्रोफ़ाइल पूरी करें", ofProfile:"10 में से विवरण जोड़े गए", profileMissingDefault:"स्थानीय मिलान के लिए गाँव का नाम जोड़ें।", nextStep:"अगला कदम", nextStepTitle:"सिंचाई के दस्तावेज़ जाँचें", nextStepBody:"आपकी जानकारी सूक्ष्म सिंचाई सहायता से मेल खा सकती है। पंप कनेक्शन और आधिकारिक सूची जाँचें।", twoLandRecords:"7/12 और 8-A उपलब्ध के रूप में दर्ज", seeChecklist:"दस्तावेज़ सूची देखें", basedOnProfile:"आपकी प्रोफ़ाइल के आधार पर", pathsTitle:"कुछ विकल्प देखें", viewAll:"सभी देखें", trustTitle:"मार्गदर्शन, सरकारी निर्णय नहीं", trustBody:"योजना मित्र प्रोफ़ाइल मिलान समझाता है। अंतिम पात्रता और मंज़ूरी संबंधित विभाग तय करता है।", sourceReview:"आधिकारिक स्रोत पृष्ठ 07 Oct 2026 को देखे गए", findEyebrow:"योजना खोज", findTitle:"आपके खेत से मेल खाते विकल्प", findIntro:"प्रोफ़ाइल मिलान के अनुसार क्रमबद्ध। नियम और बाकी जानकारी देखने के लिए परिणाम खोलें।", searchPlaceholder:"फसल, लाभ या योजना खोजें", filterAll:"सभी योजनाएँ", filterIrrigation:"सिंचाई", filterHorticulture:"बागवानी", filterMachinery:"मशीनरी", resultText:"डेमो सूची में योजना विकल्प", matchKey:"प्रोफ़ाइल मिलान ≠ मंज़ूरी की संभावना", feedbackQuestion:"क्या ये सुझाव उपयोगी थे?", feedbackSub:"आपकी प्रतिक्रिया प्रासंगिकता जाँचने में मदद करती है; सरकारी नियम नहीं बदलती।", yesUseful:"हाँ, उपयोगी", notYet:"अभी नहीं", yourShortlist:"आपकी सूची", savedTitle:"सहेजी योजनाएँ", savedIntro:"जानकारी की पुष्टि करते समय उपयोगी विकल्प साथ रखें।", noSavedTitle:"अभी कुछ सहेजा नहीं", noSavedBody:"अपनी सूची से कोई योजना सहेजें; वह यहाँ दिखेगी।", browseSchemes:"योजनाएँ देखें", yourRecords:"आपके रिकॉर्ड", applicationsTitle:"आवेदन ट्रैकर", applicationsIntro:"अपनी प्रगति स्वयं दर्ज करें। योजना मित्र को MahaDBT की लाइव स्थिति नहीं मिलती।", addRecord:"रिकॉर्ड जोड़ें", manualTracker:"केवल मैन्युअल ट्रैकर", manualTrackerBody:"नीचे की हर स्थिति किसान द्वारा दर्ज है, सरकारी प्रणाली से सत्यापित नहीं।", noAppsTitle:"कोई आवेदन रिकॉर्ड नहीं", noAppsBody:"आधिकारिक पोर्टल पर आवेदन करने के बाद अपना संदर्भ यहाँ लिखें।", addFirstRecord:"पहला रिकॉर्ड जोड़ें", evidenceEyebrow:"सेवा पहले · क्षेत्रीय साक्ष्य", pilotTitle:"कहानी नहीं, सेवा मापें", pilotIntro:"यह पैनल डेमो गतिविधि और सर्वे दर्ज करता है। किसान प्रभाव का दावा नहीं करता।", demoEvents:"केवल डेमो गतिविधि", demoEventsBody:"नीचे की संख्या स्थानीय डेमो डेटाबेस की है। यह पायलट या प्रतिनिधि सर्वे परिणाम नहीं है।", captureObservation:"अवलोकन दर्ज करें", surveyTitle:"संक्षिप्त पायलट सर्वे", noPersonalData:"पहचान जानकारी नहीं", surveyPhase:"सर्वे चरण", baseline:"उपयोग से पहले", postUse:"उपयोग के बाद", timeQuestion:"प्रासंगिक योजना खोजने में समय (मिनट)", relevantKnown:"क्या किसान प्रासंगिक योजना बता सका?", yes:"हाँ", no:"नहीं", unsure:"दर्ज नहीं", docsKnown:"क्या किसान आवश्यक दस्तावेज़ पहचान सका?", nextStepKnown:"क्या किसान अगला कदम जानता था?", observationNotes:"अवलोकन (वैकल्पिक; नाम/संवेदनशील विवरण नहीं)", observationPlaceholder:"किस बात से भ्रम हुआ? क्या मददगार था?", consentNote:"सूचित सहमति के साथ ही उपयोग करें। वास्तविक परिणाम तभी दर्ज करें जब वे सच में एकत्र हों।", saveObservation:"अवलोकन सहेजें", savedObservation:"अवलोकन सहेजा गया।", challengeReadiness:"चैलेंज तैयारी", evidenceNeeded:"अभी आवश्यक साक्ष्य", fieldInterviews:"किसान साक्षात्कार", fieldInterviewsBody:"समस्या की आवृत्ति, मौजूदा प्रक्रिया, लगा समय।", baselinePost:"पहले/बाद का आधार", baselinePostBody:"वास्तविक प्रतिभागियों के साथ वही काम मापें।", ownerPilot:"विभागीय स्वामी और पायलट", ownerPilotBody:"प्रस्तावित स्वामी पहचानें; साझेदारी का दावा न करें।", costEvidence:"लागत और स्थिरता", costEvidenceBody:"इकाई लागत का अनुमान लगाकर पायलट में जाँचें।", openEvidencePlan:"साक्ष्य योजना खोलें", footerSources:"आधिकारिक पृष्ठ 07 Oct 2026 को देखे गए · सरकारी संबद्धता का दावा नहीं", importantNote:"महत्वपूर्ण सूचना", editYourProfile:"अपने खेत के बारे में बताएँ", profilePrivacy:"यहाँ केवल कृत्रिम डेमो प्रोफ़ाइल उपयोग करें। आधार नंबर या दस्तावेज़ अपलोड न करें।", nameLabel:"नाम", districtLabel:"ज़िला", talukaLabel:"तालुका", villageLabel:"गाँव (वैकल्पिक)", landAreaLabel:"आप कितनी ज़मीन पर खेती करते हैं? (एकड़)", cropLabel:"मुख्य फसल", farmerCategory:"भूमि श्रेणी", socialCategory:"सामाजिक श्रेणी (केवल योजना पूछे तो)", irrigationLabel:"क्या सिंचाई है?", electricPump:"क्या बिजली पंप उपयोग करते हैं?", permanentConnection:"स्थायी बिजली कनेक्शन?", previousMicro:"इस खेत पर पहले सूक्ष्म सिंचाई लाभ मिला?", supportNeedLabel:"आपको किस सहायता की ज़रूरत है?", needIrrigation:"सिंचाई", needHorticulture:"बागवानी", needMachinery:"मशीनरी", aadhaarPresence:"आधार उपलब्ध है (नंबर न लिखें)", land712Available:"7/12 उपलब्ध के रूप में दर्ज", land8aAvailable:"8-A उपलब्ध के रूप में दर्ज", selfReportNote:"दस्तावेज़ स्थिति स्वयं बताई गई है। इस डेमो में असली दस्तावेज़ अपलोड न करें।", cancel:"रद्द करें", saveProfile:"डेमो प्रोफ़ाइल सहेजें", manualRecord:"उपयोगकर्ता द्वारा दर्ज", addApplicationTitle:"आवेदन रिकॉर्ड जोड़ें", applicationNote:"यह केवल आपकी प्रविष्टि है। आवेदन भेजा या सत्यापित नहीं होता।", schemeLabel:"योजना", statusLabel:"स्थिति", dateLabel:"आवेदन तिथि", referenceLabel:"संदर्भ संख्या (वैकल्पिक)", notesLabel:"टिप्पणी (वैकल्पिक)", saveRecord:"रिकॉर्ड सहेजें", groundedDemo:"स्रोत-आधारित डेमो सहायक", assistantTitle:"योजना के बारे में पूछें", assistantSub:"उत्तर दर्ज किए गए आधिकारिक नोट्स पर आधारित हैं, लाइव सरकारी API पर नहीं।", askAbout:"इसके बारे में पूछें", suggestWhy:"यह क्यों मिला?", suggestDocs:"कौन से दस्तावेज़?", suggestApply:"आवेदन कहाँ करें?", assistantPlaceholder:"हिंदी या अंग्रेज़ी में प्रश्न पूछें...", assistantDisclaimer:"स्रोत नोट में जानकारी न हो तो सहायक बताएगा कि वह पुष्टि नहीं कर सकता। अंतिम निर्णय विभाग का है।", guidanceNotDecision:"मार्गदर्शन, निर्णय नहीं", fullDisclaimer:"योजना मित्र एक स्वतंत्र डेमो है। यह MahaDBT या किसी सरकारी विभाग का हिस्सा नहीं है। आधिकारिक स्रोत लिंक किए गए हैं और 7 अक्टूबर 2026 को देखे गए; वास्तविक पायलट से पहले विशेषज्ञ समीक्षा आवश्यक है। प्रोफ़ाइल मिलान पात्रता या मंज़ूरी नहीं है। डेमो आवेदन जमा नहीं करता, दस्तावेज़ सत्यापित नहीं करता और आधिकारिक आवेदन स्थिति नहीं लेता।", privacyDisclaimer:"यह डेमो खाता ईमेल और खेती की प्रोफ़ाइल जानकारी रखता है। केवल काल्पनिक या परीक्षण विवरण उपयोग करें। वास्तविक आधार या बैंक विवरण न डालें और असली दस्तावेज़ अपलोड न करें। सुरक्षित दस्तावेज़ संग्रह और स्वतंत्र गोपनीयता/सुरक्षा समीक्षा उपलब्ध नहीं है।", understood:"समझ गया"
  }
};

const extraTranslations = {
  en: {
    secureAccess:"SECURE FARMER ACCESS", authWelcome:"Welcome to Scheme Mitra", authIntro:"Sign in to save your farm profile and scheme shortlist.", signIn:"Sign in", createAccount:"Create account", emailLabel:"Email", passwordLabel:"Password", fullNameLabel:"Full name", orTryDemo:"or explore the synthetic demo", openDemo:"Open demo farmer", authPrivacy:"This demo stores account email and farm-profile data. Use test details only; never enter real Aadhaar or bank details or upload real documents.", independentDemo:"Independent service demo · Not a government portal", adminConsole:"Admin console", signOut:"Sign out",
    profileMatchShort:"profile fit", viewDetailsShort:"View details", profileMatchLabel:"Profile match", basedOn:"Based on", missingProfilePrefix:"Still to add:", profileCompleteMessage:"Your core profile details are complete.", noResultsTitle:"No matches in this demo catalog", noResultsBody:"Try another keyword or update your profile. The catalog is intentionally small.", referenceShort:"Ref", noNotes:"No note added", userEnteredStatus:"User-entered status — not official", metricRecommendations:"Recommendations generated", metricOfficialClicks:"Official portal clicks", metricFeedback:"Useful feedback", feedbackCount:"Responses captured", metricSurveys:"Baseline / post-use surveys", surveyCount:"Entries captured", demoOnly:"Demo events", recommendationsReady:"Your profile-fit shortlist is ready.", generalQuestion:"General scheme question", selfReportedAvailable:"Self-reported available", needsVerification:"Needs verification", notYetRequired:"Not yet required", issuedLater:"Issued through process", notMarkedAvailable:"Not marked available", markNotAvailable:"Change", markAvailable:"Mark available", removeSaved:"Remove saved", saveScheme:"Save scheme", sourceCaptured:"Official source page captured", checkedOn:"checked", needsHumanReview:"Demo summary needs human domain sign-off.", benefitSummary:"Benefit summary from source", overview:"Overview", whyMatch:"Why this appears for you", conditionsTitle:"Source-backed conditions to confirm", nextSteps:"A sensible next step", nextOne:"Review the complete scheme page and choose the correct component.", nextTwo:"Confirm the unresolved conditions with the official portal or department.", nextThree:"Apply only through the official portal; Scheme Mitra does not submit forms.", documentReadiness:"Document readiness", markedAvailable:"marked available", checklistSelfReport:"Checklist statuses are self-reported; no document file is stored or validated.", sourceAndRules:"Source & verification", dataStatus:"Data status", sourceChecked:"Source checked", applyOfficial:"Apply on official portal", applyOfficialShort:"Official portal", askAboutThis:"Ask about this scheme", eligibilityDisclaimer:"A profile match is not an eligibility decision. Final eligibility is decided by the concerned authority.", viewOfficialSource:"View official source", removedSavedToast:"Removed from saved schemes", savedToast:"Scheme saved to your shortlist", profileSavedToast:"Demo profile updated", selfReportUpdated:"Checklist updated — self-reported only", recordSavedToast:"User-entered record saved", manualStatusUpdated:"Manual status updated — not official", checkingSource:"Checking the captured source notes…", noRecommendationsFeedback:"Generate a shortlist first.", thanksFeedback:"Thanks — your feedback was recorded for this demo.", surveySavedToast:"Observation saved. Please collect real results before making claims.", signedOutToast:"Signed out."
  },
  mr: {
    secureAccess:"सुरक्षित शेतकरी प्रवेश", authWelcome:"योजना मित्रमध्ये आपले स्वागत आहे", authIntro:"तुमची शेतीची माहिती आणि योजना यादी जतन करण्यासाठी प्रवेश करा.", signIn:"प्रवेश करा", createAccount:"खाते तयार करा", emailLabel:"ईमेल", passwordLabel:"पासवर्ड (१२+ अक्षरे)", fullNameLabel:"पूर्ण नाव", orTryDemo:"किंवा बनावट डेमो पाहा", openDemo:"डेमो शेतकरी उघडा", authPrivacy:"आधार क्रमांक किंवा खरी कागदपत्रे टाकू/अपलोड करू नका.", independentDemo:"स्वतंत्र सेवा डेमो · सरकारी पोर्टल नाही", adminConsole:"प्रशासन", signOut:"बाहेर पडा",
    profileMatchShort:"प्रोफाइल जुळवणी", viewDetailsShort:"तपशील पाहा", profileMatchLabel:"प्रोफाइल जुळवणी", basedOn:"आधार", missingProfilePrefix:"अजून भरायचे:", profileCompleteMessage:"मूलभूत माहिती पूर्ण आहे.", noResultsTitle:"डेमो यादीत जुळणाऱ्या योजना नाहीत", noResultsBody:"दुसरा शब्द शोधा किंवा प्रोफाइल बदला. ही यादी मर्यादित डेमो आहे.", referenceShort:"संदर्भ", noNotes:"टीप नाही", userEnteredStatus:"वापरकर्त्याची नोंद — अधिकृत नाही", metricRecommendations:"तयार केलेल्या सूचना", metricOfficialClicks:"अधिकृत पोर्टल क्लिक", metricFeedback:"उपयोगी अभिप्राय", feedbackCount:"नोंदी", metricSurveys:"आधी/नंतर सर्वेक्षण", surveyCount:"नोंदी", demoOnly:"डेमो नोंदी", recommendationsReady:"तुमची प्रोफाइल-जुळवणी यादी तयार आहे.", generalQuestion:"सामान्य योजना प्रश्न", selfReportedAvailable:"स्वतः उपलब्ध म्हणून नोंद", needsVerification:"पडताळणी आवश्यक", notYetRequired:"अजून आवश्यक नाही", issuedLater:"प्रक्रियेतून मिळेल", notMarkedAvailable:"उपलब्ध म्हणून नोंद नाही", markNotAvailable:"बदला", markAvailable:"उपलब्ध म्हणून नोंद", removeSaved:"जतन काढा", saveScheme:"योजना जतन करा", sourceCaptured:"अधिकृत स्रोत पृष्ठ नोंदवले", checkedOn:"तपासले", needsHumanReview:"डेमो सारांशाला तज्ज्ञांची मान्यता आवश्यक.", benefitSummary:"स्रोतावरील लाभ माहिती", overview:"आढावा", whyMatch:"ही योजना का दिसते", conditionsTitle:"स्रोतावरील अटी तपासा", nextSteps:"योग्य पुढचे पाऊल", nextOne:"संपूर्ण योजना पृष्ठ पाहून योग्य घटक निवडा.", nextTwo:"अपूर्ण अटी अधिकृत पोर्टल किंवा विभागाकडून तपासा.", nextThree:"अर्ज फक्त अधिकृत पोर्टलवर करा; योजना मित्र अर्ज पाठवत नाही.", documentReadiness:"कागदपत्रांची तयारी", markedAvailable:"उपलब्ध म्हणून नोंद", checklistSelfReport:"स्थिती स्वतः नोंदवलेली; कागदपत्र साठवले किंवा तपासलेले नाही.", sourceAndRules:"स्रोत व पडताळणी", dataStatus:"माहिती स्थिती", sourceChecked:"स्रोत तपासला", applyOfficial:"अधिकृत पोर्टलवर अर्ज करा", applyOfficialShort:"अधिकृत पोर्टल", askAboutThis:"या योजनेबद्दल विचारा", eligibilityDisclaimer:"प्रोफाइल जुळवणी सरकारी पात्रता नाही. अंतिम पात्रता संबंधित विभाग ठरवतो.", viewOfficialSource:"अधिकृत स्रोत पाहा", removedSavedToast:"जतन यादीतून काढले", savedToast:"योजना जतन केली", profileSavedToast:"डेमो माहिती अद्ययावत", selfReportUpdated:"यादी बदलली — स्वतः नोंदवलेली", recordSavedToast:"वापरकर्त्याची नोंद जतन झाली", manualStatusUpdated:"मॅन्युअल स्थिती बदलली — अधिकृत नाही", checkingSource:"स्रोत नोंदी तपासत आहे…", noRecommendationsFeedback:"आधी योजना यादी तयार करा.", thanksFeedback:"धन्यवाद — डेमो अभिप्राय नोंदवला.", surveySavedToast:"निरीक्षण जतन झाले. दावा करण्यापूर्वी प्रत्यक्ष पुरावे गोळा करा."
  },
  hi: {
    secureAccess:"सुरक्षित किसान प्रवेश", authWelcome:"योजना मित्र में आपका स्वागत है", authIntro:"अपनी खेती की प्रोफ़ाइल और योजना सूची सहेजने के लिए साइन इन करें।", signIn:"साइन इन", createAccount:"खाता बनाएँ", emailLabel:"ईमेल", passwordLabel:"पासवर्ड (12+ अक्षर)", fullNameLabel:"पूरा नाम", orTryDemo:"या कृत्रिम डेमो देखें", openDemo:"डेमो किसान खोलें", authPrivacy:"आधार नंबर न डालें और असली दस्तावेज़ अपलोड न करें।", independentDemo:"स्वतंत्र सेवा डेमो · सरकारी पोर्टल नहीं", adminConsole:"प्रशासन", signOut:"साइन आउट",
    profileMatchShort:"प्रोफ़ाइल मिलान", viewDetailsShort:"विवरण देखें", profileMatchLabel:"प्रोफ़ाइल मिलान", basedOn:"आधार", missingProfilePrefix:"अभी जोड़ें:", profileCompleteMessage:"मुख्य प्रोफ़ाइल विवरण पूरे हैं।", noResultsTitle:"डेमो सूची में मेल नहीं मिला", noResultsBody:"दूसरा शब्द खोजें या प्रोफ़ाइल बदलें। यह सूची सीमित डेमो है।", referenceShort:"संदर्भ", noNotes:"कोई टिप्पणी नहीं", userEnteredStatus:"उपयोगकर्ता द्वारा दर्ज — आधिकारिक नहीं", metricRecommendations:"बनी सुझाव सूचियाँ", metricOfficialClicks:"आधिकारिक पोर्टल क्लिक", metricFeedback:"उपयोगी प्रतिक्रिया", feedbackCount:"प्रतिक्रियाएँ", metricSurveys:"पहले/बाद के सर्वे", surveyCount:"प्रविष्टियाँ", demoOnly:"डेमो गतिविधि", recommendationsReady:"आपकी प्रोफ़ाइल-मिलान सूची तैयार है।", generalQuestion:"सामान्य योजना प्रश्न", selfReportedAvailable:"स्वयं उपलब्ध बताया", needsVerification:"सत्यापन आवश्यक", notYetRequired:"अभी आवश्यक नहीं", issuedLater:"प्रक्रिया में जारी होगा", notMarkedAvailable:"उपलब्ध दर्ज नहीं", markNotAvailable:"बदलें", markAvailable:"उपलब्ध दर्ज करें", removeSaved:"सहेजना हटाएँ", saveScheme:"योजना सहेजें", sourceCaptured:"आधिकारिक स्रोत पृष्ठ दर्ज", checkedOn:"जाँचा गया", needsHumanReview:"डेमो सारांश को विशेषज्ञ समीक्षा चाहिए।", benefitSummary:"स्रोत के अनुसार लाभ", overview:"अवलोकन", whyMatch:"यह आपके लिए क्यों दिखी", conditionsTitle:"स्रोत पर दी शर्तें जाँचें", nextSteps:"अगला सही कदम", nextOne:"पूरा योजना पृष्ठ देखें और सही घटक चुनें।", nextTwo:"बाकी शर्तें आधिकारिक पोर्टल या विभाग से पुष्टि करें।", nextThree:"आवेदन केवल आधिकारिक पोर्टल पर करें; योजना मित्र आवेदन नहीं भेजता।", documentReadiness:"दस्तावेज़ तैयारी", markedAvailable:"उपलब्ध दर्ज", checklistSelfReport:"स्थिति स्वयं बताई गई है; दस्तावेज़ संग्रहीत या सत्यापित नहीं हैं।", sourceAndRules:"स्रोत और सत्यापन", dataStatus:"डेटा स्थिति", sourceChecked:"स्रोत जाँचा", applyOfficial:"आधिकारिक पोर्टल पर आवेदन", applyOfficialShort:"आधिकारिक पोर्टल", askAboutThis:"इस योजना के बारे में पूछें", eligibilityDisclaimer:"प्रोफ़ाइल मिलान सरकारी पात्रता नहीं है। अंतिम निर्णय संबंधित विभाग करता है।", viewOfficialSource:"आधिकारिक स्रोत देखें", removedSavedToast:"सहेजी सूची से हटाया", savedToast:"योजना सहेजी गई", profileSavedToast:"डेमो प्रोफ़ाइल अपडेट हुई", selfReportUpdated:"सूची अपडेट — स्वयं बताई गई", recordSavedToast:"उपयोगकर्ता रिकॉर्ड सहेजा गया", manualStatusUpdated:"मैन्युअल स्थिति बदली — आधिकारिक नहीं", checkingSource:"दर्ज स्रोत नोट जाँचे जा रहे हैं…", noRecommendationsFeedback:"पहले सूची बनाएं।", thanksFeedback:"धन्यवाद — डेमो प्रतिक्रिया दर्ज हुई।", surveySavedToast:"अवलोकन सहेजा गया। दावा करने से पहले वास्तविक साक्ष्य लें।"
  }
};
function t(key) {
  return (translations[appState.language] && translations[appState.language][key]) ||
    (extraTranslations[appState.language] && extraTranslations[appState.language][key]) ||
    translations.en[key] || extraTranslations.en[key] || key;
}
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
function cookieValue(name) {
  const prefix = `${name}=`;
  const item = document.cookie.split(";").map(value => value.trim()).find(value => value.startsWith(prefix));
  return item ? decodeURIComponent(item.slice(prefix.length)) : "";
}
async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const csrf = cookieValue("scheme_mitra_csrf");
  const headers = {"Content-Type":"application/json", ...(options.headers || {})};
  if (!["GET","HEAD","OPTIONS"].includes(method) && csrf) headers["X-CSRF-Token"] = csrf;
  const response = await fetch(API + path, {
    method,
    credentials: "same-origin",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined
  });
  let payload;
  try { payload = await response.json(); } catch { payload = {}; }
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/auth/")) showAuthGate();
    throw new Error(payload?.error?.message || payload?.detail || `Request failed (${response.status})`);
  }
  return payload;
}
function schemeTitle(scheme) {
  return appState.language === "mr" && scheme.name_mr ? scheme.name_mr : scheme.name;
}
function iconName(scheme) {
  if (scheme.icon === "water") return "i-water";
  if (scheme.icon === "tractor") return "i-tractor";
  return "i-sprout";
}
function iconSvg(id) { return `<svg aria-hidden="true"><use href="#${id}"></use></svg>`; }
function showToast(message) {
  const node = document.getElementById("toast");
  node.textContent = message;
  node.classList.add("show");
  clearTimeout(appState.toastTimer);
  appState.toastTimer = setTimeout(() => node.classList.remove("show"), 2600);
}
function openModal(id) {
  document.getElementById(id)?.classList.remove("hidden");
  document.body.style.overflow = "hidden";
}
function closeModal(id) {
  document.getElementById(id)?.classList.add("hidden");
  if (!document.querySelector(".modal-scrim:not(.hidden)")) document.body.style.overflow = "";
}
function applyLanguage() {
  document.documentElement.lang = appState.language;
  document.querySelectorAll("[data-i18n]").forEach(node => {
    const key = node.dataset.i18n;
    if (t(key) !== key) node.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(node => {
    const key = node.dataset.i18nPlaceholder;
    if (t(key) !== key) node.setAttribute("placeholder", t(key));
  });
  document.querySelectorAll("[data-lang]").forEach(button => button.classList.toggle("selected", button.dataset.lang === appState.language));
  const crumb = document.getElementById("current-crumb");
  const navKey = {overview:"navOverview",find:"navFind",saved:"navSaved",applications:"navApplications",pilot:"navPilot"}[appState.activePage];
  if (crumb && navKey) crumb.textContent = t(navKey);
  renderCurrentPage();
}
function formatCategory(category) {
  const values = {Irrigation: t("filterIrrigation"), Horticulture: t("filterHorticulture"), "Farm machinery": t("filterMachinery")};
  return values[category] || category;
}
function renderCard(scheme, compact = false) {
  const evaluation = scheme.evaluation || {};
  const score = Number(evaluation.profile_match || 0);
  const saved = appState.saved.some(item => item.slug === scheme.slug);
  const brief = scheme.summary.length > 132 ? scheme.summary.slice(0, 129) + "…" : scheme.summary;
  return `<article class="scheme-card ${compact ? "compact-card" : ""}">
    <div class="scheme-card-top"><span class="scheme-icon">${iconSvg(iconName(scheme))}</span><div class="scheme-card-title"><h3>${esc(schemeTitle(scheme))}</h3><small>${esc(scheme.department)}</small></div>
      <button class="save-icon ${saved ? "is-saved" : ""}" data-save="${esc(scheme.slug)}" aria-label="${saved ? "Unsave" : "Save"} ${esc(schemeTitle(scheme))}" title="${saved ? "Remove saved scheme" : "Save scheme"}">${iconSvg("i-bookmark")}</button></div>
    <p class="scheme-card-summary">${esc(brief)}</p><div class="scheme-tags"><span class="scheme-tag">${esc(formatCategory(scheme.category))}</span><span class="scheme-tag">${esc(scheme.source_name)}</span></div>
    <div class="scheme-card-foot"><span class="fit-badge"><span class="score-dot"></span>${esc(evaluation.status_label || "Potential fit")}</span><span class="mini-fit"><b>${score}</b><span>${t("profileMatchShort") || "fit"}</span></span><button class="open-card" data-open-scheme="${esc(scheme.slug)}">${t("viewDetailsShort") || "View details"} →</button></div>
  </article>`;
}
function renderListCard(scheme) {
  const evaluation = scheme.evaluation || {};
  const score = Number(evaluation.profile_match || 0);
  const reasons = (evaluation.match_reasons || []).slice(0, 3);
  const chips = reasons.length ? reasons.slice(0,3).map(reason => { const short = reason.length > 54 ? reason.slice(0,51) + "…" : reason; return `<span class="reason-chip"><span>✓</span>${esc(short)}</span>`; }).join("") : `<span class="reason-chip"><span>✓</span>${esc(formatCategory(scheme.category))} focus</span>`;
  const saved = appState.saved.some(item => item.slug === scheme.slug);
  return `<article class="scheme-list-card">
    <div class="list-main"><div class="list-top"><span class="scheme-icon">${iconSvg(iconName(scheme))}</span><div class="list-title"><h3>${esc(schemeTitle(scheme))}</h3><small>${esc(scheme.department)} · ${esc(formatCategory(scheme.category))}</small></div>
      <button class="save-icon ${saved ? "is-saved" : ""}" data-save="${esc(scheme.slug)}" aria-label="${saved ? "Unsave" : "Save"} ${esc(schemeTitle(scheme))}">${iconSvg("i-bookmark")}</button></div>
      <p class="list-summary">${esc(scheme.summary)}</p><div class="reason-row">${chips}</div></div>
    <div class="list-right"><div class="fit-head"><span>${t("profileMatchLabel") || "Profile match"}</span><strong>${score}<small>/100</small></strong></div><div class="fit-bar" aria-label="Profile match ${score} out of 100"><span style="width:${Math.max(0, Math.min(100, score))}%"></span></div><div class="status-label">${esc(evaluation.status_label || "Potential fit")}</div>
      <div class="list-actions"><button class="button button-quiet" data-open-scheme="${esc(scheme.slug)}">${t("viewDetailsShort") || "View details"}</button><a class="button button-primary apply-link" href="${esc(scheme.application_url)}" target="_blank" rel="noreferrer" data-official="${esc(scheme.slug)}">${t("applyOfficialShort") || "Official portal"}</a></div></div>
  </article>`;
}
function updateProfileUI() {
  if (!appState.profile) return;
  const p = appState.profile;
  const completeness = appState.completeness || {percent:90,complete:9,total:10,missing:["village"]};
  const percent = completeness.percent;
  const firstName = p.name || "Farmer";
  document.getElementById("greeting-name").textContent = firstName;
  document.getElementById("sidebar-name").textContent = firstName;
  document.getElementById("sidebar-avatar").textContent = firstName.split(/\s+/).map(s=>s[0]).slice(0,2).join("").toUpperCase();
  document.getElementById("sidebar-place").textContent = [p.taluka, p.district].filter(Boolean).join(", ") || "Maharashtra";
  document.getElementById("profile-percent").textContent = `${percent}%`;
  document.getElementById("profile-complete-count").textContent = completeness.complete;
  document.querySelector(".progress-ring").style.background = `conic-gradient(#80a85b 0 ${percent}%, #e9eee4 ${percent}% 100%)`;
  const missingText = completeness.missing.length ? `${t("missingProfilePrefix") || "Still to add:"} ${completeness.missing.map(formatMissingProfile).join(", ")}.` : t("profileCompleteMessage") || "Your core profile details are complete.";
  document.getElementById("missing-profile-copy").textContent = missingText;
  const crop = p.crop ? p.crop[0].toUpperCase() + p.crop.slice(1) : "Crop not added";
  const area = p.land_area_acres ? `${p.land_area_acres} acres` : "Land area not added";
  document.getElementById("profile-facts").innerHTML = `<span class="fact-pill"><b>⌖</b>${esc([p.taluka,p.district].filter(Boolean).join(", ") || "Location missing")}</span><span class="fact-pill"><b>▱</b>${esc(area)}</span><span class="fact-pill"><b>♧</b>${esc(crop)}</span><span class="fact-pill"><b>◌</b>${esc(p.irrigation === "yes" ? "Irrigation available" : p.irrigation === "no" ? "No irrigation" : "Irrigation unknown")}</span>`;
}
function formatMissingProfile(key) {
  const map = {district:"district",taluka:"taluka",village:"village",land:"land area",crop:"crop",farmer_category:"farm size",irrigation:"irrigation",aadhaar:"Aadhaar availability",land_7_12:"7/12 status",land_8a:"8-A status"};
  return map[key] || key.replaceAll("_", " ");
}
function renderHome() {
  updateProfileUI();
  const recommendations = appState.recommendations.slice(0, 3);
  document.getElementById("home-recommendations").innerHTML = recommendations.map(item => renderCard(item, true)).join("");
  document.getElementById("nav-match-count").textContent = String(appState.recommendations.length || appState.schemes.length || 3);
  const micro = appState.recommendations.find(item => item.slug === "pmksy-micro-irrigation") || appState.schemes.find(item => item.slug === "pmksy-micro-irrigation");
  if (micro?.evaluation) {
    const available = micro.evaluation.documents_available;
    const total = micro.evaluation.documents_total;
    const row = document.querySelector(".mini-doc-row b");
    if (row) row.textContent = `${available}/${total}`;
  }
}
function filteredSchemes() {
  const source = appState.recommendations.length ? appState.recommendations : appState.schemes;
  const query = appState.search.trim().toLowerCase();
  return source.filter(scheme => {
    const categoryMatch = appState.activeFilter === "all" || scheme.category === appState.activeFilter;
    const searchMatch = !query || [scheme.name, scheme.name_mr, scheme.summary, scheme.benefit_summary, scheme.category, scheme.department].join(" ").toLowerCase().includes(query);
    return categoryMatch && searchMatch;
  });
}
function renderFind() {
  const list = filteredSchemes();
  document.getElementById("results-count").textContent = list.length;
  document.getElementById("result-profile-note").textContent = `${t("basedOn") || "Based on"} ${appState.profile?.crop || "your farm"} · ${appState.profile?.taluka || "Maharashtra"}`;
  document.getElementById("scheme-results").innerHTML = list.length ? list.map(renderListCard).join("") : `<div class="empty-state"><span class="empty-icon">⌕</span><h3>${t("noResultsTitle") || "No matches in this demo catalog"}</h3><p>${t("noResultsBody") || "Try another keyword or update your profile. The catalog is intentionally small."}</p><button class="button button-quiet" data-edit-profile>${t("editProfile")}</button></div>`;
}
function renderSaved() {
  const container = document.getElementById("saved-results");
  const empty = document.getElementById("saved-empty");
  container.innerHTML = appState.saved.map(renderListCard).join("");
  empty.classList.toggle("hidden", appState.saved.length !== 0);
}
const statusLabels = {
  DRAFT: "Draft", SUBMITTED: "Submitted", UNDER_REVIEW: "Under review", DOCUMENTS_REQUIRED: "Documents required", APPROVED: "Approved · user-entered", REJECTED: "Rejected · user-entered", UNKNOWN: "Unknown"
};
function renderApplications() {
  const container = document.getElementById("application-list");
  document.getElementById("applications-empty").classList.toggle("hidden", appState.applications.length > 0);
  container.innerHTML = appState.applications.map(record => `<article class="application-card"><span class="app-status-icon">${iconSvg("i-clipboard")}</span><div class="application-copy"><h3>${esc(record.scheme_name)}</h3><p>${record.reference ? `${t("referenceShort") || "Ref"}: ${esc(record.reference)} · ` : ""}${record.applied_on ? `${esc(record.applied_on)} · ` : ""}${record.notes ? esc(record.notes) : t("noNotes") || "No note added"}</p><span class="manual-label">● ${t("userEnteredStatus") || "User-entered status — not official"}</span></div><div class="app-status-control"><select aria-label="Update user-entered status" data-app-status="${record.id}">${Object.entries(statusLabels).map(([value,label])=>`<option value="${value}" ${record.status===value?"selected":""}>${esc(tStatus(value,label))}</option>`).join("")}</select></div></article>`).join("");
}
function tStatus(status, fallback) {
  const map = {Draft:"draft",Submitted:"submitted", "Under review":"underReview", "Documents required":"documentsRequired", "Approved · user-entered":"approvedManual", "Rejected · user-entered":"rejectedManual",Unknown:"unknownStatus"};
  return translations[appState.language]?.[map[fallback]] || fallback;
}
function renderPilot(metrics) {
  const events = metrics.events || {};
  const baseline = metrics.baseline_surveys || {count:0,average_time_minutes:null};
  const post = metrics.post_use_surveys || {count:0,average_time_minutes:null};
  const useful = metrics.feedback || {total:0,useful:0};
  const cards = [
    [t("metricRecommendations") || "Recommendations generated", events.recommendations_generated || 0, t("demoOnly") || "Demo events"],
    [t("metricOfficialClicks") || "Official portal clicks", events.official_application_click || 0, t("demoOnly") || "Demo events"],
    [t("metricFeedback") || "Useful feedback", `${useful.useful}/${useful.total}`, t("feedbackCount") || "Responses captured"],
    [t("metricSurveys") || "Baseline / post-use surveys", `${baseline.count} / ${post.count}`, t("surveyCount") || "Entries captured"]
  ];
  document.getElementById("pilot-metrics").innerHTML = cards.map(([label,value,note])=>`<article class="metric-card"><span>${esc(label)}</span><strong>${esc(value)}</strong><small>${esc(note)}</small></article>`).join("");
}
function renderCurrentPage() {
  if (appState.activePage === "overview") renderHome();
  if (appState.activePage === "find") renderFind();
  if (appState.activePage === "saved") renderSaved();
  if (appState.activePage === "applications") renderApplications();
  if (appState.activePage === "pilot") loadMetrics().catch(err => showToast(err.message));
}
function navigate(page) {
  appState.activePage = page;
  document.querySelectorAll(".view").forEach(view => view.classList.toggle("active", view.dataset.view === page));
  document.querySelectorAll(".nav-item").forEach(button => button.classList.toggle("active", button.dataset.page === page));
  const navKey = {overview:"navOverview",find:"navFind",saved:"navSaved",applications:"navApplications",pilot:"navPilot"}[page];
  document.getElementById("current-crumb").textContent = t(navKey);
  renderCurrentPage();
  window.scrollTo({top:0,behavior:"smooth"});
}
function showAuthGate(errorText = "") {
  document.getElementById("auth-gate").classList.remove("hidden");
  document.getElementById("app-shell").classList.add("hidden");
  const error = document.getElementById("auth-error");
  error.textContent = errorText;
  error.classList.toggle("hidden", !errorText);
  appState.user = null;
}
function showMainApp(user) {
  appState.user = user;
  document.getElementById("auth-gate").classList.add("hidden");
  document.getElementById("app-shell").classList.remove("hidden");
  const isAdmin = ["ADMIN","DATA_VERIFIER","SUPER_ADMIN"].includes(user.role);
  document.getElementById("admin-link").classList.toggle("hidden", !isAdmin);
  document.querySelector(".demo-pill").classList.toggle("hidden", !user.is_demo);
}
async function bootstrapAuth() {
  try {
    const result = await api("/auth/me");
    if (!result.authenticated || !result.user) return showAuthGate();
    showMainApp(result.user);
    await loadAll();
  } catch (error) {
    showAuthGate(error.message);
  }
}
async function completeAuthentication(path, body) {
  const error = document.getElementById("auth-error");
  error.classList.add("hidden");
  try {
    const result = await api(path, {method:"POST",body});
    showMainApp(result.user);
    await loadAll();
  } catch (err) {
    showAuthGate(err.message);
  }
}
async function loadAll() {
  const [profileData, recommendationData, savedData, appData, schemeData] = await Promise.all([
    api("/profile"), api("/recommendations"), api("/saved"), api("/applications"), api("/schemes")
  ]);
  appState.profile = profileData.profile;
  appState.completeness = profileData.completeness;
  appState.recommendations = recommendationData.recommendations;
  appState.saved = savedData.saved;
  appState.applications = appData.applications;
  appState.schemes = schemeData.schemes;
  renderAll();
}
function renderAll() {
  updateProfileUI();
  renderHome();
  renderFind();
  renderSaved();
  renderApplications();
  updateSchemeSelects();
}
async function generateRecommendations() {
  try {
    const result = await api("/recommendations/generate", {method:"POST",body:{}});
    appState.recommendations = result.recommendations;
    appState.completeness = result.profile_completeness;
    renderAll();
    navigate("find");
    showToast(t("recommendationsReady") || "Your profile-fit shortlist is ready.");
  } catch (err) { showToast(err.message); }
}
function updateSchemeSelects() {
  const options = appState.schemes.map(s => `<option value="${esc(s.slug)}">${esc(schemeTitle(s))}</option>`).join("");
  const applicationSelect = document.getElementById("application-scheme");
  const assistantSelect = document.getElementById("assistant-scheme");
  const oldApp = applicationSelect?.value;
  const oldAssistant = assistantSelect?.value;
  if (applicationSelect) applicationSelect.innerHTML = options;
  if (assistantSelect) assistantSelect.innerHTML = `<option value="">${esc(t("generalQuestion") || "General scheme question")}</option>${options}`;
  if (oldApp && applicationSelect.querySelector(`[value="${CSS.escape(oldApp)}"]`)) applicationSelect.value = oldApp;
  if (oldAssistant && assistantSelect.querySelector(`[value="${CSS.escape(oldAssistant)}"]`)) assistantSelect.value = oldAssistant;
}
async function openScheme(slug) {
  try {
    const {scheme,evaluation} = await api(`/schemes/${encodeURIComponent(slug)}`);
    appState.selectedScheme = {...scheme,evaluation};
    await api("/events", {method:"POST",body:{event_name:"scheme_viewed",metadata:{scheme_slug:slug}}}).catch(()=>{});
    document.getElementById("scheme-modal-content").innerHTML = renderSchemeDetail(appState.selectedScheme);
    openModal("scheme-modal");
  } catch (err) { showToast(err.message); }
}
function docStateInfo(documentItem) {
  const state = documentItem.state;
  if (state === "self_reported_available") return {symbol:"✓",kind:"available",label:t("selfReportedAvailable") || "Self-reported available"};
  if (state === "needs_verification") return {symbol:"!",kind:"missing",label:t("needsVerification") || "Needs verification"};
  if (state === "not_yet_required") return {symbol:"·",kind:"later",label:t("notYetRequired") || "Not yet required"};
  if (state === "not_yet_issued") return {symbol:"·",kind:"later",label:t("issuedLater") || "Issued through process"};
  return {symbol:"!",kind:"missing",label:t("notMarkedAvailable") || "Not marked available"};
}
function renderSchemeDetail(scheme) {
  const ev = scheme.evaluation || {};
  const checks = (ev.checks || []).map(check => `<div class="rule-row"><span class="rule-icon ${esc(check.status)}">${check.status === "pass" ? "✓" : check.status === "not_applicable" ? "–" : "!"}</span><div>${esc(check.label)}<small>${esc(check.explanation)}</small></div></div>`).join("");
  const matchReasons = (ev.match_reasons || []).map(reason => `<div class="rule-row"><span class="rule-icon pass">✓</span><div>${esc(reason)}</div></div>`).join("");
  const docs = (ev.documents || []).map(item => {
    const state = docStateInfo(item);
    const canToggle = !["not_yet_required","not_yet_issued"].includes(item.state);
    const nextState = item.state === "self_reported_available" ? "not_provided" : "available";
    const button = canToggle ? `<button class="doc-status-action" data-doc-toggle="${esc(item.id)}" data-next-state="${nextState}">${item.state === "self_reported_available" ? (t("markNotAvailable") || "Change") : (t("markAvailable") || "Mark available")}</button>` : "";
    return `<div class="document-row"><span class="doc-check ${state.kind}">${state.symbol}</span><div class="doc-copy"><b>${esc(item.label)}</b><small>${esc(item.stage)} · ${esc(state.label)}</small></div>${button}</div>`;
  }).join("");
  const sourceUrl = safeOfficialUrl(scheme.source_url);
  const applyUrl = safeOfficialUrl(scheme.application_url);
  const saveText = appState.saved.some(s=>s.slug===scheme.slug) ? (t("removeSaved") || "Remove saved") : (t("saveScheme") || "Save scheme");
  return `<div class="scheme-detail-head"><span class="scheme-icon">${iconSvg(iconName(scheme))}</span><div class="detail-head-copy"><div class="modal-kicker">${esc(formatCategory(scheme.category))} · ${esc(scheme.level)}</div><h2 id="scheme-modal-title">${esc(schemeTitle(scheme))}</h2><div class="detail-source">${esc(scheme.department)} · ${esc(scheme.source_name)}</div></div><div class="detail-head-side"><div class="detail-score"><span>${t("profileMatchLabel")}</span><b>${Number(ev.profile_match||0)}<small>/100</small></b></div></div></div>
  <div class="detail-source-status"><span class="dot"></span><span>${t("sourceCaptured") || "Official source page captured"} · ${t("checkedOn") || "checked"} ${esc(scheme.source_checked_at || "")}. ${t("needsHumanReview") || "Demo summary needs human domain sign-off."}</span></div>
  <div class="detail-grid"><div class="detail-column"><section class="detail-section"><h3>${t("overview") || "Overview"}</h3><p>${esc(scheme.summary)}</p><div class="benefit-box"><b>${t("benefitSummary") || "Benefit summary from source"}</b>${esc(scheme.benefit_summary)}</div></section>
    <section class="detail-section" style="margin-top:11px"><h3>${t("whyMatch") || "Why this appears for you"}</h3><div class="rule-list">${matchReasons}</div><div class="checks-heading">${t("conditionsTitle") || "Source-backed conditions to confirm"}</div><div class="rule-list">${checks}</div></section>
    <section class="detail-section" style="margin-top:11px"><h3>${t("nextSteps") || "A sensible next step"}</h3><ul><li>${t("nextOne") || "Review the complete scheme page and choose the correct component."}</li><li>${t("nextTwo") || "Confirm the unresolved conditions with the official portal or department."}</li><li>${t("nextThree") || "Apply only through the official portal; Scheme Mitra does not submit forms."}</li></ul></section></div>
    <div class="detail-column"><section class="detail-section"><div class="surface-head"><h3>${t("documentReadiness") || "Document readiness"}</h3><span class="tag tag-green">${ev.documents_available||0}/${ev.documents_total||0} ${t("markedAvailable") || "marked available"}</span></div><p>${t("checklistSelfReport") || "Checklist statuses are self-reported; no document file is stored or validated."}</p><div class="document-list">${docs}</div></section>
    <section class="detail-section" style="margin-top:11px"><h3>${t("sourceAndRules") || "Source & verification"}</h3><ul>${(scheme.source_facts||[]).map(f=>`<li>${esc(f)}</li>`).join("")}</ul><p class="source-note-line"><b>${t("dataStatus") || "Data status"}:</b> ${esc(scheme.data_status)}<br><b>${t("sourceChecked") || "Source checked"}:</b> ${esc(scheme.source_checked_at)}</p></section></div></div>
  <div class="detail-actions"><a class="button button-primary apply-link" href="${applyUrl}" target="_blank" rel="noreferrer" data-official="${esc(scheme.slug)}">${t("applyOfficial") || "Apply on official portal"} ${iconSvg("i-external")}</a><button class="button button-quiet" data-save="${esc(scheme.slug)}">${saveText}</button><button class="button button-quiet" data-ask-scheme="${esc(scheme.slug)}">✦ ${t("askAboutThis") || "Ask about this scheme"}</button></div>
  <div class="detail-disclaimer">${esc(ev.evaluated_note || t("eligibilityDisclaimer") || "A profile match is not an eligibility decision. Final eligibility is decided by the concerned authority.")} <a href="${sourceUrl}" target="_blank" rel="noreferrer">${t("viewOfficialSource") || "View official source"} ↗</a></div>`;
}
function safeOfficialUrl(url) {
  try {
    const parsed = new URL(url, window.location.origin);
    if (parsed.protocol === "https:" && parsed.hostname === "mahadbt.maharashtra.gov.in") return parsed.href;
  } catch { }
  return "https://mahadbt.maharashtra.gov.in/Farmer/";
}
async function toggleSaved(slug) {
  const isSaved = appState.saved.some(item=>item.slug===slug);
  try {
    if (isSaved) await api(`/saved/${encodeURIComponent(slug)}`, {method:"DELETE"});
    else await api(`/saved/${encodeURIComponent(slug)}`, {method:"POST",body:{}});
    await refreshSaved();
    renderAll();
    if (appState.selectedScheme?.slug === slug && !document.getElementById("scheme-modal").classList.contains("hidden")) {
      const fresh = await api(`/schemes/${encodeURIComponent(slug)}`);
      appState.selectedScheme = {...fresh.scheme,evaluation:fresh.evaluation};
      document.getElementById("scheme-modal-content").innerHTML = renderSchemeDetail(appState.selectedScheme);
    }
    showToast(isSaved ? (t("removedSavedToast") || "Removed from saved schemes") : (t("savedToast") || "Scheme saved to your shortlist"));
  } catch (err) { showToast(err.message); }
}
async function refreshSaved() {
  const data = await api("/saved");
  appState.saved = data.saved;
}
function openProfileForm() {
  const p = appState.profile;
  if (!p) return;
  const form = document.getElementById("profile-form");
  for (const key of ["name","district","taluka","village","land_area_acres","crop","farmer_category","social_category","irrigation","electric_water_pump","permanent_electric_connection","prior_micro_benefit_year"]) {
    const input = form.elements.namedItem(key);
    if (input) input.value = p[key] ?? "";
  }
  form.elements.namedItem("aadhaar_present").checked = !!p.aadhaar_present;
  form.elements.namedItem("land_7_12").checked = p.documents?.land_7_12 === "available";
  form.elements.namedItem("land_8a").checked = p.documents?.land_8a === "available";
  form.querySelectorAll('input[name="support_needs"]').forEach(box=>box.checked=(p.support_needs||[]).includes(box.value));
  openModal("profile-modal");
}
async function saveProfile(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const fd = new FormData(form);
  const docs = {...(appState.profile.documents||{})};
  docs.land_7_12 = form.elements.namedItem("land_7_12").checked ? "available" : "not_provided";
  docs.land_8a = form.elements.namedItem("land_8a").checked ? "available" : "not_provided";
  const data = {
    name:fd.get("name"),district:fd.get("district"),taluka:fd.get("taluka"),village:fd.get("village"),
    land_area_acres:fd.get("land_area_acres"),crop:fd.get("crop"),farmer_category:fd.get("farmer_category"),
    social_category:fd.get("social_category"),irrigation:fd.get("irrigation"),
    electric_water_pump:fd.get("electric_water_pump"),permanent_electric_connection:fd.get("permanent_electric_connection"),
    prior_micro_benefit_year:fd.get("prior_micro_benefit_year"),
    support_needs:[...form.querySelectorAll('input[name="support_needs"]:checked')].map(box=>box.value),
    aadhaar_present:form.elements.namedItem("aadhaar_present").checked,documents:docs
  };
  try {
    const result = await api("/profile", {method:"PUT",body:data});
    appState.profile = result.profile; appState.completeness = result.completeness;
    const recommendations = await api("/recommendations"); appState.recommendations = recommendations.recommendations;
    renderAll(); closeModal("profile-modal"); showToast(t("profileSavedToast") || "Demo profile updated");
  } catch (err) { showToast(err.message); }
}
async function toggleDocument(id, nextState) {
  try {
    await api(`/documents/${encodeURIComponent(id)}`, {method:"PATCH",body:{state:nextState}});
    const fresh = await api(`/schemes/${encodeURIComponent(appState.selectedScheme.slug)}`);
    appState.selectedScheme = {...fresh.scheme,evaluation:fresh.evaluation};
    await loadAll();
    document.getElementById("scheme-modal-content").innerHTML = renderSchemeDetail(appState.selectedScheme);
    showToast(t("selfReportUpdated") || "Checklist updated — self-reported only");
  } catch (err) { showToast(err.message); }
}
function openApplicationForm(slug = "") {
  updateSchemeSelects();
  const select = document.getElementById("application-scheme");
  if (slug) select.value = slug;
  document.getElementById("application-form").reset();
  if (slug) select.value = slug;
  openModal("application-modal");
}
async function saveApplication(event) {
  event.preventDefault();
  const fd = new FormData(event.currentTarget);
  try {
    await api("/applications", {method:"POST",body:{
      scheme_slug:fd.get("scheme_slug"),status:fd.get("status"),applied_on:fd.get("applied_on"),reference:fd.get("reference"),notes:fd.get("notes")
    }});
    const data = await api("/applications"); appState.applications = data.applications;
    renderApplications(); closeModal("application-modal"); navigate("applications"); showToast(t("recordSavedToast") || "User-entered record saved");
  } catch (err) { showToast(err.message); }
}
async function updateApplicationStatus(id, status) {
  try {
    await api(`/applications/${id}`, {method:"PUT",body:{status}});
    const data = await api("/applications"); appState.applications = data.applications; renderApplications();
    showToast(t("manualStatusUpdated") || "Manual status updated — not official");
  } catch (err) { showToast(err.message); }
}
function openAssistant(slug = "") {
  updateSchemeSelects();
  document.getElementById("assistant-scheme").value = slug || "";
  document.getElementById("assistant-answer").classList.add("hidden");
  document.getElementById("assistant-answer").textContent = "";
  openModal("assistant-modal");
}
async function askAssistant(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const question = new FormData(form).get("question");
  if (!String(question||"").trim()) return;
  const answerNode = document.getElementById("assistant-answer");
  answerNode.classList.remove("hidden");
  answerNode.textContent = t("checkingSource") || "Checking the captured source notes…";
  try {
    const response = await api("/assistant/question", {method:"POST",body:{question,scheme_slug:document.getElementById("assistant-scheme").value || null,language:appState.language}});
    answerNode.textContent = response.answer;
    if (response.source_url) {
      const anchor = document.createElement("a");
      anchor.href = safeOfficialUrl(response.source_url); anchor.target = "_blank"; anchor.rel = "noreferrer";
      anchor.textContent = `${response.source_name || "Official source"} ↗`;
      anchor.setAttribute("aria-label", `${response.source_name || "Official source"} (opens new tab)`);
      answerNode.append(document.createElement("br"), anchor);
    }
    form.reset();
  } catch (err) { answerNode.textContent = err.message; }
}
async function submitFeedback(useful) {
  const first = appState.recommendations[0];
  if (!first) return showToast(t("noRecommendationsFeedback") || "Generate a shortlist first.");
  try {
    await api("/recommendation-feedback", {method:"POST",body:{useful,reason:"recommendation_set"}});
    showToast(t("thanksFeedback") || "Thanks — your feedback was recorded for this demo.");
    await loadMetrics();
  } catch (err) { showToast(err.message); }
}
async function loadMetrics() {
  const metrics = await api("/pilot-metrics");
  renderPilot(metrics);
}
async function saveSurvey(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const fd = new FormData(form);
  const bool = (name) => { const value=fd.get(name); return value === "yes" ? true : value === "no" ? false : null; };
  const time = fd.get("time_minutes");
  try {
    await api("/pilot-surveys", {method:"POST",body:{
      phase:fd.get("phase"),time_minutes:time || null,
      knows_relevant_schemes:bool("knows_relevant_schemes"),understands_documents:bool("understands_documents"),
      knows_next_step:bool("knows_next_step"),comment:fd.get("comment")
    }});
    form.reset();
    document.getElementById("survey-success").classList.remove("hidden");
    setTimeout(()=>document.getElementById("survey-success").classList.add("hidden"),3000);
    await loadMetrics(); showToast(t("surveySavedToast") || "Observation saved. Please collect real results before making claims.");
  } catch (err) { showToast(err.message); }
}

// Primary navigation and stable controls
for (const button of document.querySelectorAll(".nav-item")) button.addEventListener("click",()=>navigate(button.dataset.page));
document.querySelectorAll("[data-lang]").forEach(button=>button.addEventListener("click",()=>{
  appState.language=button.dataset.lang; localStorage.setItem("schememitra-language",appState.language); applyLanguage(); updateSchemeSelects();
}));
document.getElementById("hero-find").addEventListener("click",generateRecommendations);
document.getElementById("view-all-schemes").addEventListener("click",()=>navigate("find"));
document.getElementById("edit-profile-top").addEventListener("click",openProfileForm);
document.getElementById("edit-profile-link").addEventListener("click",openProfileForm);
document.getElementById("open-micro-detail").addEventListener("click",()=>openScheme("pmksy-micro-irrigation"));
document.getElementById("open-assistant-side").addEventListener("click",()=>openAssistant());
document.getElementById("open-assistant-top").addEventListener("click",()=>openAssistant());
document.getElementById("footer-disclaimer").addEventListener("click",()=>openModal("disclaimer-modal"));
document.getElementById("add-application").addEventListener("click",()=>openApplicationForm());
document.getElementById("add-application-empty").addEventListener("click",()=>openApplicationForm());
document.getElementById("profile-form").addEventListener("submit",saveProfile);
document.getElementById("application-form").addEventListener("submit",saveApplication);
document.getElementById("assistant-form").addEventListener("submit",askAssistant);
document.getElementById("survey-form").addEventListener("submit",saveSurvey);
document.getElementById("scheme-search").addEventListener("input",event=>{appState.search=event.target.value;renderFind();});
document.querySelectorAll(".filter-chip").forEach(button=>button.addEventListener("click",()=>{
  appState.activeFilter=button.dataset.filter;
  document.querySelectorAll(".filter-chip").forEach(item=>item.classList.toggle("active",item===button));renderFind();
}));
document.querySelectorAll("[data-feedback]").forEach(button=>button.addEventListener("click",()=>submitFeedback(button.dataset.feedback==="true")));
document.querySelectorAll("[data-goto]").forEach(button=>button.addEventListener("click",()=>navigate(button.dataset.goto)));
document.querySelectorAll("[data-close]").forEach(button=>button.addEventListener("click",()=>closeModal(button.dataset.close)));
document.querySelectorAll(".modal-scrim").forEach(scrim=>scrim.addEventListener("click",event=>{if(event.target===scrim)closeModal(scrim.id);}));
document.querySelectorAll("[data-question]").forEach(button=>button.addEventListener("click",()=>{
  const input=document.querySelector('#assistant-form input[name="question"]');input.value=button.dataset.question;document.getElementById("assistant-form").requestSubmit();
}));
document.querySelectorAll("[data-page]").forEach(button=>button.addEventListener("click",()=>{}));
document.getElementById("application-list").addEventListener("change",event=>{
  if(event.target.matches("[data-app-status]")) updateApplicationStatus(event.target.dataset.appStatus,event.target.value);
});
document.getElementById("application-list").addEventListener("click",()=>{});
document.getElementById("scheme-modal-content").addEventListener("click",async event=>{
  const open = event.target.closest("[data-open-scheme]");if(open)return openScheme(open.dataset.openScheme);
  const save = event.target.closest("[data-save]");if(save)return toggleSaved(save.dataset.save);
  const ask = event.target.closest("[data-ask-scheme]");if(ask)return openAssistant(ask.dataset.askScheme);
  const doc = event.target.closest("[data-doc-toggle]");if(doc)return toggleDocument(doc.dataset.docToggle,doc.dataset.nextState);
});
document.addEventListener("click",async event=>{
  const open = event.target.closest("[data-open-scheme]"); if(open && !document.getElementById("scheme-modal-content").contains(open)) return openScheme(open.dataset.openScheme);
  const save = event.target.closest("[data-save]"); if(save && !document.getElementById("scheme-modal-content").contains(save)) return toggleSaved(save.dataset.save);
  const official = event.target.closest("[data-official]");
  if(official){ api("/events",{method:"POST",body:{event_name:"official_application_click",metadata:{scheme_slug:official.dataset.official}}}).catch(()=>{}); }
  if(event.target.closest("[data-edit-profile]")) openProfileForm();
});
document.getElementById("assistant-scheme").addEventListener("change",()=>{document.getElementById("assistant-answer").classList.add("hidden");});
document.addEventListener("keydown",event=>{if(event.key==="Escape"){document.querySelectorAll(".modal-scrim:not(.hidden)").forEach(node=>closeModal(node.id));}});

document.getElementById("login-form").addEventListener("submit",event=>{
  event.preventDefault();const values=new FormData(event.currentTarget);
  completeAuthentication("/auth/login",{email:values.get("email"),password:values.get("password")});
});
document.getElementById("register-form").addEventListener("submit",event=>{
  event.preventDefault();const values=new FormData(event.currentTarget);
  completeAuthentication("/auth/register",{email:values.get("email"),password:values.get("password"),full_name:values.get("full_name"),district:values.get("district"),taluka:values.get("taluka"),state:"Maharashtra"});
});
document.getElementById("demo-entry").addEventListener("click",()=>completeAuthentication("/auth/demo",{}));
document.querySelectorAll("[data-auth-tab]").forEach(button=>button.addEventListener("click",()=>{
  const register=button.dataset.authTab==="register";
  document.getElementById("login-form").classList.toggle("hidden",register);
  document.getElementById("register-form").classList.toggle("hidden",!register);
  document.querySelectorAll("[data-auth-tab]").forEach(tab=>tab.classList.toggle("active",tab===button));
  document.getElementById("auth-error").classList.add("hidden");
}));
document.getElementById("logout-button").addEventListener("click",async()=>{
  try{await api("/auth/logout",{method:"POST",body:{}});showAuthGate();showToast(t("signedOutToast")||"Signed out.");}
  catch(err){showToast(err.message);}
});

applyLanguage();
bootstrapAuth();
