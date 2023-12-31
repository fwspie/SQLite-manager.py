import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class DatabaseManager:
    def __init__(self, master):
        self.master = master
        self.master.title("SQLite Database Manager")

        # Database connection
        self.connection = None
        self.cursor = None
        self.tables = []  # Store the list of tables

        # Dark mode flag
        self.dark_mode = tk.BooleanVar(value=False)

        # Selected table
        self.selected_table = tk.StringVar()

        # Settings window
        self.settings_window = None
        self.settings_window_open = False  # Flag to track if the settings window is open

        # GUI components
        self.create_navigation_bar()

        # Create a frame to contain the result box and scrollbars
        self.result_frame = tk.Frame(master)
        self.result_frame.pack(expand=True, fill=tk.BOTH)

        # Add vertical scrollbar
        self.y_scrollbar = tk.Scrollbar(self.result_frame, orient=tk.VERTICAL)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add horizontal scrollbar
        self.x_scrollbar = tk.Scrollbar(self.result_frame, orient=tk.HORIZONTAL)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Add text widget with vertical and horizontal scrollbars
        self.result_text = tk.Text(self.result_frame, wrap=tk.NONE,
                                   yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)
        self.result_text.pack(expand=True, fill=tk.BOTH)

        # Configure vertical scrollbar
        self.y_scrollbar.config(command=self.result_text.yview)

        # Configure horizontal scrollbar
        self.x_scrollbar.config(command=self.result_text.xview)

        # Bind window resize event
        self.master.bind("<Configure>", self.on_window_resize)

    def create_navigation_bar(self):
        navigation_bar = tk.Frame(self.master, bg="lightgray", pady=5)
        navigation_bar.pack(side=tk.TOP, fill=tk.X)

        # Database button
        db_button = tk.Button(navigation_bar, text="Select Database", command=self.select_database)
        db_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Table button
        table_button = tk.Button(navigation_bar, text="Manage Tables", command=self.manage_tables)
        table_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Settings button
        settings_button = tk.Button(navigation_bar, text="Settings", command=self.open_settings)
        settings_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # Select Table dropdown
        table_label = tk.Label(navigation_bar, text="Select Table:")
        table_label.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        self.table_combobox = ttk.Combobox(navigation_bar, textvariable=self.selected_table, state="readonly")
        self.table_combobox.grid(row=0, column=4, padx=10, pady=5, sticky="ew")

        # Select Table button
        select_table_button = tk.Button(navigation_bar, text="Select Table", command=self.select_table)
        select_table_button.grid(row=0, column=5, padx=10, pady=5, sticky="ew")

        # Read Table button
        read_button = tk.Button(navigation_bar, text="Read Table", command=self.read_table)
        read_button.grid(row=0, column=6, padx=10, pady=5, sticky="ew")

        # Configure row and column weights
        navigation_bar.grid_rowconfigure(0, weight=1)
        for col in range(7):  # Assuming there are 7 columns
            navigation_bar.grid_columnconfigure(col, weight=1)

    def select_database(self):
        file_path = filedialog.askopenfilename(title="Select SQLite Database", filetypes=[("SQLite Database", "*.db")])

        if file_path:
            try:
                self.connection = sqlite3.connect(file_path)
                self.cursor = self.connection.cursor()

                # Get the list of tables
                self.refresh_tables()

                messagebox.showinfo("Success", f"Connected to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Unable to connect to the database:\n{str(e)}")

    def refresh_tables(self):
        # Get the list of tables
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in self.cursor.fetchall()]
        self.tables = tables

        # Update the Combobox values
        self.table_combobox["values"] = tables

    def manage_tables(self):
        if not self.connection:
            messagebox.showwarning("Warning", "Please select a database first.")
            return

        # Fetch the list of tables
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in self.cursor.fetchall()]

        # Create a new window to manage tables
        manage_tables_window = tk.Toplevel(self.master)
        manage_tables_window.title("Manage Tables")

        # Create a Listbox to display tables
        tables_listbox = tk.Listbox(manage_tables_window, selectmode=tk.SINGLE)
        for table in tables:
            tables_listbox.insert(tk.END, table)
        tables_listbox.pack(padx=10, pady=10)

        # View Table Schema button
        view_schema_button = tk.Button(manage_tables_window, text="View Table Schema", command=lambda: self.view_table_schema(tables_listbox.get(tk.ACTIVE)))
        view_schema_button.pack(pady=5)

        # Delete Table button
        delete_table_button = tk.Button(manage_tables_window, text="Delete Table", command=lambda: self.delete_table(tables_listbox.get(tk.ACTIVE)))
        delete_table_button.pack(pady=5)

    def view_table_schema(self, table_name):
        if not table_name:
            messagebox.showwarning("Warning", "Please select a table.")
            return

        # Fetch the table schema
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        schema = self.cursor.fetchall()

        # Display the schema in the result box
        result_text = self.format_table(schema)
        self.result_text.delete("1.0", tk.END)  # Clear previous results
        self.result_text.insert(tk.END, result_text)

    def delete_table(self, table_name):
        if not table_name:
            messagebox.showwarning("Warning", "Please select a table.")
            return

        confirmation = messagebox.askyesno("Delete Table", f"Are you sure you want to delete the table: {table_name}?")
        if confirmation:
            try:
                # Execute the SQL query to delete the table
                self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                self.connection.commit()

                messagebox.showinfo("Delete Table", f"Table {table_name} deleted successfully.")

                # Refresh the list of tables
                self.refresh_tables()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting table {table_name}:\n{str(e)}")

    def select_table(self):
        if self.selected_table.get() in self.tables:
            messagebox.showinfo("Table Selection", f"Selected table: {self.selected_table.get()}")
        else:
            messagebox.showwarning("Table Selection", "Please select a valid table.")

    def read_table(self):
        if not self.selected_table.get():
            messagebox.showwarning("Warning", "Please select a table first.")
            return

        query = f"SELECT * FROM {self.selected_table.get()};"
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        if data:
            result_text = self.format_table(data)
            self.result_text.delete("1.0", tk.END)  # Clear previous results
            self.result_text.insert(tk.END, result_text)
        else:
            messagebox.showinfo("Read Table", f"No data found in table: {self.selected_table.get()}")

    def format_table(self, data):
        # Calculate maximum column widths
        headers = [desc[0] for desc in self.cursor.description]
        max_widths = [max(len(str(row[i])) for row in data + [headers]) for i in range(len(headers))]

        # Format data as a table
        separator_line = "+".join(["-" * (width + 2) for width in max_widths])
        header_line = "|".join([f" {headers[i].ljust(max_widths[i])} " for i in range(len(headers))])

        rows = [separator_line, header_line, separator_line]

        for row in data:
            row_line = "|".join([f" {str(row[i]).ljust(max_widths[i])} " for i in range(len(headers))])
            rows.extend([row_line, separator_line])

        return "\n".join(rows)

    def on_window_resize(self, event):
        # Update the result box and scrollbars on window resize
        self.result_frame.pack_configure(expand=True, fill=tk.BOTH)

    def open_settings(self):
        global settings_window_instance

        if not self.settings_window_open:
            self.settings_window = tk.Toplevel(self.master)
            self.settings_window.title("Settings")

            # Dark mode toggle button
            dark_mode_label = tk.Label(self.settings_window, text="Dark Mode:")
            dark_mode_label.pack()

            dark_mode_toggle = tk.Checkbutton(self.settings_window, text="Enable Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
            dark_mode_toggle.pack()

            # Bind window focus event
            self.settings_window.protocol("WM_DELETE_WINDOW", self.on_settings_close)
            self.settings_window_open = True
            self.settings_window.focus_set()  # Set focus to the settings window
            self.settings_window.focus_force()  # Force focus

            settings_window_instance = self.settings_window  # Store the instance globally



    def toggle_dark_mode(self):
        # Toggle dark mode
        if self.dark_mode.get():
            self.master.configure(bg="black")
            self.result_text.configure(bg="black", fg="white")
        else:
            self.master.configure(bg="white")
            self.result_text.configure(bg="white", fg="black")

    def on_settings_close(self):
        # Update the settings window state when closed
        self.settings_window_open = False
        self.settings_window.destroy()  # Destroy the settings window


if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager(root)
    root.mainloop()

