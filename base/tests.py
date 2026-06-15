from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Customer, IssueCategory, ImpactCategory, Issue
import io
from .models import EmailLog
from django.test.utils import override_settings
from django.utils import timezone


class CSVImportTests(TestCase):
    def setUp(self):
        # Create a user to own created issues
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.client = Client()
        self.client.force_login(self.user)

    def test_happy_path_import(self):
        # Prepare CSV content with header + one valid row
        csv_content = (
            'ID,Department,Customer,Invoice Type,Issue Category,Description,Identified On,Identified By,Revenue Impact,Impact Category,Root Cause,Root Cause Owner,Customer Received,Impacted Customers,Containment Action,Corrective Action,Rebilled/Credited,Rebill/Credit Proof,Action Owner,Due Date,Status,Approved By,Remarks,Attachment,Created By,Created At,Updated At\n'
            '1,Billing,TestCustomer,Fulfillment,TestCategory,An issue,10/20/2025,Reporter,100.00,Financial,Root cause,Owner,True,SomeCustomer,Containment,Corrective,False,,Owner,10/27/2025,Open,,Remarks,,tester,2025-10-20,2025-10-20\n'
        )

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded = SimpleUploadedFile('issues.csv', csv_content.encode('utf-8'), content_type='text/csv')
        response = self.client.post(
            reverse('import-issues'),
            {'csv_file': uploaded},
        )

        # After import, check that the issue was created
        self.assertEqual(Issue.objects.count(), 1)
        issue = Issue.objects.first()
        self.assertEqual(issue.customer.name, 'TestCustomer')
        self.assertEqual(issue.issue_cat.name, 'TestCategory')
        # Customer Received and Rebilled/Credited stored as Yes/No strings
        self.assertIn(issue.customer_received, ('Yes', 'No'))
        self.assertIn(issue.rebilled_credited, ('Yes', 'No'))

        # Check summary render
        self.assertContains(response, 'Successfully imported')

    def test_malformed_row_skipped(self):
        # Header + malformed row (too few columns)
        csv_content = (
            'ID,Customer,Invoice Type,Issue Category,Description,Identified On,Identified By\n'
            '1,OnlyOneColumn\n'
        )

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded = SimpleUploadedFile('issues.csv', csv_content.encode('utf-8'), content_type='text/csv')
        response = self.client.post(
            reverse('import-issues'),
            {'csv_file': uploaded},
        )

        # No issues should be created
        self.assertEqual(Issue.objects.count(), 0)
        # Summary should include error line
        self.assertContains(response, 'Errors')

    def test_email_logging_success(self):
        # Create an issue to email
        cust = Customer.objects.create(name='C1', is_active=True)
        cat = IssueCategory.objects.create(name='Cat1', is_active=True)
        issue = Issue.objects.create(
            customer=cust,
            inv_type='Fulfillment',
            issue_cat=cat,
            description='test',
            identified_on=timezone.now(),
            identified_by='tester',
            revenue_impact=0,
            root_cause='cause',
            root_cause_owner='owner',
            containment_action='c',
            corrective_action='c',
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.user
        )

        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(reverse('issue-email', args=[issue.id]), {
                'to_email': 'recipient@example.com',
                'subject': 'Test',
                'message': 'Hello',
                'include_issue_details': 'on'
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

            self.assertEqual(response.status_code, 200)
            # JSON response should have status and message
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('message', data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(EmailLog.objects.filter(issue=issue, status='sent').count(), 1)

    def test_email_logging_failure(self):
        # Create issue and simulate failure by using a bad backend (invalid settings)
        cust = Customer.objects.create(name='C2', is_active=True)
        cat = IssueCategory.objects.create(name='Cat2', is_active=True)
        issue = Issue.objects.create(
            customer=cust,
            inv_type='OME',
            issue_cat=cat,
            description='test2',
            identified_on=timezone.now(),
            identified_by='tester',
            revenue_impact=0,
            root_cause='cause2',
            root_cause_owner='owner2',
            containment_action='c2',
            corrective_action='c2',
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.user
        )

        # Temporarily set an email backend that raises an exception by using a dummy backend path
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend', EMAIL_HOST='invalid_host'):
            response = self.client.post(reverse('issue-email', args=[issue.id]), {
                'to_email': 'recipient2@example.com',
                'subject': 'TestFail',
                'message': 'Hello',
                'include_issue_details': 'on'
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

            # Should still return a JSON error response
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('message', data)
            self.assertEqual(data['status'], 'error')
            self.assertEqual(EmailLog.objects.filter(issue=issue, status='failed').count(), 1)

    def test_admin_export_emaillogs_csv(self):
        # Create a sample EmailLog
        user = self.user
        cust = Customer.objects.create(name='AC', is_active=True)
        cat = IssueCategory.objects.create(name='CatX', is_active=True)
        issue = Issue.objects.create(
            customer=cust,
            inv_type='Fulfillment',
            issue_cat=cat,
            description='e',
            identified_on=timezone.now(),
            identified_by='u',
            revenue_impact=0,
            root_cause='r',
            root_cause_owner='o',
            containment_action='c',
            corrective_action='c',
            due_date=timezone.now(),
            created_by=user
        )
        EmailLog.objects.create(issue=issue, sent_by=user, to_email='a@b.com', subject='S', message='M', status='sent')

        # Log in as staff user to access admin export
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        admin_login = self.client.login(username=self.user.username, password='testpass')
        self.assertTrue(admin_login)

        # Call admin action via POST to admin changelist action URL
        from django.urls import reverse
        changelist_url = reverse('admin:base_emaillog_changelist')
        qs = EmailLog.objects.all()
        # emulate selecting all objects
        response = self.client.post(changelist_url, {'action': 'export_as_csv', '_selected_action': [str(obj.id) for obj in qs]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn('to_email', content)

    def test_admin_resend_emaillog(self):
        # Create a sample EmailLog
        user = self.user
        cust = Customer.objects.create(name='AC', is_active=True)
        cat = IssueCategory.objects.create(name='CatY', is_active=True)
        issue = Issue.objects.create(
            customer=cust,
            inv_type='Fulfillment',
            issue_cat=cat,
            description='e2',
            identified_on=timezone.now(),
            identified_by='u',
            revenue_impact=0,
            root_cause='r',
            root_cause_owner='o',
            containment_action='c',
            corrective_action='c',
            due_date=timezone.now(),
            created_by=user
        )
        elog = EmailLog.objects.create(issue=issue, sent_by=user, to_email='x@y.com', subject='S2', message='M2', status='sent')

        # make user superuser/staff and login
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username=self.user.username, password='testpass')

        from django.urls import reverse
        res_url = reverse('admin:base_emaillog_resend', args=[elog.id])
        response = self.client.get(res_url)
        # should redirect back to change view
        self.assertEqual(response.status_code, 302)
        # a new EmailLog entry (resend attempt) should have been created
        self.assertTrue(EmailLog.objects.filter(issue=issue).count() >= 2)

    def test_rebill_proof_imported(self):
        # CSV with the new Rebill/Credit Proof column included
        csv_content = (
            'ID,Department,Customer,Invoice Type,Issue Category,Description,Identified On,Identified By,Revenue Impact,Impact Category,Root Cause,Root Cause Owner,Customer Received,Impacted Customers,Containment Action,Corrective Action,Rebilled/Credited,Rebill/Credit Proof,Action Owner,Due Date,Status,Approved By,Remarks,Attachment,Created By,Created At,Updated At\n'
            '1,Billing,ProofCustomer,Fulfillment,ProofCategory,Proof issue,10/20/2025,Reporter,0.00,Financial,Root cause,Owner,True,SomeCustomer,Containment,Corrective,True,Invoice#12345,Owner,10/27/2025,Open,,ProofRemarks,,tester,2025-10-20,2025-10-20\n'
        )

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded = SimpleUploadedFile('issues_with_proof.csv', csv_content.encode('utf-8'), content_type='text/csv')
        response = self.client.post(
            reverse('import-issues'),
            {'csv_file': uploaded},
        )

        # After import, check that the issue was created and rebill_proof saved
        self.assertEqual(Issue.objects.count(), 1)
        issue = Issue.objects.first()
        self.assertEqual(issue.customer.name, 'ProofCustomer')
        self.assertEqual(issue.issue_cat.name, 'ProofCategory')
        self.assertEqual(issue.rebilled_credited, 'Yes')
        self.assertIn('Invoice#12345', (issue.rebill_proof or ''))
        # Check summary render
        self.assertContains(response, 'Successfully imported')

    def test_ajax_import_returns_json(self):
        # Prepare CSV content with header + one valid row
        csv_content = (
            'ID,Department,Customer,Invoice Type,Issue Category,Description,Identified On,Identified By,Revenue Impact,Impact Category,Root Cause,Root Cause Owner,Customer Received,Impacted Customers,Containment Action,Corrective Action,Rebilled/Credited,Rebill/Credit Proof,Action Owner,Due Date,Status,Approved By,Remarks,Attachment,Created By,Created At,Updated At\n'
            '1,Billing,AJAXCust,Fulfillment,AJAXCat,Ajax issue,10/20/2025,Reporter,0.00,Financial,Root cause,Owner,True,SomeCustomer,Containment,Corrective,True,Proof,Owner,10/27/2025,Open,,Remarks,,tester,2025-10-20,2025-10-20\n'
        )

        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded = SimpleUploadedFile('ajax_issues.csv', csv_content.encode('utf-8'), content_type='text/csv')
        response = self.client.post(
            reverse('import-issues'),
            {'csv_file': uploaded},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Should return JSON with success status
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('summary', data)
        self.assertEqual(Issue.objects.filter(customer__name='AJAXCust').count(), 1)

    def test_ajax_import_oversize_rejected(self):
        # Create a dummy large file >5MB
        large_content = 'a' * (6 * 1024 * 1024)
        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded = SimpleUploadedFile('large.csv', large_content.encode('utf-8'), content_type='text/csv')
        response = self.client.post(
            reverse('import-issues'),
            {'csv_file': uploaded},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Should return 400 JSON error
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_issue_create_persists_department(self):
        # Create required lookups
        cust = Customer.objects.create(name='FormCust', is_active=True)
        # Use free-text category resolution in the form

        post_data = {
            'customer': str(cust.id),
            'inv_type': 'Fulfillment',
            'issue_cat': 'FormCategory',
            'description': 'Form created issue',
            'identified_on': timezone.now().strftime('%m/%d/%Y'),
            'identified_by': 'formtester',
            'due_date': (timezone.now() + timezone.timedelta(days=7)).strftime('%m/%d/%Y'),
            'status': 'Open',
            'department': 'Billing'
        }

        response = self.client.post(reverse('issue-create'), post_data, follow=True)
        # Should redirect to detail and create the issue
        self.assertEqual(Issue.objects.filter(department='Billing').count(), 1)

    def test_issue_update_persists_department(self):
        cust = Customer.objects.create(name='UpdCust', is_active=True)
        cat = IssueCategory.objects.create(name='UpdCat', is_active=True)
        issue = Issue.objects.create(
            customer=cust,
            inv_type='Fulfillment',
            issue_cat=cat,
            description='to update',
            identified_on=timezone.now(),
            identified_by='uploader',
            revenue_impact=0,
            root_cause='r',
            root_cause_owner='o',
            containment_action='c',
            corrective_action='c',
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.user
        )

        update_url = reverse('issue-update', args=[issue.id])
        post_data = {
            'customer': str(cust.id),
            'inv_type': 'Fulfillment',
            'issue_cat': cat.name,
            'description': 'updated description',
            'identified_on': timezone.now().strftime('%m/%d/%Y'),
            'identified_by': 'updater',
            'due_date': (timezone.now() + timezone.timedelta(days=10)).strftime('%m/%d/%Y'),
            'status': 'Open',
            'department': 'Operations'
        }

        response = self.client.post(update_url, post_data, follow=True)
        issue.refresh_from_db()
        self.assertEqual(issue.department, 'Operations')

    def test_issueform_save_persists_department(self):
        """Directly test IssueForm: validate, save commit=False, set created_by and persist department"""
        # Prepare required lookup
        cust = Customer.objects.create(name='FormDirectCust', is_active=True)

        form_data = {
            'customer': str(cust.id),
            'inv_type': 'Fulfillment',
            'issue_cat': 'DirectFormCat',
            'description': 'Form API created issue',
            'identified_on': timezone.now().strftime('%m/%d/%Y'),
            'identified_by': 'formapi',
            'due_date': (timezone.now() + timezone.timedelta(days=7)).strftime('%m/%d/%Y'),
            'status': 'Open',
            'department': 'Billing'
        }

        from .forms import IssueForm

        form = IssueForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        issue_obj = form.save(commit=False)
        # created_by is required on the model
        issue_obj.created_by = self.user
        issue_obj.save()

        # Refresh from DB and assert department persisted
        issue_obj.refresh_from_db()
        self.assertEqual(issue_obj.department, 'Billing')
