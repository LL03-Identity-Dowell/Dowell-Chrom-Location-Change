# Generated by Django 4.2.5 on 2023-10-10 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo_search', '0010_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='location',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='geo_search.location'),
        ),
    ]
