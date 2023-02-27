# Generated by Django 4.0.3 on 2022-08-17 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0013_alter_ratingmodel_learner_alter_ratingmodel_quiz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingmodel',
            name='learner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='elearn.learner'),
        ),
        migrations.AlterField(
            model_name='ratingmodel',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='elearn.quiz'),
        ),
    ]