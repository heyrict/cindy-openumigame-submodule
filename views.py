from django.core.paginator import Paginator
from django.db.models import Case, Count, When
from django.shortcuts import render

from sui_hei.models import Puzzle

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
