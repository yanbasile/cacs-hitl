"""
CACS Django Admin Configuration
"""
from django.contrib import admin
from .models import Agent, Communication, TODO, Activation, RateLimitEvent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Admin interface for Agent model"""

    list_display = ('name', 'role', 'category', 'is_active', 'pending_messages', 'last_activated')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'role')
    readonly_fields = ('created_at', 'updated_at', 'last_activated')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'role', 'category', 'directory_path')
        }),
        ('Zellij Configuration', {
            'fields': ('zellij_session_name',)
        }),
        ('Status', {
            'fields': ('is_active', 'pending_messages', 'last_activated')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    """Admin interface for Communication model"""

    list_display = ('subject', 'from_agent', 'to_agent', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'from_agent', 'to_agent')
    search_fields = ('subject', 'from_agent', 'to_agent', 'content')
    readonly_fields = ('file_hash', 'created_at', 'read_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Communication Details', {
            'fields': ('from_agent', 'to_agent', 'subject', 'priority')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('File Information', {
            'fields': ('file_path', 'file_hash')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'read_at')
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """Mark selected communications as read"""
        for comm in queryset:
            comm.mark_as_read()
        self.message_user(request, f"{queryset.count()} communications marked as read.")
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_unread(self, request, queryset):
        """Mark selected communications as unread"""
        count = queryset.update(status='unread', read_at=None)
        self.message_user(request, f"{count} communications marked as unread.")
    mark_as_unread.short_description = "Mark selected as unread"


@admin.register(TODO)
class TODOAdmin(admin.ModelAdmin):
    """Admin interface for TODO model"""

    list_display = ('agent', 'line_count', 'compliance_status', 'last_synced')
    list_filter = ('agent__category',)
    search_fields = ('agent__name', 'content')
    readonly_fields = ('file_hash', 'last_synced', 'compliance_status', 'exceeds_limit')

    fieldsets = (
        ('Agent', {
            'fields': ('agent',)
        }),
        ('TODO Content', {
            'fields': ('content', 'line_count')
        }),
        ('File Information', {
            'fields': ('file_path', 'file_hash')
        }),
        ('Compliance', {
            'fields': ('compliance_status', 'exceeds_limit', 'last_synced')
        }),
    )


@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    """Admin interface for Activation model"""

    list_display = ('agent', 'activated_by', 'activation_type', 'success', 'timestamp')
    list_filter = ('success', 'activation_type', 'agent')
    search_fields = ('agent__name', 'activated_by', 'command_sent', 'error_message')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Activation Details', {
            'fields': ('agent', 'activated_by', 'activation_type')
        }),
        ('Command', {
            'fields': ('command_sent',)
        }),
        ('Result', {
            'fields': ('success', 'error_message', 'timestamp')
        }),
    )


@admin.register(RateLimitEvent)
class RateLimitEventAdmin(admin.ModelAdmin):
    """Admin interface for RateLimitEvent model"""

    list_display = ('batch_id', 'agent_count', 'delay_seconds', 'initiated_by', 'timestamp')
    list_filter = ('initiated_by',)
    search_fields = ('batch_id', 'initiated_by')
    readonly_fields = ('batch_id', 'timestamp')
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_id', 'agent_count', 'delay_seconds')
        }),
        ('Metadata', {
            'fields': ('initiated_by', 'timestamp')
        }),
    )
