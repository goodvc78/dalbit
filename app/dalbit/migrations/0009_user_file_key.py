# Generated by Django 2.1.15 on 2020-04-26 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dalbit', '0008_auto_20200426_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='file_key',
            field=models.CharField(max_length=10, null=True),
        ),
    ]