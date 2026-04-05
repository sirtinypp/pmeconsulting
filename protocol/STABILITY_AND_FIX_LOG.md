# 🛡️ PME Learning | System Stability & Fix Knowledgebase

This document serves as the **Master Fix Log** and **Stability Baseline** for the PME Learning platform. It records the current architecture, roles, and historical resolutions to prevent regression and ensure rapid restoration.

---

## 📌 Current Stable Baseline: 1.0 (2026-04-06)
**STATUS**: ✅ FUNCTIONAL & VERIFIED
**COMMIT REFERENCE**: `main` (Last Git Restore point)

### 🗝️ Core Role Architecture
| Role | Access Level | Responsibilities | Default Dashboard |
| :--- | :--- | :--- | :--- |
| **GUEST** | Discovery | Initial signup. Restricted access to courses/materials. | `dashboards/guest.html` |
| **STUDENT** | Learning | Paid/Verified. Full access to CEFR courses and clinical resources. | `dashboards/student.html` |
| **SCHOOL_ADMIN** | Management | Oversees students, enrollments, and local materials. | `dashboards/school_admin.html` |
| **SUPERUSER** | Oversight | Global access to all models and schools via Django Admin. | `/admin/` |

---

## 🛠️ Critical Fix History & Learnings

### 1. Model Namespace Conflicts
- **Issue**: Attempting to add a second `Post` model in `core` conflicted with the existing `resources.Post` used for student guides.
- **Fix**: The administrative news system was renamed to **`Announcement`**.
- **Rule**: Avoid generic model names like `Post`, `Resource`, or `User` in local apps to prevent collisions.

### 2. Template Syntax Errors
- **Issue**: malformed tags (e.g., `{% {% block %}`) or trailing blocks caused site-wide crashes.
- **Fix**: All dashboards (`school_admin`, `student`, `guest`) have been audited for clean block inheritance.
- **Rule**: Always perform a `python manage.py runserver` check and browse as multiple roles after template refactors.

### 3. URL Namespacing & NoReverseMatch
- **Issue**: Manual restoration of files lost uncommitted URL names (`signup`, `upgrade`, `contact`).
- **Fix**: Re-registered crucial paths in `german_learning/urls.py` with explicit names.
- **Rule**: If a page shows `NoReverseMatch`, check if the `{ % url 'name' % }` exists in the main URL patterns.

### 4. Logout Redirection
- **Issue**: Inconsistent redirection upon logout.
- **Fix**: Set `LOGOUT_REDIRECT_URL = 'public_index'` in `settings.py`.
- **Learning**: This ensures all roles land on the public home page, providing a consistent professional exit.

---

## 🔑 Known Credentials (FOR DEVELOPMENT ONLY)
- **Superuser**: `grootadmin` / `xiarabasa12`
- **School Admin**: `schooladmin` / `pmeconsulting`
- **Student**: `student1` / `pmeconsulting`

---

## 🚨 Emergency Restore Checklist
If the system crashes during development:
1.  **Check Terminal**: Identify `NameError` or `TemplateSyntaxError`.
2.  **Git Restore**: `git restore core/ models.py views.py forms.py german_learning/urls.py`.
3.  **Migration Check**: Ensure `python manage.py showmigrations` matches the code state.
4.  **Baseline Test**: Login as each role and verify the dashboard header.

---
© 2026 PME Consulting EU. All rights reserved.
