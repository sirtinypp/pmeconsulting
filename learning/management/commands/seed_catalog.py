from django.core.management.base import BaseCommand
from django.utils import timezone
from learning.models import Course, Lesson, TrainingEvent
from core.models import School
import random

COURSES = [
    {
        'title': 'German for Doctors: Patient Communication',
        'level': 'B2',
        'duration': '8 Weeks',
        'description': 'Master the art of clinical interviews, explaining diagnoses, and empathetic patient communication in a German hospital setting.',
        'lessons': ['The Initial History Taking', 'Explaining Diagnostic Procedures', 'Dealing with Difficult News', 'Informed Consent Conversations']
    },
    {
        'title': 'Nursing German: Documentation & Handovers',
        'level': 'B1',
        'duration': '6 Weeks',
        'description': 'Focus on professional medical terminology for daily nursing duties, patient records, and shift handovers (Übergabe).',
        'lessons': ['Vital Signs Documentation', 'The ISBAR Handover Method', 'Patient Care Planning', 'Professional Email Writing']
    },
    {
        'title': 'Emergency Medicine: Rapid Response German',
        'level': 'B2',
        'duration': '4 Weeks',
        'description': 'High-pressure communication for ER and ICU settings. Concise reporting and emergency protocols.',
        'lessons': ['Triage Protocols', 'ACLS Communication', 'Shock Room Interactions', 'Trauma Assessment Reporting']
    },
    {
        'title': 'Surgical Procedures: OR Communication',
        'level': 'C1',
        'duration': '10 Weeks',
        'description': 'Highly specialized vocabulary for surgeons, scrub nurses, and anesthesiologists. Intraoperative instructions and checklists.',
        'lessons': ['Surgical Instrument Vocabulary', 'Anesthesia Protocols', 'WHO Surgical Safety Checklist', 'Post-Op Instructions']
    },
    {
        'title': 'Pharmacology Basics: Meds & Dosage',
        'level': 'B1',
        'duration': '5 Weeks',
        'description': 'Learn drug classes, active ingredients, and how to explain dosage and side effects to German patients.',
        'lessons': ['Common Drug Groups', 'Explaining Side Effects', 'Calculating Dosages', 'Pharmacy Interactions']
    },
    {
        'title': 'Medical Vocabulary: Anatomy & Physiology',
        'level': 'A2',
        'duration': '12 Weeks',
        'description': 'A foundational course building the core vocabulary for the human body and its systems.',
        'lessons': ['The Skeletal System', 'Circulatory System Basics', 'Internal Organs Vocabulary', 'Nervous System Overview']
    },
    {
        'title': 'Informed Consent: Ethics & Legal German',
        'level': 'C1',
        'duration': '4 Weeks',
        'description': 'Advanced legal and ethical terminology for obtaining informed consent and navigating medical law in Germany.',
        'lessons': ['Patient Rights in Germany', 'Liability and Negligence', 'Data Privacy (GDPR/DSGVO)', 'Power of Attorney Concepts']
    },
    {
        'title': 'Psychiatry: Clinical Interviews',
        'level': 'C1',
        'duration': '8 Weeks',
        'description': 'Nuanced communication for psychiatric assessments, mental state examinations, and therapy discussions.',
        'lessons': ['Mental State Examination', 'Addiction Medicine Intro', 'Depression Assessment', 'Crisis Intervention']
    },
    {
        'title': 'Pediatrics: Interacting with Families',
        'level': 'B2',
        'duration': '6 Weeks',
        'description': 'Pediatric-specific communication for pediatricians and nurses. Dealing with concerned parents.',
        'lessons': ['Age-Appropriate Explanations', 'Childhood Vaccination Counseling', 'Emergency Pediatrics', 'Neonatology Basics']
    },
    {
        'title': 'German Healthcare: Insurance & Structure',
        'level': 'B1',
        'duration': '3 Weeks',
        'description': 'Understand how the system works: GKV vs. PKV, the role of the Hausarzt, and billing (EBM/GOÄ).',
        'lessons': ['Statutory vs Private Insurance', 'The Referral System', 'Medical Billing Intro', 'Professional Guilds (Landesärztekammer)']
    }
]

class Command(BaseCommand):
    help = "Seeds the course catalog with 10 professional clinical German courses"

    def handle(self, *args, **options):
        school = School.objects.first()
        if not school:
            self.stdout.write(self.style.ERROR("No school found. Please create one first."))
            return

        created_courses = 0
        created_lessons = 0

        for c_data in COURSES:
            course, created = Course.objects.get_or_create(
                title=c_data['title'],
                school=school,
                defaults={
                    'level': c_data['level'],
                    'duration': c_data['duration'],
                    'description': c_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_courses += 1
                for i, l_title in enumerate(c_data['lessons']):
                    Lesson.objects.get_or_create(
                        course=course,
                        title=l_title,
                        defaults={
                            'order': i,
                            'lesson_type': 'DOC',
                            'description': f"Learning materials for {l_title}."
                        }
                    )
                    created_lessons += 1

        self.stdout.write(self.style.SUCCESS(f"✓ Seeded {created_courses} courses and {created_lessons} lessons."))

        # Also seed 3 training events
        events = [
            ('Live Q&A: The Fachsprachprüfung (FSP)', timezone.now() + timezone.timedelta(days=7), 'Online Zoom'),
            ('Workshop: Clinical Handover Techniques', timezone.now() + timezone.timedelta(days=14), 'Berlin Clinical Hub'),
            ('Seminar: Patient Data Privacy in Germany', timezone.now() + timezone.timedelta(days=21), 'Online Webex'),
        ]
        
        for title, date, loc in events:
            TrainingEvent.objects.get_or_create(
                title=title,
                school=school,
                defaults={
                    'date': date,
                    'location': loc,
                    'description': f"Professional workshop for medical practitioners."
                }
            )
        self.stdout.write(self.style.SUCCESS("✓ Seeded 3 training events."))
