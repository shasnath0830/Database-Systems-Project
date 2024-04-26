import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Deletes all HTML and Python comments from the project files.'

    def handle(self, *args, **options):
        project_directory = settings.BASE_DIR

        def delete_comments(file_path):
            with open(file_path, 'r') as file:
                content = file.read()

            content = re.sub(r'', '', content)

            with open(file_path, 'w') as file:
                file.write(content)

        def delete_comments_recursive(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.html') or file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        delete_comments(file_path)

        self.stdout.write('Deleting comments from project files...')
        delete_comments_recursive(project_directory)
        self.stdout.write(self.style.SUCCESS('Comments deleted successfully.'))