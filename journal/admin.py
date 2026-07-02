from django.contrib import admin
from .models import Setup, Finding, StrategyNote

@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):
    list_display = ['setup_number', 'user', 'pair', 'date', 'grade', 'outcome', 'planned_rr', 'actual_r']
    list_filter = ['grade', 'outcome', 'session', 'entry_tf', 'user']
    search_fields = ['pair', 'setup_notes', 'grade_reason']
    ordering = ['-setup_number']

@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'setup', 'created_at']
    list_filter = ['category', 'user']

@admin.register(StrategyNote)
class StrategyNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'updated_at']
