from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Product(models.Model):
	name = models.CharField(max_length=255)
	manufacturer = models.CharField(max_length=255)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	quantity = models.PositiveIntegerField(validators = [MinValueValidator(0), MaxValueValidator(1)],)
	description = models.TextField(max_length=1000)
	image = models.ImageField(upload_to='product_images/', null=False, blank=False)
	
	def __str__(self):
		return self.name
    
