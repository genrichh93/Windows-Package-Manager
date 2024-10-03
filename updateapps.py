import subprocess
import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Menu

# Function to handle winget command with spaces in package names
def run_winget_command(command, action_desc):
    log_text.config(state="normal")  # Enable the log box to insert text
    log_text.insert(tk.END, f"{action_desc}\n")
    log_text.insert(tk.END, f"Executing command: {' '.join(command)}\n")
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        log_text.insert(tk.END, f"Return code: {result.returncode}\n")

        # Remove control characters from stdout and stderr
        stdout_clean = re.sub(r'[\x00-\x1F\x7F-\x9F]+', '', result.stdout)
        stderr_clean = re.sub(r'[\x00-\x1F\x7F-\x9F]+', '', result.stderr)

        # Remove progress indicators
        progress_pattern = re.compile(r'[\-\|\/\\]+')
        stdout_clean = progress_pattern.sub('', stdout_clean)

        # Remove excessive empty lines
        stdout_clean = re.sub(r'\n\s*\n', '\n', stdout_clean).strip()
        stderr_clean = re.sub(r'\n\s*\n', '\n', stderr_clean).strip()

        log_text.insert(tk.END, f"Standard Output:\n{stdout_clean}\n")
        log_text.insert(tk.END, f"Standard Error:\n{stderr_clean}\n")
    except Exception as e:
        log_text.insert(tk.END, f"Exception occurred: {e}\n")
    log_text.config(state="disabled")  # Disable the log box to prevent editing

# Function to uninstall a selected package
def uninstall_package(package_id):
    command = ['winget', 'uninstall', '--id', package_id]
    if force_var.get():
        command.append('--force')
    # Remove the '-h' flag or replace it with '--silent' if you want silent mode
    # command.append('-h')  # Remove or comment out this line
    # If you want silent mode, uncomment the next line
    # command.append('--silent')
    run_winget_command(command, f"Uninstalling {package_id}...")


# Function to update a selected package
def update_package(package_id):
    command = ['winget', 'upgrade', '--id', package_id]
    if force_var.get():
        command.append('--force')
    if eula_var.get():
        command.append('--accept-package-agreements')
    run_winget_command(command, f"Updating {package_id}...")

# Function to update all packages
def update_all_packages():
    command = ['winget', 'upgrade', '--all']
    if force_var.get():
        command.append('--force')
    if eula_var.get():
        command.append('--accept-package-agreements')
    run_winget_command(command, "Updating all packages...")

# Function to refresh the table with available updates or all packages
def refresh_table(show_all=False):
    global original_data
    update_table.delete(*update_table.get_children())  # Clear the table

    if show_all:
        packages = list_all_packages()  # Get all installed packages
        hide_columns(["Available Version", "Source"])  # Hide columns when showing all packages
        updates_count_label.config(text="Available Updates: N/A")  # No updates shown when showing all packages
    else:
        packages = get_available_updates()  # Get available updates
        show_columns(["Available Version", "Source"])  # Show columns when showing available updates
        updates_count_label.config(text=f"Available Updates: {len(packages)}")  # Update the label to show the number of updates

    original_data = packages  # Store the original unfiltered data

    for package in packages:
        update_table.insert("", "end", values=package)

# Function to hide specific columns
def hide_columns(columns_to_hide):
    for col in columns_to_hide:
        update_table.column(col, width=0, stretch=False)

# Function to show specific columns
def show_columns(columns_to_show):
    for col in columns_to_show:
        update_table.column(col, width=150, stretch=True)  # Set the width back to a reasonable default

