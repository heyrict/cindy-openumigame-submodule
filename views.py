from django.db.models import Case, Count, When
from django.shortcuts import render

from sui_hei.models import Puzzle

# Create your views here.


def mondai(request, *args, **kwargs):
    unsolved_puzzles = Puzzle.objects.filter(status__exact=0).order_by("-id")
    unsolved_puzzles = unsolved_puzzles.annotate(
        qcount=Count('dialogue'),
        uaqcount=Count(Case(When(dialogue__answer="", then=1))))
    print(unsolved_puzzles[0].qcount)
    #solved_puzzles = Puzzle.objects.filter(status__gt=0)
    return render(request, "mondai/index.html",
                  {'unsolved_puzzles': unsolved_puzzles})
