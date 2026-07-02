from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Setup(models.Model):
    GRADE_CHOICES = [
        ('A', 'A-grade'),
        ('B', 'B-grade'),
        ('SKIP', 'Skip / Invalid'),
    ]
    SESSION_CHOICES = [
        ('london_open', 'London open'),
        ('london_mid', 'London mid'),
        ('ny_open', 'NY open'),
        ('ny_mid', 'NY mid'),
        ('overlap', 'London/NY overlap'),
        ('asian', 'Asian'),
        ('off', 'Off-session'),
    ]
    BIAS_CHOICES = [
        ('long', 'Long'),
        ('short', 'Short'),
        ('ranging', 'Ranging'),
    ]
    ENTRY_TF_CHOICES = [
        ('m15', 'M15 direct'),
        ('m5', 'M5'),
        ('m3', 'M3'),
        ('m1', 'M1'),
    ]
    OUTCOME_CHOICES = [
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('be', 'Break-even'),
        ('not_taken', 'Not taken'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='setups')
    setup_number = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)
    time = models.TimeField(null=True, blank=True)
    pair = models.CharField(max_length=20)
    session = models.CharField(max_length=20, choices=SESSION_CHOICES, blank=True)
    m15_bias = models.CharField(max_length=10, choices=BIAS_CHOICES, blank=True)
    entry_tf = models.CharField(max_length=5, choices=ENTRY_TF_CHOICES, blank=True)

    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)
    grade_reason = models.TextField(blank=True)

    entry_price = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    sl_distance = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    planned_rr = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    risk_percent = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES, blank=True)
    actual_r = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    exit_reason = models.CharField(max_length=200, blank=True)

    screenshot = models.ImageField(upload_to='screenshots/%Y/%m/', null=True, blank=True)

    setup_notes = models.TextField(blank=True)
    improvement_notes = models.TextField(blank=True)

    psych_tags = models.JSONField(default=list, blank=True)
    psych_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-setup_number']
        unique_together = ['user', 'setup_number']

    def __str__(self):
        return f"#{self.setup_number} {self.pair} — {self.grade} — {self.outcome}"

    @property
    def outcome_display_short(self):
        map_ = {'win': 'W', 'loss': 'L', 'be': 'BE', 'not_taken': '—'}
        return map_.get(self.outcome, '—')

    @property
    def pair_upper(self):
        return self.pair.upper()


class Finding(models.Model):
    CATEGORY_CHOICES = [
        ('entry_refinement', 'Entry refinement (M5/M3/M1)'),
        ('session_pattern', 'Session pattern'),
        ('stopout_condition', 'Stop-out condition'),
        ('breakeven_rule', 'Break-even rule'),
        ('higher_level', 'Moving to higher level'),
        ('general', 'General observation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='findings')
    setup = models.ForeignKey(Setup, on_delete=models.CASCADE, related_name='findings', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        ref = f"Setup #{self.setup.setup_number}" if self.setup else "General"
        return f"{ref} — {self.get_category_display()}"


class StrategyNote(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='strategy_note')
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — Strategy note"
