# Generated manually for counter_number addition on QueueToken

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuetoken',
            name='counter_number',
            field=models.CharField(
                blank=True,
                default='Counter 1',
                help_text='Desk or Counter number calling/serving this token',
                max_length=50,
                verbose_name='Counter Number'
            ),
        ),
    ]
