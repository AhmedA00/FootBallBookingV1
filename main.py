import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import sqlite3


class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soccer Field Booking")
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height, bg="green")


        self.date_label = tk.Label(root, text="", font=("Helvetica", 14))
        self.date_label.pack(pady=10)

        self.create_booking_table()
        self.update_date_label()

        self.setup_database()
        self.load_bookings()

        self.canvas.pack()

    def setup_database(self):
        self.conn = sqlite3.connect("bookings.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY, field INTEGER, hour TEXT, date TEXT, name TEXT)")
        self.conn.commit()

    def create_booking_table(self):
        self.canvas = tk.Canvas(self.root, width=900, height=600, bg="green")
        self.canvas.pack()

        self.booking_slots = []

        for hour in range(16, 26):  # End at 2 AM (26th hour)
            for field in range(1, 7):


                slot_time = f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'} - {(hour + 1) % 12 or 12}:00 {'AM' if (hour + 1) % 24 < 12 else 'PM'}"
                slot_x = (field - 1) * 150
                slot_y = (hour - 16) * 75
                slot_id = self.canvas.create_rectangle(slot_x, slot_y, slot_x + 150, slot_y + 75, outline="white",
                                                       fill="green")


                self.booking_slots.append(
                    {"id": slot_id, "field": field, "hour": hour, "is_booked": False, "booking_id": None})

                circle_x = slot_x + 75
                self.canvas.create_oval(circle_x - 20, slot_y + 37.5 - 20, circle_x + 20, slot_y + 37.5 + 20,
                                        outline="white")
                self.canvas.create_line(circle_x, slot_y, circle_x, slot_y + 75, fill="white", width=1)  # Vertical line

                goal_rect_width = 20
                self.canvas.create_rectangle(slot_x, slot_y + 27.5, slot_x + goal_rect_width, slot_y + 47.5,
                                             outline="white")
                self.canvas.create_rectangle(slot_x + 150 - goal_rect_width, slot_y + 27.5, slot_x + 150, slot_y + 47.5,
                                             outline="white")

                small_square_size = 20
                self.canvas.create_rectangle(slot_x, slot_y + 27.5, slot_x + small_square_size, slot_y + 47.5,
                                             outline="white")
                self.canvas.create_rectangle(slot_x + 150 - small_square_size, slot_y + 27.5, slot_x + 150,
                                             slot_y + 47.5, outline="white")

                self.canvas.create_text(circle_x, slot_y + 37.5, text=f"Field {field}\n{slot_time}", fill="white",
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
            name = simpledialog.askstring("Booking", "Enter your name:")
            if name:
                self.book_slot(slot, name)
        else:
            if messagebox.askyesno("Cancel Booking", "Do you want to cancel this booking?"):
                self.cancel_booking(slot)
                self.canvas.itemconfig(slot["id"], fill="green")
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

        slot["is_booked"] = False
        slot["booking_id"] = None
        slot["text_id"] = None  # Set the text_id to None to clear the association

    def load_bookings(self):
        self.cursor.execute("SELECT id, field, hour, name FROM bookings WHERE date=?",
                            (datetime.now().strftime("%Y-%m-%d"),))
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
