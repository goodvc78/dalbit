# Generated by Django 2.1.15 on 2020-05-02 12:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dalbit', '0016_auto_20200502_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.CharField(default='full', max_length=10)),
                ('file_ver', models.CharField(default='0.0.1', max_length=50)),
                ('start_idx', models.IntegerField()),
                ('end_idx', models.IntegerField()),
                ('file_path', models.CharField(max_length=512)),
                ('reg_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
