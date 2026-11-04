\# ECHO — Personal Knowledge Management System



ECHO is a secure, multi-user personal knowledge management application built with Python, Flask and SQLite.



\## Features



\- User registration and login

\- Secure password hashing

\- Personal note creation

\- Note editing and deletion

\- Note searching

\- Multi-user data isolation

\- Session management

\- CSRF protection

\- Automated testing



\## Technologies



\- Python

\- Flask

\- SQLite

\- HTML

\- CSS

\- Flask-WTF

\- Werkzeug



\## Project Structure



```text

ECHO/

│

├── echo.py

├── flask\_app.py

├── test\_echo.py

├── test\_flask\_app.py

├── migrate\_database.py

├── requirements.txt

├── .gitignore

│

├── templates/

│   ├── index.html

│   ├── edit.html

│   ├── login.html

│   └── register.html

│

└── static/

&#x20;   └── style.css

```



\## Installation



Clone the repository:



```bash

git clone YOUR\_REPOSITORY\_URL

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Run the application:



```bash

python flask\_app.py

```



Open:



```text

http://127.0.0.1:5000

```



\## Testing



Run the original application tests:



```bash

python -m unittest test\_echo -v

```



Run authentication and security tests:



```bash

python -m unittest test\_flask\_app -v

```



\## Security



\- Passwords are hashed.

\- Database queries use parameterized SQL.

\- User notes are restricted to their owners.

\- CSRF protection is enabled.



\## Project Status



Core application and multi-user authentication implemented. Further security hardening and deployment improvements are planned.

