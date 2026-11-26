from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Case, When, Value, IntegerField, F
from django.utils import timezone
from .models import Task
from .forms import TaskForm


def index(request):
    return render(request, 'tasks/index.html')


@login_required
def task_list(request):
    tasks = Task.objects.filter(owner=request.user).annotate(
        priority_order=Case(
            When(priority='high', then=Value(1)),
            When(priority='normal', then=Value(2)),
            When(priority='low', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by(
        'completed',
        'priority_order',
        F('due_date').asc(nulls_last=True),
        '-date_added',
    )
    context = {'tasks': tasks, 'now': timezone.now()}
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method != 'POST':
        form = TaskForm()
    else:
        form = TaskForm(data=request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            return redirect('tasks:task_list')

    context = {'form': form}
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method != 'POST':
        form = TaskForm(instance=task)
    else:
        form = TaskForm(instance=task, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks:task_list')

    context = {'task': task, 'form': form}
    return render(request, 'tasks/task_form.html', context)


@login_required
@require_POST
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    task.delete()
    return redirect('tasks:task_list')


@login_required
@require_POST
def task_toggle(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('tasks:task_list')
