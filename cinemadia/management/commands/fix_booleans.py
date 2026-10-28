import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

BOOLEAN_PATTERN = re.compile(r'\b(true|false)\b', flags=re.IGNORECASE)


class Command(BaseCommand):
    """Fix lowercase JSON booleans in a file (true/false -> True/False)."""

    help = 'Fayldagi true/false qiymatlarni Python True/False ga aylantiradi.'

    def add_arguments(self, parser):
        parser.add_argument('filename', help='Tuzatiladigan fayl yo‘li')

    def handle(self, *args, **options):
        path = Path(options['filename'])
        if not path.is_file():
            raise CommandError(f'Fayl topilmadi: {path}')

        content = path.read_text(encoding='utf-8')
        fixed = BOOLEAN_PATTERN.sub(lambda match: match.group(1).capitalize(), content)
        path.write_text(fixed, encoding='utf-8')

        self.stdout.write(
            self.style.SUCCESS(f"'{path}' faylidagi true/false qiymatlar to‘g‘rilandi.")
        )
