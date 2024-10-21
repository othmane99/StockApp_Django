from rest_framework import serializers
from .models import Fournisseur, Employe, Departement, Produit, Inventaire, Event, Bucket

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = '__all__'

class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

class InventaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventaire
        fields = '__all__'

##########################################################################################

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class BucketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bucket
        fields = '__all__'