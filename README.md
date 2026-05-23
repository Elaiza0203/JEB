# 📸 Luminary — Photo Album Management System

A production-ready Django photo album application featuring Class-Based Views, Role-Based Access Control, Cloudinary media storage, and PostgreSQL — deployed on Render.

---

## 🌐 Live Application

**[https://luminary-photoalbum.onrender.com](https://luminary-photoalbum.onrender.com)**

> Note: Render free-tier instances spin down after inactivity. The first request may take ~30 seconds to wake up.

---

## 📁 Repository

**[https://github.com/yourusername/luminary-photoalbum](https://github.com/yourusername/luminary-photoalbum)**

---

## ✅ Requirements Coverage

| Requirement | Implementation |
|---|---|
| Class-Based Views | All views use Django CBVs (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`) |
| Role-Based Access Control | `AlbumRole` model with Viewer / Contributor / Admin roles + custom mixins |
| Cloudinary Storage | `django-cloudinary-storage` with auto-transformations (thumbnails, WebP conversion) |
| PostgreSQL | `dj-database-url` with Render-provisioned Postgres |
| Deployed to Render | Live URL above; `render.yaml` included |

---

## 🏗 Architecture

```
photoalbum/               ← Django project root
├── photoalbum/
│   ├── settings.py       ← Environment-driven settings
│   ├── urls.py           ← Root URL configuration
│   └── wsgi.py
├── albums/
│   ├── models.py         ← Album, Photo, AlbumRole models
│   ├── views.py          ← All CBV views
│   ├── views_auth.py     ← Registration CBV
│   ├── mixins.py         ← RBAC mixins (AlbumViewMixin, AlbumEditMixin, AlbumAdminMixin)
│   ├── forms.py          ← Django forms
│   ├── urls.py           ← Album/Photo URL patterns
│   ├── urls_auth.py      ← Registration URL
│   └── admin.py          ← Django Admin registration
├── templates/
│   ├── base.html         ← Base layout
│   ├── albums/           ← Album & photo templates
│   └── registration/     ← Auth templates
├── requirements.txt
├── render.yaml           ← Render deployment config
└── .env.example
```

---

## 🔒 Role-Based Access Control

Three roles are enforced at the view level via custom mixins:

| Role | View Photos | Upload Photos | Edit/Delete Photos | Manage Members | Delete Album |
|---|:---:|:---:|:---:|:---:|:---:|
| **Viewer** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Contributor** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Owner** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Staff** | ✅ | ✅ | ✅ | ✅ | ✅ |

### Mixin Implementation

```python
# albums/mixins.py

class AlbumViewMixin:
    """Allows access if album is public OR user has any role."""

class AlbumEditMixin(LoginRequiredMixin):
    """Requires Contributor or Admin role."""

class AlbumAdminMixin(LoginRequiredMixin):
    """Requires Owner or Django staff."""
```

---

## 📷 Cloudinary Integration

- All uploaded images are stored in Cloudinary under the `photoalbum/` folder
- Auto-transforms on retrieval:
  - **Thumbnails**: 400×300px, `crop=fill`, `gravity=auto`, WebP
  - **Full view**: max 800px wide, `quality=auto`, WebP
- `DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'` — no local media in production

---

## 🚀 Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/luminary-photoalbum.git
cd luminary-photoalbum
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=                          # leave blank for SQLite
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

> Get Cloudinary credentials at [cloudinary.com](https://cloudinary.com) → Dashboard → API Keys

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

## ☁️ Deploying to Render

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/luminary-photoalbum.git
git push -u origin main
```

### Step 2: Create a Render account

Sign up at [render.com](https://render.com).

### Step 3: New Web Service

1. Click **New → Web Service**
2. Connect your GitHub repository
3. Render will detect `render.yaml` automatically

### Step 4: Set Environment Variables

In the Render dashboard → Environment, add:

| Key | Value |
|---|---|
| `SECRET_KEY` | Generate a secure random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | Auto-filled from Render Postgres |
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Your Cloudinary API secret |

### Step 5: Deploy

Click **Deploy** and wait ~3 minutes for the first build.

### Step 6: Create admin user on Render

```bash
# In Render dashboard → Shell
python manage.py createsuperuser
```

---

## 🧩 Key Models

### Album
```python
class Album(models.Model):
    title        = CharField
    description  = TextField
    owner        = ForeignKey(User)
    collaborators = ManyToManyField(User)
    cover_photo  = ForeignKey(Photo, null=True)
    is_public    = BooleanField
```

### Photo
```python
class Photo(models.Model):
    album       = ForeignKey(Album)
    image       = CloudinaryField          # Cloudinary storage
    title       = CharField
    description = TextField
    uploaded_by = ForeignKey(User)
    taken_at    = DateTimeField(null=True)
```

### AlbumRole
```python
class AlbumRole(models.Model):
    album      = ForeignKey(Album)
    user       = ForeignKey(User)
    role       = CharField  # viewer | contributor | admin
    granted_by = ForeignKey(User)
```

---

## 🔑 URL Structure

```
/                          → Redirect to /albums/
/albums/                   → AlbumListView
/albums/create/            → AlbumCreateView  [login required]
/albums/<pk>/              → AlbumDetailView
/albums/<pk>/edit/         → AlbumUpdateView  [owner/admin]
/albums/<pk>/delete/       → AlbumDeleteView  [owner/admin]
/albums/<pk>/members/add/  → AlbumMemberAddView
/albums/<pk>/photos/upload/         → PhotoUploadView  [contributor+]
/albums/<pk>/photos/<pk>/           → PhotoDetailView
/albums/<pk>/photos/<pk>/edit/      → PhotoUpdateView  [contributor+]
/albums/<pk>/photos/<pk>/delete/    → PhotoDeleteView  [contributor+]
/albums/<pk>/photos/<pk>/set-cover/ → SetCoverPhotoView [owner/admin]
/accounts/login/           → Django LoginView
/accounts/logout/          → Django LogoutView
/accounts/register/        → RegisterView (CustomUserCreationForm)
/admin/                    → Django Admin
```

---

## 🛡 Security

- `SECRET_KEY` and all credentials read from environment variables — never hardcoded
- `SECURE_SSL_REDIRECT = True` in production
- `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` enabled in production
- CSRF protection on all POST forms
- Permission checks at view level via RBAC mixins (raises `PermissionDenied` → 403)
- `WhiteNoise` for static files with `CompressedManifestStaticFilesStorage`

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Framework | Django 5.0 |
| Language | Python 3.12 |
| Database | PostgreSQL (Render) / SQLite (dev) |
| Media Storage | Cloudinary |
| Static Files | WhiteNoise |
| Server | Gunicorn |
| Hosting | Render |

---

## 📌 Admin Panel

Access at `/admin/` with your superuser credentials.  
Manage users, albums, photos, and roles directly.

---

*Built with Django · Deployed on Render · Media by Cloudinary*
