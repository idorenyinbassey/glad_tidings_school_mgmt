#!/usr/bin/env python
"""
Script to create sample data for the Result Management System
"""
import os
import sys
import django
from datetime import datetime, date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from results.models import (
    AcademicSession, AcademicTerm, Subject, StudentClass, Assessment,
    StudentResult, TermResult, ResultSheet
)
from students.models import StudentProfile
from staff.models import StaffProfile
from users.models import CustomUser

def create_sample_result_data():
    print("Creating sample result management data...")
    print("=" * 50)
    
    # 1. Create Academic Session
    session, created = AcademicSession.objects.get_or_create(
        name="2024/2025",
        defaults={
            'start_date': date(2024, 9, 1),
            'end_date': date(2025, 7, 15),
            'is_current': True
        }
    )
    if created:
        print(f"✓ Created Academic Session: {session.name}")
    else:
        print(f"✓ Academic Session already exists: {session.name}")
    
    # 2. Create Academic Terms
    terms_data = [
        ('first', date(2024, 9, 1), date(2024, 12, 15), True),
        ('second', date(2025, 1, 8), date(2025, 4, 15), False),
        ('third', date(2025, 4, 22), date(2025, 7, 15), False),
    ]
    
    created_terms = []
    for term_name, start_date, end_date, is_current in terms_data:
        term, created = AcademicTerm.objects.get_or_create(
            session=session,
            name=term_name,
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'is_current': is_current
            }
        )
        created_terms.append(term)
        if created:
            print(f"✓ Created Academic Term: {term}")
        else:
            print(f"✓ Academic Term already exists: {term}")
    
    # 3. Create Subjects
    subjects_data = [
        ('Mathematics', 'MATH101', 'Science'),
        ('English Language', 'ENG101', 'Arts'),
        ('Physics', 'PHY101', 'Science'),
        ('Chemistry', 'CHE101', 'Science'),
        ('Biology', 'BIO101', 'Science'),
        ('Literature', 'LIT101', 'Arts'),
        ('History', 'HIS101', 'Arts'),
        ('Geography', 'GEO101', 'Arts'),
        ('Computer Science', 'CS101', 'Science'),
        ('French', 'FRE101', 'Arts'),
    ]
    
    created_subjects = []
    for name, code, department in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'department': department,
                'is_active': True
            }
        )
        created_subjects.append(subject)
        if created:
            print(f"✓ Created Subject: {subject}")
        else:
            print(f"✓ Subject already exists: {subject}")
    
    # 4. Create Student Classes
    classes_data = [
        ('Grade 10A', 'Grade 10'),
        ('Grade 11B', 'Grade 11'),
        ('Grade 9C', 'Grade 9'),
        ('JSS 1A', 'JSS 1'),
        ('JSS 2B', 'JSS 2'),
        ('SS 1A', 'SS 1'),
        ('SS 2B', 'SS 2'),
    ]
    
    created_classes = []
    for name, level in classes_data:
        student_class, created = StudentClass.objects.get_or_create(
            name=name,
            defaults={
                'level': level,
                'is_active': True
            }
        )
        # Add subjects to the class
        if created:
            student_class.subjects.set(created_subjects[:6])  # First 6 subjects
        created_classes.append(student_class)
        if created:
            print(f"✓ Created Student Class: {student_class}")
        else:
            print(f"✓ Student Class already exists: {student_class}")
    
    # 5. Create Assessments
    assessments_data = [
        ('First CA', 'ca1', 20, 15.0),
        ('Second CA', 'ca2', 20, 15.0),
        ('Third CA', 'ca3', 20, 20.0),
        ('Examination', 'exam', 60, 50.0),
        ('Assignment', 'assignment', 10, 5.0),
        ('Project', 'project', 20, 10.0),
    ]
    
    created_assessments = []
    for name, type_code, max_score, weight in assessments_data:
        assessment, created = Assessment.objects.get_or_create(
            name=name,
            type=type_code,
            defaults={
                'max_score': max_score,
                'weight_percentage': weight,
                'is_active': True,
                'description': f'{name} assessment for all subjects'
            }
        )
        created_assessments.append(assessment)
        if created:
            print(f"✓ Created Assessment: {assessment}")
        else:
            print(f"✓ Assessment already exists: {assessment}")
    
    # 6. Create Sample Student Results (if students exist)
    students = StudentProfile.objects.all()[:3]  # Get first 3 students
    if students:
        print(f"\n📝 Creating sample results for {len(students)} students...")
        
        import random
        current_term = created_terms[0]  # First term
        
        for student in students:
            # Get student's class (assuming it's stored in a field or we'll use the first class)
            student_class = created_classes[0]  # Use first class for simplicity
            
            # Create results for first 4 subjects and first 4 assessments
            for subject in created_subjects[:4]:
                for assessment in created_assessments[:4]:
                    # Generate random score based on assessment max_score
                    max_score = assessment.max_score
                    # Generate scores between 60-95% of max score
                    min_score = int(max_score * 0.6)
                    max_possible = int(max_score * 0.95)
                    score = random.randint(min_score, max_possible)
                    
                    result, created = StudentResult.objects.get_or_create(
                        student=student,
                        subject=subject,
                        session=session,
                        term=current_term,
                        student_class=student_class,
                        assessment=assessment,
                        defaults={
                            'score': score,
                            'remarks': 'Good performance' if score >= max_score * 0.8 else 'Needs improvement'
                        }
                    )
                    
                    if created:
                        print(f"  ✓ Result: {student.user.get_full_name()} - {subject.name} - {assessment.name}: {score}/{max_score}")
    
    print("\n" + "=" * 50)
    print("🎉 SAMPLE RESULT DATA CREATED SUCCESSFULLY!")
    print("=" * 50)
    print(f"📚 Academic Session: {session.name}")
    print(f"📅 Terms: {len(created_terms)} terms created")
    print(f"📖 Subjects: {len(created_subjects)} subjects created")
    print(f"🏫 Classes: {len(created_classes)} classes created")
    print(f"📝 Assessments: {len(created_assessments)} assessments created")
    print(f"📊 Student Results: {StudentResult.objects.count()} total results")
    
    print("\n🌐 Access the Result Management System at:")
    print("http://127.0.0.1:8000/results/")
    print("\n📋 Admin Panel (to manage data):")
    print("http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    create_sample_result_data()
