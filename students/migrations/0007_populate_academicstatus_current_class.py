from django.db import migrations


def populate_academicstatus_current_class(apps, schema_editor):
    AcademicStatus = apps.get_model('students', 'AcademicStatus')
    StudentClass = apps.get_model('results', 'StudentClass')
    for status in AcademicStatus.objects.all():
        class_name = getattr(status, 'old_current_class', None)
        if class_name and isinstance(class_name, str):
            try:
                student_class = StudentClass.objects.get(name=class_name)
                status.current_class_fk = student_class
                status.save()
            except StudentClass.DoesNotExist:
                # leave as null if no matching class is found
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_alter_academicstatus_current_class'),
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_academicstatus_current_class, reverse_code=migrations.RunPython.noop),
    ]
