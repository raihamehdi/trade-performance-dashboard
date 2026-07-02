from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setup',
            name='psych_note',
            field=models.TextField(blank=True),
        ),
    ]
