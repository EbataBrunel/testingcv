# Generated by Django 4.1.6 on 2023-04-07 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eab', '0044_parcours_annee1_profile_apropos_profile_droitmes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='competence',
            name='statusan',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
