"""Views pour l'app accounts."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetCompleteView as BasePasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView as BasePasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView as BasePasswordResetDoneView
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import (
    PasswordChangeForm,
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from .models import LoginHistory, UserSession


def get_client_ip(request):
    """Récupère l'adresse IP du client."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def register_view(request):
    """Gère l'inscription des utilisateurs."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Compte créé avec succès ! Vous pouvez maintenant vous connecter."
            )
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Gère la connexion des utilisateurs."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

                # Enregistrer l'historique de connexion
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    success=True,
                )

                # Créer une session utilisateur
                UserSession.objects.create(
                    user=user,
                    session_key=request.session.session_key or "",
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    is_active=True,
                )

                # Gérer "Se souvenir de moi"
                if not remember_me:
                    request.session.set_expiry(0)

                messages.success(request, f"Bienvenue, {user.first_name} !")

                # Rediriger vers la page demandée ou l'accueil
                next_url = request.GET.get("next")
                return redirect(next_url or "home")

            # Enregistrer l'échec de connexion
            LoginHistory.objects.create(
                user=None,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                success=False,
                failure_reason="Identifiants invalides",
            )
            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Gère la déconnexion."""
    if request.method == "POST":
        # Désactiver la session utilisateur
        if request.user.is_authenticated:
            UserSession.objects.filter(
                user=request.user, session_key=request.session.session_key or "", is_active=True
            ).update(is_active=False)

        logout(request)
        messages.info(request, "Vous avez été déconnecté.")
        return redirect("home")

    return render(request, "accounts/logout.html")


@login_required
def profile_view(request):
    """Affiche le profil de l'utilisateur connecté."""
    user = request.user

    # Récupère les dernières connexions
    login_history = LoginHistory.objects.filter(user=user)[:10]

    context = {
        "user": user,
        "profile": user.profile,
        "login_history": login_history,
    }

    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit_view(request):
    """Permet de modifier le profil."""
    user = request.user

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect("accounts:profile")
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }

    return render(request, "accounts/profile_edit.html", context)


@login_required
def password_change_view(request):
    """Permet de changer le mot de passe."""
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Votre mot de passe a été changé avec succès.")
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "accounts/password_change.html", {"form": form})


class PasswordResetView(BasePasswordResetView):
    """Vue pour demander la réinitialisation du mot de passe."""

    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(BasePasswordResetDoneView):
    """Vue de confirmation d'envoi de l'email de réinitialisation."""

    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    """Vue pour confirmer la réinitialisation du mot de passe."""

    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(BasePasswordResetCompleteView):
    """Vue de confirmation de réinitialisation complète."""

    template_name = "accounts/password_reset_complete.html"


@login_required
def sessions_view(request):
    """Affiche et gère les sessions actives de l'utilisateur."""
    user = request.user

    if request.method == "POST":
        session_key = request.POST.get("session_key")
        if session_key:
            # Désactiver la session spécifiée
            session = get_object_or_404(
                UserSession, user=user, session_key=session_key, is_active=True
            )
            session.deactivate()
            messages.success(request, "Session déconnectée avec succès.")
            return redirect("accounts:sessions")

    # Récupérer les sessions actives
    active_sessions = UserSession.objects.active_for_user(user)

    context = {
        "sessions": active_sessions,
        "current_session_key": request.session.session_key,
    }

    return render(request, "accounts/sessions.html", context)
