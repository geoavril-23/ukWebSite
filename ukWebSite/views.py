from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from .models import MessageContact, User, Profile

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        institution = request.POST.get('institution')
        promotion = request.POST.get('promotion')
        sujet = request.POST.get('sujet')
        message_text = request.POST.get('message')

        # Conversion de la promotion en entier si possible
        promo_val = None
        if promotion and promotion.isdigit():
            promo_val = int(promotion)

        # Lier le message à l'utilisateur s'il est connecté
        auteur = request.user if request.user.is_authenticated else None

        # Création du message dans la base de données
        MessageContact.objects.create(
            prenom=prenom,
            nom=nom,
            email=email,
            telephone=telephone,
            institution=institution,
            promotion=promo_val,
            sujet=sujet,
            message=message_text,
            auteur=auteur
        )

        messages.success(request, "Votre message a été envoyé avec succès ! L'équipe vous contactera très prochainement.")
        return redirect('contact')

    return render(request, 'contact.html')

def events(request):
    return render(request, 'events.html')

def members(request):
    return render(request, 'members.html')

def ressources(request):
    return render(request, 'ressources.html')

def actualites(request):
    return render(request, 'actualites.html')

def admin_dashboard(request):
    # **CHOIX 1** : Superuser → direct Users ! Manager → stats messages
    if request.user.is_superuser:
        return redirect('admin_users')
    
    # Garde stats pour Manager (comme avant)
    total_messages = MessageContact.objects.count()
    pending_messages = MessageContact.objects.filter(statut='attente').count()
    whatsapp_contacts = MessageContact.objects.exclude(telephone='').count()
    
    context = {
        'total_messages': total_messages,
        'pending_messages': pending_messages,
        'whatsapp_contacts': whatsapp_contacts,
    }
    return render(request, 'dashboard/index.html', context)

# **NOUVEAU** : Ajouter user (formulaire POST)
def add_user(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = request.POST.get('role', 'visiteur')
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()

        # Validations
        if not username or not email or not password:
            messages.error(request, "Nom d'utilisateur, email et mot de passe sont obligatoires.")
            return redirect('admin_users')

        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('admin_users')

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('admin_users')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Le nom d'utilisateur « {username} » est déjà pris.")
            return redirect('admin_users')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"L'adresse email « {email} » est déjà utilisée.")
            return redirect('admin_users')

        if role not in ['manager', 'visiteur']:
            role = 'visiteur'

        # Créer l'utilisateur
        new_user = User.objects.create_user(username=username, email=email, password=password)
        new_user.first_name = prenom
        new_user.last_name = nom
        new_user.save()

        # Créer/mettre à jour le profil avec le rôle choisi
        profile, created = Profile.objects.get_or_create(user=new_user)
        profile.role = role
        profile.prenom = prenom
        profile.nom = nom
        profile.save()

        role_label = "Manager" if role == 'manager' else "Visiteur"
        messages.success(request, f"✅ Compte de {username} créé avec succès en tant que {role_label} !")
        return redirect('admin_users')
    
    return redirect('admin_users')

# **NOUVEAU** : Modifier user
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        prenom   = request.POST.get('prenom', '').strip()
        nom      = request.POST.get('nom', '').strip()

        # Vérifier unicité username (sauf pour lui-même)
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, f"Le nom d'utilisateur « {username} » est déjà pris.")
            return redirect('admin_users')

        target_user.username   = username
        target_user.email      = email
        target_user.first_name = prenom
        target_user.last_name  = nom
        if password:
            target_user.set_password(password)
        target_user.save()

        # Mettre à jour le profil
        profile, _ = Profile.objects.get_or_create(user=target_user)
        profile.prenom = prenom
        profile.nom    = nom
        profile.save()

        messages.success(request, f"✅ Compte de {username} mis à jour avec succès !")
        return redirect('admin_users')
    
    return redirect('admin_users')

# **NOUVEAU** : Supprimer user
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    return JsonResponse({'success': f'User {username} supprimé'})

def admin_messages(request):
    # **SÉCURITÉ** : Superuser → UNIQUEMENT Users !
    if request.user.is_superuser:
        messages.error(request, "Messages réservés aux Managers.")
        return redirect('admin_users')
    
    # **MANAGER UNIQUEMENT** : Vérif role
    try:
        user_role = request.user.profile.role
        if user_role != 'manager':
            messages.error(request, "Accès réservé aux Managers.")
            return redirect('admin_dashboard')
    except:
        messages.error(request, "Rôle non configuré.")
        return redirect('admin_dashboard')
    
    qs = MessageContact.objects.all().order_by('-date_envoi')

    # Filtre statut
    statut_filter = request.GET.get('statut', '')
    if statut_filter in ['attente', 'termine']:
        qs = qs.filter(statut=statut_filter)

    # Filtre période
    periode = request.GET.get('periode', '')   # jour | mois | annee
    jour    = request.GET.get('jour', '')
    mois    = request.GET.get('mois', '')
    annee   = request.GET.get('annee', '')

    from django.utils import timezone
    import datetime

    if periode == 'jour' and jour:
        try:
            d = datetime.datetime.strptime(jour, '%Y-%m-%d').date()
            qs = qs.filter(date_envoi__date=d)
        except ValueError:
            pass
    elif periode == 'mois' and mois and annee:
        try:
            qs = qs.filter(date_envoi__year=int(annee), date_envoi__month=int(mois))
        except ValueError:
            pass
    elif periode == 'annee' and annee:
        try:
            qs = qs.filter(date_envoi__year=int(annee))
        except ValueError:
            pass

    # Compteurs pour les onglets
    total_attente = MessageContact.objects.filter(statut='attente').count()
    total_termine = MessageContact.objects.filter(statut='termine').count()
    total_all     = MessageContact.objects.count()

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Années disponibles pour le filtre
    from django.db.models.functions import ExtractYear
    annees_dispo = (MessageContact.objects
                    .annotate(y=ExtractYear('date_envoi'))
                    .values_list('y', flat=True)
                    .distinct()
                    .order_by('-y'))

    context = {
        'page_obj':      page_obj,
        'statut_filter': statut_filter,
        'periode':       periode,
        'jour':          jour,
        'mois':          mois,
        'annee':         annee,
        'total_attente': total_attente,
        'total_termine': total_termine,
        'total_all':     total_all,
        'annees_dispo':  list(annees_dispo),
    }
    return render(request, 'dashboard/messages.html', context)

