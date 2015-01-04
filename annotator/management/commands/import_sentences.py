from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import get_autocommit, set_autocommit, commit
from django.db import IntegrityError

from annotator.models import Sentence

class Command(BaseCommand):
    args = '<input_path ..>'
    help = 'Import sentences'

    def handle(self, *args, **options):
        saved_ac = get_autocommit()
        try:
            set_autocommit(False)
            for path in args:
                with open(path, 'r') as f:
                    for l in f:
                        try:
                            source_id, text = l.rstrip().split('\t')
                            sent = Sentence.objects.create(source_id=source_id, text=text)
                            sent.save()
                        except IntegrityError:
                            print(source_id, 'cannot be inserted')
            commit()
        except:
            raise

        finally:
            set_autocommit(saved_ac)
