"""Views pour l'app url_shortener."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, View

from .forms import ShortenedURLForm
from .models import ShortenedURL


class ShortenedURLListView(LoginRequiredMixin, ListView):
    """Liste des URLs raccourcies de l'utilisateur connecté."""
    
    model = ShortenedURL
    template_name = "url_shortener/shortenedurl_list.html"
    context_object_name = "shortened_urls"
    paginate_by = 20
    ordering = ["-created_at"]
    
    def get_queryset(self):
        """Retourne uniquement les liens de l'utilisateur connecté."""
        return ShortenedURL.objects.filter(
            created_by=self.request.user
        ).order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        """Ajoute des données contextuelles."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Mes liens raccourcis"
        return context


class ShortenedURLCreateView(LoginRequiredMixin, CreateView):
    """Création d'une nouvelle URL raccourcie."""
    
    model = ShortenedURL
    form_class = ShortenedURLForm
    template_name = "url_shortener/shortenedurl_form.html"
    success_url = reverse_lazy("url_shortener:list")
    
    def get_context_data(self, **kwargs):
        """Ajoute des données contextuelles."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Raccourcir un lien"
        context["action"] = "Créer"
        return context
    
    def form_valid(self, form):
        """Gère la création réussie."""
        try:
            self.object = form.save(user=self.request.user)
            
            short_url = self.object.get_short_url()
            
            messages.success(
                self.request,
                f'Le lien a été créé avec succès ! Votre lien court est : {short_url}'
            )
            
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(
                self.request,
                f'Une erreur est survenue lors de la création du lien : {str(e)}'
            )
            return self.form_invalid(form)


class ShortenedURLDeleteView(LoginRequiredMixin, DeleteView):
    """Suppression d'une URL raccourcie."""
    
    model = ShortenedURL
    template_name = "url_shortener/shortenedurl_confirm_delete.html"
    success_url = reverse_lazy("url_shortener:list")
    slug_url_kwarg = "code"
    slug_field = "code"
    
    def get_queryset(self):
        """S'assurer que l'utilisateur ne peut supprimer que ses propres liens."""
        return ShortenedURL.objects.filter(created_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Ajoute des données contextuelles."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Supprimer le lien"
        return context
    
    def delete(self, request, *args, **kwargs):
        """Gère la suppression avec message de confirmation."""
        self.object = self.get_object()
        short_url = self.object.get_short_url()
        
        messages.success(
            request,
            f'Le lien "{short_url}" a été supprimé avec succès.'
        )
        
        return super().delete(request, *args, **kwargs)


class ShortenedURLRedirectView(View):
    """Redirection vers l'URL originale."""
    
    def get(self, request, code, *args, **kwargs):
        """Gère la redirection."""
        shortened_url = get_object_or_404(ShortenedURL, code=code)
        return HttpResponseRedirect(shortened_url.original_url)


@login_required
def shortened_url_list(request):
    """Vue fonctionnelle alternative pour la liste des URLs."""
    shortened_urls = ShortenedURL.objects.filter(
        created_by=request.user
    ).order_by("-created_at")
    
    context = {
        "shortened_urls": shortened_urls,
        "title": "Mes liens raccourcis"
    }
    
    return render(request, "url_shortener/shortenedurl_list.html", context)
