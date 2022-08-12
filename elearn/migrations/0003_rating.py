# Generated by Django 4.0.3 on 2022-08-09 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0002_takenquiz_correct_alter_module_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('correct', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('learner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='elearn.learner')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='elearn.quiz')),
            ],
        ),
    ]