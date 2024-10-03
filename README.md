# Windows-Package-Manager
Windows Package Manager (Tkinter-based GUI)

This Python-based package manager is built to simplify the management of packages on Windows systems, leveraging winget as the underlying engine. With an intuitive GUI designed using Tkinter, the application provides users with tools to update, install, and uninstall packages easily. It includes interactive tables, search capabilities, and logging features, making it a comprehensive solution for Windows package management.

## Features
### Package Update Management:

- View available updates for installed packages.
- Update individual packages or update all at once.
- Force updates or accept EULA when necessary.

### Installation Features:

- Search for new packages to install via winget.
- Install specific versions of packages.
- Right-click context menu for easy interaction with package options.

### Uninstall Packages:

- Uninstall installed packages with ease.
- Use the --force flag to remove packages forcefully when needed.

### Search and Filter:

- Real-time search filtering for packages based on name, ID, or version.
- Toggle between showing only updatable packages or all installed packages.

### Settings Window:

- Configure options such as forced installations and accepting EULAs.

### Interactive Tables:

- Sortable tables for updates and installations.
- Right-click functionality for quick actions (update, uninstall, show versions).

### Logging and Monitoring:

- Logging of winget commands and output.
- Integrated log viewer with options to clear or toggle visibility.

## How It Works
- Winget Integration: The app uses subprocess to run winget commands and parses their output using regex and other text manipulation techniques.
- Package Management: Packages are listed in a table, providing detailed information on their name, version, and availability.
- Updates: Users can trigger updates, uninstallations, or installations directly from the interface, with clear feedback through the integrated log.
- Customizable Settings: Options such as forced updates or automatic EULA acceptance are configurable via a settings window.

## Getting Started
Clone the repository:

bash
Code kopieren
`git clone <https://github.com/genrichh93/Windows-Package-Manager/tree/main>`
cd <repository>
Install required dependencies:


`pip install tkinter`
Run the application:


`python app.py`


## Requirements
Python 3.x
Tkinter (comes pre-installed with most Python installations)
winget installed and accessible on the system

## Future Enhancements
- More Filters: Enhance filtering capabilities to allow for more detailed search (e.g., by source).
- Package Details View: Provide more detailed information about packages, including descriptions, release dates, etc.


Feel free to open issues for bug reports, feature requests, or general questions!
