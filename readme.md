# Django Chatbot Demo

This Django project is a simple demonstration of the chatbot application to be used by Creatego.

## Technologies Used

- Django: A high-level Python web framework for rapid development.
- Django Channels: Adds asynchronous capabilities to Django, enabling real-time features.
- WebSocket: A communication protocol that provides full-duplex communication channels over a single TCP connection.
- HTML/CSS/JavaScript: Frontend development technologies for building the user interface and interaction.
- SQLite: A lightweight relational database used for storing user data.

## Setup

1. Clone the repository:

    ```
    git clone <repository_url>
    ```

2. Navigate to the project directory:

    ```
    cd <project_directory>
    ```

3. Create a virtual environment:

    ```
    python3 -m venv venv
    ```

4. Activate the virtual environment:

    - On macOS and Linux:

    ```
    source venv/bin/activate
    ```

    - On Windows (cmd.exe):

    ```
    .\venv\Scripts\activate
    ```

5. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

6. Apply database migrations:

    ```
    python manage.py migrate
    ```

7. Run the development server:

    ```
    python manage.py runserver
    ```

8. Access the application at [http://localhost:8000](http://localhost:8000) in your web browser.

