# Generated by Django 5.1.2 on 2024-10-18 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='blockchain_tx_hash',
            field=models.CharField(blank=True, max_length=66, null=True),
        ),
    ]
