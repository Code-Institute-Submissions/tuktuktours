# Generated by Django 3.1.5 on 2021-01-31 11:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_auto_20210117_0808'),
        ('contact', '0003_message_user_profile'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Message',
            new_name='Contact',
        ),
    ]
