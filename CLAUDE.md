# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

H3Blog is a lightweight blog system built with Flask, supporting multi-tenancy, multiple databases (SQLite/MySQL), theme switching, and payment integration (Alipay/WeChat). It features a modular architecture with separate blueprints for admin, main (frontend), and API.

## Development Environment

### Environment Setup
```bash
# Install dependencies using uv
uv sync

# Activate virtual environment
# Windows:
.venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate
```

### Running the Application
```bash
# Set environment (Windows PowerShell)
$env:FLASK_ENV="development"

# Start Flask development server
flask run

# Alternative: use python
python -m flask run
```

The app will be available at:
- Blog frontend: http://127.0.0.1:5000
- Admin backend: http://127.0.0.1:5000/admin (default: admin/123456)

### Database Commands
```bash
# Initialize database with default data
flask initdb

# Drop and recreate all tables
flask initdb --drop
```

### Production Deployment
Use Gunicorn with the provided config:
```bash
gunicorn -c gunicorn.py wsgi:app
```

## Architecture

### Application Structure
- **Factory Pattern**: `app/__init__.py` - `create_app()` initializes the Flask application
- **Blueprints**: Three main blueprints registered in `register_blueprints()`
  - `main` - Frontend blog (template path: `app/main/themes/`)
  - `admin` - Backend management (url prefix: `/admin`)
  - `api` - REST API (url prefix: `/api`)

### Key Directories
- `app/admin/` - Admin blueprint with system management (users, roles, menus) and CMS (articles, categories, tags)
- `app/main/` - Frontend blueprint with theme support in `themes/` subdirectory
- `app/api/` - API endpoints for login and VIP features
- `app/model/` - SQLAlchemy models (BaseModel, User, Role, Menu, Article, Category, Tag, etc.)
- `app/util/` - Utilities including authentication, permissions, payment processing
- `app/ext/` - Flask extensions initialization (db, login_manager, csrf, cache, sitemap)
- `app/settings.py` - Configuration classes (development, testing, production)

### Configuration
- Environment variables loaded from `.env` file in project root
- Key configs in `app/settings.py`:
  - `DATABASE_URL` - Database connection string
  - `H3BLOG_TEMPLATE` - Active frontend theme (default: 'tend')
  - `H3BLOG_UPLOAD_TYPE` - File storage (local/qiniu)
  - Payment settings for Alipay/WeChat

### Database Models
- **BaseModel** - Abstract base with timestamps, soft delete, org tracking
- **User** - Authentication with role-based access control (user_type: admin/member/vip)
- **Role/Menu** - RBAC with many-to-many relationship
- **Article/Category/Tag** - CMS content with hierarchical categories
- **Setting** - Runtime configuration stored in database
- **PayLog** - Payment transaction records
- **Org** - Multi-tenancy organization support

### Permission System
- Decorator: `@admin_perm(model_name, operation, permission_string)` in `app/util/permission.py`
- Permissions checked via `get_perms_cache()` - cached per user
- Admin user (`username='admin'`) has all permissions
- Menu perms format: `sys:user:view`, `cms:article:add`

### Theme System
- Frontend themes located in `app/main/themes/{theme_name}/`
- Active theme determined by `H3BLOG_TEMPLATE` config or database Theme model
- Each theme has `static/` folder (CSS/JS/images) and Jinja2 templates
- Blueprint's static_folder dynamically changed in `change_static_folder()`

### Content Rendering
- Markdown content stored in `Article.content`, converted to HTML in `content_html`
- Uses `markdown-checklist` extension and Pygments for syntax highlighting
- Custom `CustomHtmlFormatter` in `app/util/common.py` for code blocks
- Hidden content support with role-based access (h_role, h_content fields)

### Payment Integration
- Unified interface in `app/util/onepay/pay.py`
- Alipay: `app/util/onepay/ali/`
- WeChat: `app/util/onepay/wx/`
- Payment logging via `PayLog` model

## Project Structure

### Overall Directory Structure

```
h3blog/
├── app/                          # Main application directory
│   ├── admin/                    # Admin backend Blueprint
│   ├── api/                      # REST API Blueprint
│   ├── main/                     # Frontend main Blueprint
│   ├── model/                    # SQLAlchemy models
│   ├── util/                     # Utility functions
│   ├── ext/                      # Flask extensions initialization
│   ├── static/                   # Global static files
│   ├── templates/                # Global templates
│   ├── settings.py               # Configuration classes
│   └── __init__.py               # Application factory
├── uploads/                      # Uploaded files directory
├── logs/                         # Log files directory
├── .venv/                        # Python virtual environment
├── data-dev.db                   # SQLite development database
├── gunicorn.py                   # Gunicorn config for production
├── wsgi.py                       # WSGI entry point
└── CLAUDE.md                     # This file
```

