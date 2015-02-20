from django.contrib import admin
from management.models import Node

#@admin.register(Node)
#class NodeAdmin(admin.ModelAdmin):
    #pass

admin.site.register(Node)
