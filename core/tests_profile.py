from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from students.models import StudentProfile
from staff.models import StaffProfile
import datetime

User = get_user_model()

class ProfileUpdateTest(TestCase):
    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            username='student1',
            password='testpass123',
            email='student1@example.com',
            first_name='Student',
            last_name='One',
            role='student'
        )
        
        # Create a student profile
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_number='S12345',
            date_of_birth=datetime.date(2005, 5, 15),
            address='123 Student Street',
            guardian_name='Parent One',
            guardian_contact='555-1234'
        )
        
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staff1',
            password='testpass456',
            email='staff1@example.com',
            first_name='Staff',
            last_name='One',
            role='staff'
        )
        
        # Create a staff profile
        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            staff_id='T12345',
            position='teacher',
            department='science',
            phone='555-6789',
            address='456 Staff Avenue'
        )
        
        # Set up the test client
        self.client = Client()
    
    def test_student_profile_update(self):
        """Test that a student can update their profile"""
        # Log in as student
        self.client.login(username='student1', password='testpass123')
        
        # Prepare update data
        update_data = {
            'first_name': 'Student',
            'last_name': 'Updated',
            'email': 'student_updated@example.com',
            'address': 'New Address Street',
            'guardian_name': 'New Parent Name',
            'guardian_contact': '555-9876'
        }
        
        # Submit the form
        response = self.client.post(reverse('profile'), update_data)
        
        # Should redirect back to profile page
        self.assertRedirects(response, reverse('profile'))
        
        # Refresh user and profile from database
        self.student_user.refresh_from_db()
        self.student_profile.refresh_from_db()
        
        # Check that values were updated
        self.assertEqual(self.student_user.last_name, 'Updated')
        self.assertEqual(self.student_user.email, 'student_updated@example.com')
        self.assertEqual(self.student_profile.address, 'New Address Street')
        self.assertEqual(self.student_profile.guardian_name, 'New Parent Name')
        self.assertEqual(self.student_profile.guardian_contact, '555-9876')
    
    def test_staff_profile_update(self):
        """Test that a staff member can update their profile"""
        # Log in as staff
        self.client.login(username='staff1', password='testpass456')
        
        # Prepare update data
        update_data = {
            'first_name': 'Staff',
            'last_name': 'Updated',
            'email': 'staff_updated@example.com',
            'position': 'senior teacher',
            'phone': '555-4321',
            'address': 'New Staff Address'
        }
        
        # Submit the form
        response = self.client.post(reverse('profile'), update_data)
        
        # Should redirect back to profile page
        self.assertRedirects(response, reverse('profile'))
        
        # Refresh user and profile from database
        self.staff_user.refresh_from_db()
        self.staff_profile.refresh_from_db()
        
        # Check that values were updated
        self.assertEqual(self.staff_user.last_name, 'Updated')
        self.assertEqual(self.staff_user.email, 'staff_updated@example.com')
        self.assertEqual(self.staff_profile.position, 'senior teacher')
        self.assertEqual(self.staff_profile.phone, '555-4321')
        self.assertEqual(self.staff_profile.address, 'New Staff Address')
