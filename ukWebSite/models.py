from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.contrib.auth.models import User


class Membre(models.Model):
    """Bureau exécutif et alumni affichés sur la page Membres."""

    ROLES = [
        ('none',       'Membre ordinaire'),
        ('president',  'Président(e)'),
        ('vp',         'Vice-Président(e)'),
        ('sg',         'Secrétaire Général(e)'),
        ('tresorier',  'Trésorier(ière)'),
        ('programmes', 'Chargé(e) des Programmes'),
        ('comm',       'Communication'),
        ('relations',  'Relations Institutionnelles')
    ]
    NIVEAU_ETUDE = [
        ('licence', 'Licence'),
        ('master', 'Master')
    ]

    prenom       = models.CharField(max_length=50)
    nom          = models.CharField(max_length=50)
    role         = models.CharField(max_length=50, choices=ROLES, default='none')
    promotion    = models.PositiveIntegerField(
        help_text="Année de la promotion (ex: 2023)"
    )
    institution  = models.CharField(max_length=200)
    bio          = models.CharField(max_length=300, blank=True)
    photo        = models.ImageField(upload_to='membres/', blank=True, null=True)
    actif        = models.BooleanField(default=True)
    niveau_etude = models.CharField(max_length=50, choices=NIVEAU_ETUDE)    

    class Meta:
        ordering = ['nom', 'role']
        verbose_name = "Membre"
        verbose_name_plural = "Membres"

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def initiales(self):
        return f"{self.prenom[0]}.{self.nom[0]}"


class Actualite(models.Model):
    """Articles et actualités affichés sur la page Actualités."""

    CATEGORIES = [
        ('evenement',   'Événement phare'),
        ('academique',  'Académique'),
        ('publication', 'Publication'),
        ('nomination', 'Nomination'),
        ('initiative', 'Initiative')
    ]

    titre     = models.CharField(max_length=255)
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='autre')
    extrait   = models.TextField(max_length=400)
    contenu   = models.TextField()
    photo     = models.ImageField(upload_to='actualites/', blank=True, null=True)
    lieu      = models.CharField(max_length=150, blank=True, help_text="Ex: Noépé, Togo")
    date_pub  = models.DateField()
    publie    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_pub']
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"

    def __str__(self):
        return f"{self.titre}"


class Ressource(models.Model):
    """Documents et publications de la bibliothèque alumni."""

    TYPES = [
        ('guide',     'Guide pratique'),
        ('note',      'Note de politique'),
        ('recherche', 'Travail de recherche'),
        ('outil',     'Outil méthodologique'),
        ('rapport',   'Rapport d\'activités'),
    ]

    titre       = models.CharField(max_length=255)
    type_doc    = models.CharField(max_length=20, choices=TYPES, default='guide')
    description = models.CharField(max_length=300)
    fichier     = models.FileField(upload_to='ressources/', blank=True, null=True)
    lien        = models.URLField(blank=True, help_text="Lien si hébergé ailleurs")
    publique    = models.BooleanField(default=True, help_text="Faux = réservé aux membres")
    date_ajout  = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_ajout']
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"

    def __str__(self):
        return f"{self.titre}"


class MessageContact(models.Model):
    """Messages soumis via le formulaire de contact."""

    SUJETS = [
        ('adhesion',    'Adhésion'),
        ('partenariat', 'Partenariat / Collaboration'),
        ('ressources',  'Ressources / Publications'),
        ('share',       'Événement Share To Us'),
        ('autre',       'Autre demande'),
    ]

    STATUTS = [
        ('attente', 'En attente'),
        ('termine', 'Terminé'),
    ]

    prenom      = models.CharField(max_length=100)
    nom         = models.CharField(max_length=100)
    email       = models.EmailField()
    telephone   = models.CharField(max_length=20, blank=True, help_text="Numéro WhatsApp")
    institution = models.CharField(max_length=200, blank=True)
    promotion   = models.PositiveIntegerField(null=True, blank=True)
    sujet       = models.CharField(max_length=20, choices=SUJETS, default='autre')
    message     = models.TextField()
    statut      = models.CharField(max_length=10, choices=STATUTS, default='attente')
    lu          = models.BooleanField(default=False)
    date_envoi  = models.DateTimeField(auto_now_add=True)
    auteur      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes')

    class Meta:
        ordering = ['-date_envoi']
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.get_sujet_display()}"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('visiteur', 'Visiteur'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='visiteur')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    prenom = models.CharField(max_length=50, blank=True)
    nom = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return static('dashboard/img/undraw_profile.svg')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
