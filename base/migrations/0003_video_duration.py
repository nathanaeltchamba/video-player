# Generated by Django 4.1.5 on 2023-01-18 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0002_alter_video_video_upload"),
    ]

    operations = [
        migrations.AddField(
            model_name="video",
            name="duration",
            field=models.CharField(default="N/A", max_length=20),
        ),
    ]
