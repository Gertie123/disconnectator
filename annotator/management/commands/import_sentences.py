from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import get_autocommit, set_autocommit, commit
from django.db import IntegrityError

from annotator.models import Sentence, PairConnective, SingleConnective
from annotator.views import analyse_tokens

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
                            tokens = text.strip().split(' ')
                            targets, _, _ = analyse_tokens(tokens)
                            if len(targets) > 0:
                                sent = Sentence.objects.create(source_id=source_id, text=text)
                                sent.save()
                            else:
                                print(source_id, 'does not have connectives')
                        except IntegrityError:
                            print(source_id, 'cannot be inserted')
            commit()
        except:
            raise

        finally:
            set_autocommit(saved_ac)
