def normalize_phone(phone):
    if phone and phone.startswith("8"):
        phone = "+7" + phone[1:]
    return phone
