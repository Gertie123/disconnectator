import json
import random

from collections import defaultdict

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from annotator.models import Annotation, PairConnective, Sentence, SingleConnective, Task

@login_required
@ensure_csrf_cookie
def dashboard(request):
    return render(request,  'annotator/dashboard.html', {'title': 'Dashboard', 'username': request.user.username})

@ensure_csrf_cookie
def thanks(request, token=None):
    if token is not None:
        logout(request)
        login_with_token(request, token)
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(dashboard))
    else:
        return render(request, 'annotator/thanks.html')

# -- Ajax functions -- #

def ajax(request):
    if request.method == 'POST' and request.is_ajax():
        fnc = request.POST['fnc']
        if fnc == 'login':
            if login_with_token(request, request.POST['token']):
                return HttpResponse()
        elif request.user.is_authenticated():
            if fnc == 'logout':
                logout(request)
                return HttpResponse()
            elif fnc == 'show-task-list':
                return show_task_list(request.user)
            elif fnc == 'show-task':
                return show_task(request.user, int(request.POST['sentence']))
            elif fnc == 'update':
                return update_task(request.user, int(request.POST['sentence']),
                        request.POST.getlist('singles[]'),
                        request.POST.getlist('pairs[]'),
                        request.POST['time_spent'])

    return HttpResponseServerError()

def login_with_token(request, token):
    user = authenticate(username=token, password=token)
    if user is not None and user.is_active:
        login(request, user)
        return True
    else:
        return False

def show_task_list(user):
    tasks = [{'sentence': t.sentence.id, 'done': t.is_done} for t in Task.objects.filter(annotator=user)]
    done = sum(t['done'] for t in tasks)

    response_data = {'total': len(tasks), 'done': done, 'tasks': tasks, 'task_mode': user.is_task_mode, 'next': get_undone_sentence(user)}

    return HttpResponse(json.dumps(response_data), content_type='application/json')

def show_task(user, sentence_num):
    sentence = Sentence.objects.get(id=sentence_num)
    if sentence is not None:
        if not user.is_task_mode:
            if not Task.objects.filter(annotator=user, sentence=sentence).exists():
                Task.objects.create(annotator=user, sentence=sentence).save()
        task = Task.objects.get(annotator=user, sentence=sentence)
        if task is not None:
            total = Task.objects.filter(annotator=user)
            done = total.filter(is_done=True)

            tokens = sentence.text.strip().split(' ')
            targets, singles, pairs = analyse_tokens(tokens)

            annotations = Annotation.objects.filter(annotator=user, sentence=sentence)
            m_singles = {}
            m_pairs = {}
            for x in annotations:
                pos = x.positions.split(',')
                if len(pos) == 2:
                    a, b = (int(x) for x in pos)
                    if a in pairs and b in pairs[a]:
                        m_pairs[int(pos[0])] = int(pos[1])
                else:
                    a = int(pos[0])
                    if a in singles:
                        m_singles[int(pos[0])] = True

            response_data = {'total': total.count(), 'done': done.count(), 'tokens': tokens,
                    'targets': targets, 'singles': singles, 'pairs': pairs,
                    'm_singles': m_singles, 'm_pairs': m_pairs}

            return HttpResponse(json.dumps(response_data), content_type='application/json')

    return HttpResponseServerError()

def analyse_tokens(tokens):
    c_singles = {t.text for t in SingleConnective.objects.all()}
    c_pairs = defaultdict(list)
    for t in PairConnective.objects.all():
        c_pairs[t.first_half].append(t.second_half)

    singles = {i: True for i in range(len(tokens)) if tokens[i] in c_singles}
    targets = dict(singles)

    pairs = defaultdict(dict)
    for i, x in enumerate(tokens):
        if x in c_pairs:
            paired = {idx: True for idx in indices(tokens, c_pairs[x], start=i)}
            if len(paired) > 0:
                pairs[i] = paired
                targets[i] = True
                for idx in paired:
                    targets[idx] = True

    for fst, snds in list(pairs.items()):
        for snd in list(snds):
            pairs[snd][fst] = True

    return targets, singles, pairs

def indices(lst, value_list, *, start=0):
    for i, x in enumerate(lst):
        if i >= start and x in value_list:
            yield i

def update_task(user, sentence_num, m_singles, m_pairs, time_spent):
    sentence = Sentence.objects.get(id=sentence_num)
    if sentence is not None:
        task = Task.objects.get(annotator=user, sentence=sentence)
        if task is not None:
            # validate update
            tokens = sentence.text.strip().split(' ')
            _, singles, pairs = analyse_tokens(tokens)

            if not all(int(offset) in singles for offset in m_singles):
                return HttpResponseServerError()

            m_pairs = list(map(lambda x: (int(x[0]), int(x[1])), (x.split('-') for x in m_pairs)))

            for x, y in m_pairs:
                if x not in pairs or y not in pairs[x]:
                    return HttpResponseServerError()

            # update annotation

            Annotation.objects.filter(annotator=user, sentence=sentence).delete()

            for x in m_singles:
                Annotation.objects.create(annotator=user, sentence=sentence, positions=x).save()

            for x, y in m_pairs:
                if x > y:
                    x, y = y, x
                Annotation.objects.create(annotator=user, sentence=sentence, positions='{},{}'.format(x, y)).save()

            # update task
            task.is_done = True

            time_spents = ','.join([time_spent] + task.finished_times.split(',')).strip(',')
            # ensure length limit
            while len(time_spents) > 90:
                splited = time_spents.rsplit(',', 1)
                if len(splited) == 1:
                    time_spents = ''
                else:
                    time_spents = splited[0]
            task.finished_times = time_spents

            task.save()

            response_data = {'next': get_undone_sentence(user)}

            return HttpResponse(json.dumps(response_data), content_type='application/json')

    return HttpResponseServerError()

def get_undone_sentence(user):
    if user.is_task_mode:
        next_tasks = Task.objects.filter(annotator=user, is_done=False)
        if next_tasks.exits():
            return next_tasks[0]
        else:
            return 'none'
    else:
        sents = {}
        for sent in Sentence.objects.all():
            sents[sent.id] = 0

        for t in Task.objects.filter(is_done=True):
            sents[t.sentence.id] += 1

        for t in Task.objects.filter(annotator=user, is_done=True):
            del sents[t.sentence.id]

        if len(sents) == 0:
            return 'none'

        undone = list(sents.keys())
        random.shuffle(undone)
        undone.sort(key=lambda x: sents[x])

        return undone[0]
