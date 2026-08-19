# Generated migration for gender, country, and residency fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0016_customuser_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.CharField(
                blank=True,
                choices=[
                    ('male', 'Male'),
                    ('female', 'Female'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='country',
            field=models.CharField(blank=True, default='Kenya', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='residencyType',
            field=models.CharField(
                blank=True,
                choices=[
                    ('on-campus', 'On-Campus Resident'),
                    ('off-campus', 'Off-Campus Resident'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='hallOfResidence',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='offCampusArea',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