# Function to get available updates using winget
def get_available_updates():
    result = subprocess.run(['winget', 'upgrade'], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        return []

    updates = []
    lines = result.stdout.splitlines()

    # Track whether the header has been skipped
    header_skipped = False

    # Ignore first line (header) and parse the remaining lines
    for line in lines:
        if not header_skipped:
            if "Name" in line and "ID" in line and "Version" in line:
                header_skipped = True  # Skip the header row
            continue

        if "----" in line or len(line.strip()) == 0:
            continue  # Skip separator lines and empty lines

        # Check for footer keywords and skip those lines
        if "Mindestens" in line or "Paket" in line or "verfügt" in line:
            continue  # Skip the footer line

        # Split the line based on multiple spaces
        update_info = line.split()
        if len(update_info) >= 5:
            updates.append(update_info[:5])  # Append Name, ID, Version, Available Version, Source

    return updates

# Function to list all installed packages using regular expressions for robust parsing
def list_all_packages():
    result = subprocess.run(['winget', 'list'], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        return []

    packages = []
    lines = result.stdout.splitlines()

    # Define the regex pattern to match the columns: Name, ID, Version, Source
    pattern = re.compile(r"^(.+?)\s{2,}(.+?)\s{2,}(.+?)\s{2,}(.+)$")

    # Track whether the header has been skipped
    header_skipped = False

    # Ignore the first line (header) and parse the remaining lines
    for line in lines:
        if not header_skipped:
            if "Name" in line and "ID" in line and "Version" in line:
                header_skipped = True  # Skip the header row
            continue

        if "----" in line or len(line.strip()) == 0:
            continue  # Skip separator lines and empty lines

        # Use regex to match the line
        match = pattern.match(line)
        if match:
            name = match.group(1).strip()
            package_id = match.group(2).strip()
            version = match.group(3).strip()
            source = match.group(4).strip()
            packages.append([name, package_id, version, source])

    return packages

# Function to filter the main table based on search input
def search_table(event):
    search_term = search_field.get().lower()  # Get the search term and convert to lowercase for case-insensitive comparison

    # Clear current table entries
    update_table.delete(*update_table.get_children())

    # Filter and display the data from original_data (unfiltered data)
    for package in original_data:
        # Check if any column contains the search term
        if any(search_term in str(value).lower() for value in package):
            update_table.insert("", "end", values=package)

# Function to handle right-click menu actions in main window
def on_right_click(event):
    selected_item = update_table.identify_row(event.y)
    if selected_item:
        update_table.selection_set(selected_item)
        item = update_table.item(selected_item)
        package_id = item['values'][1]  # Get the package ID from the selected row
        popup_menu = Menu(window, tearoff=0)
        popup_menu.add_command(label="Update", command=lambda: update_package(package_id))
        popup_menu.add_command(label="Uninstall", command=lambda: uninstall_package(package_id))
        popup_menu.add_command(label="Show Available Versions", command=lambda: show_available_versions(package_id))
        popup_menu.post(event.x_root, event.y_root)

# Function to fetch and display available versions
def show_available_versions(package_id):
    # Create a new window
    versions_window = tk.Toplevel(window)
    versions_window.title(f"Available Versions for {package_id}")

    # Fetch available versions
    versions = get_available_versions(package_id)
    if not versions:
        messagebox.showinfo("No Versions Found", f"No available versions found for {package_id}")
        versions_window.destroy()
        return

    # Create a listbox to display versions
    versions_listbox = tk.Listbox(versions_window, height=15, width=50)
    for version in versions:
        versions_listbox.insert(tk.END, version)
    versions_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Install button
    install_button = tk.Button(versions_window, text="Install Selected Version", command=lambda: install_specific_version(package_id, versions_listbox.get(tk.ACTIVE)))
    install_button.grid(row=1, column=0, padx=10, pady=5)

    # Configure the window to resize properly
    versions_window.grid_rowconfigure(0, weight=1)
    versions_window.grid_columnconfigure(0, weight=1)

# Function to get available versions of a package
def get_available_versions(package_id):
    command = ['winget', 'show', '--id', package_id, '--versions']
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            return []
        
        output = result.stdout
        lines = output.splitlines()
        versions = []
        
        # Flags to control parsing
        parsing_versions = False

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check for the "Version" header
            if line == "Version":
                parsing_versions = True
                continue
            # Skip the line of dashes after the header
            if parsing_versions and all(c == '-' for c in line):
                continue
            if parsing_versions:
                # If we reach another section or the end, stop parsing
                if ':' in line or line.startswith("Gefunden"):
                    break
                versions.append(line)
        return versions
    except Exception as e:
        print(f"Error fetching versions: {e}")
        return []

# Function to install a specific version of a package
def install_specific_version(package_id, version):
    if not version:
        messagebox.showwarning("No Version Selected", "Please select a version to install.")
        return
    command = ['winget', 'install', '--id', package_id, '--version', version]
    if eula_var.get():
        command.append('--accept-package-agreements')
    run_winget_command(command, f"Installing {package_id} Version {version}...")

# Function to handle right-click menu actions in install window
def on_install_right_click(event, install_table):
    selected_item = install_table.identify_row(event.y)
    if selected_item:
        install_table.selection_set(selected_item)
        item = install_table.item(selected_item)
        package_id = item['values'][1]
        popup_menu = Menu(install_window, tearoff=0)
        popup_menu.add_command(label="Install", command=lambda: install_selected_package(install_table))
        popup_menu.add_command(label="Show Available Versions", command=lambda: show_available_versions(package_id))
        popup_menu.post(event.x_root, event.y_root)

# Function to handle sorting for the install window table
def sort_install_table(col, reverse, install_table):
    global install_table_data, columns_install  # Use global data

    col_idx = columns_install.index(col)  # Get the index of the selected column

    # Function to ensure everything is converted to string for safe comparison
    def convert(value):
        try:
            return str(value).lower()  # Convert all values to strings for comparison
        except Exception:
            return ''  # Handle cases where conversion fails

    # Sort the install table data by the selected column
    install_table_data.sort(key=lambda row: convert(row[col_idx]), reverse=reverse)

    # Clear and re-populate the table with sorted data
    install_table.delete(*install_table.get_children())
    for package in install_table_data:
        install_table.insert("", "end", values=package)

    # Toggle sorting order for the next click
    install_table.heading(col, command=lambda: sort_install_table(col, not reverse, install_table))

# Function to open the installation search window
def open_install_window():
    global install_window
    install_window = tk.Toplevel(window)
    install_window.title("Install a Package")

    search_label = tk.Label(install_window, text="Enter package name or ID:")
    search_label.grid(row=0, column=0, padx=5, pady=5)

    search_entry = tk.Entry(install_window)
    search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

    # Bind the Enter key to trigger the search_package function
    search_entry.bind("<Return>", lambda event: search_package(search_entry.get(), install_table))

    search_button = tk.Button(install_window, text="Search", command=lambda: search_package(search_entry.get(), install_table))
    search_button.grid(row=0, column=2, padx=5, pady=5)

    # Scrollbar for the install table
    install_table_frame = tk.Frame(install_window)
    install_table_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

    install_table_scrollbar = tk.Scrollbar(install_table_frame, orient="vertical")
    install_table_scrollbar.grid(row=0, column=1, sticky='ns')

    install_table = ttk.Treeview(install_table_frame, columns=columns_install, show='headings', yscrollcommand=install_table_scrollbar.set)
    install_table_scrollbar.config(command=install_table.yview)

    for col in columns_install:
        install_table.heading(col, text=col, command=lambda _col=col: sort_install_table(_col, False, install_table))
        install_table.column(col, anchor="w")

    install_table.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    # Right-click binding for install_table
    install_table.bind("<Button-3>", lambda event: on_install_right_click(event, install_table))

    install_button = tk.Button(install_window, text="Install Selected", command=lambda: install_selected_package(install_table))
    install_button.grid(row=2, column=1, padx=5, pady=5)

    # Configure grid weights for resizing
    install_window.grid_rowconfigure(1, weight=1)
    install_window.grid_columnconfigure(0, weight=1)
    install_window.grid_columnconfigure(1, weight=1)
    install_window.grid_columnconfigure(2, weight=1)

    install_table_frame.grid_rowconfigure(0, weight=1)
    install_table_frame.grid_columnconfigure(0, weight=1)

# Define the global install_table_data
install_table_data = []

# Define columns globally for the install table
columns_install = ["Name", "ID", "Version", "Match", "Source"]

# Function to search for packages using winget in the install window
def search_package(package_name, install_table):
    result = subprocess.run(['winget', 'search', package_name], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        messagebox.showerror("Error", "Failed to search for packages")
        return

    lines = result.stdout.splitlines()

    # Skip header rows and separator lines
    global install_table_data
    install_table_data = []
    header_skipped = False
    for line in lines:
        if not header_skipped:
            if "Name" in line and "ID" in line and "Version" in line:
                header_skipped = True  # Skip the header row
            continue

        if "----" in line or len(line.strip()) == 0:
            continue  # Skip separator lines and empty lines

        package_info = line.split()
        if len(package_info) >= 5:  # Ensure we have at least 5 columns
            install_table_data.append(package_info[:5])  # Name, ID, Version, Match, Source

    # Clear and add new search results to the table
    install_table.delete(*install_table.get_children())
    for package in install_table_data:
        install_table.insert("", "end", values=package)

# Function to install the selected package
def install_selected_package(search_table):
    selected_item = search_table.selection()
    if selected_item:
        item = search_table.item(selected_item)
        package_id = item['values'][1]
        command = ['winget', 'install', package_id]
        if eula_var.get():
            command.append('--accept-package-agreements')
        run_winget_command(command, f"Installing {package_id}...")

# Function to clear the log
def clear_log():
    log_text.config(state="normal")  # Enable the log box to clear text
    log_text.delete(1.0, tk.END)
    log_text.config(state="disabled")  # Disable it again after clearing

# Function to handle sorting columns
def sort_column(col, reverse):
    global original_data, columns  # Ensure we're using the correct columns reference
    col_idx = columns.index(col)

    # Function to ensure everything is converted to string for safe comparison
    def convert(value):
        try:
            return str(value).lower()  # Convert all values to strings, ensuring case-insensitive comparison
        except Exception:
            return ''  # Handle cases where the value can't be converted

    # Sort the original data
    original_data.sort(key=lambda row: convert(row[col_idx]), reverse=reverse)

    # Clear the table and re-populate with sorted data
    update_table.delete(*update_table.get_children())
    for package in original_data:
        update_table.insert("", "end", values=package)

    # Toggle sorting order for the next click
    update_table.heading(col, command=lambda: sort_column(col, not reverse))

# Function to open settings window
def open_settings_window():
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")

    # Force option
    force_label = tk.Label(settings_window, text="Force:")
    force_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    force_checkbox = tk.Checkbutton(settings_window, variable=force_var)
    force_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Accept EULA option
    eula_label = tk.Label(settings_window, text="Accept EULA:")
    eula_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    eula_checkbox = tk.Checkbutton(settings_window, variable=eula_var)
    eula_checkbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Close button
    close_button = tk.Button(settings_window, text="Close", command=settings_window.destroy)
    close_button.grid(row=2, column=0, columnspan=2, pady=10)

# GUI Main Window Setup
window = tk.Tk()
window.title("Windows Package Manager")

# Now we can define the BooleanVars after initializing the root window
force_var = tk.BooleanVar(value=True)
eula_var = tk.BooleanVar(value=True)

# Define columns for the main table
columns = ["Name", "ID", "Version", "Available Version", "Source"]

# Scrollable frame for main table
main_table_frame = tk.Frame(window)
main_table_frame.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

# Scrollbar for main table
main_table_scrollbar = tk.Scrollbar(main_table_frame, orient="vertical")
main_table_scrollbar.grid(row=0, column=1, sticky='ns')

# Treeview with scrollbar
update_table = ttk.Treeview(main_table_frame, columns=columns, show='headings', yscrollcommand=main_table_scrollbar.set)
main_table_scrollbar.config(command=update_table.yview)

for col in columns:
    update_table.heading(col, text=col, anchor="w", command=lambda _col=col: sort_column(_col, False))
    update_table.column(col, anchor="w")

update_table.grid(row=0, column=0, sticky="nsew")

# Right-click binding for update_table
update_table.bind("<Button-3>", on_right_click)

# Configure grid weight for table resizing
main_table_frame.grid_columnconfigure(0, weight=1)
main_table_frame.grid_rowconfigure(0, weight=1)

# Search field and label
search_label = tk.Label(window, text="Search:")
search_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")

search_field = tk.Entry(window)
search_field.grid(row=0, column=1, padx=5, pady=10, sticky="we")

# Bind the search function to the search field
search_field.bind("<KeyRelease>", search_table)

# Install New Package button
install_button = tk.Button(window, text="Install New Package", command=open_install_window)
install_button.grid(row=0, column=2, padx=(5, 5), pady=10, sticky="we")

# Settings button
settings_button = tk.Button(window, text="Settings", command=open_settings_window)
settings_button.grid(row=0, column=3, padx=(5, 5), pady=10, sticky="we")

# Remove the Log button since the log is now integrated
# Alternatively, add a Toggle Log button (code provided below)

# Configure grid weight for main window resizing
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(1, weight=1)

# Create a LabelFrame to group the Update All Packages button and checkboxes
frame = tk.LabelFrame(window, text="Package Actions", bg="lightgrey", padx=5, pady=5)
frame.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky="we")

# Update all button
update_all_button = tk.Button(frame, text="Update All Packages", command=update_all_packages)
update_all_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

# Show all packages checkbox
show_all_var = tk.BooleanVar()
show_all_checkbox = tk.Checkbutton(frame, text="Show all packages", variable=show_all_var, command=lambda: refresh_table(show_all_var.get()), bg="lightgrey")
show_all_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Refresh button
refresh_button = tk.Button(window, text="Refresh", command=lambda: refresh_table(show_all_var.get()))
refresh_button.grid(row=3, column=0, padx=5, pady=10, sticky="w")

# Available updates count label (right aligned)
updates_count_label = tk.Label(window, text="Available Updates: 0")
updates_count_label.grid(row=3, column=4, padx=10, pady=10, sticky="e")

# Log frame at the bottom
log_frame = tk.Frame(window)
log_frame.grid(row=4, column=0, columnspan=5, padx=10, pady=5, sticky="nsew")

# Log label
log_label = tk.Label(log_frame, text="Log Output:")
log_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

# Create the scrolled text widget for the log
log_text = scrolledtext.ScrolledText(log_frame, width=80, height=10)
log_text.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")
log_text.config(state="disabled")

# Clear log button
clear_log_button = tk.Button(log_frame, text="Clear Log", command=clear_log)
clear_log_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

# Configure grid weights to allow resizing
window.grid_rowconfigure(4, weight=1)  # Allow the log frame to expand vertically
window.grid_columnconfigure(0, weight=1)

log_frame.grid_columnconfigure(0, weight=1)
log_frame.grid_rowconfigure(1, weight=1)

# Optionally, add a Toggle Log button
def toggle_log():
    if log_frame.winfo_viewable():
        log_frame.grid_remove()
    else:
        log_frame.grid()
        
toggle_log_button = tk.Button(window, text="Toggle Log", command=toggle_log)
toggle_log_button.grid(row=3, column=1, padx=5, pady=10, sticky="w")

# Start application
refresh_table()
window.mainloop()
