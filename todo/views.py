from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Todo
from .forms import TodoForm

class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todo/todo_list.html'
    context_object_name = 'todos'
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos = context['todos']
        context.update({
            'total_todos': todos.count(),
            'completed_todos': todos.filter(completed=True).count(),
            'pending_todos': todos.filter(completed=False).count(),
            'overdue_todos': len([todo for todo in todos if todo.is_overdue])
        })
        return context

class TodoDetailView(LoginRequiredMixin, DetailView):
    model = Todo
    template_name = 'todo/todo_detail.html'
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Todo created successfully!')
        return super().form_valid(form)

class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Todo updated successfully!')
        return reverse_lazy('todo:detail', kwargs={'pk': self.object.pk})

class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'todo/todo_confirm_delete.html'
    success_url = reverse_lazy('todo:list')
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Todo deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def toggle_todo_completed(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    return JsonResponse({
        'status': 'success',
        'completed': todo.completed
    })