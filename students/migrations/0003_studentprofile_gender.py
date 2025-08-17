from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_studentprofile_created_at_studentprofile_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=10),
        ),
    ]
