import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import sqlite3
from PIL import Image, ImageTk



class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soccer Field Booking")

        #By changing it to true it will display on fullscreen, Having it turned to False will add Maximize and Minimize
        self.root.attributes('-fullscreen', False)  # Start the app in fullscreen mode

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.canvas = tk.Canvas(self.root, bg="green")

        # Create a frame for the contact information
        contact_frame = tk.Frame(root, bg="black")
        contact_frame.pack(side="bottom", anchor="n", padx=0.5, pady=0.5)  # Anchored to the bottom left with padding

        # Create a label for the contact information
        contact_label = tk.Label(contact_frame, text="For Reservations: +971505531330", font=("Helvetica", 14),
                                 fg="white", bg="black")
        contact_label.pack()

        # Load your logo image
        logo_image = Image.open("Asset/GreenZone.png")  # Replace with the path to your logo image
        logo_image = logo_image.resize((240, 98))  # Adjust the size as needed
        self.logo_photo = ImageTk.PhotoImage(logo_image)

        # Create a frame for the logo
        self.logo_frame = tk.Frame(self.root, bg="black")  # Adjust the background color as needed
        self.logo_frame.pack(side="bottom", fill="x")  # Place it at the bottom

        # Create a label to display the logo within the frame
        self.logo_label = tk.Label(self.logo_frame, image=self.logo_photo,
                                   bg="black")  # Match the frame's background color
        self.logo_label.pack()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack()

        self.date_label = tk.Label(self.main_frame, text="", font=("Helvetica", 14), pady=10)
        self.date_label.pack()

        self.booking_slots = []  # Initialize booking_slots here

        self.create_booking_table()
        self.update_date_label()

        self.setup_database()  # Initialize the database
        self.load_bookings()  # Load existing bookings from the database

        self.canvas.pack(fill=tk.BOTH, expand=True)  # Fill the entire window with the canvas
    def setup_database(self):
        self.conn = sqlite3.connect("bookings.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY, field INTEGER, hour TEXT, date TEXT, name TEXT)")
        self.conn.commit()


    def create_booking_table(self):
        canvas_width = self.root.winfo_screenwidth()
        canvas_height = self.root.winfo_screenheight()
        self.canvas.config(width=canvas_width, height=canvas_height, bg="dark green")

        start_hour = 16
        end_hour = 26  # 1-2 AM
        num_fields = 6  # Number of fields

        slot_width = canvas_width // num_fields
        slot_height = (canvas_height - 100) // (end_hour - start_hour + 1)  # +1 to include the last hour

        self.booking_slots = []

        for hour in range(start_hour, end_hour + 1):
            for field in range(1, num_fields + 1):
                slot_time = f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'} - {(hour + 1) % 12 or 12}:00 {'AM' if (hour + 1) % 24 < 12 else 'PM'}"
                slot_x = (field - 1) * slot_width
                slot_y = (hour - start_hour) * slot_height
                slot_id = self.canvas.create_rectangle(slot_x, slot_y, slot_x + slot_width, slot_y + slot_height,
                                                       outline="white", fill="dark green")
                self.booking_slots.append(
                    {"id": slot_id, "field": field, "hour": hour, "is_booked": False, "booking_id": None})

                # Add a vertical line to separate fields
                if field < num_fields+1:
                    self.canvas.create_line(slot_x + slot_width, slot_y, slot_x + slot_width, slot_y + slot_height,
                                            fill="black", width=10)

                    # Add a horizontal line to separate rows
                    if hour < end_hour +1:
                        self.canvas.create_line(slot_x, slot_y + slot_height, slot_x + slot_width, slot_y + slot_height,
                                                fill="black", width=10)



                circle_x = slot_x + slot_width // 2
                self.canvas.create_oval(circle_x - 20, slot_y + slot_height // 2 - 20, circle_x + 20,
                                        slot_y + slot_height // 2 + 20, outline="white")
                self.canvas.create_line(circle_x, slot_y, circle_x, slot_y + slot_height, fill="white",
                                        width=1)  # Vertical line

                goal_rect_width = 24
                goal_area_height = slot_height * 0.85  # Adjust this value to make the goal area taller

                self.canvas.create_rectangle(slot_x, slot_y + goal_area_height, slot_x + goal_rect_width,
                                             slot_y + slot_height - goal_area_height, outline="white")
                self.canvas.create_rectangle(slot_x + slot_width - goal_rect_width, slot_y + goal_area_height,
                                             slot_x + slot_width, slot_y + slot_height - goal_area_height,
                                             outline="white")

                small_square_size = 15
                self.canvas.create_rectangle(slot_x, slot_y + slot_height * 0.38, slot_x + small_square_size,
                                             slot_y + slot_height * 0.58, outline="white")
                self.canvas.create_rectangle(slot_x + slot_width - small_square_size, slot_y + slot_height * 0.38,
                                             slot_x + slot_width, slot_y + slot_height * 0.58, outline="white")

                self.canvas.create_text(circle_x, slot_y + slot_height // 2, text=f"Field {field}\n{slot_time}",
                                        fill="white",
                                        font=("Helvetica", 9))

        self.canvas.bind("<Button-1>", self.canvas_clicked)

    def update_date_label(self):
        now = datetime.now()
        self.date_label.config(text=now.strftime("%A, %B %d, %Y"))
        self.check_reset_time(now)

    def canvas_clicked(self, event):
        x, y = event.x, event.y
        for slot in self.booking_slots:
            slot_coords = self.canvas.coords(slot["id"])
            if slot_coords[0] <= x <= slot_coords[2] and slot_coords[1] <= y <= slot_coords[3]:
                self.slot_clicked(slot)
                break

    def slot_clicked(self, slot):
        if not slot["is_booked"]:
            name = simpledialog.askstring("Booking", "Enter Booking Name:")
            if name:
                self.book_slot(slot, name)
        else:
            if messagebox.askyesno("Cancel Booking", "Do you want to cancel this booking?"):
                self.cancel_booking(slot)
                self.canvas.itemconfig(slot["id"], fill="dark green")
                slot["is_booked"] = False

    def book_slot(self, slot, name):
        slot["is_booked"] = True
        self.canvas.itemconfig(slot["id"], fill="red")

        x, y = self.canvas.coords(slot["id"])[0] + 75, self.canvas.coords(slot["id"])[1] + 37.5
        text_id = self.canvas.create_text(x, y, text=name, fill="Black", font=("Berlin Sans FB ", 13, "bold"))
        slot["booking_id"] = self.cursor.lastrowid

        # Assign the text item to the slot using a unique tag
        self.canvas.addtag_withtag("name_tag_" + str(slot["id"]), text_id)

        self.canvas.update()  # Update the canvas immediately

        current_time = datetime.now()
        date = current_time.strftime("%Y-%m-%d")
        self.cursor.execute("INSERT INTO bookings (field, hour, date, name) VALUES (?, ?, ?, ?)",
                            (slot["field"], slot["hour"], date, name))
        self.conn.commit()

    def cancel_booking(self, slot):
        booking_id = slot["booking_id"]
        self.cursor.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
        self.conn.commit()

        if slot.get("text_id"):
            self.canvas.delete(slot["text_id"])  # Delete the associated booking name text item
            self.canvas.dtag("name_tag_" + str(slot["id"]), slot["text_id"])  # Remove the name tag
            slot["text_id"] = None  # Clear the association

        slot["is_booked"] = False
        slot["booking_id"] = None

        # Add this line to explicitly refresh the canvas after canceling the booking
        self.canvas.update()

    def load_bookings(self):
        # Function to load existing bookings from the database
        self.cursor.execute("SELECT id, field, hour, name FROM bookings")
        booked_slots = self.cursor.fetchall()
        for booking_id, field, hour, name in booked_slots:
            slot = self.find_slot_by_field_hour(field, hour)
            if slot:
                slot["is_booked"] = True
                self.canvas.itemconfig(slot["id"], fill="red")
                slot["booking_id"] = booking_id

                x, y = self.canvas.coords(slot["id"])[0] + 75, self.canvas.coords(slot["id"])[1] + 37.5
                text_id = self.canvas.create_text(x, y, text=name, fill="black", font=("Berlin Sans FB ", 13, "bold"))
                slot["text_id"] = text_id

    def find_slot_by_field_hour(self, field, hour):
        for slot in self.booking_slots:
            if slot["field"] == field and slot["hour"] == hour:
                return slot
        return None

    def check_reset_time(self, now):
        if now.hour == 2 and now.minute == 0:
            self.reset_day()

    def reset_day(self):
        self.cursor.execute("DELETE FROM bookings WHERE date=?", (datetime.now().strftime("%Y-%m-%d"),))
        self.conn.commit()
        for slot in self.booking_slots:
            if slot["is_booked"]:
                self.canvas.delete(slot["text_id"])  # Delete the associated booking name text item
            slot["is_booked"] = False
            slot["booking_id"] = None


if __name__ == "__main__":
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()
