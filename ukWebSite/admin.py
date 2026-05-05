from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, MessageContact, Membre, Actualite, Ressource

# Custom UserAdmin avec Profile inline
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'is_staff', 'profile_role')
    
    def profile_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'N/A'
    profile_role.short_description = 'Rôle'

# Enregistrer User custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'telephone', 'sujet', 'statut', 'date_envoi')
    list_filter = ('sujet', 'statut')
    search_fields = ('prenom', 'nom', 'telephone', 'email')
    actions = ['marquer_termine']

    def marquer_termine(self, request, queryset):
        count = queryset.update(statut='termine')
        self.message_user(request, f'{count} message(s) marqué(s) terminé(s)')
    marquer_termine.short_description = "Marquer sélectionnés comme terminés"

@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'role', 'promotion', 'actif')
    list_filter = ('role', 'actif', 'niveau_etude')
    search_fields = ('prenom', 'nom', 'institution')

@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'date_pub', 'publie')
    list_filter = ('categorie', 'publie')
    search_fields = ('titre', 'contenu')

@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_doc', 'publique', 'date_ajout')
    list_filter = ('type_doc', 'publique')
    search_fields = ('titre', 'description')
