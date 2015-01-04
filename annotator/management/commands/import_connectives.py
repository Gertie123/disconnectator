from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.db.transaction import get_autocommit, set_autocommit, commit

from annotator.models import PairConnective, SingleConnective

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
                            tokens = l.strip().split('\t')
                            if len(tokens) == 1:
                                single = SingleConnective.objects.create(text=tokens[0])
                                single.save()
                            elif len(tokens) == 2:
                                pair = PairConnective.objects.create(first_half=tokens[0], second_half=tokens[1])
                                pair.save()
                        except IntegrityError:
                            print(l, 'cannot be inserted')
            commit()
        except:
            raise

        finally:
            set_autocommit(saved_ac)
