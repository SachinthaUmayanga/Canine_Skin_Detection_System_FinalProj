# Canine Skin Detection System
This Flask-based web application is designed for canine skin disease detection. The system allows users to upload images and videos for detection, generate reports, and manage admin functionalities like viewing and filtering upload logs.

## Features

- Upload images and videos for detection.
- Generate and download PDF reports.
- Filter logs based on date range and user.
- Toast notifications for various system actions.
- Admin dashboard for managing upload logs.
- Bootstrap 5.3 for responsive design.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Admin Routes](#admin-routes)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8+
- Virtual Environment (optional but recommended)
- Flask

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/SachinthaUmayanga/Canine_Skin_Detection_System_FinalProj.git

2. Navigate to the project directory:

    cd canine-skin-detection

3. Create and activate a virtual environment (optional):

    - On Windows:

        ```bash
        python -m venv env
        env\Scripts\activate

    - On macOS/Linux:

        ```bash
        python3 -m venv env
        source env/bin/activate

4. Install the project dependencies:

    ```bash
    pip install -r requirements.txt

5. Run the application

    ```bash
    flask run

The application should now be running at http://127.0.0.1:5000/.
