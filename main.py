import customtkinter as ctk
import tkinter as tk
import pyperclip
from PIL import Image  # فقط اگر بخواهید از CTkImage برای نمایش لوگو استفاده کنید

# ==================== CONFIGURATION ====================
# مسیرهای پیشنهادی برای آیکون پنجره و لوگوی هدر
# می‌توانید این مسیرها را تغییر دهید یا فایل‌ها را در پوشه assets قرار دهید
WINDOW_ICON_PATH = "assets/icon.ico"       # برای آیکون پنجره (ترجیحاً .ico - در ویندوز بهترین نتیجه)
LOGO_IMAGE_PATH  = "assets/logo.png"       # برای نمایش لوگو در بالای برنامه (png/jpg)
# ======================================================

# Define categories
CATEGORIES = ["Length", "Weight", "Temperature", "Volume"]

# Define units for each category
UNITS = {
    "Length": ["Meter", "Centimeter", "Kilometer", "Millimeter", "Inch", "Foot", "Yard", "Mile"],
    "Weight": ["Kilogram", "Gram", "Milligram", "Ton", "Pound", "Ounce"],
    "Temperature": ["Celsius", "Fahrenheit", "Kelvin"],
    "Volume": ["Liter", "Milliliter", "Cubic Meter", "US Gallon", "US Fluid Ounce", "Cubic Foot"],
}

# Define conversion factors to base unit for non-temperature categories
# For Length: base = Meter
# For Weight: base = Kilogram
# For Volume: base = Liter
FACTORS = {
    "Length": {
        "Meter": 1,
        "Centimeter": 0.01,
        "Kilometer": 1000,
        "Millimeter": 0.001,
        "Inch": 0.0254,
        "Foot": 0.3048,
        "Yard": 0.9144,
        "Mile": 1609.344,
    },
    "Weight": {
        "Kilogram": 1,
        "Gram": 0.001,
        "Milligram": 0.000001,
        "Ton": 1000,
        "Pound": 0.45359237,
        "Ounce": 0.028349523125,
    },
    "Volume": {
        "Liter": 1,
        "Milliliter": 0.001,
        "Cubic Meter": 1000,
        "US Gallon": 3.785411784,
        "US Fluid Ounce": 0.0295735295625,
        "Cubic Foot": 28.316846592,
    },
}

class ThughUnitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ThughUnit")
        self.root.geometry("540x600")
        self.root.resizable(False, False)

        # Set window icon (اگر فایل وجود داشته باشد)
        if WINDOW_ICON_PATH and os.path.exists(WINDOW_ICON_PATH):
            try:
                if WINDOW_ICON_PATH.lower().endswith('.ico'):
                    self.root.iconbitmap(WINDOW_ICON_PATH)
                else:
                    # برای png و سایر فرمت‌ها
                    icon_img = tk.PhotoImage(file=WINDOW_ICON_PATH)
                    self.root.iconphoto(True, icon_img)
            except Exception as e:
                print(f"Warning: Could not load window icon - {e}")

        # Set dark mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Header with logo support
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.pack(pady=(20, 5))

        # نمایش لوگو اگر فایل وجود داشته باشد
        if LOGO_IMAGE_PATH and os.path.exists(LOGO_IMAGE_PATH):
            try:
                logo_pil = Image.open(LOGO_IMAGE_PATH)
                # اندازه پیشنهادی برای لوگو - می‌توانید تغییر دهید
                logo_ctk = ctk.CTkImage(light_image=logo_pil, size=(90, 90))
                self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_ctk, text="")
                self.logo_label.pack(pady=(0, 8))
            except Exception as e:
                print(f"Warning: Could not load logo image - {e}")
                self._add_text_title()
        else:
            self._add_text_title()

        # عنوان متنی اصلی (رنگ نئونی)
        self.title_label = ctk.CTkLabel(self.header_frame, text="ThughUnit",
                                       font=("Arial", 36, "bold"), text_color="#00FFFF")
        self.title_label.pack()

        # زیرعنوان
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Modern Unit Converter",
                                          font=("Arial", 16), text_color="#A9A9A9")
        self.subtitle_label.pack(pady=5)

        # بقیه کد بدون تغییر ...

        # Category selector
        self.category_frame = ctk.CTkFrame(self.root)
        self.category_frame.pack(pady=10)
        self.category_label = ctk.CTkLabel(self.category_frame, text="Category:", font=("Arial", 14))
        self.category_label.pack(side="left", padx=10)
        self.category_combo = ctk.CTkComboBox(self.category_frame, values=CATEGORIES, command=self.update_units, width=200)
        self.category_combo.pack(side="left", padx=10)

        # Input section
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(pady=10)
        self.value_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter number...", width=400, font=("Arial", 14))
        self.value_entry.pack(pady=10)

        self.from_frame = ctk.CTkFrame(self.input_frame)
        self.from_frame.pack(pady=5)
        self.from_label = ctk.CTkLabel(self.from_frame, text="From:", font=("Arial", 14))
        self.from_label.pack(side="left", padx=10)
        self.from_combo = ctk.CTkComboBox(self.from_frame, width=200)
        self.from_combo.pack(side="left", padx=10)

        self.to_frame = ctk.CTkFrame(self.input_frame)
        self.to_frame.pack(pady=5)
        self.to_label = ctk.CTkLabel(self.to_frame, text="To:", font=("Arial", 14))
        self.to_label.pack(side="left", padx=10)
        self.to_combo = ctk.CTkComboBox(self.to_frame, width=200)
        self.to_combo.pack(side="left", padx=10)

        # Convert button
        self.convert_button = ctk.CTkButton(self.root, text="CONVERT →", command=self.convert,
                                           width=200, height=40, font=("Arial", 16, "bold"))
        self.convert_button.pack(pady=20)

        # Result display
        self.result_label = ctk.CTkLabel(self.root, text="", font=("Arial", 24, "bold"), text_color="green")
        self.result_label.pack(pady=10)

        # Copy button
        self.copy_button = ctk.CTkButton(self.root, text="Copy Result", command=self.copy_result,
                                        width=150, height=30)
        self.copy_button.pack(pady=10)

        # Initialize with first category
        self.category_combo.set(CATEGORIES[0])
        self.update_units(None)

    def _add_text_title(self):
        """در صورتی که لوگو لود نشد، فقط عنوان متنی بزرگ نمایش داده شود"""
        temp_label = ctk.CTkLabel(self.header_frame, text="ThughUnit",
                                 font=("Arial", 42, "bold"), text_color="#00FFFF")
        temp_label.pack()

    # بقیه متدها بدون تغییر
    def update_units(self, event):
        """Update From and To comboboxes when category changes."""
        category = self.category_combo.get()
        unit_list = UNITS.get(category, [])

        self.from_combo.set("")
        self.from_combo.configure(values=unit_list)
        if unit_list:
            self.from_combo.set(unit_list[0])

        self.to_combo.set("")
        self.to_combo.configure(values=unit_list)
        if unit_list:
            self.to_combo.set(unit_list[0])

        self.result_label.configure(text="")

    def convert(self):
        try:
            value = float(self.value_entry.get())
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
            if from_unit == "Kelvin" and value < 0:
                self.result_label.configure(text="Kelvin cannot be negative!", text_color="red")
                return

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
                self.result_label.configure(text="Resulting Kelvin cannot be negative!", text_color="red")
                return
        else:
            factor_from = FACTORS[category][from_unit]
            factor_to = FACTORS[category][to_unit]
            result = value * factor_from / factor_to

        result_str = f"{result:.6g} {to_unit}"
        self.result_label.configure(text=result_str, text_color="#00FF00")

    def copy_result(self):
        result_text = self.result_label.cget("text")
        if not result_text:
            return
        try:
            num_str = result_text.split()[0]
            pyperclip.copy(num_str)
            self.copy_button.configure(text="(Copied!)")
            self.root.after(2000, lambda: self.copy_button.configure(text="Copy Result"))
        except:
            pass


if __name__ == "__main__":
    import os  # برای چک کردن وجود فایل‌ها
    root = ctk.CTk()
    app = ThughUnitApp(root)
    root.mainloop()