# Marquer terminé (AJAX)
def mark_completed(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=403)
    try:
        if request.user.profile.role != 'manager':
            return JsonResponse({'error': 'Managers uniquement'}, status=403)
    except Exception:
        return JsonResponse({'error': 'Profil introuvable'}, status=403)

    msg_obj = get_object_or_404(MessageContact, pk=pk)
    msg_obj.statut = 'termine'
    msg_obj.save()

    whatsapp_url = None
    if msg_obj.telephone:
        import urllib.parse
        import re
        # Nettoyer le numéro : garder uniquement les chiffres (supprimer +, espaces, tirets, parenthèses)
        telephone_propre = re.sub(r'[^\d]', '', msg_obj.telephone)
        texte = "Votre demande a été traitée avec succès"
        whatsapp_url = f"https://wa.me/{telephone_propre}?text={urllib.parse.quote(texte)}"

    return JsonResponse({
        'status':    'success',
        'message':   f'Demande #{pk} marquée comme terminée.',
        'whatsapp':  whatsapp_url,
        'prenom':    msg_obj.prenom,
        'telephone': msg_obj.telephone,
    })

def delete_message(request, pk):
    user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'visiteur'
    
    if not (request.user.is_superuser or user_role == 'manager'):
        return JsonResponse({'status': 'error', 'message': "Accès refusé : Seul l'Administrateur ou le Manager peut supprimer des messages."}, status=403)
    message = get_object_or_404(MessageContact, pk=pk)
    message.delete()
    return JsonResponse({'status': 'success', 'message': "Le message a été supprimé."})

def admin_users(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('admin_dashboard')
    
    users = User.objects.all()
    return render(request, 'dashboard/users.html', {'users': users})

def change_role(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': "Action non autorisée"}, status=403)
    
    target_user = get_object_or_404(User, id=user_id)
    new_role = request.GET.get('role')
    
    if new_role in ['manager', 'visiteur']:
        profile, created = Profile.objects.get_or_create(user=target_user)
        profile.role = new_role
        profile.save()
        return JsonResponse({'status': 'success', 'message': "Rôle mis à jour."})
    
    return JsonResponse({'status': 'error', 'message': "Rôle invalide."}, status=400)

def get_pending_count(request):
    """AJAX : Compteur messages attente (Manager only)"""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0}, status=403)
    
    try:
        if request.user.profile.role != 'manager':
            return JsonResponse({'count': 0}, status=403)
        count = MessageContact.objects.filter(statut='attente').count()
        return JsonResponse({'count': count})
    except:
        return JsonResponse({'count': 0})

def admin_trash(request):
    if not request.user.is_superuser:
        messages.error(request, "Corbeille réservée Superuser.")
        return redirect('admin_users')
    
    deleted_items = []
    context = {
        'deleted_items': deleted_items,
        'total_deleted': 0
    }
    return render(request, 'dashboard/trash.html', context)

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    context = {'profile': profile, 'user': request.user}
    return render(request, 'dashboard/profile.html', context)

def profile_update(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return redirect('profile')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    action = request.POST.get('action', 'info')

    if action == 'photo':
        if 'photo' in request.FILES:
            # Supprimer l'ancienne photo si elle existe
            if profile.photo:
                import os
                if os.path.isfile(profile.photo.path):
                    os.remove(profile.photo.path)
            profile.photo = request.FILES['photo']
            profile.save()
            messages.success(request, '✅ Photo de profil mise à jour !')
        else:
            messages.error(request, 'Aucune photo sélectionnée.')

    elif action == 'delete_photo':
        if profile.photo:
            import os
            if os.path.isfile(profile.photo.path):
                os.remove(profile.photo.path)
            profile.photo = None
            profile.save()
            messages.success(request, '🗑️ Photo de profil supprimée.')

    elif action == 'info':
        profile.prenom = request.POST.get('prenom', '').strip()
        profile.nom = request.POST.get('nom', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        profile.save()
        # Mettre à jour l'email de l'utilisateur
        email = request.POST.get('email', '').strip()
        if email:
            request.user.email = email
            request.user.save()
        messages.success(request, '✅ Profil mis à jour avec succès !')

    return redirect('profile')

# --- AUTHENTIFICATION ---
def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user, defaults={'role': 'visiteur'})
            auth_login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue sur AAPSE-UK.")
            return redirect('user_dashboard')
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez vérifier les informations saisies.")
    else:
        form = UserCreationForm()
        
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Heureux de vous revoir, {user.username} !")
            
            if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'manager'):
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    auth_logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')

def user_dashboard(request):
    # Visiteur dashboard
    if not request.user.is_authenticated:
        return redirect('login')
        
    demandes = MessageContact.objects.filter(auteur=request.user).order_by('-date_envoi')
    return render(request, 'user_dashboard.html', {'demandes': demandes})
