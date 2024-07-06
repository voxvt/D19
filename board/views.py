from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from .models import Ad, Response
from .forms import AdForm, ResponseForm
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.models import User
from .forms import NewsletterForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .filters import AdFilter

class AdsList(FilterView):
    model = Ad
    ordering = "-created_at"
    template_name = "ads_list.html"
    context_object_name = "ads"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = AdFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

class AdDetail(DetailView):
    models = Ad
    template_name = "ad_detail.html"
    context_object_name = "ad"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = Response.object.filter(ad=self.object)
        return context

class AdCreate(CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ad_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class AdUpdate(UpdateView):
    model = Ad
    form_class = AdForm
    template_name = "ad_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

from django.views.generic import DeleteView
from django.urls import reverse_lazy
from .models import Ad

class AdDelete(DeleteView):
    model = Ad
    template_name = "ad_delete.html"
    success_url = reverse_lazy('ads_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class ResponseCreate(CreateView):
    model = Response
    form_class = ResponseForm
    template_name = "response_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.ad = get_object_or_404(Ad, id=self.kwargs['ad_id'])
        response = super().form_valid(form)

        send_mail(
            'Новый отклик на Вашем объявлении',
            'Ваше объявление получило новый отклик'
            'ruslanSkillFactory@yandex.ru'
            [form.instance.ad.user.email],
            fail_silently=False,
        )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad'] = get_object_or_404(Ad, id=self.kwargs['ad_id'])
        return context

class ResponseDelete(View):
    def post(self, request, pk, *args, **kwargs):
        response = get_object_or_404(Response, pk=pk)
        if response.ad.user == request.user:
            response.delete()
        return redirect('ad_detail', ad_id=response.ad.id)

class ResponseAccept(View):
    def post(self, request, pk, *args, **kwargs):
        response = get_object_or_404(Response, pk=pk)
        if response.ad.user == request.user:
            response.accepted = True
            response.save()
            send_mail(
                'Ваш отклик был принят',
                'Ваш отклик на объявление был принят.',
                'ruslanSkillFactory@yandex.ru',
                [response.user.email],
                fail_silently=False,
            )
        return redirect('response_list')

class ResponseListView(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'response_list.html'
    context_object_name = 'responses'

    def get_queryset(self):
        return Response.objects.filter(ad__user=self.request.user)

class NewsletterView(FormView):
    template_name = 'newsletter.html'
    form_class = NewsletterForm
    success_url = reverse_lazy('newsletter')

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        recipients = [user.email for user in User.objects.all() if user.email]

        send_mail(subject, message, None, recipients)

        return super().form_valid(form)



