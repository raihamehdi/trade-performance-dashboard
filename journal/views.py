import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, Max
from django.http import JsonResponse
from .models import Setup, Finding, StrategyNote
from .forms import SetupForm, FindingForm, StrategyNoteForm, PSYCH_CHOICES


def stats_for_user(user):
    qs = Setup.objects.filter(user=user)
    total = qs.count()
    taken = qs.exclude(outcome__in=['not_taken', ''])
    wins = taken.filter(outcome='win')
    win_rate = round((wins.count() / taken.count()) * 100) if taken.count() else None
    a_grade = qs.filter(grade='A')
    a_pct = round((a_grade.count() / total) * 100) if total else None
    avg_rr = qs.filter(planned_rr__isnull=False).aggregate(a=Avg('planned_rr'))['a']
    avg_rr = round(float(avg_rr), 1) if avg_rr else None
    return {
        'total': total,
        'win_rate': win_rate,
        'a_pct': a_pct,
        'avg_rr': avg_rr,
        'progress_pct': min(round((total / 1000) * 100, 1), 100),
    }


@login_required
def dashboard(request):
    setups = Setup.objects.filter(user=request.user).order_by('-setup_number')[:20]
    stats = stats_for_user(request.user)
    next_num = (Setup.objects.filter(user=request.user).aggregate(m=Max('setup_number'))['m'] or 0) + 1
    form = SetupForm(initial={'setup_number': next_num, 'date': datetime.date.today()})
    return render(request, 'journal/dashboard.html', {
        'setups': setups,
        'stats': stats,
        'form': form,
        'next_num': next_num,
        'psych_choices': PSYCH_CHOICES,
    })


@login_required
def add_setup(request):
    if request.method == 'POST':
        form = SetupForm(request.POST, request.FILES)
        if form.is_valid():
            setup = form.save(commit=False)
            setup.user = request.user
            setup.save()
            messages.success(request, f'Setup #{setup.setup_number} saved.')
            return redirect('dashboard')
        else:
            setups = Setup.objects.filter(user=request.user).order_by('-setup_number')[:20]
            stats = stats_for_user(request.user)
            next_num = (Setup.objects.filter(user=request.user).aggregate(m=Max('setup_number'))['m'] or 0) + 1
            return render(request, 'journal/dashboard.html', {
                'setups': setups,
                'stats': stats,
                'form': form,
                'next_num': next_num,
                'psych_choices': PSYCH_CHOICES,
            })
    return redirect('dashboard')


@login_required
def setup_list(request):
    qs = Setup.objects.filter(user=request.user)
    grade_filter = request.GET.get('grade', '')
    outcome_filter = request.GET.get('outcome', '')
    pair_filter = request.GET.get('pair', '').strip()
    if grade_filter:
        qs = qs.filter(grade=grade_filter)
    if outcome_filter:
        qs = qs.filter(outcome=outcome_filter)
    if pair_filter:
        qs = qs.filter(pair__icontains=pair_filter)
    stats = stats_for_user(request.user)
    pairs = Setup.objects.filter(user=request.user).values_list('pair', flat=True).distinct()
    return render(request, 'journal/list.html', {
        'setups': qs,
        'stats': stats,
        'grade_filter': grade_filter,
        'outcome_filter': outcome_filter,
        'pair_filter': pair_filter,
        'pairs': pairs,
    })


