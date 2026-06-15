"""
Management command to create sample issues for testing
Usage: python manage.py create_sample_issues
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from base.models import Issue


class Command(BaseCommand):
    help = 'Create sample issues for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of sample issues to create (default: 5)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create a user for the issues
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
            
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding user: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Creating {count} sample issues...'))
        
        # Sample data
        sample_issues = [
            {
                'customer': 'Mediacom',
                'inv_type': 'Fulfillment',
                'issue_cat': 'ManError',
                'description': 'Incorrect billing amount entered in the system. Customer was overcharged by $150 due to manual data entry error.',
                'identified_by': 'John Smith',
                'revenue_impact': 150.00,
                'impact_category': 'Overcharge',
                'root_cause': 'Manual data entry error during invoice processing',
                'root_cause_owner': 'Billing Team',
                'customer_received': 'Yes',
                'impacted_customer': 'Mediacom',
                'containment_action': 'Immediately corrected the invoice and issued credit memo to customer',
                'corrective_action': 'Implemented double-check process for all manual entries above $100',
                'rebilled_credited': 'Yes',
                'department': 'Billing',
                'action_owner': 'Sarah Johnson',
                'status': 'Closed',
                'approved': 'patrick',
                'remarks': 'Issue resolved. Customer satisfied with quick response.'
            },
            {
                'customer': 'Midco',
                'inv_type': 'C&C',
                'issue_cat': 'MachineError',
                'description': 'Automated billing system generated duplicate invoices for the same service period.',
                'identified_by': 'Mike Davis',
                'revenue_impact': 2500.00,
                'impact_category': 'Overcharge',
                'root_cause': 'Software bug in billing automation system causing duplicate invoice generation',
                'root_cause_owner': 'IT Department',
                'customer_received': 'Yes',
                'impacted_customer': 'Midco',
                'containment_action': 'Disabled automated billing temporarily and manually reviewed all invoices',
                'corrective_action': 'Fixed software bug and implemented duplicate detection algorithm',
                'rebilled_credited': 'Yes',
                'department': 'Operations',
                'action_owner': 'Tom Wilson',
                'status': 'Open',
                'approved': 'neha',
                'remarks': 'Software fix deployed. Monitoring for 30 days.'
            },
            {
                'customer': 'Frontier',
                'inv_type': 'OME',
                'issue_cat': 'MaterialError',
                'description': 'Wrong pricing sheet used for contract renewal, resulting in undercharging.',
                'identified_by': 'Lisa Anderson',
                'revenue_impact': 500.00,
                'impact_category': 'Undercharge',
                'root_cause': 'Outdated pricing sheet not updated in the system after contract renewal',
                'root_cause_owner': 'Contract Management',
                'customer_received': 'No',
                'impacted_customer': 'Frontier',
                'containment_action': 'Identified all affected invoices and prepared corrected versions',
                'corrective_action': 'Implemented automated pricing sheet update process with version control',
                'rebilled_credited': 'No',
                'department': 'Billing',
                'action_owner': 'David Brown',
                'status': 'Open',
                'approved': 'patrick',
                'remarks': 'Waiting for customer approval before rebilling.'
            },
            {
                'customer': 'Mediacom',
                'inv_type': 'Fulfillment',
                'issue_cat': 'MethodError',
                'description': 'Incorrect calculation method used for service charges resulting in billing discrepancy.',
                'identified_by': 'Emily White',
                'revenue_impact': 750.00,
                'impact_category': 'Credit',
                'root_cause': 'New calculation method not properly communicated to billing team',
                'root_cause_owner': 'Finance Department',
                'customer_received': 'Yes',
                'impacted_customer': 'Mediacom',
                'containment_action': 'Recalculated all affected invoices using correct method',
                'corrective_action': 'Created standard operating procedure document and conducted team training',
                'rebilled_credited': 'Yes',
                'department': 'Ops',
                'action_owner': 'Jennifer Lee',
                'status': 'Closed',
                'approved': 'neha',
                'remarks': 'All team members trained on new procedure. Issue fully resolved.'
            },
            {
                'customer': 'Midco',
                'inv_type': 'C&C',
                'issue_cat': 'MeasureableError',
                'description': 'Service usage metrics incorrectly measured leading to inaccurate billing.',
                'identified_by': 'Robert Taylor',
                'revenue_impact': 1200.00,
                'impact_category': 'Debit',
                'root_cause': 'Faulty meter reading equipment providing incorrect usage data',
                'root_cause_owner': 'Operations Team',
                'customer_received': 'No',
                'impacted_customer': 'Midco',
                'containment_action': 'Replaced faulty equipment and re-measured service usage for affected period',
                'corrective_action': 'Implemented weekly equipment calibration checks and automated anomaly detection',
                'rebilled_credited': 'No',
                'department': 'Support',
                'action_owner': 'Michael Chen',
                'status': 'Open',
                'approved': 'patrick',
                'remarks': 'Equipment replaced. Monitoring accuracy for next billing cycle.'
            },
            {
                'customer': 'Frontier',
                'inv_type': 'OME',
                'issue_cat': 'ManError',
                'description': 'Service discount not applied correctly during invoice generation.',
                'identified_by': 'Amanda Martinez',
                'revenue_impact': 300.00,
                'impact_category': 'Overcharge',
                'root_cause': 'Discount code not entered in billing system during order processing',
                'root_cause_owner': 'Sales Team',
                'customer_received': 'Yes',
                'impacted_customer': 'Frontier',
                'containment_action': 'Applied discount retroactively and issued credit to customer',
                'corrective_action': 'Added automated discount validation in order entry system',
                'rebilled_credited': 'Yes',
                'department': 'Billing',
                'action_owner': 'Chris Rodriguez',
                'status': 'Dismissed',
                'approved': 'neha',
                'remarks': 'Customer accepted credit. Automation prevents future occurrences.'
            },
            {
                'customer': 'Mediacom',
                'inv_type': 'Fulfillment',
                'issue_cat': 'MachineError',
                'description': 'System timeout during invoice processing caused incomplete invoice generation.',
                'identified_by': 'Kevin Park',
                'revenue_impact': 0.00,
                'impact_category': None,
                'root_cause': 'Database performance issue causing system timeouts during peak load',
                'root_cause_owner': 'IT Infrastructure',
                'customer_received': 'No',
                'impacted_customer': None,
                'containment_action': 'Manually completed invoice generation and verified all data',
                'corrective_action': 'Upgraded database server and optimized query performance',
                'rebilled_credited': 'No',
                'department': 'Operations',
                'action_owner': 'Daniel Kim',
                'status': 'Open',
                'approved': 'patrick',
                'remarks': 'Infrastructure upgrade in progress. Expected completion in 2 weeks.'
            },
            {
                'customer': 'Midco',
                'inv_type': 'C&C',
                'issue_cat': 'MaterialError',
                'description': 'Incorrect tax rate applied to invoices due to outdated tax table.',
                'identified_by': 'Patricia Garcia',
                'revenue_impact': 450.00,
                'impact_category': 'Undercharge',
                'root_cause': 'Tax rate update not synchronized with billing system after regulatory change',
                'root_cause_owner': 'Compliance Team',
                'customer_received': 'No',
                'impacted_customer': 'Midco',
                'containment_action': 'Updated tax tables and recalculated affected invoices',
                'corrective_action': 'Implemented automated tax rate update process with regulatory monitoring',
                'rebilled_credited': 'No',
                'action_owner': 'Laura Thompson',
                'status': 'Open',
                'approved': 'neha',
                'remarks': 'Awaiting customer confirmation before issuing corrected invoices.'
            },
        ]
        
        created_count = 0
        for i, issue_data in enumerate(sample_issues[:count]):
            try:
                # Set dates
                identified_on = timezone.now() - timedelta(days=30-i*3)
                due_date = identified_on + timedelta(days=14)
                
                # Create the issue
                issue = Issue.objects.create(
                    customer=issue_data['customer'],
                    inv_type=issue_data['inv_type'],
                    issue_cat=issue_data['issue_cat'],
                    description=issue_data['description'],
                    identified_on=identified_on,
                    identified_by=issue_data['identified_by'],
                    revenue_impact=issue_data['revenue_impact'],
                    impact_category=issue_data.get('impact_category'),
                    root_cause=issue_data['root_cause'],
                    root_cause_owner=issue_data['root_cause_owner'],
                    customer_received=issue_data['customer_received'],
                    impacted_customer=issue_data.get('impacted_customer'),
                    containment_action=issue_data['containment_action'],
                    corrective_action=issue_data['corrective_action'],
                    rebilled_credited=issue_data['rebilled_credited'],
                    action_owner=issue_data['action_owner'],
                    due_date=due_date,
                    status=issue_data['status'],
                    approved=issue_data.get('approved'),
                    remarks=issue_data['remarks'],
                    created_by=user,
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created Issue #{issue.id}: {issue.customer} - {issue.issue_cat} ({issue.status})'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating issue {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully created {created_count} sample issues!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'View them at: http://127.0.0.1:8000/issues/')
        )
