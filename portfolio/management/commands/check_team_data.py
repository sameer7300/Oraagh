from django.core.management.base import BaseCommand
from portfolio.models import TeamMember, LeaseTeamMember

class Command(BaseCommand):
    help = 'Checks the data in the TeamMember and LeaseTeamMember tables'

    def handle(self, *args, **options):
        self.stdout.write('--- Checking Team Members ---')
        team_members = TeamMember.objects.all()
        if team_members.exists():
            for member in team_members:
                self.stdout.write(f'ID: {member.id}, Name: {member.name}')
        else:
            self.stdout.write('No team members found.')

        self.stdout.write('\n--- Checking Lease-TeamMember Associations ---')
        associations = LeaseTeamMember.objects.all()
        if associations.exists():
            for assoc in associations:
                self.stdout.write(f'Lease ID: {assoc.lease_id}, Team Member ID: {assoc.team_member_id}, Role: {assoc.role}')
        else:
            self.stdout.write('No lease-team member associations found.')
