from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.text import slugify

# Create your models here.

class Lease(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    SIZE_CHOICES = (
        ('Small (1-10 acres)', 'Small (1-10 acres)'),
        ('Medium (11-50 acres)', 'Medium (11-50 acres)'),
        ('Large (51-100 acres)', 'Large (51-100 acres)'),
        ('Extra Large (100+ acres)', 'Extra Large (100+ acres)'),
    )
    size = models.CharField(max_length=100, choices=SIZE_CHOICES, default='Medium (11-50 acres)')
    MINERAL_CHOICES = (
        ('Coal', 'Coal'),
        ('Copper', 'Copper'),
        ('Gold', 'Gold'),
        ('Iron Ore', 'Iron Ore'),
        ('Limestone', 'Limestone'),
        ('Marble', 'Marble'),
        ('Salt', 'Salt'),
        ('Gypsum', 'Gypsum'),
        ('Chromite', 'Chromite'),
        ('Bauxite', 'Bauxite'),
    )
    mineral_type = models.CharField(max_length=100, choices=MINERAL_CHOICES, default='Coal')
    OPERATIONAL_STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Completed', 'Completed'),
    )
    operational_status = models.CharField(max_length=100, choices=OPERATIONAL_STATUS_CHOICES, default='Active')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    @property
    def featured_image(self):
        image = self.media.filter(is_video=False).first()
        return image.media_file if image else None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='team_photos/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class LeaseTeamMember(models.Model):
    lease = models.ForeignKey(Lease, related_name='team_members', on_delete=models.CASCADE)
    team_member = models.ForeignKey(TeamMember, related_name='leases', on_delete=models.CASCADE)
    role = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.team_member.name} ({self.role})"

class LeaseMedia(models.Model):
    lease = models.ForeignKey(Lease, related_name='media', on_delete=models.CASCADE)
    media_file = models.FileField(upload_to='lease_media/')
    is_video = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Media for {self.lease.name}"
