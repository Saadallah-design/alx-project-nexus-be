# Keep Track of the Project
This readme file is for me to keep track of the project as I progress through it.

So, currently: 

### 1. ⚙️ Environment & Database

* **PostgreSQL:** Server successfully installed via Homebrew (`postgresql@14`) and running as a service.
* **Database:** Created dedicated application database (`ecommerce_db`) and application user (`db_user`).
* **Migrations:** All core initial migrations have been **applied** to the database:
    * `users` (for `CustomUser`)
    * `django` core tables
    * `catalog` (for `Category` and `Product`)

### 2. 🛡️ Security & Configuration

* **Environment Variables:** Implemented **`django-environ`** to manage secrets (`SECRET_KEY`, `DATABASE_URL`) via a secure `.env` file.
* **Custom Authentication:** Configured Django to use the custom **`CustomUser`** model (login via email, UUID primary keys).
* **Errors Resolved:** Successfully fixed critical startup errors (`ModuleNotFoundError`, `LookupError`, database connection issues, and UUID imports).

### 3. 🛍️ Core Data Structure

* **Catalog Models:** Defined and migrated the core e-commerce models:
    * **`Category`**
    * **`Product`** (includes fields for UUID PK, pricing, inventory validation, and editorial marketing flags).

### 4. 👨‍💻 Next Step

* **Admin Setup:** Registered the **`Category`** and **`Product`** models in `catalog/admin.py`.
* **Ready to use:** The next step is to run **`python3 manage.py createsuperuser`** and then **`python3 manage.py runserver`** to verify the models are accessible in the Django Admin interface.
---------------------------------
### Note for me: 
Read the previous section to see the progress made so far.
