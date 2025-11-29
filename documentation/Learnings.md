# General Learnings

## When dealing with APIs
- if we created a model and serialized it for consumption by front end, we can add a layer of security to make key fields read-only by adding the following line to the serializer:
```python
read_only_fields = ('id', 'created_at', 'updated_at', 'sale_price')
```
- for the sale_price since defined by a property in the model, we need to calculate it dynamically 
- this calculation is done through:
```python
sale_price = property(lambda self: self.base_price - (self.base_price * self.discount_percentage / 100))
```

### JWT
- A JSON Web Token (JWT) is essentially a digital ID card or badge for a user that is used on the internet.

#### 🔑 What It Is
It's a way for two parties (ex: a web browser and a server) to securely exchange information about a user. The key features are:

* **Self-Contained**: It holds all the necessary user information (like your user ID and permissions) right inside it.

* **Tamper-Proof**: It is digitally signed by the server using a secret key, so if anyone tries to change the data inside the token, the server will immediately know it's fake and reject it.

* **Compact**: It's small enough to be sent quickly with every request.

#### 🔑 How It Works
Imagine you are going to a private club:

* Login (Getting the ID): When you first log in to a website (or enter the club), you show your initial proof (username/password).

* **Issuance (The Server Gives You the Badge)**: The server verifies you and hands you a special, signed badge (the JWT). This badge says who you are, what permissions you have, and when it expires.

* **Access (Showing the Badge)**: Every time you request something from the server (or try to enter a different area of the club), you simply show your badge.

* **Verification (The Server Checks the Signature)**: The server doesn't have to look you up in a big list every time. It just checks the signature on the badge with its secret key.

* ==> If the signature is valid, the server trusts the information on the badge instantly and lets you in.

* ==> If the signature is invalid, the badge is a fake or has been altered, and the server denies access.


- Key Terms:
    - **Bearer Token**: A token that can be used to access protected resources. It is a type of token that is used to authenticate a user or a client.
    - **JWT**: A JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. The claims in a JWT are encoded as a JSON object that is used as the payload of a JSON Web Token.
    - **Token Refresh**: A process where a new access token is generated using a refresh token. This is used to maintain a user's session without requiring them to log in again.
    - **Blacklisting**: A process where a refresh token is added to a blacklist, making it invalid and unusable. This is used to prevent a user from using a refresh token to generate new access tokens after their session has expired.

#### ==> Concerning blacklisting: 
The rest_framework_simplejwt.token_blacklist app provides a mechanism to invalidate JWT refresh tokens before their natural expiration time, which is essential for implementing secure user logout, password resets, and token rotation. 

#### Why I am setting it blacklist_after_rotation to TRUE
Its primary use is to enable:
*  immediate session termination, which is crucial for secure user logouts, especially on shared computers. 

* It also facilitates account security during password resets, instantly invalidating old tokens to prevent unauthorized access. *

* it allows administrators to force logouts for compromised accounts and supports secure token rotation, ensuring that e-commerce sites adhere to security best practices and maintain user trust.

### SIGNING_KEY to secret key
The secret string used to sign the token's signature part. Crucially, it must be our project's SECRET_KEY. This ensures only my server can create valid tokens, preventing malicious actors from forging them.