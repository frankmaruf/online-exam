# Generated by Django 4.1.7 on 2023-03-31 04:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('online_test', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='start_time',
        ),
    ]