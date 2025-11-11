"""
Management command to import agents from JSON file

Usage:
    python manage.py import_agents --json-file test_agents.json

Note: directory_path is automatically calculated from SUBAGENTS_DIR + agent name.
You only need to specify: name, role, category, zellij_session_name in JSON.
"""
import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from cacs.models import Agent


class Command(BaseCommand):
    help = 'Import agents from JSON file with strict validation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            required=True,
            help='Path to agents JSON file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing agents before importing'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        clear_existing = options['clear']

        # Validate JSON file exists
        if not os.path.exists(json_file):
            raise CommandError(f"❌ JSON file not found: {json_file}")

        self.stdout.write(f"📄 Reading agents from: {json_file}")

        # Load JSON
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f"❌ Invalid JSON format: {e}")

        # Validate JSON structure
        if 'agents' not in data:
            raise CommandError("❌ JSON must contain 'agents' key")

        if not isinstance(data['agents'], list):
            raise CommandError("❌ 'agents' must be a list")

        agents_data = data['agents']
        self.stdout.write(f"Found {len(agents_data)} agents to import")
        self.stdout.write("")

        # Clear existing agents if requested
        if clear_existing:
            count = Agent.objects.count()
            if count > 0:
                self.stdout.write(f"⚠️  Clearing {count} existing agents...")
                Agent.objects.all().delete()
                self.stdout.write(self.style.WARNING("Existing agents cleared"))
                self.stdout.write("")

        # Get SUBAGENTS_DIR from settings
        subagents_dir = settings.SUBAGENTS_DIR
        self.stdout.write(f"Using SUBAGENTS_DIR: {subagents_dir}")
        self.stdout.write("")

        # Validate and import each agent
        errors = []
        success_count = 0

        for idx, agent_data in enumerate(agents_data, 1):
            agent_name = agent_data.get('name', f'UNKNOWN_{idx}')
            self.stdout.write(f"[{idx}/{len(agents_data)}] Processing: {agent_name}")

            # Calculate directory_path automatically from SUBAGENTS_DIR + agent name
            directory_path = os.path.join(subagents_dir, agent_name)
            agent_data['directory_path'] = directory_path

            # Validate required fields (STRICT)
            validation_errors = self._validate_agent(agent_data)

            if validation_errors:
                errors.append({
                    'agent': agent_name,
                    'errors': validation_errors
                })
                self.stdout.write(self.style.ERROR(f"  ❌ Validation failed"))
                for error in validation_errors:
                    self.stdout.write(self.style.ERROR(f"     - {error}"))
                self.stdout.write("")
                continue

            # Create or update agent
            try:
                agent, created = Agent.objects.update_or_create(
                    name=agent_data['name'],
                    defaults={
                        'directory_path': directory_path,
                        'role': agent_data['role'],
                        'category': agent_data['category'],
                        'zellij_session_name': agent_data['zellij_session_name'],
                    }
                )

                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"  ✓ {action}: {agent.name}"))
                success_count += 1

            except Exception as e:
                errors.append({
                    'agent': agent_name,
                    'errors': [f"Database error: {str(e)}"]
                })
                self.stdout.write(self.style.ERROR(f"  ❌ Failed: {e}"))

            self.stdout.write("")

        # Summary
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS(f"✓ Successfully imported: {success_count} agents"))

        if errors:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {len(errors)} agents"))
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("ERRORS:"))
            for error in errors:
                self.stdout.write(f"  Agent: {error['agent']}")
                for err_msg in error['errors']:
                    self.stdout.write(f"    - {err_msg}")
                self.stdout.write("")

            raise CommandError("Import completed with errors")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("🎉 Import completed successfully!"))

    def _validate_agent(self, agent_data):
        """Validate agent data with STRICT requirements

        Note: directory_path is calculated automatically, not required in JSON
        """
        errors = []

        # Required fields in JSON file (directory_path is auto-calculated)
        required_fields = ['name', 'role', 'category', 'zellij_session_name']

        for field in required_fields:
            if field not in agent_data:
                errors.append(f"Missing required field: '{field}'")
            elif not agent_data[field]:
                errors.append(f"Empty required field: '{field}'")

        # If required fields are missing, return early
        if errors:
            return errors

        # Validate name format (all caps, underscores only)
        name = agent_data['name']
        if not name.isupper():
            errors.append(f"Agent name must be uppercase: '{name}'")
        if not all(c.isalnum() or c == '_' for c in name):
            errors.append(f"Agent name can only contain letters, numbers, and underscores: '{name}'")

        # Validate directory path exists (now auto-calculated from SUBAGENTS_DIR + name)
        directory_path = agent_data.get('directory_path')
        if not directory_path:
            errors.append("Directory path not calculated (internal error)")
            return errors

        if not os.path.exists(directory_path):
            errors.append(f"Directory does not exist: '{directory_path}'")
            errors.append(f"Expected agent directory at: {directory_path}")
            errors.append(f"Create it with: mkdir -p {directory_path}/inbox {directory_path}/.triggers")

        # Validate inbox directory exists
        inbox_path = os.path.join(directory_path, 'inbox')
        if not os.path.exists(inbox_path):
            errors.append(f"Missing required subdirectory: inbox/ at {inbox_path}")

        # Warnings for optional files (don't fail import)
        todo_path = os.path.join(directory_path, 'TODO.txt')
        if not os.path.exists(todo_path):
            self.stdout.write(self.style.WARNING(f"  ⚠️  TODO.txt not found (optional)"))

        triggers_path = os.path.join(directory_path, '.triggers')
        if not os.path.exists(triggers_path):
            self.stdout.write(self.style.WARNING(f"  ⚠️  .triggers/ directory not found (optional)"))

        # Validate zellij_session_name (lowercase)
        session_name = agent_data['zellij_session_name']
        if session_name != session_name.lower():
            errors.append(f"Zellij session name must be lowercase: '{session_name}'")

        return errors