### Backend Structure (app/)

```
app/
├── admin/                        # Admin backend Blueprint (/admin)
│   ├── static/                   # Admin static resources
│   │   ├── ajax/                 # Ajax related JS
│   │   ├── css/                  # CSS styles
│   │   ├── js/                   # JavaScript files
│   │   ├── img/                  # Images
│   │   ├── fonts/                # Font files
│   │   ├── editor_md/            # Markdown editor
│   │   ├── file/                 # File upload component
│   │   └── ruoyi/                # RuoYi framework components
│   ├── templates/                # Admin templates
│   │   └── admin/                # Admin page templates
│   └── views/                    # View controllers
│       ├── cms/                  # CMS content management
│       │   ├── article.py        # Article management
│       │   ├── banner.py         # Banner management
│       │   ├── category.py       # Category management
│       │   ├── tag.py            # Tag management
│       │   ├── theme.py          # Theme management
│       │   └── ...
│       └── sys/                  # System management
│           ├── user.py           # User management
│           ├── role.py           # Role management
│           ├── menu.py           # Menu management
│           ├── gencode.py        # Code generator
│           └── ...
├── api/                          # REST API Blueprint (/api)
│   ├── common.py                 # Common API endpoints
│   ├── login.py                  # Login API
│   ├── vip.py                    # VIP related API
│   └── ...
├── main/                         # Frontend Blueprint (/)
│   ├── view/                     # View controllers
│   │   ├── index.py              # Homepage
│   │   ├── login.py              # Login page
│   │   └── account.py            # User account
│   └── themes/                   # Frontend themes
│       ├── tend/                 # Default theme
│       ├── pudu/                 # Alternative theme
│       └── ...
├── model/                        # Data models
│   ├── common.py                 # Common models (User, Role, Menu, etc.)
│   └── cms.py                    # CMS models (Article, Category, Tag, etc.)
├── util/                         # Utility functions
│   ├── auth.py                   # Authentication utilities
│   ├── permission.py             # Permission control
│   ├── common.py                 # Common utilities
│   ├── onepay/                   # Payment integration
│   │   ├── pay.py                # Unified payment interface
│   │   ├── ali/                  # Alipay
│   │   └── wx/                   # WeChat Pay
│   └── ...
├── ext/                          # Flask extensions
│   ├── db.py                     # Database extension
│   ├── login_manager.py          # Flask-Login
│   ├── csrf.py                   # CSRF protection
│   ├── cache.py                  # Cache extension
│   └── ...
├── static/                       # Global static files
├── templates/                    # Global templates
├── settings.py                   # Configuration classes
└── __init__.py                   # Application factory (create_app)
```

### Frontend Theme System Structure

```
app/main/themes/{theme_name}/
├── static/                       # Theme-specific static resources
│   ├── css/                      # CSS styles
│   ├── js/                       # JavaScript files
│   ├── img/                      # Images
│   ├── fonts/                    # Fonts
│   └── vendor/                   # Third-party libraries
├── account/                      # Account-related pages
├── common/                       # Common components
├── macros/                       # Jinja2 macro definitions
├── errors/                       # Error pages
├── base.html                     # Base template
├── index.html                    # Homepage
├── article.html                  # Article detail page
├── category.html                 # Category page
├── tag.html                      # Tag page
├── archives.html                 # Archives page
├── login.html                    # Login page
├── regist.html                   # Registration page
└── ...
```

### API Structure

```
app/api/
├── common.py                     # Common API endpoints
├── login.py                      # Login/authentication API
├── vip.py                        # VIP membership API
├── doc.py                        # API documentation
├── errors.py                     # Error handling
└── ...
```

## Frontend Theme System

### Theme Architecture

The frontend supports multiple themes with complete separation of templates and static resources:

- **Theme Location**: `app/main/themes/{theme_name}/`
- **Active Theme**: Configured via `H3BLOG_TEMPLATE` in settings or database Theme model
- **Template Path**: Dynamically changed based on active theme
- **Static Files**: Each theme has its own `static/` folder with CSS, JS, and images

### Theme Components

Each theme typically contains:

