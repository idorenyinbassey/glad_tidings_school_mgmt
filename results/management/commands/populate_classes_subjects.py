from django.core.management.base import BaseCommand
from results.models import Subject, StudentClass


class Command(BaseCommand):
    help = 'Populate the database with JSS1-SS3 A-E classes and art/commerce subjects'

    def handle(self, *args, **options):
        self.stdout.write("Starting database population...")
        self.stdout.write("=" * 50)
        
        # Create subjects
        self.stdout.write("\n1. Creating subjects...")
        self.create_subjects()
        
        # Create classes
        self.stdout.write("\n2. Creating classes...")
        self.create_classes()
        
        # Assign subjects to classes
        self.stdout.write("\n3. Assigning subjects to classes...")
        self.assign_subjects_to_classes()
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Database population completed!")
        self.stdout.write(f"Total subjects: {Subject.objects.count()}")
        self.stdout.write(f"Total classes: {StudentClass.objects.count()}")
        self.stdout.write(f"Active subjects: {Subject.objects.filter(is_active=True).count()}")
        self.stdout.write(f"Active classes: {StudentClass.objects.filter(is_active=True).count()}")

    def create_subjects(self):
        """Create subjects for art, science, and commerce streams"""
        subjects_data = [
            # Core subjects for all classes
            {'name': 'Mathematics', 'code': 'MATH', 'department': 'Core'},
            {'name': 'English Language', 'code': 'ENG', 'department': 'Core'},
            {'name': 'Civic Education', 'code': 'CIV', 'department': 'Core'},
            
            # Junior Secondary subjects
            {'name': 'Basic Science', 'code': 'BSC', 'department': 'Science'},
            {'name': 'Basic Technology', 'code': 'BTECH', 'department': 'Technology'},
            {'name': 'Home Economics', 'code': 'HEC', 'department': 'Vocational'},
            {'name': 'Agricultural Science', 'code': 'AGRIC', 'department': 'Science'},
            {'name': 'Computer Studies', 'code': 'COMP', 'department': 'Technology'},
            {'name': 'French', 'code': 'FRE', 'department': 'Languages'},
            {'name': 'Social Studies', 'code': 'SOS', 'department': 'Social Sciences'},
            {'name': 'Christian Religious Studies', 'code': 'CRS', 'department': 'Religious Studies'},
            {'name': 'Islamic Religious Studies', 'code': 'IRS', 'department': 'Religious Studies'},
            {'name': 'Fine Art', 'code': 'ART', 'department': 'Arts'},
            {'name': 'Music', 'code': 'MUS', 'department': 'Arts'},
            
            # Senior Secondary Science subjects
            {'name': 'Physics', 'code': 'PHY', 'department': 'Science'},
            {'name': 'Chemistry', 'code': 'CHE', 'department': 'Science'},
            {'name': 'Biology', 'code': 'BIO', 'department': 'Science'},
            {'name': 'Further Mathematics', 'code': 'FMATH', 'department': 'Science'},
            
            # Senior Secondary Art subjects
            {'name': 'Literature in English', 'code': 'LIT', 'department': 'Arts'},
            {'name': 'Government', 'code': 'GOV', 'department': 'Arts'},
            {'name': 'History', 'code': 'HIS', 'department': 'Arts'},
            {'name': 'Geography', 'code': 'GEO', 'department': 'Arts'},
            {'name': 'Economics', 'code': 'ECO', 'department': 'Arts'},
            {'name': 'Yoruba Language', 'code': 'YOR', 'department': 'Languages'},
            {'name': 'Hausa Language', 'code': 'HAU', 'department': 'Languages'},
            {'name': 'Igbo Language', 'code': 'IGB', 'department': 'Languages'},
            
            # Senior Secondary Commercial subjects
            {'name': 'Accounting', 'code': 'ACC', 'department': 'Commercial'},
            {'name': 'Commerce', 'code': 'COM', 'department': 'Commercial'},
            {'name': 'Marketing', 'code': 'MKT', 'department': 'Commercial'},
            {'name': 'Office Practice', 'code': 'OFP', 'department': 'Commercial'},
            {'name': 'Data Processing', 'code': 'DTP', 'department': 'Commercial'},
            {'name': 'Financial Accounting', 'code': 'FACC', 'department': 'Commercial'},
            {'name': 'Store Management', 'code': 'STM', 'department': 'Commercial'},
        ]
        
        created_count = 0
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'department': subject_data['department'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created subject: {subject.name}")
            else:
                self.stdout.write(f"Subject already exists: {subject.name}")
        
        self.stdout.write(f"\nCreated {created_count} new subjects")

    def create_classes(self):
        """Create classes JSS1-SS3 A-E"""
        class_levels = [
            'JSS1', 'JSS2', 'JSS3',  # Junior Secondary School
            'SS1', 'SS2', 'SS3'      # Senior Secondary School
        ]
        
        class_sections = ['A', 'B', 'C', 'D', 'E']
        
        created_count = 0
        for level in class_levels:
            for section in class_sections:
                class_name = f"{level}{section}"
                student_class, created = StudentClass.objects.get_or_create(
                    name=class_name,
                    defaults={
                        'level': level,
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"Created class: {class_name}")
                else:
                    self.stdout.write(f"Class already exists: {class_name}")
        
        self.stdout.write(f"\nCreated {created_count} new classes")

    def assign_subjects_to_classes(self):
        """Assign appropriate subjects to each class level"""
        # Get subjects by department
        core_subjects = Subject.objects.filter(department='Core')
        junior_subjects = Subject.objects.filter(
            code__in=['BSC', 'BTECH', 'HEC', 'AGRIC', 'COMP', 'FRE', 'SOS', 'CRS', 'IRS', 'ART', 'MUS']
        )
        science_subjects = Subject.objects.filter(department='Science')
        arts_subjects = Subject.objects.filter(department='Arts')
        commercial_subjects = Subject.objects.filter(department='Commercial')
        language_subjects = Subject.objects.filter(department='Languages')
        
        # Assign subjects to JSS classes (all take the same subjects)
        jss_classes = StudentClass.objects.filter(level__startswith='JSS')
        for cls in jss_classes:
            subjects_to_add = list(core_subjects) + list(junior_subjects)
            cls.subjects.set(subjects_to_add)
            self.stdout.write(f"Assigned {len(subjects_to_add)} subjects to {cls.name}")
        
        # Assign subjects to SS classes (more specialized)
        ss_classes = StudentClass.objects.filter(level__startswith='SS')
        for cls in ss_classes:
            # All SS classes get core subjects
            subjects_to_add = list(core_subjects)
            
            # Add science subjects for all SS classes (they can choose streams)
            subjects_to_add.extend(science_subjects)
            
            # Add arts and commercial subjects for all SS classes
            subjects_to_add.extend(arts_subjects)
            subjects_to_add.extend(commercial_subjects)
            subjects_to_add.extend(language_subjects)
            
            cls.subjects.set(subjects_to_add)
            self.stdout.write(f"Assigned {len(subjects_to_add)} subjects to {cls.name}")
        
        self.stdout.write("\nSubject assignment completed")
