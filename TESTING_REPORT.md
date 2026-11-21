
# CAMPUS PHARMACY MANAGEMENT SYSTEM
## SYSTEM TESTING REPORT

### 1. Introduction
This report documents the testing performed on the
Multi-Branch Campus Pharmacy Inventory, Dispensing
and Reporting System.

### 2. Testing Objectives
- Verify medicine registration and validation.
- Verify branch stock management.
- Verify prescription creation.
- Verify controlled-medicine authorisation.
- Verify atomic dispensing and transaction rollback.
- Verify low-stock reporting.

### 3. Testing Results

| Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|
| Valid medicine registration | Accepted | Accepted| |
| Invalid medicine price | Rejected | Rejected| |
| Duplicate medicine code | Rejected | Rejected| |
| Receive stock | Quantity increases | Quantity increases| |
| Overselling | Rejected | Rejected| |
| Create prescription | Saved | Saved| |
| Controlled medicine, authorised prescriber | Allowed | Allowed| |
| Controlled medicine, unauthorised prescriber | Rejected | Rejected| |
| Insufficient stock | Rejected | Rejected| |
| Transaction rollback | All changes reversed | All changes reversed| |
| Double dispensing | Rejected | Rejected| |
| Low-stock reporting | Correct medicines identified | Correct medicines indentified| |

### 4. Conclusion
The system was tested against its major functional
requirements. Any failed test cases should be corrected
and retested before final deployment.
