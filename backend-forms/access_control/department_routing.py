DEVICE_RELATED_FORMS = {
    "OGCM-REPLACEMENT",
    "OGCM-TROUBLESHOOTING",
    "OGCM-INFRASTRUCTURE",
    "OGFS-REPLACEMENT",
    "OGFS-TROUBLESHOOTING",
    "OGFS-INFRASTRUCTURE",
    "OST-ISSUE",
    "OST-TROUBLESHOOTING",
}


DEPARTMENT_EMAILS = {
    "Administrator": "administrator@optimum-g.com",
    "Account Officers": "accountofficers@optimum-g.com",
    "Finance Dashboard": "financedashboard@optimum-g.com",
    "Financial Control": "financialcontrol@optimum-g.com",
    "Global Dashboard": "globaldashboard@optimum-g.com",
    "Internal Control": "internalcontrol@optimum-g.com",
    "INVESTMENT MODULE SETUP": "investmentsetup@optimum-g.com",
    "IT Support": "it-helpdesk@optimum-g.com",
    "Operations": "operations@optimum-g.com",
    "OPERATIONS DASHBOARD": "operationsdashboard@optimum-g.com",
    "Support Manager": "supportmanager@optimum-g.com",
    "TREASURY OPERATIONS": "treasuryoperations@optimum-g.com",

    # Employee department returned by Entra ID
    "Technology": "it-helpdesk@optimum-g.com",
}


def get_approval_department(
    form_code,
    employee_department
):
    """
    Determines which department should approve a form.

    Device-related forms are always routed to IT Support.

    Enclusia access requests are routed to the employee's
    own department.
    """

    employee_department = str(
        employee_department or ""
    ).strip()

    if form_code in DEVICE_RELATED_FORMS:

        department = "IT Support"

    elif form_code == "OST-ENCLUSIA-ACCESS":

        department = employee_department

    else:

        raise ValueError(
            f"No approval routing configured for form: {form_code}"
        )

    email = DEPARTMENT_EMAILS.get(
        department
    )

    if not email:

        raise ValueError(
            "No approval email configured for "
            f"department: {department}"
        )

    return {
        "department": department,
        "email": email,
    }