- **base.html** - Base template with common layout
- **index.html** - Homepage template
- **article.html** - Article detail page
- **category.html** - Category listing page
- **tag.html** - Tag listing page
- **archives.html** - Article archives
- **account/** - User account related pages
- **common/** - Reusable components
- **macros/** - Jinja2 macros for template reuse
- **static/** - Theme-specific assets

### Theme Switching Mechanism

1. **Config-based**: Set `H3BLOG_TEMPLATE` in `app/settings.py`
2. **Database-based**: Update Theme model in database
3. **Dynamic switching**: Blueprint's `static_folder` and `template_folder` are modified in `change_static_folder()` function

### Creating a New Theme

1. Create theme directory: `app/main/themes/{theme_name}/`
2. Add `static/` subdirectory with CSS/JS/images
3. Create required Jinja2 templates (base.html, index.html, article.html, etc.)
4. Optional: Add theme-specific components in `common/` and `macros/`
5. Set theme via Setting model or `H3BLOG_TEMPLATE` config
6. Reference: See `模板开发参考文档.md` for detailed template development guide

## Admin Backend Structure

### Unified Architecture

The admin backend uses a consistent structure across all modules:

- **URL Prefix**: All admin routes are under `/admin`
- **Blueprint Pattern**: Each functional area is a separate Blueprint
- **View Organization**: Views organized by module in `app/admin/views/`
- **Template Organization**: Templates mirror view structure in `app/admin/templates/admin/`
- **Static Resources**: Shared static files in `app/admin/static/`

### CRUD Pattern

All admin CRUD operations follow a unified pattern:

1. **List View**: `@bp.route('/')` - Display data table with search and pagination
2. **Add View**: `@bp.route('/add')` - Form for creating new records
3. **Edit View**: `@bp.route('/edit/<int:id>')` - Form for editing existing records
4. **Delete View**: `@bp.route('/delete/<int:id>')` - Delete record (soft delete)
5. **Export**: `@bp.route('/export')` - Export data to Excel

### Permission Control

All admin views use the `@admin_perm()` decorator:

```python
@admin_perm('cms:article:view', '查看文章')
def list():
    pass

@admin_perm('cms:article:add', '添加文章')
def add():
    pass
```

- Permission format: `{module}:{model}:{action}`
- Admin user (`username='admin'`) has all permissions
- Permissions cached via `get_perms_cache()` for performance

### Menu Registration

Menus are registered in `app/initdb.py` with hierarchical structure:

- **Level 1 (M)**: Module menu (e.g., CMS, System)
- **Level 2 (C)**: Feature menu (e.g., Article, Category)
- **Level 3-4 (F)**: Action buttons (View, Add, Edit, Delete)

### Common UI Components

- **Bootstrap Table**: Data tables with sorting, pagination
- **jQuery Validation**: Form validation
- **SweetAlert2**: Alert dialogs
- **Layer**: Popup modals
- **Summernote**: Rich text editor
- **File Upload**: Image/file upload component

## Code Generator

### Overview

H3Blog includes a powerful code generator that automatically creates complete admin CRUD interfaces from SQLAlchemy models. This significantly accelerates development by following the "convention over configuration" principle.

### Core Components

- **Models**: [GenModel](app/model/common.py:335) and [GenColumn](app/model/common.py:367) in `app/model/common.py`
- **Controller**: [gencode.py](app/admin/views/sys/gencode.py) - Code generation controller
- **Templates**: `app/admin/templates/admin/sys/gencode/vm/` - Code generation templates

### Supported Template Types

| Type | Description | Use Case |
|------|-------------|----------|
| `crud` | Standard CRUD with Bootstrap Table | General data management |
| `crud_html` | CRUD with HTML-rendered list | Simple management interfaces |
| `tree` | Tree structure CRUD | Hierarchical data (menus, categories) |
| `api` | RESTful API endpoints | Mobile/backend integration |
| `sub` | Master-detail table CRUD | Related data structures |

### Field Configuration

#### HTML Type Mapping

The generator automatically maps database column types to HTML input types:

| Database Type | HTML Type | Control |
|---------------|-----------|---------|
| `DATETIME` | `datetime` | Date/time picker |
| `TEXT` | `summernote` | Rich text editor |
| String | `input` | Text input |
| - | `textarea` | Textarea |
| - | `select` | Dropdown (with dict_type) |
| - | `radio` | Radio buttons (with dict_type) |
| - | `checkbox` | Checkboxes |
| - | `upload` | File upload |
| - | `upload_img` | Image upload |

#### Column Configuration Options

- **is_required**: Whether field is required (1=required, 0=optional)
- **is_insert**: Show in add form
- **is_edit**: Show in edit form
- **is_list**: Show in list table
- **is_query**: Enable as search filter
- **query_type**: Search method (=, !=, >, <, between, like)
- **html_type**: HTML input control type
- **dict_type**: Dictionary type for select/radio options

### Usage Workflow

1. **Access Generator**: Navigate to `/admin/sys/gencode/`
2. **Select Model**: Choose a SQLAlchemy model from dropdown (auto-scanned)
3. **Configure Fields**:
   - Set HTML control type for each field
   - Configure required/insert/edit/list/query flags
   - Set query type and dict_type if applicable
4. **Configure Generation**:
   - Select template type (crud, tree, api, etc.)
   - Set view path and template path
   - Choose parent menu
5. **Preview**: Click preview to see generated code
6. **Generate**: Confirm to write files to filesystem

### Auto-Generated Features

The generator creates complete CRUD functionality including:

- **List page**: Data table with search, pagination, sort
- **Add/Edit forms**: Dynamic forms with validation
- **Delete operation**: Soft delete with confirmation
- **Export**: Excel export functionality
- **Permissions**: Auto-generated permission points
- **Routes**: Blueprint registration with URL prefix
- **Menus**: 4-level menu structure (Module > Feature > View/Add/Edit/Delete)
- **Tree support**: For tree template, includes tree picker
- **File upload**: Handling for upload fields

### Generated File Structure

```
app/admin/views/{view_path}/{model_name}.py          # View controller
app/admin/templates/admin/{tpl_path}/
    ├── list.html                                     # List page
    ├── add.html                                      # Add form
    └── edit.html                                     # Edit form
```

### Special Features

1. **Smart Field Recognition**: Auto-excludes system fields (id, ctime, utime, deleted, etc.)
2. **Permission Integration**: Auto-generates permission decorators and menu entries
3. **Dictionary Support**: Integrates with system dictionary for select/radio fields
4. **Data Authority**: Supports data-level permissions based on organization
5. **Responsive Design**: Generated UI fully responsive

### Example: Generating Article Module

1. Navigate to `/admin/sys/gencode/`
2. Select `Article` model
3. Configure fields:
   - `title`: input, required, list, query (like)
   - `content`: summernote, required
   - `category_id`: select (with dict_type), list, query
4. Choose template type: `crud`
5. Set paths: view=`cms`, tpl=`cms/article`
6. Select parent menu: "CMS"
7. Preview and generate

Result: Complete article management module with list, add, edit, delete, export, and permissions.

## Important Patterns

### Database Session Management
- Sessions auto-commit in `teardown_appcontext` handler
- Manual `db.session.commit()` after mutations
- Rollback on exception in teardown handler

### Multi-tenancy
- `Org` model with hierarchical structure
- `g.org` set in `before_app_request` based on subdomain
- Models include `org_id` field (via BaseModel's `default_create_org()`)

### Soft Deletes
- `deleted` column on all BaseModel-derived models (0=active, 1=deleted)
- Queries should filter: `Model.query.filter(Model.deleted == 0)`

### User Authentication
- Flask-Login with custom user loader in `app/ext/__init__.py`
- User IDs prefixed: `admin.{id}` for admins, `member.{id}` for members
- Token-based auth via `Authorization` header (Basic auth encoding)

### Template Globals
- Registered in `app/template_global.py`
- Available in all templates: `get_articles()`, `get_categorys()`, `get_tags()`, etc.
- Helper for template development documented in `模板开发参考文档.md`

## Default Credentials
- Admin: username `admin`, password `123456`

## Common Tasks

### Generating Admin CRUD (Recommended Method)

**Using the Code Generator is the fastest way to create admin modules:**

1. Navigate to `/admin/sys/gencode/`
2. Select your model (auto-detected from `app/model/`)
3. Configure field properties (HTML types, validation, search options)
4. Choose template type (crud/tree/api)
5. Preview and generate

The generator automatically creates:
- View controller with full CRUD operations
- HTML templates (list, add, edit)
- Permission decorators
- Menu structure
- Blueprint registration

**For detailed instructions, see the [Code Generator](#code-generator) section above.**

### Adding a New CMS Model Manually

If you need manual control:

1. Create model class inheriting from `BaseModel` in `app/model/cms.py` or `app/model/common.py`
2. **Recommended**: Use code generator to create admin interface
3. **Or**: Manually add admin views in `app/admin/views/cms/`
4. Register menu items in `app/initdb.py`
5. Create forms in `app/admin/forms.py` if needed

### Creating a New Theme

1. Create directory: `app/main/themes/{theme_name}/`
2. Add `static/` subdirectory with CSS/JS
3. Create Jinja2 templates:
   - `base.html` - Base layout
   - `index.html` - Homepage
   - `article.html` - Article detail
   - `category.html` - Category listing
   - `tag.html` - Tag listing
   - `archives.html` - Archives
   - `login.html` - Login page
   - `regist.html` - Registration page
4. Optional: Add components in `common/` and `macros/`
5. Set theme via Setting model or `H3BLOG_TEMPLATE` config
6. Reference: See `模板开发参考文档.md` for detailed guide

### Adding API Endpoints

1. Create view function in `app/api/`
2. Use `@admin_perm()` decorator for permission checks if needed
3. Return JSON using `ajax_result()` from `app/util/ajax_result.py`
4. For full CRUD API, use code generator with template type `api`
