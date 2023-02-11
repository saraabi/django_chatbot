# Generated by Django 4.1.5 on 2023-02-05 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_alter_answer_options_alter_question_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='respondent',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='is_training',
        ),
        migrations.AddField(
            model_name='question',
            name='is_training',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='question',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.userprofile'),
        ),
    ]