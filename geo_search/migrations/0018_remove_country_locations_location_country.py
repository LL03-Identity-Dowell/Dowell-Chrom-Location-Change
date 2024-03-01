# Generated by Django 4.2.5 on 2023-10-10 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo_search', '0017_rename_names_country_name_remove_location_country_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='locations',
        ),
        migrations.AddField(
            model_name='location',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='geo_search.country'),
            preserve_default=False,
        ),
    ]