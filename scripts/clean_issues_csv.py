import pandas as pd
from datetime import datetime, timedelta

# Read the CSV file
df = pd.read_csv('base_issue.csv')

# Fix column names
df.columns = [
    'Customer', 'Invoice Type', 'Issue Category', 'Description', 'Identified On',
    'Identified By', 'Revenue Impact', 'Impact Category', 'Root Cause',
    'Root Cause Owner', 'Customer Received', 'Impacted Customers',
    'Containment Action', 'Corrective Action', 'Rebilled/Credited',
    'Action Owner', 'Due Date', 'Status', 'Approved By', 'Remarks'
]

# Replace 'NaN' strings with empty strings
df = df.replace('NaN', '')
df = df.replace('NA', '')

# Fix status values
df['Status'] = df['Status'].replace({
    'clsoed': 'Closed',
    'closed': 'Closed',
    'Open': 'Open',
    'dismissed': 'Dismissed'
})

# Standardize Invoice Types
df['Invoice Type'] = df['Invoice Type'].replace({
    'oem': 'OEM',
    'Clean & Screen': 'Clean & Screen',
    'FullFilment': 'Fulfillment'  # Fix typo in Fulfillment
})

# Fill missing Issue Categories with "UnCategorized"
df['Issue Category'] = df['Issue Category'].fillna('UnCategorized')
df.loc[df['Issue Category'] == '', 'Issue Category'] = 'UnCategorized'

# Fix dates
def fix_date(date_str):
    if pd.isna(date_str) or date_str == '#VALUE!':
        return datetime.now().strftime('%Y-%m-%d')
    try:
        # Try parsing DD-MM-YYYY format
        return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
    except:
        try:
            # Try parsing MM-DD-YYYY format
            return datetime.strptime(date_str, '%m-%d-%Y').strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')

df['Identified On'] = df['Identified On'].apply(fix_date)
df['Due Date'] = df['Due Date'].apply(fix_date)

# Fill required fields
df['Description'] = df['Description'].fillna('No description provided')
df['Identified By'] = df['Identified By'].fillna('System')
df['Root Cause'] = df['Root Cause'].fillna('Under Investigation')
df['Root Cause Owner'] = df['Root Cause Owner'].fillna('Not Assigned')
df['Customer Received'] = df['Customer Received'].fillna('No')
df['Rebilled/Credited'] = df['Rebilled/Credited'].fillna('No')
df['Invoice Type'] = df['Invoice Type'].fillna('UnCategorized')

# Save the cleaned CSV
df.to_csv('cleaned_issues.csv', index=False)