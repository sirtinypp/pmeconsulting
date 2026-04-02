from django.core.management.base import BaseCommand
from django.utils import timezone
from learning.models import Course, Lesson, TrainingEvent, LessonResource
from core.models import School
import random

COURSES = [
    {
        'title': 'German for Doctors: Patient Communication',
        'level': 'B2',
        'duration': '8 Weeks',
        'description': 'Master the art of clinical interviews, explaining diagnoses, and empathetic patient communication in a German hospital setting.',
        'lessons': [
            {
                'title': 'The Initial History Taking (Anamnese)',
                'content': 'Key phrases: "Guten Tag, mein Name ist Dr. ... Was führt Sie heute zu uns?" Explain the symptoms using "Seit wann bestehen diese Beschwerden?" and "Können Sie den Schmerz beschreiben?"',
                'type': 'DOC'
            },
            {
                'title': 'Explaining Diagnostic Procedures',
                'content': 'How to explain an MRT or blood test. "Wir müssen eine Blutuntersuchung durchführen, um Ihre Entzündungswerte zu prüfen."',
                'type': 'VID'
            },
            {
                'title': 'Dealing with Difficult News',
                'content': 'Communication strategies for palliative care and serious diagnoses. "Es fällt mir nicht leicht, Ihnen das sagen zu müssen..."',
                'type': 'SPK'
            }
        ]
    },
    {
        'title': 'Nursing German: Documentation & Handovers',
        'level': 'B1',
        'duration': '6 Weeks',
        'description': 'Focus on professional medical terminology for daily nursing duties, patient records, and shift handovers (Übergabe).',
        'lessons': [
            {
                'title': 'The ISBAR Handover Method',
                'content': 'Identify, Situation, Background, Assessment, Recommendation. "Ich übergebe Frau Müller, 72 Jahre, gestern post-OP eingetroffen..."',
                'type': 'DOC'
            },
            {
                'title': 'Vital Signs Documentation',
                'content': 'Terminology for blood pressure (Blutdruck), pulse (Puls), and oxygen saturation (Sauerstoffsättigung).',
                'type': 'EXC'
            }
        ]
    },
    {
        'title': 'Emergency Medicine: Rapid Response German',
        'level': 'B2',
        'duration': '4 Weeks',
        'description': 'High-pressure communication for ER and ICU settings. Concise reporting and emergency protocols.',
        'lessons': [
            {
                'title': 'Triage Protocols (Ersteinschätzung)',
                'content': 'Categorizing patients by urgency. "Rot: Unmittelbare Lebensgefahr. Gelb: Schwere Verletzung."',
                'type': 'DOC'
            },
            {
                'title': 'Shock Room Interactions',
                'content': 'Commands and coordination during resuscitation. "Atemwege sichern! Zugang legen!"',
                'type': 'SPK'
            }
        ]
    }
]

class Command(BaseCommand):
    help = "Seeds the course catalog with realistic clinical German courses and live events"

    def handle(self, *args, **options):
        school = School.objects.first()
        if not school:
            self.stdout.write(self.style.ERROR("No school found."))
            return

        created_courses = 0
        created_lessons = 0

        for c_data in COURSES:
            course = Course.objects.create(
                title=c_data['title'],
                school=school,
                level=c_data['level'],
                duration=c_data['duration'],
                description=c_data['description'],
                is_active=True
            )
            created_courses += 1
            
            for i, l_data in enumerate(c_data['lessons']):
                lesson = Lesson.objects.create(
                    course=course,
                    title=l_data['title'],
                    order=i,
                    lesson_type=l_data['type'],
                    description=l_data['content']
                )
                created_lessons += 1
                
                # Add a mock resource
                LessonResource.objects.create(
                    lesson=lesson,
                    title="Clinical Reference Guide.pdf",
                    resource_type='DOC',
                    url="https://example.com/medical-resource.pdf"
                )

        self.stdout.write(self.style.SUCCESS(f"✓ Seeded {created_courses} realistic courses and {created_lessons} lessons."))

        # Today's Live Event (for THE PULSE!)
        TrainingEvent.objects.create(
            title="🔴 LIVE: Simulation Training - Patient Handover",
            school=school,
            date=timezone.now().replace(hour=10, minute=0, second=0),
            location="Virtual Simulation Room A",
            description="Active roleplaying session for clinical handovers using the ISBAR method. Join now for feedback from Dr. Schmidt."
        )

        # Other events
        TrainingEvent.objects.create(
            title="Workshop: The German Licensing Exam (Approbation)",
            school=school,
            date=timezone.now() + timezone.timedelta(days=5),
            location="Berlin Center / Zoom",
            description="Preparation strategies for the FSP and KP exams."
        )

        self.stdout.write(self.style.SUCCESS("✓ Seeded Live events (including today's pulse session)."))
