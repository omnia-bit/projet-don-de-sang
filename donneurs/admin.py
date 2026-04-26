from django.contrib import admin
from .models import Don, ReponseAppel


@admin.register(Don)
class DonAdmin(admin.ModelAdmin):
    list_display  = ('donneur', 'date_don', 'lieu', 'quantite', 'hopital')
    list_filter   = ('date_don', 'hopital')
    search_fields = ('donneur__user__username', 'lieu')
    ordering      = ('-date_don',)


@admin.register(ReponseAppel)
class ReponseAppelAdmin(admin.ModelAdmin):
    list_display  = ('donneur', 'demande_id', 'date_reponse', 'statut')
    list_filter   = ('statut', 'date_reponse')
    search_fields = ('donneur__user__username',)
    ordering      = ('-date_reponse',)