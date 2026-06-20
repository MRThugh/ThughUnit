import os
import customtkinter as ctk
import tkinter as tk
import pyperclip
from PIL import Image

# ==================== CONFIGURATION ====================
# Suggested paths for window icon and header logo
# You can change these paths or place the files in the assets folder
WINDOW_ICON_PATH = "assets/icon.ico"       # For window icon (preferably .ico - best result on Windows)
LOGO_IMAGE_PATH  = "assets/logo.png"       # For displaying logo at the top of the application (png/jpg)
# ======================================================

# Define categories
CATEGORIES = ["Length", "Weight", "Temperature", "Volume", "Speed", "Area", "Pressure", "Time"]

# Define units for each category
UNITS = {
    "Length": ["Meter", "Centimeter", "Kilometer", "Millimeter", "Inch", "Foot", "Yard", "Mile"],
    "Weight": ["Kilogram", "Gram", "Milligram", "Ton", "Pound", "Ounce"],
    "Temperature": ["Celsius", "Fahrenheit", "Kelvin"],
    "Volume": ["Liter", "Milliliter", "Cubic Meter", "US Gallon", "US Fluid Ounce", "Cubic Foot"],
    "Speed": ["Meter per Second", "Kilometer per Hour", "Mile per Hour", "Knot"],
    "Area": ["Square Meter", "Square Kilometer", "Square Mile", "Acre", "Hectare"],
    "Pressure": ["Pascal", "Bar", "PSI", "Atmosphere"],
    "Time": ["Second", "Minute", "Hour", "Day", "Week", "Year"],
}

# Define conversion factors to base unit for non-temperature categories
FACTORS = {
    "Length": {
        "Meter": 1.0,
        "Centimeter": 0.01,
        "Kilometer": 1000.0,
        "Millimeter": 0.001,
        "Inch": 0.0254,
        "Foot": 0.3048,
        "Yard": 0.9144,
        "Mile": 1609.344,
    },
    "Weight": {
        "Kilogram": 1.0,
        "Gram": 0.001,
        "Milligram": 0.000001,
        "Ton": 1000.0,
        "Pound": 0.45359237,
        "Ounce": 0.028349523125,
    },
    "Volume": {
        "Liter": 1.0,
        "Milliliter": 0.001,
        "Cubic Meter": 1000.0,
        "US Gallon": 3.785411784,
        "US Fluid Ounce": 0.0295735295625,
        "Cubic Foot": 28.316846592,
    },
    "Speed": {
        "Meter per Second": 1.0,
        "Kilometer per Hour": 0.2777777777777778,
        "Mile per Hour": 0.44704,
        "Knot": 0.5144444444444445,
    },
    "Area": {
        "Square Meter": 1.0,
        "Square Kilometer": 1000000.0,
        "Square Mile": 2589988.110336,
        "Acre": 4046.8564224,
        "Hectare": 10000.0,
    },
    "Pressure": {
        "Pascal": 1.0,
        "Bar": 100000.0,
        "PSI": 6894.757293168,
        "Atmosphere": 101325.0,
    },
    "Time": {
        "Second": 1.0,
        "Minute": 60.0,
        "Hour": 3600.0,
        "Day": 86400.0,
        "Week": 604800.0,
        "Year": 31536000.0,
    },
}

class ThughUnitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ThughUnit")
        self.root.geometry("540x680")
        self.root.resizable(False, False)

        # Initialize helper variables
        self.debounce_id = None
        self.history_list = []
        
        # Dictionary to store the last selected From/To units for each category
        self.last_units = {}
        for cat in CATEGORIES:
            units_list = UNITS.get(cat, [])
            if units_list:
                self.last_units[cat] = (units_list[0], units_list[0])

        # Set window icon (if the file exists)
        if WINDOW_ICON_PATH and os.path.exists(WINDOW_ICON_PATH):
            try:
                if WINDOW_ICON_PATH.lower().endswith('.ico'):
                    self.root.iconbitmap(WINDOW_ICON_PATH)
                else:
                    icon_img = tk.PhotoImage(file=WINDOW_ICON_PATH)
                    self.root.iconphoto(True, icon_img)
            except Exception as e:
                print(f"Warning: Could not load window icon - {e}")

        # Set dark mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Header with logo support
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5))

        # Core title label definition (No duplicate declarations)
        self.title_label = ctk.CTkLabel(self.header_frame, text="ThughUnit", font=("Arial", 36, "bold"), text_color="#00FFFF")

        # Show logo if file exists
        logo_loaded = False
        if LOGO_IMAGE_PATH and os.path.exists(LOGO_IMAGE_PATH):
            try:
                logo_pil = Image.open(LOGO_IMAGE_PATH)
                logo_ctk = ctk.CTkImage(light_image=logo_pil, size=(80, 80))
                self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_ctk, text="")
                self.logo_label.pack(pady=(0, 5))
                logo_loaded = True
            except Exception as e:
                print(f"Warning: Could not load logo image - {e}")

        # Adjust title font size dynamically and pack
        if logo_loaded:
            self.title_label.configure(font=("Arial", 32, "bold"))
        else:
            self.title_label.configure(font=("Arial", 42, "bold"))
        self.title_label.pack()

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Modern Unit Converter",
                                          font=("Arial", 14), text_color="#A9A9A9")
        self.subtitle_label.pack(pady=2)

        # Category selector (combobox set to readonly)
        self.category_frame = ctk.CTkFrame(self.root)
        self.category_frame.pack(pady=8)
        self.category_label = ctk.CTkLabel(self.category_frame, text="Category:", font=("Arial", 14))
        self.category_label.pack(side="left", padx=10)
        self.category_combo = ctk.CTkComboBox(self.category_frame, values=CATEGORIES, command=self.update_units, width=200, state="readonly")
        self.category_combo.pack(side="left", padx=10)

        # Input section
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(pady=5)
        self.value_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter number...", width=400, font=("Arial", 14))
        self.value_entry.pack(pady=10)
        
        # Bind key release event for debounced real-time conversion
        self.value_entry.bind("<KeyRelease>", self.on_key_release)

        # From Frame
        self.from_frame = ctk.CTkFrame(self.input_frame)
        self.from_frame.pack(pady=3)
        self.from_label = ctk.CTkLabel(self.from_frame, text="From:", font=("Arial", 14))
        self.from_label.pack(side="left", padx=10)
        self.from_combo = ctk.CTkComboBox(self.from_frame, width=200, state="readonly")
        self.from_combo.pack(side="left", padx=10)

        # Modern Swap Button with neon outline
        self.swap_button = ctk.CTkButton(
            self.input_frame, 
            text="⇅ Swap Units", 
            command=self.swap_units,
            width=160, 
            height=30, 
            font=("Arial", 13, "bold"),
            fg_color="transparent",
            border_width=1,
            border_color="#00FFFF",
            text_color="#00FFFF",
            hover_color="#1F3F3F"
        )
        self.swap_button.pack(pady=5)

        # To Frame
        self.to_frame = ctk.CTkFrame(self.input_frame)
        self.to_frame.pack(pady=3)
        self.to_label = ctk.CTkLabel(self.to_frame, text="To:", font=("Arial", 14))
        self.to_label.pack(side="left", padx=10)
        self.to_combo = ctk.CTkComboBox(self.to_frame, width=200, state="readonly")
        self.to_combo.pack(side="left", padx=10)

        # Convert button (acts as Enter to save to history)
        self.convert_button = ctk.CTkButton(self.root, text="CONVERT →", command=lambda: self.convert(force_history=True),
                                           width=200, height=35, font=("Arial", 14, "bold"))
        self.convert_button.pack(pady=10)

        # Result display
        self.result_label = ctk.CTkLabel(self.root, text="", font=("Arial", 22, "bold"), text_color="green")
        self.result_label.pack(pady=5)

        # Copy button
        self.copy_button = ctk.CTkButton(self.root, text="Copy Result", command=self.copy_result,
                                        width=150, height=28)
        self.copy_button.pack(pady=5)

        # History Display Frame
        self.history_frame = ctk.CTkFrame(self.root)
        self.history_frame.pack(pady=(10, 5), fill="x", padx=40)
        
        # History header with Clear button
        self.history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_header.pack(fill="x", padx=10, pady=(5, 0))
        
        self.history_title = ctk.CTkLabel(self.history_header, text="Recent History (Click to reload / Enter to log)", font=("Arial", 11, "bold"))
        self.history_title.pack(side="left")
        
        self.clear_btn = ctk.CTkButton(
            self.history_header, 
            text="Clear", 
            command=self.clear_history,
            width=50, 
            height=18, 
            font=("Arial", 10),
            fg_color="transparent",
            text_color="#FF5555",
            hover_color="#331111"
        )
        self.clear_btn.pack(side="right")
        
        # Refined history text box with clickable cursor feedback
        self.history_box = ctk.CTkTextbox(
            self.history_frame, 
            height=55, 
            font=("Consolas", 11),
            fg_color="#1A1A1A",
            border_color="#2B2B2B",
            border_width=1,
            cursor="hand2"
        )
        self.history_box.pack(fill="x", padx=10, pady=(5, 8))
        self.history_box.configure(state="disabled")
        
        # Bind double-click/click on history items for easy restoration
        self.history_box.bind("<ButtonRelease-1>", self.on_history_click)

        # Keyboard Shortcuts
        self.root.bind("<Return>", lambda event: self.convert(force_history=True))
        self.root.bind("<Control-c>", lambda event: self.copy_result())
        self.root.bind("<Control-C>", lambda event: self.copy_result())

        # Initialize with first category
        self.category_combo.set(CATEGORIES[0])
        self.update_units(None)

    def update_units(self, event=None):
        """Update From and To comboboxes when category changes."""
        category = self.category_combo.get()
        unit_list = UNITS.get(category, [])

        self.from_combo.configure(values=unit_list)
        self.to_combo.configure(values=unit_list)

        # Retrieve and load the last saved unit state for this category
        last_from, last_to = self.last_units.get(category, (unit_list[0], unit_list[0]) if unit_list else ("", ""))
        self.from_combo.set(last_from)
        self.to_combo.set(last_to)

        # Bind the save state event to options changing
        self.from_combo.configure(command=self.on_unit_change)
        self.to_combo.configure(command=self.on_unit_change)

        self.result_label.configure(text="")
        self.trigger_conversion()

    def on_unit_change(self, event=None):
        """Save the currently selected units state and execute calculation with debounce."""
        category = self.category_combo.get()
        self.last_units[category] = (self.from_combo.get(), self.to_combo.get())
        self.trigger_conversion()

    def swap_units(self):
        """Swap the From and To units and trigger conversion."""
        from_val = self.from_combo.get()
        to_val = self.to_combo.get()
        self.from_combo.set(to_val)
        self.to_combo.set(from_val)
        self.on_unit_change()

    def on_key_release(self, event):
        """Handler for keyboard release to trigger debounced calculation."""
        self.trigger_conversion()

    def trigger_conversion(self):
        """Manages debouncing centrally to avoid rendering lags or flickering."""
        if self.debounce_id:
            self.root.after_cancel(self.debounce_id)
        self.debounce_id = self.root.after(200, self.convert)

    def _format_result(self, value):
        """Formats precision floating point numbers safely without scientific notation."""
        # Clean exact integers without scientific notation
        if abs(value - round(value)) < 1e-9:
            return f"{round(value):,}".replace(",", "")
        
        # For standard human-readable scale
        if 1e-6 <= abs(value) < 1e15:
            formatted = f"{value:.8f}"
            if "." in formatted:
                formatted = formatted.rstrip("0").rstrip(".")
            return formatted
        else:
            # Fallback for extreme microscopic or cosmological figures
            return f"{value:.8g}"

    def _convert_temperature(self, value, from_unit, to_unit):
        """A clean helper to manage calculations strictly for Temperature."""
        if from_unit == "Kelvin" and value < 0:
            raise ValueError("Kelvin cannot be negative!")

        if from_unit == to_unit:
            result = value
        elif from_unit == "Celsius":
            if to_unit == "Fahrenheit":
                result = value * 9/5 + 32
            elif to_unit == "Kelvin":
                result = value + 273.15
        elif from_unit == "Fahrenheit":
            celsius = (value - 32) * 5/9
            if to_unit == "Celsius":
                result = celsius
            elif to_unit == "Kelvin":
                result = celsius + 273.15
        elif from_unit == "Kelvin":
            celsius = value - 273.15
            if to_unit == "Celsius":
                result = celsius
            elif to_unit == "Fahrenheit":
                result = celsius * 9/5 + 32

        if to_unit == "Kelvin" and result < 0:
            raise ValueError("Resulting Kelvin cannot be negative!")
            
        return result

    def convert(self, event=None, force_history=False):
        # Reset color to green initially at the start of any calculation
        self.result_label.configure(text_color="#00FF00")
        
        raw_val = self.value_entry.get().strip()
        
        # Keep result clean if empty or incomplete
        if not raw_val:
            self.result_label.configure(text="")
            return
            
        if raw_val in ("-", ".", "-.", "+", "+."):
            self.result_label.configure(text="")
            return

        try:
            value = float(raw_val)
        except ValueError:
            self.result_label.configure(text="Invalid number!", text_color="red")
            return

        category = self.category_combo.get()
        from_unit = self.from_combo.get()
        to_unit = self.to_combo.get()

        if not from_unit or not to_unit:
            self.result_label.configure(text="Select units!", text_color="red")
            return

        if category == "Temperature":
            try:
                result = self._convert_temperature(value, from_unit, to_unit)
            except ValueError as e:
                self.result_label.configure(text=str(e), text_color="red")
                return
        else:
            factor_from = FACTORS[category][from_unit]
            factor_to = FACTORS[category][to_unit]
            result = value * factor_from / factor_to

        formatted_result = self._format_result(result)
        result_str = f"{formatted_result} {to_unit}"
        self.result_label.configure(text=result_str)

        # Log to recent history only on manual validation and successful conversions
        if force_history and not ("!" in self.result_label.cget("text")):
            history_entry = f"{raw_val} {from_unit} → {formatted_result} {to_unit}"
            if not self.history_list or self.history_list[-1] != history_entry:
                self.history_list.append(history_entry)
                if len(self.history_list) > 5:
                    self.history_list.pop(0)
                self.update_history_display()

    def clear_history(self):
        """Clears the history list and refreshes the display."""
        self.history_list.clear()
        self.update_history_display()

    def on_history_click(self, event):
        """Double click/Click callback to parse and restore historic conversions."""
        try:
            line_index = self.history_box.index(f"@{event.x},{event.y}")
            line_number = line_index.split(".")[0]
            clicked_line = self.history_box.get(f"{line_number}.0", f"{line_number}.end").strip()
            
            if not clicked_line or "→" not in clicked_line:
                return
            
            parts = clicked_line.split("→")
            left_part = parts[0].strip().split()
            right_part = parts[1].strip().split()
            
            if len(left_part) >= 2 and len(right_part) >= 2:
                val_str = left_part[0]
                from_unit = " ".join(left_part[1:])
                to_unit = " ".join(right_part[1:])
                
                # Auto detect correct category based on unit presence
                matched_category = None
                for cat, units in UNITS.items():
                    if from_unit in units and to_unit in units:
                        matched_category = cat
                        break
                
                if matched_category:
                    self.category_combo.set(matched_category)
                    self.update_units()
                    
                    self.from_combo.set(from_unit)
                    self.to_combo.set(to_unit)
                    self.last_units[matched_category] = (from_unit, to_unit)
                    
                    self.value_entry.delete(0, "end")
                    self.value_entry.insert(0, val_str)
                    
                    self.trigger_conversion()
        except Exception as e:
            print(f"Error restoring history: {e}")

    def update_history_display(self):
        """Renders history panel items with reversed order (latest on top)."""
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        text_content = "\n".join(reversed(self.history_list))
        self.history_box.insert("1.0", text_content)
        self.history_box.configure(state="disabled")

    def copy_result(self):
        result_text = self.result_label.cget("text")
        # Prevent copying empty states or error messages
        if not result_text or "!" in result_text:
            return
        try:
            num_str = result_text.split()[0]
            pyperclip.copy(num_str)
            self.copy_button.configure(text="(Copied!)")
            self.root.after(2000, lambda: self.copy_button.configure(text="Copy Result"))
        except:
            pass


if __name__ == "__main__":
    root = ctk.CTk()
    app = ThughUnitApp(root)
    root.mainloop()
