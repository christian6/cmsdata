from django.db import models

# Create your models here.

class Supplier(models.Model):
    supruc_id = models.CharField(primary_key=True, max_length=11)
    reason = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=11)
    flag = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')

    def __unicode__(self):
        return "%s %s"%(self.sepruc, self.reason)

class Unit(models.Model):
    unit_id = models.CharField(max_length=6)
    unit = models.CharField(max_length=11)

    class Meta:
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')

    def __unicode__(self):
        return "%s %s"%(self.unit_id, self.unit)

class Materials(models.Model):
    materiales_id = models.CharField(primary_key=True, max_length=15)
    matname = models.CharField(max_length=200)
    matmet = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, to_field='unit_id')

    class Meta:
        verbose_name = _('Materials')
        verbose_name_plural = _('Materialss')

    def __unicode__(self):
        return "%s %s"%(self.materiales_id, self.matname)

class DocumentIn(models.Model):
    serie_id = models.CharField(primary_key=True, max_length=11)
    supplier = models.ForeignKey(Supplier)
    destination = models.CharField(max_length=200)
    register = models.DateTimeField(auto_now=True)
    transfer = models.DateField(null=True, blank=True)
    reference = models.CharField(null=True, blank=True)
    motive = models.CharField(null=True, blank=True)

    class Meta:
        verbose_name = _('DocumentIn')
        verbose_name_plural = _('DocumentIns')

    def __unicode__(self):
        return "%s %s"%(self.serie, self.supplier, self.transfer)

class DetDocumentin(models.Model):
    serie = models.ForeignKey(DocumentIn, to_field='serie_id')
    materials = models.ForeignKey(Materials, to_field='materiales_id')
    quantity = models.FloatField()
    price = models.FloatField()
    flag = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('DetDocumentin')
        verbose_name_plural = _('DetDocumentins')

    def __unicode__(self):
        return "%s %s"%(self.serie, serie.materials)