import re
from itertools import chain

from django.core.paginator import Paginator
from django.db.models import Case, Count, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from sui_hei.models import ChatMessage, ChatRoom, Dialogue, Hint, Puzzle

# Create your views here.


def mondai(request, *args, **kwargs):
    def _get_qs(qs):
        return qs.order_by("-id").annotate(
            qcount=Count('dialogue'),
            uaqcount=Count(Case(When(dialogue__answer="", then=1))))

    unsolved_puzzles = _get_qs(Puzzle.objects.filter(status__exact=0))
    solved_puzzles = _get_qs(Puzzle.objects.filter(status__gt=0))
    paginated_solved_puzzles = Paginator(solved_puzzles, 10)

    page_num = request.GET.get('page', 1)

    return render(
        request, "mondai/index.html", {
            'unsolved_puzzles': unsolved_puzzles,
            'solved_puzzles': paginated_solved_puzzles.page(page_num),
        })


def mondai_show(request, *args, **kwargs):
    puzzleId = kwargs.get('id')
    if not puzzleId:
        return redirect('/')

    puzzle = Puzzle.objects.get(pk=puzzleId)
    dialogue_list = Dialogue.objects.filter(
        puzzle__exact=puzzle).order_by("id")
    hint_list = Hint.objects.filter(puzzle__exact=puzzle)
    chatroom = ChatRoom.objects.get(name="puzzle-%d" % puzzleId)

    for i in range(len(dialogue_list)):
        dialogue_list[i].index = i + 1

    return render(
        request, "mondai/show.html", {
            "puzzle": puzzle,
            "union_list": sorted(chain(dialogue_list, hint_list), key=lambda x: x.created),
            "chatroom": chatroom,
        }) # yapf: disable


def mondai_show_push_answ(request, **kwargs):
    if request.method == "POST" and request.user.is_authenticated:
        puzzleId = kwargs.get('id')
        if not puzzleId:
            return redirect('/')
        try:
            to_update = {}
            PALEN = len('push_answ_')
            CGLEN = len('check_goodques_')
            CTLEN = len('check_trueansw_')
            for pk in request.POST.keys():
                if pk[:PALEN] == 'push_answ_':
                    pk = pk[PALEN:]
                    if pk not in to_update:
                        to_update[pk] = get_object_or_404(Dialogue, id=pk)
                    answer = request.POST.get('push_answ_' + pk)
                    if answer: to_update[pk].answer = answer
                elif pk[:CGLEN] == 'check_goodques_':
                    pk = pk[CGLEN:]
                    if pk not in to_update:
                        to_update[pk] = get_object_or_404(Dialogue, id=pk)
                    to_update[pk].good = not to_update[pk].good
                elif pk[:CTLEN] == 'check_trueansw_':
                    pk = pk[CTLEN:]
                    if pk not in to_update:
                        to_update[pk] = get_object_or_404(Dialogue, id=pk)
                    to_update[pk].true = not to_update[pk].true

            for _, obj in to_update.items():
                if not obj.answer:
                    obj.answeredtime = timezone.now()
                else:
                    obj.answerEditTimes += 1
                obj.save()
        except Exception as e:
            print("PushAnsw:", e)
    return redirect(request.META['HTTP_REFERER'].split('?', 1)[0])


def mondai_show_push_ques(request, **kwargs):
    if request.method == "POST" and request.user.is_authenticated:
        puzzleId = kwargs.get('id')
        if not puzzleId:
            return redirect('/')
        try:
            puzzle = get_object_or_404(Puzzle, id=puzzleId)
            content = request.POST['push_ques']
            if content == '': raise ValueError("Empty Input Data")

            ques = Dialogue(
                user=request.user,
                question=content.strip(),
                created=timezone.now(),
                puzzle=puzzle)
            ques.save()
        except Exception as e:
            print("PushQues:", e)
    return redirect(request.META['HTTP_REFERER'].split('?', 1)[0])


def mondai_show_push_chatmessage(request, **kwargs):
    if request.method == "POST" and request.user.is_authenticated:
        puzzleId = kwargs.get('id')
        chatroom = ChatRoom.objects.get(name="puzzle-%d" % puzzleId)
        if not puzzleId:
            return redirect('/')
        try:
            puzzle = get_object_or_404(Puzzle, id=puzzleId)
            content = request.POST['push_chatmessage']
            if content == '': raise ValueError("Empty Input Data")

            chatmessage = ChatMessage(
                user=request.user,
                content=content.strip(),
                created=timezone.now(),
                chatroom=chatroom)
            chatmessage.save()
        except Exception as e:
            print("PushQues:", e)
    return redirect(request.META['HTTP_REFERER'].split('?', 1)[0])
