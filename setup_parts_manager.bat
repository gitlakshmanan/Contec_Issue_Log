@echo off
echo ========================================
echo Parts Price Manager - Quick Setup
echo ========================================
echo.

echo Step 1: Creating migrations...
python manage.py makemigrations price_book
if %errorlevel% neq 0 (
    echo ERROR: Failed to create migrations
    pause
    exit /b 1
)
echo.

echo Step 2: Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)
echo.

echo Step 3: Creating user groups...
python manage.py shell -c "from django.contrib.auth.models import Group; Group.objects.get_or_create(name='Reviewers'); Group.objects.get_or_create(name='Approvers'); print('Groups created successfully!')"
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start the development server: python manage.py runserver
echo 2. Access the dashboard: http://localhost:8000/dashboard/
echo 3. Click on "Parts Price Manager" card
echo 4. Import your 92,500 records (see price_book/README.md)
echo.
echo For detailed instructions, see:
echo - INTEGRATION_SUMMARY.md
echo - price_book/README.md
echo.
pause
