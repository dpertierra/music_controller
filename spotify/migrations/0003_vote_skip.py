# Generated by Django 3.1.4 on 2021-01-06 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0002_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='skip',
            field=models.BooleanField(default=True),
        ),
    ]
