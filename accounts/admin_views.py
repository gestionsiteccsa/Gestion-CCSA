"""Vues pour la gestion des rôles (SuperAdmin)."""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import Role, User, UserRole

logger = logging.getLogger(__name__)


def is_superadmin(user):
    """Vérifie si l'utilisateur est superadmin."""
    return user.is_superuser


# ==================== VUES ROLES ====================


@login_required
@user_passes_test(is_superadmin)
def role_list_view(request):
    """Liste les rôles avec leurs statistiques."""
    roles = Role.objects.annotate(
        users_count=Count("assigned_users", filter=Q(assigned_users__is_active=True))
    ).order_by("name")

    context = {
        "roles": roles,
        "total_roles": roles.count(),
        "default_role": Role.objects.filter(is_default=True).first(),
    }
    return render(request, "accounts/admin/roles/list.html", context)


@login_required
@user_passes_test(is_superadmin)
def role_create_view(request):
    """Création d'un nouveau rôle."""
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        color = request.POST.get("color", "#3B82F6")
        is_default = request.POST.get("is_default") == "on"

        if not name:
            messages.error(request, "Le nom du rôle est obligatoire.")
            return redirect("accounts:admin_role_create")

        if Role.objects.filter(name=name).exists():
            messages.error(request, "Un rôle avec ce nom existe déjà.")
            return redirect("accounts:admin_role_create")

        try:
            with transaction.atomic():
                # Si ce rôle devient le défaut, retirer le défaut des autres
                if is_default:
                    Role.objects.filter(is_default=True).update(is_default=False)

                Role.objects.create(
                    name=name,
                    description=description,
                    color=color,
                    is_default=is_default,
                )

                messages.success(request, f"Le rôle '{name}' a été créé avec succès.")
                return redirect("accounts:admin_role_list")

        except Exception as e:
            logger.error(f"Erreur création rôle: {e}")
            messages.error(
                request, "Une erreur est survenue lors de la création du rôle."
            )

    context = {
        "color_choices": Role.COLOR_CHOICES,
    }
    return render(request, "accounts/admin/roles/create.html", context)


@login_required
@user_passes_test(is_superadmin)
def role_edit_view(request, role_id):
    """Édition d'un rôle existant."""
    role = get_object_or_404(Role, id=role_id)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        color = request.POST.get("color", "#3B82F6")
        is_default = request.POST.get("is_default") == "on"
        is_active = request.POST.get("is_active") == "on"

        if not name:
            messages.error(request, "Le nom du rôle est obligatoire.")
            return redirect("accounts:admin_role_edit", role_id=role_id)

        if Role.objects.filter(name=name).exclude(id=role_id).exists():
            messages.error(request, "Un rôle avec ce nom existe déjà.")
            return redirect("accounts:admin_role_edit", role_id=role_id)

        try:
            with transaction.atomic():
                # Si ce rôle devient le défaut
                if is_default and not role.is_default:
                    Role.objects.filter(is_default=True).update(is_default=False)

                role.name = name
                role.description = description
                role.color = color
                role.is_default = is_default
                role.is_active = is_active
                role.save()

                messages.success(request, f"Le rôle '{name}' a été mis à jour.")
                return redirect("accounts:admin_role_list")

        except Exception as e:
            logger.error(f"Erreur modification rôle: {e}")
            messages.error(request, "Une erreur est survenue.")

    context = {"role": role}
    return render(request, "accounts/admin/roles/edit.html", context)


@login_required
@user_passes_test(is_superadmin)
@require_http_methods(["POST"])
def role_delete_view(request, role_id):
    """Suppression d'un rôle."""
    role = get_object_or_404(Role, id=role_id)

    try:
        role_name = role.name
        role.delete()
        messages.success(request, f"Le rôle '{role_name}' a été supprimé.")
    except Exception as e:
        logger.error(f"Erreur suppression rôle: {e}")
        messages.error(request, "Impossible de supprimer ce rôle.")

    return redirect("accounts:admin_role_list")


# ==================== VUES UTILISATEURS ====================


@login_required
@user_passes_test(is_superadmin)
def user_list_view(request):
    """Liste les utilisateurs avec leurs rôles."""
    search = request.GET.get("search", "")

    users = User.objects.select_related().prefetch_related("user_roles__role")

    if search:
        users = users.filter(
            Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )

    paginator = Paginator(users.order_by("-date_joined"), 20)
    page = request.GET.get("page")
    users_page = paginator.get_page(page)

    context = {
        "users": users_page,
        "search": search,
        "total_users": paginator.count,
    }
    return render(request, "accounts/admin/users/list.html", context)


@login_required
@user_passes_test(is_superadmin)
def user_assign_roles_view(request, user_id):
    """Assigne les rôles à un utilisateur (drag & drop)."""
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            role_ids = data.get("role_ids", [])

            with transaction.atomic():
                # Désactiver tous les rôles actuels
                UserRole.objects.filter(user=user).update(is_active=False)

                # Activer ou créer les nouveaux rôles
                for role_id in role_ids:
                    role = get_object_or_404(Role, id=role_id)
                    user_role, created = UserRole.objects.get_or_create(
                        user=user, role=role, defaults={"assigned_by": request.user}
                    )
                    user_role.is_active = True
                    user_role.save()

                return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Erreur assignation rôles: {e}")
            return JsonResponse({"success": False, "error": str(e)})

    # GET: Afficher la page
    all_roles = Role.objects.filter(is_active=True).order_by("name")
    user_roles = UserRole.objects.filter(user=user, is_active=True).select_related(
        "role"
    )

    context = {
        "target_user": user,
        "all_roles": all_roles,
        "user_roles": [ur.role for ur in user_roles],
    }
    return render(request, "accounts/admin/users/assign_roles.html", context)
