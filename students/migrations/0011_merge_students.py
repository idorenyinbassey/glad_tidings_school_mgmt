from django.db import migrations


class Migration(migrations.Migration):

    # This is an auto-created merge migration to resolve multiple leaf nodes.
    dependencies = [
        ('students', '0006_link_academicstatus_to_classes'),
        ('students', '0010_populate_studentprofile_current_class'),
    ]

    operations = [
        # No operations: this migration only merges the two branches of the students
        # migration graph so that `migrate` can proceed. Any data/schema work is
        # already implemented in the referenced migrations.
    ]
