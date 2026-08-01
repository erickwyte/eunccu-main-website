from django.db import migrations


def forwards_update_roles(apps, schema_editor):
    CustomUser = apps.get_model("website", "CustomUser")
    CustomUser.objects.filter(role="admin").update(role="developer")
    CustomUser.objects.filter(role="publisher").update(role="member")
    CustomUser.objects.filter(role="librarian").update(role="leader")


def backwards_update_roles(apps, schema_editor):
    CustomUser = apps.get_model("website", "CustomUser")
    CustomUser.objects.filter(role="developer").update(role="admin")
    CustomUser.objects.filter(role="member").update(role="publisher")
    CustomUser.objects.filter(role="leader").update(role="librarian")


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0002_add_event_times"),
    ]

    operations = [
        migrations.RunPython(forwards_update_roles, backwards_update_roles),
    ]
