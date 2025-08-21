from django.db import migrations

def link_students_to_classes(apps, schema_editor):
    StudentProfile = apps.get_model('students', 'StudentProfile')
    StudentClass = apps.get_model('results', 'StudentClass')
    for student in StudentProfile.objects.all():
        # Use the old string value to find the class
        class_name = getattr(student, 'current_class', None)
        if class_name:
            try:
                student_class = StudentClass.objects.get(name=class_name)
                student.current_class = student_class
                student.save()
            except StudentClass.DoesNotExist:
                pass

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_studentprofile_gender'),
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(link_students_to_classes, reverse_code=migrations.RunPython.noop),
    ]
