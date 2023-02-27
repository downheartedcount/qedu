# Generated by Django 4.0.3 on 2022-08-17 19:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0012_alter_profile_tiktok_alter_profile_instagram_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingmodel',
            name='learner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rats', to='elearn.learner'),
        ),
        migrations.AlterField(
            model_name='ratingmodel',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rats', to='elearn.quiz'),
        ),
    ]