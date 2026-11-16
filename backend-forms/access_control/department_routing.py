
DEVICE_RELATED_FORMS = {
    "REPLACEMENT",
    "TROUBLESHOOTING",
    "INFRASTRUCTURE",
    "ISSUE",
}

INTERNAL_CONTROL_FORMS = {
    "ENCLUSIA-ACCESS",
    "WEALTHFORGE-ACCESS",  # Confirm this matches your actual form code
}

DEPARTMENT_EMAILS = {
    "Administrator": "administrator@optimum-g.com",
    "Account Officers": "accountofficers@optimum-g.com",
    "Finance Dashboard": "financedashboard@optimum-g.com",
    "Financial Control": "financialcontrol@optimum-g.com",
    "Global Dashboard": "globaldashboard@optimum-g.com",
    "Internal Control": "internal-control@optimum-g.com",
    "INVESTMENT MODULE SETUP": "investmentsetup@optimum-g.com",
    "IT Support": "it-helpdesk@optimum-g.com",
    "Operations": "operations@optimum-g.com",
    "OPERATIONS DASHBOARD": "operationsdashboard@optimum-g.com",
    "Support Manager": "supportmanager@optimum-g.com",
    "TREASURY OPERATIONS": "treasuryoperations@optimum-g.com",
    "Technology": "it-helpdesk@optimum-g.com",
}


def get_approval_department(form_code, employee_department):
    """
    Determines the department responsible for approving a form.

    Enclusia and WealthForge access requests go to Internal Control.
    Device-related forms go to IT Support.
    """

    form_code = str(form_code or "").strip().upper()

    if form_code in DEVICE_RELATED_FORMS:
        department = "IT Support"

    elif form_code in INTERNAL_CONTROL_FORMS:
        department = "Internal Control"

    else:
        raise ValueError(
            f"No approval routing configured for form: {form_code}"
        )

    email = DEPARTMENT_EMAILS.get(department)

    if not email:
        raise ValueError(
            f"No approval email configured for department: {department}"
        )

    return {
        "department": department,
        "email": email,
    }
