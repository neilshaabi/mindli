# mindli

Web application designed to improve outcomes for mental health services on a global scale, empowering practitioners and clients throughout the therapeutic journey.

Key features include:

- **User Account Management**: Users can register, sign in, update credentials, and delete their accounts.
- **Therapist-Client Matching**: Therapists create professional profiles; clients find therapists based on their preferences.
- **Appointment Scheduling**: Clients and therapists can manage appointments, integrated with automated email notifications.
- **Client Data Management**: Clients update personal information; therapists manage client data, appointment notes, therapy exercises and treatment plans.
- **Communication**: In-app messaging between therapists and clients.
- **Billing and Payments**: Therapists charge clients for appointments; clients make payments through the system.

## Setup and Running

Several useful commands are defined in the `Makefile` to facilitate the various development processes. It is **strongly recommended** to utilise these commands for setting up and running the application.
- Note: all `make` commands must be executed from the top-level `mindli` directory.

1. **Create virtual environment**:
   ```
   make venv
   ```

2. **Activate virtual environment**:
    ```
    source .venv/bin/activate
    ```

3. **Install dependencies**:
    ```
    make dependencies
    ```

4. **Run application**:
    ```
    make app
    ```

## Example User Credentials

Example accounts are provided for a therapist and client, with data designed to simulate the appearance of mindli with a large user base. Their login credentials are as follows:
- Therapist email: therapist@example.com
- Client email: client@example.com
- Password (both): ValidPassword1

## Makefile Commands

- `help`: Displays available commands.
- `tree`: Shows the directory tree excluding certain directories.
- `venv`: Creates a virtual environment. (Activate it manually using source .venv/bin/activate)
- `dependencies`: Installs Python and Node.js dependencies.
- `requirements`: Updates the requirements.txt file with the current dependencies.
- `app`: Builds JavaScript assets and runs the Flask application locally.
- `celery`: Starts a Celery worker for asynchronous task management. Requires Redis server.
- `redis`: Starts the Redis server.
- `migrate-db`: Generates and applies database migrations.
- `reset-db`: Resets the database by downgrading and then upgrading.
- `lint`: Formats, lints, and reorganizes imports for Python files.
- `test`: Runs tests using pytest.
- `clean`: Cleans up the directory by removing build files, caches, and virtual environment.

## Screenshots

User registration

<img width="1000" alt="User registration" src="https://github.com/user-attachments/assets/0563f154-b098-416a-a16f-83a7d67c920d">

\
Therapist directory

<img width="1512" alt="Therapist directory" src="https://github.com/user-attachments/assets/ca8e6d63-b510-4f53-978f-5b8e59ec91fc">

\
Appointment notes

<img width="1512" alt="Appointment notes" src="https://github.com/user-attachments/assets/6f8d428c-965d-49bb-b78c-47384339dca5">

\
Messages

<img width="1512" alt="Messages" src="https://github.com/user-attachments/assets/8a8a5ca0-6e46-47f5-8204-193753234c3e">
