from django.db import migrations

def link_academicstatus_to_classes(apps, schema_editor):
    AcademicStatus = apps.get_model('students', 'AcademicStatus')
    StudentClass = apps.get_model('results', 'StudentClass')
    for status in AcademicStatus.objects.all():
        # If you have a backup of the old class name, use it here. Otherwise, skip.
        # For example, if you renamed the old field to 'old_current_class' before migration:
        class_name = getattr(status, 'old_current_class', None)
        if class_name and isinstance(class_name, str):
            try:
                student_class = StudentClass.objects.get(name=class_name)
                status.current_class = student_class
                status.save()
            except StudentClass.DoesNotExist:
                pass

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_populate_academicstatus_current_class'),
        ('results', '0001_initial'),
    ]

    operations = [
        # Finalize: rename the temporary FK to the real field name and remove the old string field
        migrations.RenameField(
            model_name='academicstatus',
            old_name='current_class_fk',
            new_name='current_class',
        ),
        migrations.RemoveField(
            model_name='academicstatus',
            name='old_current_class',
        ),
        # Ensure any remaining unmigrated rows are attempted (safety noop handled previously)
        migrations.RunPython(link_academicstatus_to_classes, reverse_code=migrations.RunPython.noop),
    ]
