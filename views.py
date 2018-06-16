from itertools import chain

from django.core.paginator import Paginator
from django.db.models import Case, Count, When
from django.shortcuts import redirect, render

from sui_hei.models import ChatRoom, Dialogue, Hint, Puzzle

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
