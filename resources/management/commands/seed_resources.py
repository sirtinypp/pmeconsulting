from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from resources.models import Post
from django.contrib.auth import get_user_model


POSTS = [
    # ── DIY GUIDES ────────────────────────────────────────────────────────────
    {
        "category": "DIY",
        "cover_emoji": "🏥",
        "title": "How to Get Your Medical Technology Credentials Recognized in Germany",
        "excerpt": (
            "A complete, step-by-step guide for Filipino Medical Technologists on how to have their "
            "professional credentials recognized (Anerkennung) in Germany — from gathering documents "
            "to passing the aptitude test."
        ),
        "content": """Getting your Medical Technology (MedTech) diploma recognized in Germany is the most critical step before you can work in your profession. Here's exactly how to do it.

─────────────────────────────────────
STEP 1: UNDERSTAND THE PROCESS
─────────────────────────────────────
Germany requires "Anerkennung" (recognition) of foreign professional qualifications. For MedTechs (Medizinisch-Technische Laborassistenten / MTLA), this is handled by the regional authority (Landesbehörde) in the German state (Bundesland) where you plan to work.

─────────────────────────────────────
STEP 2: GATHER YOUR DOCUMENTS
─────────────────────────────────────
Prepare the following (all must be officially translated into German by a certified translator):

• Your Bachelor's Degree in Medical Technology (original + certified copy)
• Transcript of Records (original + certified copy)
• PRC License / Certificate of Registration
• Passport (valid, bio page copy)
• Curriculum vitae (Lebenslauf), in German
• Certificate of Professional Standing from the PRC
• Proof of work experience (employment certificates, if any)
• Two passport-sized photos
• Motivation letter (Motivationsschreiben) — optional but recommended

Pro Tip: Get everything authenticated by the Department of Foreign Affairs (DFA) and then by the German Embassy in Manila before leaving the Philippines.

─────────────────────────────────────
STEP 3: SUBMIT YOUR APPLICATION
─────────────────────────────────────
Contact the appropriate Landesbehörde for the state you're targeting. Common examples:

• Bavaria (Bayern): Landesamt für Gesundheit und Lebensmittelsicherheit (LGL)
• North Rhine-Westphalia (NRW): Bezirksregierung Münster
• Baden-Württemberg: Regierungspräsidium Stuttgart

Submit your application package by post or in-person. There is typically a processing fee of €100–€200.

─────────────────────────────────────
STEP 4: THE EVALUATION
─────────────────────────────────────
The authority will compare your Philippine curriculum to the German MTLA curriculum. The typical outcome is one of three:

1. Full Recognition — your credentials are fully equivalent. You can work immediately.
2. Compensatory Measures — you are required to either:
   a. Take an Aptitude Test (Eignungsprüfung) — a practical and/or oral exam
   b. Complete an Adaptation Period (Anpassungslehrgang) — usually 3–12 months of supervised work
3. Non-recognition — very rare, usually due to missing documentation.

Most Filipino MedTechs are required to complete an Aptitude Test or Adaptation Period.

─────────────────────────────────────
STEP 5: PREPARE FOR THE APTITUDE TEST
─────────────────────────────────────
The test typically covers:
• Laboratory procedures (hematology, clinical chemistry, microbiology, blood banking)
• Practical skills in a German hospital laboratory
• Oral examination in German (B2 level minimum recommended)

Your German language skills are critical here. Enroll in the PME Learning platform courses NOW to be well-prepared.

─────────────────────────────────────
STEP 6: RECEIVE YOUR RECOGNITION CERTIFICATE
─────────────────────────────────────
Once approved, you'll receive your recognition letter (Anerkennungsbescheid). This officially allows you to work as an MTLA in that German state.

─────────────────────────────────────
USEFUL RESOURCES
─────────────────────────────────────
• Anerkennung in Deutschland Portal: https://www.anerkennung-in-deutschland.de
• ANABIN Database (to check your institution's recognized status): https://anabin.kmk.org
• Federal Institute for Vocational Education (BIBB): https://www.bibb.de

Processing time: typically 3–6 months. Start this process early!""",
        "author": "PME Consulting EU",
        "days_ago": 10,
    },
    {
        "category": "DIY",
        "cover_emoji": "📋",
        "title": "Step-by-Step: Applying for a German Work Visa (Skilled Worker)",
        "excerpt": (
            "The Fachkräfteeinwanderungsgesetz (Skilled Immigration Act) opened doors for Filipino "
            "healthcare workers. This guide walks you through the entire visa application process "
            "for the German Skilled Worker Visa."
        ),
        "content": """Germany's Skilled Immigration Act (Fachkräfteeinwanderungsgesetz) makes it possible to obtain a work visa even before your credentials are fully recognized. Here's the full process.

─────────────────────────────────────
WHAT YOU NEED BEFORE APPLYING
─────────────────────────────────────
• A signed employment contract or a concrete job offer from a German employer
• Your credential recognition decision (or proof that the process is underway)
• B1/B2 German language certificate (Goethe-Institut recommended)
• Valid Philippine passport (at least 6 months validity)

─────────────────────────────────────
STEP 1: GET YOUR JOB OFFER
─────────────────────────────────────
Start by applying to German hospitals and laboratories. Useful job portals:
• Make it in Germany: https://www.make-it-in-germany.com
• Bundesagentur für Arbeit: https://www.arbeitsagentur.de
• Jobvector (for lab and science roles): https://www.jobvector.de
• LinkedIn and XING

─────────────────────────────────────
STEP 2: BOOK AN APPOINTMENT AT THE GERMAN EMBASSY MANILA
─────────────────────────────────────
Visa appointments fill up fast. Book as early as possible at:
https://www.germany.diplo.de/ph-en

You will need to appear in person at the Embassy of Germany, 25F Tower 2, RCBC Plaza, Makati City.

─────────────────────────────────────
STEP 3: PREPARE YOUR DOCUMENTS
─────────────────────────────────────
• Completed visa application form (signed)
• Two recent biometric passport photos
• Valid passport (original + 2 copies of bio page)
• Signed employment contract or job offer letter
• Proof of credential recognition (or proof application is underway)
• German language certificate (B1 minimum; B2 preferred)
• Educational certificates (DFA-authenticated + German-translated)
• Proof of accommodation in Germany (if available)
• Health insurance coverage / proof of future employer coverage
• Germany Block Account (Sperrkonto) — NOT required if you have a signed contract

─────────────────────────────────────
STEP 4: ATTEND YOUR VISA INTERVIEW
─────────────────────────────────────
The interview is typically short (15–30 minutes). You may be asked:
• Why Germany specifically?
• What role are you applying for?
• What is your German language level?
• Do you have family in Germany?

Answer confidently and truthfully. Bring all original documents.

─────────────────────────────────────
STEP 5: WAIT FOR PROCESSING
─────────────────────────────────────
Processing time: 4–12 weeks typically. The Embassy may request additional documents.

─────────────────────────────────────
STEP 6: RECEIVE YOUR VISA & TRAVEL
─────────────────────────────────────
Once approved, your passport will be returned with a Type D (National) Visa valid for 6 months. Travel to Germany and register your address (Anmeldung) within 14 days of arrival.

After entry, your employer will help you apply for a Residence Permit (Aufenthaltserlaubnis) at the local Ausländerbehörde. This is your long-term visa for working in Germany.

PME Consulting EU tip: Start your German language courses NOW — B2 certification significantly strengthens your visa application.""",
        "author": "PME Consulting EU",
        "days_ago": 8,
    },
    {
        "category": "DIY",
        "cover_emoji": "🏠",
        "title": "Anmeldung: How to Register Your Address in Germany",
        "excerpt": (
            "Within 14 days of arriving in Germany, you are legally required to register your address "
            "(Anmeldung) at the local Bürgeramt. Miss this and face fines. Here's exactly what to do."
        ),
        "content": """The Anmeldung (address registration) is the first administrative task after arriving in Germany. It's mandatory by law.

─────────────────────────────────────
WHAT IS ANMELDUNG?
─────────────────────────────────────
Anmeldung literally means "registration." Every person living in Germany must register their place of residence with the local registration office (Einwohnermeldeamt or Bürgeramt) within 14 days of moving in.

Failure to register can result in fines of up to €1,000.

─────────────────────────────────────
WHAT YOU NEED
─────────────────────────────────────
• Valid passport or identity document
• Wohnungsgeberbestätigung — a confirmation form signed by your landlord/host confirming you live at the address. This is mandatory since 2015.
• Completed Anmeldeformular (registration form) — usually downloadable from your city's website
• Your German visa

─────────────────────────────────────
STEP-BY-STEP
─────────────────────────────────────
1. Find your local Bürgeramt:
   Search "[your city] Bürgeramt" online. Book an appointment online where possible — walk-ins can have very long waits.

2. Bring all documents to the appointment.

3. The officer will process your registration, usually in 10–15 minutes.

4. You will receive a Meldebestätigung (registration confirmation). Keep this document — you will need it for:
   • Opening a bank account
   • Applying for a residence permit (Aufenthaltserlaubnis)
   • Getting a Tax ID (Steueridentifikationsnummer)
   • Health insurance enrollment

─────────────────────────────────────
PRACTICAL TIPS
─────────────────────────────────────
• If staying in temporary accommodation (hospital housing, a friend's apartment), ask your host to sign the Wohnungsgeberbestätigung form for you.
• Your employer's HR department will often help you with this process.
• Some cities (e.g., Berlin, Munich) have very busy offices — book your appointment online as soon as possible after arrival.

─────────────────────────────────────
WHAT COMES NEXT?
─────────────────────────────────────
After Anmeldung:
1. Open a German bank account (you'll need the Meldebestätigung)
2. Enroll in health insurance
3. Apply for your Tax ID at the Finanzamt
4. Apply for your long-term Residence Permit at the Ausländerbehörde""",
        "author": "PME Consulting EU",
        "days_ago": 6,
    },
    {
        "category": "DIY",
        "cover_emoji": "🏦",
        "title": "Opening a German Bank Account as a Filipino Expat",
        "excerpt": (
            "You'll need a German bank account to receive your salary, pay rent, and handle daily "
            "finances. Here's how to open one — whether with a traditional bank or a digital bank "
            "like N26 or Wise."
        ),
        "content": """A German bank account (Girokonto) is essential for everyday life — your salary will be paid into it, and landlords will often require a German IBAN for rent bank transfers.

─────────────────────────────────────
OPTION A: TRADITIONAL BANKS
─────────────────────────────────────
Major banks like Sparkasse, Deutsche Bank, Commerzbank, and Volksbank have branches everywhere.

Requirements typically:
• Passport
• Meldebestätigung (address registration)
• Your residence permit or valid visa
• Employment contract (some banks require this)

Walk into a branch and ask to open a Girokonto (current account). Some banks may reject non-EU nationals — Sparkasse and Deutsche Bank tend to be the most expat-friendly.

─────────────────────────────────────
OPTION B: DIGITAL / CHALLENGER BANKS (Recommended for New Arrivals)
─────────────────────────────────────
These are easier to open online, often without needing the Meldebestätigung first:

• N26 — 100% online, app-based, free basic account. Good for immediate use after arrival.
• Wise (formerly TransferWise) — excellent for international transfers to the Philippines. Low fees.
• Revolut — multi-currency card, great for travel within Europe.
• DKB — very popular with expats, free with regular deposits.

─────────────────────────────────────
SENDING MONEY HOME
─────────────────────────────────────
To send money back to the Philippines, use:
• Wise — best exchange rates, low fees
• Remitly — fast transfers, first transfer often free
• Western Union / MoneyGram — widely available but higher fees

Avoid transferring through traditional German banks to Philippine accounts — fees are very high.

─────────────────────────────────────
PRO TIPS
─────────────────────────────────────
• Open an N26 or Wise account before you leave the Philippines — you can use a Philippine address initially.
• Always keep your IBAN handy — your employer, landlord, and countless services will need it.
• Set up a separate savings account (Sparkonto) to build your emergency fund in Germany.""",
        "author": "PME Consulting EU",
        "days_ago": 5,
    },
    {
        "category": "DIY",
        "cover_emoji": "🩺",
        "title": "Guide to German Health Insurance (Krankenversicherung) for Expats",
        "excerpt": (
            "Health insurance is mandatory in Germany. As a salaried employee, you'll be automatically "
            "enrolled — but you need to understand how it works, what it covers, and what choices you have."
        ),
        "content": """In Germany, health insurance is not optional — it is a legal requirement. As a salaried Healthcare worker, you will have employer-sponsored statutory health insurance.

─────────────────────────────────────
TWO TYPES OF HEALTH INSURANCE
─────────────────────────────────────
1. Statutory Health Insurance (Gesetzliche Krankenversicherung / GKV)
   — Mandatory for employees earning under €69,300/year (2024 threshold)
   — Costs ~14.6% of gross salary, split equally between you and your employer
   — Covers medical visits, hospital stays, prescriptions, preventive care
   — Major providers: TK (Techniker Krankenkasse), AOK, Barmer, DAK

2. Private Health Insurance (Private Krankenversicherung / PKV)
   — Available if you earn above the threshold
   — Often better benefits, faster appointments, private rooms in hospitals
   — Generally not recommended for newcomers until you understand the system

─────────────────────────────────────
HOW TO ENROLL
─────────────────────────────────────
When you start work, your employer's HR team will enroll you in the GKV. You typically need to:

1. Choose a statutory insurer (Krankenkasse). If you don't choose, your employer assigns one automatically.
2. You'll receive your Gesundheitskarte (health card) within 2–4 weeks.
3. Until your card arrives, your insurer will issue a temporary certificate — use this at the pharmacy or doctor.

─────────────────────────────────────
WHAT'S COVERED
─────────────────────────────────────
• General practitioner (Hausarzt) visits — free with the health card
• Specialist referrals from your Hausarzt
• Hospital treatment
• Prescriptions (small co-pay per medication, typically €5–€10)
• Dental (basic; cosmetic procedures not covered)
• Mental health services
• Family members can be co-insured for free if they have no income (Familienversicherung)

─────────────────────────────────────
COMMON TIPS
─────────────────────────────────────
• Always register with a Hausarzt (GP/family doctor) first in your city. Specialists in Germany require a referral.
• TK (Techniker Krankenkasse) is very popular with expats and has excellent English-language support: www.tk.de/en
• Keep your Gesundheitskarte with you at all times — you'll need it at every medical visit.""",
        "author": "PME Consulting EU",
        "days_ago": 4,
    },
    # ── ARTICLES ──────────────────────────────────────────────────────────────
    {
        "category": "ART",
        "cover_emoji": "🇩🇪",
        "title": "Life as a Filipino MedTech in Germany: A First-Hand Perspective",
        "excerpt": (
            "Moving to Germany as a Medical Technologist is exciting but challenging. We spoke with "
            "PME community members about their real experiences navigating work, culture, and daily "
            "life in Deutschland."
        ),
        "content": """\"The hardest part isn't the work — the work is the same. It's the paperwork.\" — PME member, Düsseldorf

─────────────────────────────────────
THE JOURNEY BEGINS IN MANILA
─────────────────────────────────────
For many Filipino MedTechs, the journey to Germany starts years before the actual move. Language courses, credential applications, visa paperwork — layers of bureaucracy that require patience and persistence.

\"I started learning German in 2022 and applied for recognition in 2023,\" shares one PME member based in Munich. \"By early 2024, I had my Anerkennungsbescheid and my work visa within three months. But those two years of preparation made everything smooth.\"

─────────────────────────────────────
WORK CULTURE: PUNCTUALITY IS EVERYTHING
─────────────────────────────────────
German work culture is professional, structured, and highly punctual. In the laboratory, protocols are followed to the letter, and documentation is meticulous.

For Filipino MedTechs accustomed to the adaptive, problem-solving culture of Philippine hospitals, the adjustment is usually positive — the resources and equipment in German labs are world-class.

\"The analyzers here are incredible,\" says a member working in a university hospital in Hamburg. \"I felt like I was finally working with the tools the job deserves.\"

─────────────────────────────────────
THE LONELINESS IS REAL (AND MANAGEABLE)
─────────────────────────────────────
Many members cite loneliness as the most underestimated challenge. Germany can feel cold at first — not just the weather.

\"Germans are not unfriendly, they're just private,\" explains a member in Berlin. \"Once I joined a Filipino community group and some sports clubs (Vereine), things changed completely.\"

Tips from the community:
• Join a local Filipino Association (Pflegegruppe, church group, or community Facebook group)
• Enroll in a language Tandem — you practice German, your partner practices English
• Take up a group sport or hobby Verein — this is how Germans make friends

─────────────────────────────────────
FINANCES: BETTER THAN EXPECTED
─────────────────────────────────────
Entry-level MTLA salaries in Germany range from €2,800–€3,500 gross per month (depending on state and employer). After deductions (taxes, health insurance, pension), expect ~€1,900–€2,300 net.

\"I send €500–€700 home monthly and still live comfortably,\" says one member. \"The cost of living outside Munich and Frankfurt is very manageable.\"

─────────────────────────────────────
THE VERDICT
─────────────────────────────────────
Every PME member we spoke with agrees: the move is worth it. The preparation is hard, the first year is an adjustment, but the stability, career growth, and quality of life make it worthwhile.

\"Germany gave me a future I couldn't have built as fast at home. I'm grateful every day.\" — PME member, Frankfurt""",
        "author": "PME Community",
        "days_ago": 7,
    },
    {
        "category": "ART",
        "cover_emoji": "🗣️",
        "title": "Why German Language Proficiency is Non-Negotiable for Your European Career",
        "excerpt": (
            "It's tempting to think English is enough in a globalized world — but in Germany, "
            "your German language level will determine whether you get the job, pass the recognition "
            "process, and integrate successfully."
        ),
        "content": """Many Filipino healthcare professionals arrive in Germany hoping their English skills will be sufficient. While English helps in international teams, German fluency is truly non-negotiable in the clinical lab.

─────────────────────────────────────
WHY GERMAN MATTERS IN THE LAB
─────────────────────────────────────
In a hospital laboratory setting, you will:
• Receive patient samples with German-language request forms
• Communicate results to physicians and nurses — in German
• Read and follow SOPs (Standard Operating Procedures) written in German
• Document findings in German in the hospital information system (KIS)
• Handle patient inquiries about sample collection

A language error in a clinical context is not just embarrassing — it can have patient safety implications. German hospitals take this seriously.

─────────────────────────────────────
LEVELS THAT MATTER FOR EACH STAGE
─────────────────────────────────────
A1–A2 — Survival communication: greetings, simple requests. Not sufficient for work.

B1 — Basic professional communication. Minimum required by most employers and visa authorities. You can handle routine tasks but will struggle with complex discussions.

B2 — Professional working level. The sweet spot for MedTechs entering the German workforce. You can communicate fluently, understand documentation, and participate in team meetings. Highly recommended before applying.

C1 — Near-native professional proficiency. Required for senior positions, team leadership, or academic roles.

─────────────────────────────────────
HOW THE APTITUDE TEST USES YOUR GERMAN
─────────────────────────────────────
If your credentials require an Aptitude Test (Eignungsprüfung) for recognition, the oral examination will be conducted entirely in German. Examiners will:
• Ask you to explain laboratory procedures
• Discuss patient safety protocols
• Ask about quality control measures
• Explore your understanding of German laboratory standards

Without B2-level fluency, passing this exam is extremely difficult.

─────────────────────────────────────
THE PME LEARNING APPROACH
─────────────────────────────────────
Our platform teaches German through CEFR-aligned courses specifically contextualized for healthcare:
• Medical vocabulary introduced early (lab terms, anatomical terminology)
• Role-play scenarios set in laboratory and hospital environments
• Live speaking practice sessions with instructors

The sooner you start, the sooner you work. Enroll today.""",
        "author": "PME Learning Team",
        "days_ago": 3,
    },
    {
        "category": "ART",
        "cover_emoji": "⚖️",
        "title": "Know Your Rights: Filipino Workers in the European Union",
        "excerpt": (
            "Working in the EU comes with strong legal protections regardless of your nationality. "
            "From minimum wage and working hours to anti-discrimination laws — know what you're "
            "entitled to before you start."
        ),
        "content": """Germany and EU labor law provides robust protections for all workers — including non-EU citizens with valid work permits. Here's what you need to know.

─────────────────────────────────────
WORKING HOURS
─────────────────────────────────────
Under the German Working Hours Act (Arbeitszeitgesetz / ArbZG):
• Maximum: 8 hours per day (may be extended to 10 hours if averaged to 8 hours over 6 months)
• Mandatory break: 30 minutes for shifts over 6 hours; 45 minutes for shifts over 9 hours
• Mandatory rest period: 11 consecutive hours between work shifts
• Sunday work: generally prohibited (but healthcare is exempt with appropriate compensation)

─────────────────────────────────────
MINIMUM WAGE
─────────────────────────────────────
Germany's minimum wage is €12.41/hour (as of 2024). However, the healthcare sector typically pays above this via collective agreements (Tarifverträge).

If you're employed by a hospital covered by TVöD (Tarifvertrag für den öffentlichen Dienst — the public sector collective agreement), your salary is governed by standardized pay scales.

─────────────────────────────────────
ANTI-DISCRIMINATION PROTECTIONS
─────────────────────────────────────
The General Equal Treatment Act (AGG) prohibits discrimination based on:
• Race or ethnic origin
• Religion
• Gender
• Sexual orientation
• Age
• Disability

If you experience discrimination at work, you can:
1. Report it to your employer's HR or works council (Betriebsrat)
2. File a complaint with the Anti-Discrimination Agency: www.antidiskriminierungsstelle.de

─────────────────────────────────────
ANNUAL LEAVE
─────────────────────────────────────
Under German law, you are entitled to a minimum of 20 vacation days per year (based on a 5-day work week). Most collective agreements in healthcare provide 28–30 days.

─────────────────────────────────────
SICK LEAVE
─────────────────────────────────────
• First 3 days of illness: No doctor's note required (in most cases)
• From day 4: You must present a sick note (Arbeitsunfähigkeitsbescheinigung / AU) from a doctor
• First 6 weeks: Your employer pays 100% of your salary (Lohnfortzahlung)
• After 6 weeks: Your health insurer covers 70% (Krankengeld) for up to 78 weeks

─────────────────────────────────────
YOUR WORKS COUNCIL (BETRIEBSRAT)
─────────────────────────────────────
Hospitals with 5+ employees must have a Betriebsrat (works council), an elected employee representative body. They:
• Represent employee interests in negotiations with management
• Must be consulted on major changes (schedules, policies)
• Are a non-threatening first point of contact if you have a workplace issue

Get involved early — understanding your Betriebsrat is key to navigating German workplace culture.""",
        "author": "PME Legal Advisory",
        "days_ago": 2,
    },
    # ── NEWS ──────────────────────────────────────────────────────────────────
    {
        "category": "NEWS",
        "cover_emoji": "🎓",
        "title": "PME Consulting EU Launches 2026 German Language Scholarship",
        "excerpt": (
            "PME Consulting EU is pleased to announce our 2026 Language Scholarship Fund — "
            "covering full tuition for selected Filipino MedTechs enrolled in our B2 German "
            "Language Course track."
        ),
        "content": """We are thrilled to announce the PME Consulting EU 2026 German Language Scholarship.

─────────────────────────────────────
ABOUT THE SCHOLARSHIP
─────────────────────────────────────
PME Consulting EU will award full platform scholarships to 20 qualified Filipino Medical Technologists who are actively pursuing a career in Germany or another German-speaking European country.

The scholarship covers:
• Full access to all PME Learning platform courses (A1 to C2)
• Priority access to live speaking sessions
• One-on-one mentoring session with a PME certified instructor
• Certificate of Completion (PME-issued)

─────────────────────────────────────
ELIGIBILITY
─────────────────────────────────────
• Filipino citizen
• Holds a Bachelor of Science in Medical Technology (or equivalent)
• Currently pursuing or planning to pursue work in Germany, Austria, or Switzerland
• Demonstrates motivation through a brief application essay

─────────────────────────────────────
HOW TO APPLY
─────────────────────────────────────
Applications open on March 15, 2026.

To apply:
1. Create a student account on the PME Learning platform
2. Submit a 300-word essay: \"Why I want to work in Germany and how German language skills will help me achieve my goals\"
3. Upload proof of your BSMedTech degree or PRC license

Deadline: April 15, 2026.

Results will be announced on May 1, 2026.

─────────────────────────────────────
CONTACT US
─────────────────────────────────────
For questions, contact us through the PME Consulting EU official channels.

We look forward to supporting the next generation of Filipino MedTechs in Europe!""",
        "author": "PME Administration",
        "days_ago": 1,
    },
    {
        "category": "NEWS",
        "cover_emoji": "📢",
        "title": "New Course Track: B2 Examination Preparation Now Available",
        "excerpt": (
            "Our most requested course track is here — a dedicated B2 Goethe-Zertifikat "
            "preparation program, with mock exams, speaking simulations, and intensive "
            "grammar workshops."
        ),
        "content": """The B2 Goethe-Zertifikat is the gold standard for Filipino MedTechs pursuing credential recognition and employment in Germany. We've now launched a dedicated preparation track.

─────────────────────────────────────
WHAT'S INCLUDED IN THE B2 PREP TRACK
─────────────────────────────────────
• 12 structured lessons covering all four exam components:
  — Lesen (Reading) — text comprehension strategies
  — Hören (Listening) — audio exercises with German hospital scenarios
  — Schreiben (Writing) — formal letters, opinion essays, complaint letters
  — Sprechen (Speaking) — discussion simulations, role-plays
• 4 full mock exam sets (timed, with answer keys)
• Weekly live practice sessions with our instructors
• Healthcare German vocabulary supplement (lab terms, patient interaction phrases)

─────────────────────────────────────
WHO IS THIS FOR?
─────────────────────────────────────
• Students who have completed our B1 course or already have B1-level German
• Filipino MedTechs preparing for the Goethe-Zertifikat B2 examination
• Anyone targeting German credential recognition requiring B2 language proof

─────────────────────────────────────
HOW TO ENROLL
─────────────────────────────────────
Log into your PME Learning account → My Courses → Browse Catalog → filter for B2.

The track is available immediately to all active PME Learning Platform students.

Good luck — Viel Erfolg!""",
        "author": "PME Learning Team",
        "days_ago": 0,
    },
]


class Command(BaseCommand):
    help = "Seeds the resources app with sample posts about working in Europe"

    def handle(self, *args, **options):
        created = 0
        now = timezone.now()

        for data in POSTS:
            slug = data["title"].lower()
            for ch in " :,—()/":
                slug = slug.replace(ch, "-")
            # clean extra dashes
            while "--" in slug:
                slug = slug.replace("--", "-")
            slug = slug.strip("-")[:220]

            obj, was_created = Post.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": data["title"],
                    "category": data["category"],
                    "excerpt": data["excerpt"],
                    "content": data["content"],
                    "cover_emoji": data["cover_emoji"],
                    "author": data["author"],
                    "is_published": True,
                    "published_at": now - timedelta(days=data["days_ago"]),
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {obj.title[:60]}"))
            else:
                self.stdout.write(f"  – Already exists: {obj.title[:60]}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Done. {created} new post(s) seeded."))
