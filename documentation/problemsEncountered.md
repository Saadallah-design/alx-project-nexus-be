# this readme.md file is created to document the problems encountered during the project

### problems encountered:
- Initiating the database PostgreSQL.
- ==> I had some misunderstanding with postgres installation and user creation. 
- Working with .env file and the .gitignore file.

- Creation of superuser failed.
- ==> since I sat up the USERNAME_FIELD = 'email' in the custom user model, I need to provide an email address when creating a superuser. 
- However, this yields an error: 
``` 
TypeError: UserManager.create_superuser() missing 1 required positional argument: 'username'
```
So to override this, I will need to create a bridge-like function in the custom user model to handle the creation of a superuser.
- This approach is the modern way. 
- To it I need to: 
    * create a new class called CustomUserManager.
    * insert this manager between  CustomUser model and Django's default logic.
    * This manager overrides the default, broken create_superuser method.
    * ensuring  that when I run the command, it only requires and prompts me for the email and password.
==> By implementing the CustomUserManager and assigning it to the model using objects = CustomUserManager(), we guarantee that all user creation commands—including createsuperuser—will follow these rules (using email) instead of Django's default, outdated rules.

## 🎓 Key Concepts You Should Understand

1. **BaseUserManager Methods**
When you inherit from BaseUserManager, you must implement:

✅  create_user()
    - Creates regular users
✅ create_superuser()
    - Creates admin users

2. **self.model**

``` python
user = self.model(email=email, **extra_fields)
```
 - self.model refers to the CustomUser class
 - This is set automatically when you assign objects = CustomUserManager() in the model

3. self.normalize_email(email)

``` python
email = self.normalize_email(email)
```
- Built-in Django method from BaseUserManager
- Converts domain part to lowercase: User@EXAMPLE.com → User@example.com
- Prevents duplicate accounts due to case differences

4. user.set_password(password)
``` python
user.set_password(password)
```

* NEVER do user.password = password ❌
* set_password() uses PBKDF2 hashing (secure!)
* Stores hashed password like: pbkdf2_sha256$600000$...

5. **extra_fields

``` python
def create_user(self, email, password=None, **extra_fields):
```

* Captures any additional keyword arguments
* Allows passing first_name, last_name, is_active, etc.
* Makes the method flexible for different scenarios

