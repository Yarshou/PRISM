# Generated by Django 4.0.4 on 2022-05-24 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='is_avatar',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Avatar',
        ),
    ]
