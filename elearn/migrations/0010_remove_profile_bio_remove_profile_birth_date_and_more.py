# Generated by Django 4.0.3 on 2022-08-12 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0009_alter_progress_progress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='birth_date',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='country',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='favorite_animal',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='hobby',
        ),
        migrations.AddField(
            model_name='profile',
            name='TikTok',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='instagram',
            field=models.URLField(null=True),
        ),
    ]