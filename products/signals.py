from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Product

@receiver(post_save, sender=Product)
def update_search_vectors(sender, instance, **kwargs):
    # Update English search vector
    sender.objects.filter(pk=instance.pk).update(
        search_vector_en=SearchVector('name_en', 'description_en')
    )
    
    # Update Arabic search vector
    sender.objects.filter(pk=instance.pk).update(
        search_vector_ar=SearchVector('name_ar', 'description_ar')
    )
