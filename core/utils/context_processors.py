from home.models import AdminEmail, BankAccountNumberSnippet, PhoneSnippet


def biwakowa_phone(request):
    phone = PhoneSnippet.objects.last()
    return {
        "phone": phone,
    }

def biwakowa_email(request):
    email = AdminEmail.objects.last()
    return {
        "hotel_email": email,
    }

def bank_account_number(request):
    bank_account = BankAccountNumberSnippet.objects.last()
    return {
        "bank_account": bank_account.bank_account if bank_account else "",
        "owner_name": bank_account.owner_name if bank_account else "",
    }
