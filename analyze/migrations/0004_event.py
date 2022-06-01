# Generated by Django 4.0.4 on 2022-05-29 02:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0003_alter_encodings_group_alter_encodings_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analyze.photo')),
            ],
        ),
    ]