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


# Vues pour les notifications

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    """Page listant toutes les notifications de l'utilisateur."""
    notifications = Notification.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(notifications, 20)  # 20 notifications par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Marquer comme lues les notifications affichées
    if request.method == 'POST':
        if 'mark_all_read' in request.POST:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            messages.success(request, "Toutes les notifications ont été marquées comme lues.")
            return redirect('accounts:notification_list')
    
    return render(request, 'accounts/notification_list.html', {
        'page_obj': page_obj,
        'unread_count': Notification.get_unread_count(request.user),
    })


@login_required
def notification_dropdown(request):
    """Vue partielle pour le dropdown des notifications (AJAX)."""
    notifications = Notification.get_recent_for_user(request.user, limit=5)
    unread_count = Notification.get_unread_count(request.user)
    
    return render(request, 'accounts/notification_dropdown.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@require_POST
def _check_rate_limit(request, action, max_requests=10, window=60):
    """
    Vérifie le rate limiting pour une action.
    
    Args:
        request: La requête HTTP
        action: L'identifiant de l'action (ex: 'mark_read', 'mark_all')
        max_requests: Nombre max de requêtes autorisées
        window: Fenêtre de temps en secondes
    
    Returns:
        tuple: (allowed: bool, remaining: int, reset_time: int)
    """
    from django.core.cache import cache
    
    cache_key = f"rate_limit_{action}_{request.user.id}"
    current = cache.get(cache_key, 0)
    
    if current >= max_requests:
        return False, 0, window
    
    cache.set(cache_key, current + 1, window)
    return True, max_requests - current - 1, window


@login_required
def notification_mark_read(request, notification_id):
    """Marquer une notification comme lue (AJAX)."""
    # Rate limiting: max 10 requêtes par minute
    allowed, remaining, reset_time = _check_rate_limit(request, 'mark_read', max_requests=10, window=60)
    
    if not allowed:
        return JsonResponse({
            'success': False,
            'error': 'Trop de requêtes. Veuillez réessayer dans une minute.',
            'retry_after': reset_time
        }, status=429)
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'unread_count': Notification.get_unread_count(request.user),
    })


@require_POST
@login_required
def notification_mark_all_read(request):
    """Marquer toutes les notifications comme lues (AJAX)."""
    # Rate limiting: max 5 requêtes par minute (opération plus lourde)
    allowed, remaining, reset_time = _check_rate_limit(request, 'mark_all', max_requests=5, window=60)
    
    if not allowed:
        return JsonResponse({
            'success': False,
            'error': 'Trop de requêtes. Veuillez réessayer dans une minute.',
            'retry_after': reset_time
        }, status=429)
    
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return JsonResponse({
        'success': True,
        'unread_count': 0,
    })


@login_required
def notification_preferences(request):
    """Page de configuration des préférences de notification."""
    from .models import UserNotificationPreference

    # Récupérer ou créer les préférences
    preferences = UserNotificationPreference.get_user_preferences(request.user)

    if request.method == 'POST':
        updated = False

        for pref in preferences.values():
            in_app_key = f'in_app_{pref.notification_type}'
            email_key = f'email_{pref.notification_type}'

            # Mettre à jour les préférences
            pref.in_app_enabled = in_app_key in request.POST
            pref.email_enabled = email_key in request.POST
            pref.save()
            updated = True

        if updated:
            messages.success(request, "Vos préférences de notification ont été mises à jour.")

        return redirect('accounts:notification_preferences')

    return render(request, 'accounts/notification_preferences.html', {
        'preferences': preferences,
    })


@login_required
def logs_view(request):
    """Page de logs système (superuser uniquement)."""
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
        return redirect('home:index')
    
    # Lire les logs depuis le fichier
    import os
    from django.conf import settings
    
    log_file = os.path.join(settings.BASE_DIR, 'logs', 'django.log')
    logs = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Parser les dernières lignes (format standard Django)
            for line in lines[-100:]:  # Dernières 100 lignes
                if 'ERROR' in line or 'WARNING' in line or 'INFO' in line:
                    parts = line.split(' ', 3)
                    if len(parts) >= 4:
                        logs.append({
                            'timestamp': ' '.join(parts[:2]),
                            'level': parts[2] if parts[2] in ['ERROR', 'WARNING', 'INFO', 'DEBUG'] else 'INFO',
                            'module': parts[3].split(':')[0] if ':' in parts[3] else 'unknown',
                            'message': parts[3].split(':', 1)[1].strip() if ':' in parts[3] else parts[3],
                        })
    
    # Appliquer les filtres
    level_filter = request.GET.get('level')
    module_filter = request.GET.get('module')
    
    if level_filter:
        logs = [log for log in logs if log['level'] == level_filter]
    
    if module_filter:
        logs = [log for log in logs if module_filter in log['module']]
    
    return render(request, 'accounts/logs.html', {
        'logs': logs,
    })
