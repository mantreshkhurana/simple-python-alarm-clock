import threading
import tkinter as tk
from tkinter import messagebox
import time
import math
from pygame import mixer

width = 200
height = 200

mixer.init()


class AlarmClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Alarm Clock")
        self.geometry("350x620")
        self.resizable(False, False)
        self.iconphoto(False, tk.PhotoImage(file="assets/icon.png"))
        self.alarms = []
        self.play_alarm = True

        analog_frame = tk.Frame(self)
        analog_frame.pack(pady=10)

        self.digital_clock = tk.Label(self, font=("Helvetica", 24))
        self.digital_clock.pack(pady=10)

        self.analog_canvas = tk.Canvas(analog_frame, width=width, height=height)
        self.analog_canvas.pack()

        input_frame = tk.Frame(self)
        input_frame.pack()

        self.time_var = tk.StringVar(value="12:00")
        self.time_picker = tk.Entry(
            input_frame, textvariable=self.time_var, font=("Helvetica", 14), width=5
        )
        self.time_picker.grid(row=0, column=0, padx=10)

        self.am_pm_var = tk.StringVar(value="AM")
        self.am_pm_menu = tk.OptionMenu(input_frame, self.am_pm_var, "AM", "PM")
        self.am_pm_menu.grid(row=0, column=1, padx=10)

        self.format_var = tk.StringVar(value="12-Hour Format")
        self.format_menu = tk.OptionMenu(
            input_frame, self.format_var, "12-Hour Format", "24-Hour Format"
        )
        self.format_menu.grid(row=0, column=2, padx=10)

        self.set_alarm_button = tk.Button(
            self, text="Set Alarm", command=self.set_alarm
        )
        self.set_alarm_button.pack(pady=10)

        self.alarms_label = tk.Label(self, text="Alarms:")
        self.alarms_label.pack()

        self.alarms_listbox = tk.Listbox(self, selectmode=tk.SINGLE, exportselection=0)
        self.alarms_listbox.pack()

        self.delete_alarm_button = tk.Button(
            self, text="Delete Alarm", command=self.delete_alarm, width=15
        )
        self.delete_alarm_button.pack(pady=10)

        self.update_clock()
        self.update_alarms()
        self.update_analog_clock()

    def update_clock(self):
        current_time = time.strftime(
            "%I:%M:%S %p" if self.format_var.get() == "12-Hour Format" else "%H:%M:%S"
        )
        self.digital_clock.config(text=current_time)
        self.after(1000, self.update_clock)

    def set_alarm(self):
        alarm_time = self.time_var.get()
        am_pm = self.am_pm_var.get()

        try:
            alarm_time = (
                time.strptime(alarm_time, "%I:%M")
                if self.format_var.get() == "12-Hour Format"
                else time.strptime(alarm_time, "%H:%M")
            )
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid time (HH:MM).")
            return

        if self.format_var.get() == "12-Hour Format":
            if am_pm == "PM":
                alarm_time = time.struct_time(
                    (
                        alarm_time.tm_year,
                        alarm_time.tm_mon,
                        alarm_time.tm_mday,
                        alarm_time.tm_hour + 12,
                        alarm_time.tm_min,
                        0,
                        0,
                        0,
                        -1,
                    )
                )
            else:
                alarm_time = time.struct_time(
                    (
                        alarm_time.tm_year,
                        alarm_time.tm_mon,
                        alarm_time.tm_mday,
                        alarm_time.tm_hour,
                        alarm_time.tm_min,
                        0,
                        0,
                        0,
                        -1,
                    )
                )

        self.alarms.append(alarm_time)
        self.alarms_listbox.insert(
            tk.END,
            time.strftime(
                "%I:%M %p" if self.format_var.get() == "12-Hour Format" else "%H:%M",
                alarm_time,
            ),
        )
        self.time_var.set("12:00")

    def delete_alarm(self):
        selected_index = self.alarms_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.alarms_listbox.delete(index)
            del self.alarms[index]

    def update_alarms(self):
        current_time = time.localtime()
        for i, alarm_time in enumerate(self.alarms):
            if current_time >= alarm_time:
                self.alarms_listbox.delete(i)
                del self.alarms[i]

                if self.play_alarm:
                    alarm_thread = threading.Thread(target=self.play_alarm_sound)
                    alarm_thread.start()

                    response = messagebox.askquestion(
                        "Wake Up Now", "Time to wake up! Repeat the alarm in 5 minutes?"
                    )
                    if response == "yes":
                        new_alarm = time.mktime(time.localtime()) + 5 * 60
                        self.alarms.append(time.localtime(new_alarm))
                        self.alarms_listbox.insert(
                            tk.END,
                            time.strftime(
                                "%I:%M %p"
                                if self.format_var.get() == "12-Hour Format"
                                else "%H:%M",
                                time.localtime(new_alarm),
                            ),
                        )
                    else:
                        mixer.music.stop()
                        break
                else:
                    self.play_alarm = True

        self.after(60000, self.update_alarms)

    def play_alarm_sound(self):
        if self.play_alarm:
            mixer.music.load("assets/alarm.mp3")
            mixer.music.set_volume(1.0)
            mixer.music.play()

    def update_analog_clock(self):
        canvas = self.analog_canvas
        canvas.delete("all")
        now = time.localtime()
        hour = now.tm_hour % 12
        minute = now.tm_min
        second = now.tm_sec

        canvas.create_oval(2, 2, width, height, outline="black", width=2)

        for i in range(12):
            angle = i * math.pi / 6 - math.pi / 2
            x = width / 2 + 0.7 * width / 2 * math.cos(angle)
            y = height / 2 + 0.7 * width / 2 * math.sin(angle)
            if i == 0:
                canvas.create_text(x, y - 10, text=str(i + 12), font=("Helvetica", 12))
            else:
                canvas.create_text(x, y, text=str(i), font=("Helvetica", 12))

        for i in range(60):
            angle = i * math.pi / 30 - math.pi / 2
            x1 = width / 2 + 0.8 * width / 2 * math.cos(angle)
            y1 = height / 2 + 0.8 * height / 2 * math.sin(angle)
            x2 = width / 2 + 0.9 * width / 2 * math.cos(angle)
            y2 = height / 2 + 0.9 * height / 2 * math.sin(angle)
            if i % 5 == 0:
                canvas.create_line(x1, y1, x2, y2, fill="black", width=3)
            else:
                canvas.create_line(x1, y1, x2, y2, fill="black", width=1)

        hour_angle = (hour + minute / 60) * math.pi / 6 - math.pi / 2
        hour_x = width / 2 + 0.5 * width / 2 * math.cos(hour_angle)
        hour_y = height / 2 + 0.5 * height / 2 * math.sin(hour_angle)
        canvas.create_line(width / 2, height / 2, hour_x, hour_y, fill="black", width=6)

        minute_angle = (minute + second / 60) * math.pi / 30 - math.pi / 2
        minute_x = width / 2 + 0.7 * width / 2 * math.cos(minute_angle)
        minute_y = height / 2 + 0.7 * height / 2 * math.sin(minute_angle)
        canvas.create_line(
            width / 2, height / 2, minute_x, minute_y, fill="black", width=4
        )

        second_angle = second * math.pi / 30 - math.pi / 2
        second_x = width / 2 + 0.6 * width / 2 * math.cos(second_angle)
        second_y = height / 2 + 0.6 * width / 2 * math.sin(second_angle)
        canvas.create_line(
            width / 2, height / 2, second_x, second_y, fill="red", width=2
        )

        canvas.after(1000, self.update_analog_clock)


if __name__ == "__main__":
    alarm_clock = AlarmClockApp()
    alarm_clock.mainloop()
