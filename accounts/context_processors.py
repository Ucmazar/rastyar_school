# accounts/context_processors.py
def sidebar_menu(request):
    menu_items = [
        {"name": "شاگردان", "url": "student_list", "roles": ["admin", "teacher"]},
        {"name": "معلمین", "url": "teacher_list", "roles": ["admin"]},
        {"name": "مضامین", "url": "subject_list", "roles": ["admin"]},
        {"name": "دسته بندی مضامین", "url": "subjectgroup_list", "roles": ["admin", "teacher"]},
        {"name": "صنوف", "url": "class_list", "roles": ["admin", "teacher"]},
        {"name": "ثبت امتحان", "url": "examtype_list", "roles": ["admin"]},
        {"name": "ثبت نمرات", "url": "grade_entry", "roles": ["admin"]},
    ]

    allowed_items = []
    if request.user.is_authenticated and hasattr(request.user, "role"):
        allowed_items = [item for item in menu_items if request.user.role in item["roles"]]

    return {"sidebar_menu_items": allowed_items}
