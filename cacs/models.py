"""
CACS Database Models

Defines the 5 core models:
1. Agent - Represents a coding agent
2. Communication - Mirrors communication files
3. TODO - Mirrors TODO.txt files
4. Activation - Tracks agent activation history
5. RateLimitEvent - Tracks rate limiting events
"""
import os
import uuid
from django.db import models
from django.utils import timezone


class Agent(models.Model):
    """Represents a coding agent in the system"""

    CATEGORY_CHOICES = [
        ('core', 'Core'),
        ('infrastructure', 'Infrastructure'),
        ('support', 'Support'),
        ('executive', 'Executive'),
        ('other', 'Other'),
    ]

    # Required fields
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Agent name (e.g., MAIN_AGENT)"
    )
    directory_path = models.CharField(
        max_length=500,
        help_text="Absolute path to agent's directory"
    )
    role = models.CharField(
        max_length=200,
        help_text="Agent's role/responsibility"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Agent category"
    )
    zellij_session_name = models.CharField(
        max_length=100,
        help_text="Zellij session name (lowercase)"
    )

    # Status fields
    is_active = models.BooleanField(
        default=False,
        help_text="Is Zellij session currently active?"
    )
    last_activated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last activation timestamp"
    )
    pending_messages = models.IntegerField(
        default=0,
        help_text="Count of unread communications"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agents'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def inbox_path(self):
        """Path to agent's inbox directory"""
        return os.path.join(self.directory_path, 'inbox')

    @property
    def todo_path(self):
        """Path to agent's TODO.txt file"""
        return os.path.join(self.directory_path, 'TODO.txt')

    @property
    def trigger_path(self):
        """Path to agent's wake_up trigger file"""
        return os.path.join(self.directory_path, '.triggers', 'wake_up.txt')


class Communication(models.Model):
    """Mirrors communication files from file system"""

    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('archived', 'Archived'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Communication fields
    from_agent = models.CharField(
        max_length=100,
        help_text="Sender agent name",
        db_index=True
    )
    to_agent = models.CharField(
        max_length=100,
        help_text="Recipient agent name",
        db_index=True
    )
    subject = models.CharField(
        max_length=200,
        help_text="Communication subject"
    )
    content = models.TextField(
        help_text="Full markdown content"
    )

    # File tracking
    file_path = models.CharField(
        max_length=500,
        unique=True,
        help_text="Absolute path to .md file"
    )
    file_hash = models.CharField(
        max_length=64,
        help_text="SHA256 hash of file content",
        db_index=True
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unread'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal'
    )

    # Timestamps
    created_at = models.DateTimeField(
        help_text="File creation timestamp"
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When marked as read"
    )

    class Meta:
        db_table = 'communications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['from_agent', 'to_agent']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.from_agent} → {self.to_agent}: {self.subject}"

    def mark_as_read(self):
        """Mark communication as read and update agent pending count"""
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()

            # Decrement pending_messages for recipient
            try:
                agent = Agent.objects.get(name=self.to_agent)
                agent.pending_messages = max(0, agent.pending_messages - 1)
                agent.save()
            except Agent.DoesNotExist:
                pass


class TODO(models.Model):
    """Mirrors TODO.txt files from file system"""

    agent = models.OneToOneField(
        Agent,
        on_delete=models.CASCADE,
        related_name='todo',
        help_text="Agent this TODO belongs to"
    )
    content = models.TextField(
        help_text="Full TODO.txt content",
        blank=True
    )
    line_count = models.IntegerField(
        default=0,
        help_text="Number of lines in TODO.txt"
    )
    file_path = models.CharField(
        max_length=500,
        help_text="Absolute path to TODO.txt"
    )
    file_hash = models.CharField(
        max_length=64,
        help_text="SHA256 hash of content"
    )
    last_synced = models.DateTimeField(
        auto_now=True,
        help_text="Last sync from file system"
    )

    class Meta:
        db_table = 'todos'
        verbose_name = 'TODO'
        verbose_name_plural = 'TODOs'

    def __str__(self):
        return f"TODO: {self.agent.name}"

    @property
    def exceeds_limit(self):
        """Check if TODO exceeds 150 line limit"""
        return self.line_count > 150

    @property
    def compliance_status(self):
        """Get protocol compliance status"""
        if self.line_count == 0:
            return 'empty'
        elif self.line_count <= 150:
            return 'compliant'
        else:
            return 'violation'


class Activation(models.Model):
    """Tracks agent activation history"""

    TYPE_CHOICES = [
        ('manual', 'Manual (Web UI)'),
        ('api', 'API Call'),
        ('batch', 'Batch Activation'),
        ('scheduled', 'Scheduled'),
    ]

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='activations',
        help_text="Agent that was activated"
    )
    activated_by = models.CharField(
        max_length=100,
        help_text="Who/what triggered activation (HITL, MAIN_AGENT, etc)"
    )
    activation_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='manual'
    )
    command_sent = models.TextField(
        help_text="Command sent to Zellij"
    )
    success = models.BooleanField(
        help_text="Was activation successful?"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if failed"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        db_table = 'activations'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['agent', '-timestamp']),
            models.Index(fields=['success']),
        ]

    def __str__(self):
        status = '✓' if self.success else '✗'
        return f"{status} {self.agent.name} by {self.activated_by}"


class RateLimitEvent(models.Model):
    """Tracks API rate limiting events"""

    batch_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="Unique batch identifier",
        db_index=True
    )
    agent_count = models.IntegerField(
        help_text="Number of agents in batch"
    )
    delay_seconds = models.FloatField(
        help_text="Delay applied (seconds)"
    )
    initiated_by = models.CharField(
        max_length=100,
        help_text="Who initiated the batch"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        db_table = 'rate_limit_events'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Batch {self.agent_count} agents with {self.delay_seconds}s delay"
