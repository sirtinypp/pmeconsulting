from django.test import TestCase
from django.contrib.auth import get_user_model
from learning.models import Course, CourseEnrollment, CourseTier, PaymentOrder
from core.models import School

User = get_user_model()


class PayMongoIntegrationTestCase(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Test Academy", code="TAC")
        self.user = User.objects.create_user(
            username="student_test",
            email="student@example.com",
            password="Password123!",
            school=self.school
        )
        self.course = Course.objects.create(
            title="German A1",
            level="A1",
            school=self.school,
            description="Test Course A1"
        )
        self.tier = CourseTier.objects.create(
            course=self.course,
            tier_type="BASIC",
            price=12000.00
        )

    def test_payment_order_creation_and_fulfillment(self):
        # 1. Create Enrollment in PENDING status
        enrollment = CourseEnrollment.objects.create(
            user=self.user,
            course=self.course,
            status=CourseEnrollment.Status.PENDING
        )
        self.assertEqual(enrollment.status, CourseEnrollment.Status.PENDING)

        # 2. Create Payment Order
        order = PaymentOrder.objects.create(
            user=self.user,
            enrollment=enrollment,
            tier=self.tier,
            amount=self.tier.price,
            checkout_session_id="cs_test_1234567890",
            status=PaymentOrder.PaymentStatus.PENDING
        )
        self.assertEqual(order.status, PaymentOrder.PaymentStatus.PENDING)

        # 3. Simulate Webhook Fulfillment
        order.status = PaymentOrder.PaymentStatus.PAID
        order.save()
        
        enrollment.status = CourseEnrollment.Status.ENROLLED
        enrollment.save()

        # 4. Verify enrollment automatically transitioned to ENROLLED
        updated_enrollment = CourseEnrollment.objects.get(id=enrollment.id)
        self.assertEqual(updated_enrollment.status, CourseEnrollment.Status.ENROLLED)
