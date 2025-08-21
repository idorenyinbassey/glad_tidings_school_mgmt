from django.db import migrations

def link_academicstatus_to_classes(apps, schema_editor):
    AcademicStatus = apps.get_model('students', 'AcademicStatus')
    StudentClass = apps.get_model('results', 'StudentClass')
    for status in AcademicStatus.objects.all():
        # Use the old string value to find the class
        class_name = getattr(status, 'current_class', None)
        if class_name and isinstance(class_name, str):
            try:
                student_class = StudentClass.objects.get(name=class_name)
                status.current_class = student_class
                status.save()
            except StudentClass.DoesNotExist:
                pass

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_studentprofile_current_class'),
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(link_academicstatus_to_classes, reverse_code=migrations.RunPython.noop),
    ]
