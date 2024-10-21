from datetime import datetime, timedelta
import uuid
from django.db import models
from django.utils import timezone

class Fournisseur(models.Model):
    fournisseur_id = models.AutoField(primary_key=True)
    fournisseur_name = models.CharField(max_length=100)
    tel = models.CharField(max_length=20)

    def __str__(self):
        return self.fournisseur_name

class Employe(models.Model):
    employe_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    poste = models.CharField(max_length=100)
    departement_de_travail = models.ForeignKey('Departement', on_delete=models.SET_NULL, null=True)
    est_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

class Departement(models.Model):
    departement_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    #chef_de_departement = models.OneToOneField(Employe, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.department_name



from django.db import models
from django.utils import timezone
import uuid
import datetime

class Produit(models.Model):
    produit_id = models.AutoField(primary_key=True)
    produit_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    code_bar = models.CharField(max_length=32, unique=True, editable=False)
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    fournisseur = models.ForeignKey('Fournisseur', on_delete=models.CASCADE)
    departement = models.ForeignKey('Departement', on_delete=models.SET_NULL, null=True)
    warranty_period = models.IntegerField(null=True, blank=True)  # in months
    warranty_start_date = models.DateTimeField(null=True, blank=True)
    warranty_end_date = models.DateTimeField(null=True, blank=True)
    warranty_isValid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Calculate warranty_end_date if warranty_period and warranty_start_date are provided
        if self.warranty_period and self.warranty_start_date:
            self.warranty_end_date = self.warranty_start_date + datetime.timedelta(days=self.warranty_period * 30)
        else:
            self.warranty_end_date = None

        # Update warranty_isValid based on warranty_end_date and current time
        #self.warranty_isValid = self.warranty_end_date and self.warranty_end_date >= timezone.now()
        self.warranty_isValid = bool(self.warranty_end_date and self.warranty_end_date >= timezone.now())

        # Generate code_bar if not already set
        if not self.code_bar:
            department_id_str = str(self.departement.departement_id).zfill(2)
            self.code_bar = department_id_str + uuid.uuid4().hex[:10]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.produit_name



class Inventaire(models.Model):
    inventaire_id = models.AutoField(primary_key=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    etat_InOut_choices = [
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    ]
    etat_InOut = models.CharField(max_length=20, choices=etat_InOut_choices, default='IN')
    date_in = models.DateField()
    quantite_produit = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    state_choices = [
        ('On', 'On'),
        ('Off', 'Off'),
        ('Maintenance', 'Maintenance')
    ]
    state = models.CharField(max_length=20, choices=state_choices, default='On')

    def __str__(self):
        return f"{self.produit.produit_name} (ID: {self.inventaire_id}, Quantité: {self.quantite_produit})"


###################################################################################3


from django.db import models
from django.utils import timezone
import uuid

class Bucket(models.Model):
    bucket_id = models.AutoField(primary_key=True)
    barcode = models.CharField(max_length=100, unique=True, editable=False)
    products = models.ManyToManyField('Inventaire', related_name='buckets')

    def save(self, *args, **kwargs):
        if not self.barcode:
            prefix = '00'
            uuid_part = uuid.uuid4().hex[:10]
            self.barcode = prefix + uuid_part
        super().save(*args, **kwargs)

    def __str__(self):
        return self.barcode


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    event_pre_date = models.DateTimeField()
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    event_post_date = models.DateTimeField()
    list_of_products = models.ManyToManyField('Inventaire', related_name='events')
    list_of_buckets = models.ManyToManyField(Bucket, related_name='events')

    def handle_event_pre_date(self):
        if timezone.now() >= self.event_pre_date:
            for inventaire in self.list_of_products.filter(etat_InOut='IN'):
                inventaire.etat_InOut = 'OUT'
                print("IN to OUT")
                inventaire.save()

    def handle_event_post_date(self):
        if timezone.now() >= self.event_post_date:
            for inventaire in self.list_of_products.filter(etat_InOut='OUT'):
                inventaire.etat_InOut = 'IN'
                print("IN to OUT")
                inventaire.save()

    def __str__(self):
        return self.event_name
