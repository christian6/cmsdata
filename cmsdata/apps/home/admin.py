# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import *


admin.site.register(Supplier)
admin.site.register(Materials)
admin.site.register(Unit)
admin.site.register(Customer)
admin.site.register(DocumentIn)
admin.site.register(DetDocumentIn)
admin.site.register(DocumentOut)
admin.site.register(DetDocumentOut)
admin.site.register(userProfile)
admin.site.register(Currency)
admin.site.register(Exchangerate)
admin.site.register(Document)
admin.site.register(Operation)