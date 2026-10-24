# Cyber Security Base Project
LINK: https://github.com/HorttanainenSami/cyber-security-base-project

We use Owasp 2021 list

### Init on linux: 
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py loaddata sample_data
python manage.py runserver
```
`python manage.py loaddata sample_data` loads some test data to database
along with following users:
```
admin:admin
jaska:qwerty
joni:password123
```

## FLAW 1: 
## A07:2021 - Identification and Authentication Failures 
- bruteforce allowed
https://github.com/HorttanainenSami/cyber-security-base-project/blob/9bb402dc22343d06198d91b93ef204bbbe0a9154/todo/views/auth.py#L16

Problem in login is that user can retry login attempts without any timeouts. The absence of the rate limiting is reason that the malicious user can guess passwords with a brute force.

### How to test:
run `python scripts/flaw_1.py` in root directory

### How to fix:
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L31

The fix for the problem is by introducing a rate limiter with Django’s built in cache. By storing failed login attempts from same IP and limiting after 5 consecutive failed logins from the same IP for the next minute.

Limitations: Bot farm could use multiple IP’s to brute force the password. Rate limiting the login attempts by IP and username would prevent bot farm from brute forcing certain users password but it would also enable malicious user to lock usernames indefinitely from login by continuing failing the login attempts for one username. 
### Screenshots
before ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_1_before.png)
after ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_1_after.png)

## FLAW 2:
## A02:2021 - Cryptographic Failures 
- weak password hashing
https://github.com/HorttanainenSami/cyber-security-base-project/blob/9bb402dc22343d06198d91b93ef204bbbe0a9154/mysite/settings.py#L32

Weak password hashing: Problem is that if we use MD5 which is weak hashing algorithm. Our application users are in danger if their passwords are leaked for example with SQL injection like in our FLAW 4.  Because application is using weak password hashing algorithm, malicious actor could easily break the snatched password.

Django docs is suggesting that we are downgrading the password hashing algorithm to MD5 for testing, because the default algorithm is by design, slow. This can be nuisance if developers are authenticating multiple users in tests. If this change isn’t handled correctly it might end up in production. The MD5 Hashing algorithm was developed to be fast and cracking MD5 password is relatively easy for modern GPU. Modern Nvidia RTX 5090 can crack 48% of passwords under one minute and 60% in an hour.

https://www.theregister.com/security/2026/05/07/60-of-md5-password-hashes-are-crackable-in-under-an-hour/5234954

https://docs.djangoproject.com/en/6.1/topics/testing/overview/#password-hashing

### How to test:
Go to http://127.0.0.1:8000/admin/ and login with user: admin password: admin
Go to http://127.0.0.1:8000/admin/auth/user/1/change/
under password: you can see there is algorithm used: MD5

### How to fix: 
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/mysite/settings.py#L37

Use the latest and up-to-date password hashing algorithm. Owasp is recommending the Argon2 password hasher that is developed to be slow and resource heavy so it would be expensive to try crack passwords hashed with Argon2. In fix the MD5 still remains as a second in the list. When user with MD5 hashed password logs in, Django verifies it with MD5 and rehashes that with Argon2

Retry steps in how to test 
make sure you logout and then relogin as the password is then changed to Argon2

### Screenshots
before ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_2_before.png)
after ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_2_after.png)
## FLAW 3:
## A09:2021 - Security Logging and Monitoring Failures 
- successful and failed logins not logged
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L16

Application is not logging any actions of authentication logic. This is problematic as if the software is under a on going attack some logging monitor could detect ongoing attack and make safety measures to prevent it. And if the attacker gains access to software there is not enough logs to trace what attacker has been doing inside our software.


### How to fix:
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L8
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L31
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L39
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L47
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L54
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/auth.py#L73
This fix requires the fix 1 to be in place. All places that needs to be uncommented are above

We are using python library logging, its easy way to get logs to separate file that way we have persistent logs and they aren’t lost when the server is restarted. The separate file allows us to use external monitoring tools for our logs. It also allows to attach timestamp, IP, etc for every action that is logged. 

We also make sure that we are escaping any user input from the logs with !r. That will prevent log injection, what might be used to tamper our logs.
https://community.owasp.org/attacks/Log_Injection

### How to test:
try the bruteforce script: run ‘python scripts/flaw_1.py’ in root directory
and there should be generated a file csp1/auth.log which will log the login attempts for user.

### Screenshots
after ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_3_after.png)
## FLAW 4:
## A03:2021 - Injection
https://github.com/HorttanainenSami/cyber-security-base-project/blob/9bb402dc22343d06198d91b93ef204bbbe0a9154/todo/views/todo.py#L40


Problem is that backend is trusting client and the client input is not parametrized. This opens up possibility for database injection. For example user could manipulate backends SQL Query to return whole lot different response that our application is expecting. 

### How to test:
User must be logged in.
input following line in search input field on http://127.0.0.1:8000/todo/search/
```
' UNION SELECT id, username || ':' || password FROM auth_user --
```

It will return all users from the database with their passwords (hashed) 

``` 
' UNION SELECT t.id, u.username || ': ' || t.todo FROM todo_todo t JOIN auth_user u ON u.id = t.owner_id --
```
Returns all todos from all users

### How to fix:
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/todo.py#L54

In backend should not trust client and clients input should always be parametrized. Here one solution is by using Django’s ORM that will parametrize input automatically. It will send the query and data separately so user input cannot be part of the query.

### Screenshots
before ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_4_before.png)
after ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_4_after.png)


## FLAW 5:

### A01:2021 - Broken Access Control 
https://github.com/HorttanainenSami/cyber-security-base-project/blob/9bb402dc22343d06198d91b93ef204bbbe0a9154/todo/views/todo.py#L16

- trust client by checking the HTTP parameter for admin privileges
Problem is that backend is still trusting client to not try and manipulate the input in anyway. In this vulnerable code client is providing incorrect information about users privileges and backend is not checking it from database and thus grants admin access to non admin user.

### How to test:
be logged in with non admin user (jaska or joni) and input url http://127.0.0.1:8000/todo/admin/?is_staff=true

### How to fix:
https://github.com/HorttanainenSami/cyber-security-base-project/blob/b22783680b65df50483c819c65e13a6cd1859893/todo/views/todo.py#L25

We are not trusting client and we are checking the privileges from the database.
Backend should not trust clients data and check the data that is in its own possession, like database. In fix backend is checking whether request making user is in fact privileged to do the action.

### Screenshots
before ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_5_before.png)
after ![](https://raw.github.com/HorttanainenSami/cyber-security-base-project/main/screenshots/flaw_5_after.png)
