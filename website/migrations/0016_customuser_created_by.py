# Generated migration for created_by field

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_customuser_completed_customuser_must_change_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users_registered', to=settings.AUTH_USER_MODEL),
        ),
    ]
