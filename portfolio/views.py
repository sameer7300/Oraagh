from django.shortcuts import render, get_object_or_404
from .models import Lease, TeamMember, LeaseMedia
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.

def portfolio_home(request):
    leases = Lease.objects.all()
    location = request.GET.get('location')
    mineral_type = request.GET.get('mineral_type')
    status = request.GET.get('status')
    query = request.GET.get('q')
    if location:
        leases = leases.filter(location__icontains=location)
    if mineral_type:
        leases = leases.filter(mineral_type__icontains=mineral_type)
    if status:
        leases = leases.filter(operational_status__icontains=status)
    if query:
        leases = leases.filter(Q(name__icontains=query) | Q(mineral_type__icontains=query))
    locations = Lease.objects.values_list('location', flat=True).distinct()
    mineral_types = Lease.objects.values_list('mineral_type', flat=True).distinct()
    statuses = Lease.objects.values_list('operational_status', flat=True).distinct()
    # Annotate each lease with its first image (if any)
    for lease in leases:
        images = lease.media.filter(is_video=False)
        lease.thumbnail = images[0].media_file.url if images else None
        lease.status_badge = lease.operational_status.lower()
    # Pagination
    paginator = Paginator(leases, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'portfolio/home.html', {
        'leases': page_obj,
        'page_obj': page_obj,
        'locations': locations,
        'mineral_types': mineral_types,
        'statuses': statuses,
        'selected_location': location,
        'selected_mineral_type': mineral_type,
        'selected_status': status,
        'search_query': query,
    })

def lease_detail(request, slug):
    lease = get_object_or_404(Lease, slug=slug)
    team_members = lease.team_members.all()
    media = lease.media.all()
    # Related leases (same location, different slug)
    related_leases = Lease.objects.filter(location=lease.location).exclude(slug=lease.slug)[:4]
    return render(request, 'portfolio/lease_detail.html', {
        'lease': lease,
        'team_members': team_members,
        'media': media,
        'related_leases': related_leases,
    })

def lease_pdf(request, slug):
    lease = get_object_or_404(Lease, slug=slug)
    team_members = lease.team_members.all()
    media = lease.media.all()
    related_leases = Lease.objects.filter(location=lease.location).exclude(slug=lease.slug)[:4]
    template = get_template('portfolio/lease_pdf.html')
    html = template.render({
        'lease': lease,
        'team_members': team_members,
        'media': media,
        'related_leases': related_leases,
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lease_{lease.pk}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def map_view(request):
    leases = Lease.objects.all()
    context = {'leases': leases}
    return render(request, 'portfolio/map.html', context)

def portfolio_map(request):
    leases = Lease.objects.all()
    return render(request, 'portfolio/map.html', {'leases': leases})

def team(request):
    team_members = TeamMember.objects.all()
    return render(request, 'portfolio/team.html', {'team_members': team_members})

def team_member_detail(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'portfolio/team_member_detail.html', {'team_member': team_member})
