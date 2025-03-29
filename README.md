# Django Test Coordinator

A Django application that coordinates testing for a FastAPI sister service.

## Features

- First user becomes an authenticated admin user
- Onboarding wizard for admin to set up testing environment
- Create and manage API test cases
- Organize test cases into test queues
- Track test execution history
- Monitor test results

## Setup

1. Clone this repository
2. Set up environment variables for PostgreSQL connection:
   - `PGDATABASE` - Database name (default: "testcoordinator")
   - `PGUSER` - Database user (default: "postgres")
   - `PGPASSWORD` - Database password (default: "postgres")
   - `PGHOST` - Database host (default: "localhost")
   - `PGPORT` - Database port (default: "5432")
   - `FASTAPI_BASE_URL` - URL of FastAPI test service (default: "http://fastapi:8000")

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

1. Create the first user, who will automatically become an admin
2. Follow the onboarding wizard to configure FastAPI connection
3. Create test cases for your API endpoints
4. Group test cases into test queues for batch execution
5. Run tests and monitor results

## Deployment

This application is configured to run in an isolated container with:
- Django web server
- PostgreSQL database
- Connection to FastAPI service