@login_required
def setup_detail(request, pk):
    setup = get_object_or_404(Setup, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SetupForm(request.POST, request.FILES, instance=setup)
        if form.is_valid():
            form.save()
            messages.success(request, f'Setup #{setup.setup_number} updated.')
            return redirect('setup_detail', pk=pk)
    else:
        form = SetupForm(instance=setup)
    findings = setup.findings.all()
    finding_form = FindingForm(user=request.user, initial={'setup': setup})
    return render(request, 'journal/detail.html', {
        'setup': setup,
        'form': form,
        'psych_choices': PSYCH_CHOICES,
        'findings': findings,
        'finding_form': finding_form,
    })


@login_required
def setup_delete(request, pk):
    setup = get_object_or_404(Setup, pk=pk, user=request.user)
    if request.method == 'POST':
        num = setup.setup_number
        setup.delete()
        messages.success(request, f'Setup #{num} deleted.')
        return redirect('setup_list')
    return render(request, 'journal/confirm_delete.html', {'setup': setup})


@login_required
def analytics(request):
    qs = Setup.objects.filter(user=request.user)
    stats = stats_for_user(request.user)

    session_data = {}
    for s in qs.values('session').annotate(total=Count('id'), wins=Count('id', filter=Q(outcome='win'))):
        label = dict(Setup.SESSION_CHOICES).get(s['session'], s['session'] or 'Unknown')
        wr = round((s['wins'] / s['total']) * 100) if s['total'] else 0
        session_data[label] = {'total': s['total'], 'win_rate': wr}

    tf_data = {}
    for s in qs.values('entry_tf').annotate(total=Count('id'), wins=Count('id', filter=Q(outcome='win'))):
        label = dict(Setup.ENTRY_TF_CHOICES).get(s['entry_tf'], s['entry_tf'] or 'Unknown')
        wr = round((s['wins'] / s['total']) * 100) if s['total'] else 0
        tf_data[label] = {'total': s['total'], 'win_rate': wr}

    grade_data = {}
    for s in qs.values('grade').annotate(total=Count('id'), wins=Count('id', filter=Q(outcome='win'))):
        label = dict(Setup.GRADE_CHOICES).get(s['grade'], s['grade'] or 'Unknown')
        wr = round((s['wins'] / s['total']) * 100) if s['total'] else 0
        grade_data[label] = {'total': s['total'], 'win_rate': wr}

    psych_loss = {}
    for s in qs.filter(outcome='loss'):
        for tag in (s.psych_tags or []):
            psych_loss[tag] = psych_loss.get(tag, 0) + 1
    psych_loss = sorted(psych_loss.items(), key=lambda x: -x[1])

    return render(request, 'journal/analytics.html', {
        'stats': stats,
        'session_data': session_data,
        'tf_data': tf_data,
        'grade_data': grade_data,
        'psych_loss': psych_loss,
    })


@login_required
def mastery(request):
    """
    The 'What to consider next' mastery page.
    Lists all findings grouped by category, plus a form to add new ones.
    Also shows coins tested (unique pairs from logs).
    """
    findings_qs = Finding.objects.filter(user=request.user).select_related('setup')

    # Group findings by category
    grouped = {}
    for cat_key, cat_label in Finding.CATEGORY_CHOICES:
        items = findings_qs.filter(category=cat_key)
        grouped[cat_label] = {'key': cat_key, 'items': items}

    # Coins being tested — unique pairs from setups, uppercased, deduplicated
    coins = list(
        Setup.objects.filter(user=request.user)
        .values_list('pair', flat=True)
        .distinct()
        .order_by('pair')
    )
    coins = sorted(set(c.upper() for c in coins))

    if request.method == 'POST':
        form = FindingForm(user=request.user, data=request.POST)
        if form.is_valid():
            finding = form.save(commit=False)
            finding.user = request.user
            finding.save()
            messages.success(request, 'Finding saved.')
            return redirect('mastery')
    else:
        form = FindingForm(user=request.user)

    stats = stats_for_user(request.user)

    return render(request, 'journal/mastery.html', {
        'grouped': grouped,
        'coins': coins,
        'form': form,
        'stats': stats,
        'finding_categories': Finding.CATEGORY_CHOICES,
    })


@login_required
def finding_delete(request, pk):
    finding = get_object_or_404(Finding, pk=pk, user=request.user)
    if request.method == 'POST':
        finding.delete()
        messages.success(request, 'Finding deleted.')
        return redirect('mastery')
    return redirect('mastery')


@login_required
def strategy_page(request):
    note, _ = StrategyNote.objects.get_or_create(user=request.user, defaults={'content': DEFAULT_STRATEGY})
    if request.method == 'POST':
        form = StrategyNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Strategy saved.')
            return redirect('strategy_page')
    else:
        form = StrategyNoteForm(instance=note)
    return render(request, 'journal/strategy.html', {'form': form, 'note': note})


DEFAULT_STRATEGY = """# Strategy A — SMC Structure Entry

## Core concept
Based on Advanced SMC (Smart Money Concepts). Trades structural breaks with confirmation.

## Key definitions

**BOS (Break of Structure)**
A BOS occurs when price takes the liquidity of the last significant swing low (in an uptrend) or swing high (in a downtrend), confirming continuation of the current leg.

**CHoCH (Change of Character)**
A CHoCH occurs when price takes the liquidity of the last swing high/low against the prevailing trend, signalling a potential reversal and the start of a new directional move.

**Strong High / Strong Low**
- After a CHoCH or BOS, the origin point of the impulse move becomes a Strong High (in a bearish structure) or Strong Low (in a bullish structure).
- This is the zone price is likely to return to — it represents institutional order flow origin.

## Entry rules

1. Identify structure on M15 — confirm BOS or CHoCH
2. Mark the Strong High or Strong Low (origin of the impulse)
3. Wait for price to return to that zone
4. Entry trigger: price enters the zone, then closes a candle BACK OUTSIDE the zone (on M15, confirmed on M5/M3/M1)
5. Stop loss: beyond the Strong High/Low zone
6. Take profit: next liquidity zone (opposing swing high/low or equal highs/lows)

## Why this works
Price always seeks liquidity. Institutional orders are placed at origin zones. When price returns, it either fills and reverses (confirming the zone) or sweeps through (invalidating it). The close-back-outside confirmation avoids entering on wicks that don't close.

## Coin watchlist approach
- Monitor 10–15 coins simultaneously on M15
- Expect 3–4 setups per coin per month
- Monitoring 15 coins = ~45–60 setups/month

## Refinement checklist (in progress)
- [ ] Which sessions give cleanest entry closes?
- [ ] M5 vs M1 entry: which reduces SL distance more?
- [ ] What does a failing zone look like vs a holding zone?
- [ ] When to move to break-even vs let it run?
"""
