import customtkinter as ctk
import random
import keyboard
import threading
import mouse
import ctypes
from time import sleep


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title('Simple Auto Clicker')
        self.geometry(
            f"450x200"
            f"+{int(self.winfo_screenwidth() / 2 - 450 / 2)}"
            f"+{int(self.winfo_screenheight() / 2 - 250 / 2)}"
        )
        self.resizable(False, False)

        self.stop_main_thread: bool = False

        self.interval_ms = ctk.StringVar(value='100')
        self.interval_s = ctk.StringVar(value='0')
        self.interval_min = ctk.StringVar(value='0')
        self.interval_hr = ctk.StringVar(value='0')

        self.interval_ms.trace('w', lambda x, y, z: self.validate(self.interval_ms))
        self.interval_s.trace('w', lambda x, y, z: self.validate(self.interval_s))
        self.interval_min.trace('w', lambda x, y, z: self.validate(self.interval_min))
        self.interval_hr.trace('w', lambda x, y, z: self.validate(self.interval_hr))

        self.button = ctk.StringVar(value='Left')
        self.hotkey = ctk.StringVar(value='f8')

        self.super_mode = ctk.BooleanVar(value=False)

        # Advanced options
        self.random_time_offset_enabled = ctk.BooleanVar(value=False)
        self.random_time_offset = ctk.StringVar(value='0')

        self.random_mouse_offset_enabled = ctk.BooleanVar(value=False)
        self.random_mouse_offset_x = ctk.StringVar(value='0')
        self.random_mouse_offset_y = ctk.StringVar(value='0')

        self.click_type = ctk.StringVar(value='Single')
        self.hold_duration = ctk.StringVar(value='0')

        self.repeat_option = ctk.StringVar(value='Toggle')
        self.repeat_value = ctk.StringVar(value='0')

        self.killswitch_hotkey = ctk.StringVar(value='Ctrl+Shift+K')

        self.appearence = ctk.StringVar(value='System')
        self.theme = ctk.StringVar(value='Blue')

        self.random_time_offset.trace('w', lambda x, y, z: self.validate(self.random_time_offset))
        self.random_mouse_offset_x.trace('w', lambda x, y, z: self.validate(self.random_mouse_offset_x))
        self.random_mouse_offset_y.trace('w', lambda x, y, z: self.validate(self.random_mouse_offset_y))
        self.hold_duration.trace('w', lambda x, y, z: self.validate(self.hold_duration))
        self.repeat_value.trace('w', lambda x, y, z: self.validate(self.repeat_value))

        self.advanced_options_vars = (
            self.random_time_offset_enabled,
            self.random_time_offset,
            self.random_mouse_offset_enabled,
            self.random_mouse_offset_x,
            self.random_mouse_offset_y,
            self.click_type,
            self.hold_duration,
            self.repeat_option,
            self.repeat_value,
            self.killswitch_hotkey,
        )

        MainFrame(
            self,
            (self.interval_ms, self.interval_s, self.interval_min, self.interval_hr),
            self.button,
            self.advanced_options_vars
        )
        ButtonsFrame(self, (self.start_clicking, self.stop_clicking, self.change_hotkey), self.hotkey)
        InfoFrame(self, self.super_mode)

        keyboard.add_hotkey('Ctrl+Shift+k', self.destroy)

        self.mainloop()

    def get_interval_sum(self) -> float | int:
        interval_ms = 0.001 if self.interval_ms.get() == '' else int(self.interval_ms.get()) * 0.001

        interval_s = 0 if self.interval_ms.get() == '' else int(self.interval_s.get())

        interval_min = 0 if self.interval_ms.get() == '' else int(self.interval_min.get()) * 60

        interval_hr = 0 if self.interval_ms.get() == '' else int(self.interval_hr.get()) * 3600

        return interval_ms + interval_s + interval_min + interval_hr

    def start_clicking(self, buttons_frame) -> None:
        self.stop_main_thread = False
        keyboard.remove_hotkey(self.hotkey.get())
        buttons_frame.start_button.configure(state='disabled')
        buttons_frame.stop_button.configure(state='enabled')
        keyboard.add_hotkey(self.hotkey.get(), lambda: self.stop_clicking(buttons_frame))
        threading.Thread(
            target=self.clicking_thread,
            args=(self.get_interval_sum(), self.button.get(), buttons_frame),
            daemon=True
        ).start()

    def stop_clicking(self, buttons_frame) -> None:
        self.stop_main_thread = True
        keyboard.remove_hotkey(self.hotkey.get())
        buttons_frame.start_button.configure(state='enabled')
        buttons_frame.stop_button.configure(state='disabled')
        keyboard.add_hotkey(self.hotkey.get(), lambda: self.start_clicking(buttons_frame))

    def clicking_thread(self, click_interval: float | int, button, buttons_frame) -> None:
        mouse_button = button.lower()
        if self.super_mode.get():
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            # Directly calling system to click even faster (really unstable)
            # Works only with left mouse button, because you're prob not going to need other buttons for this task,
            # and it's faster
            # 0x201 - LEFTBUTTONUP
            # 0x202 - LEFTBUTTONUP
            while not self.stop_main_thread:
                user32.mouse_event(0x201, 0, 0, 0, 0)
                user32.mouse_event(0x202, 0, 0, 0, 0)
        else:
            if self.repeat_option.get() == 'Repeat':
                for _ in range(int(self.repeat_value.get())):
                    if self.stop_main_thread:
                        break
                    if self.random_mouse_offset_enabled:
                        x = random.randint(
                            -int(self.random_mouse_offset_x.get()), int(self.random_mouse_offset_x.get())
                        )
                        y = random.randint(
                            -int(self.random_mouse_offset_y.get()), int(self.random_mouse_offset_y.get())
                        )
                        mouse.move(x, y, absolute=False)
                    mouse.press(mouse_button)
                    sleep(int(self.hold_duration.get()) / 1000)
                    mouse.release(mouse_button)
                    if self.click_type.get() == 'Double':
                        mouse.press(mouse_button)
                        sleep(int(self.hold_duration.get()) / 1000)
                        mouse.release(mouse_button)
                    sleep(click_interval + random.uniform(0, int(self.random_time_offset.get()) / 1000)
                          if self.random_time_offset_enabled else click_interval)
                    if self.random_mouse_offset_enabled:
                        mouse.move(-x, -y, absolute=False)
                self.stop_clicking(buttons_frame)
            else:
                while not self.stop_main_thread:
                    if self.random_mouse_offset_enabled.get():
                        x = random.randint(
                            -int(self.random_mouse_offset_x.get()), int(self.random_mouse_offset_x.get())
                        )
                        y = random.randint(
                            -int(self.random_mouse_offset_y.get()), int(self.random_mouse_offset_y.get())
                        )
                        mouse.move(x, y, absolute=False)
                    mouse.press(mouse_button)
                    sleep(int(self.hold_duration.get()) / 1000)
                    mouse.release(mouse_button)
                    if self.click_type.get() == 'Double':
                        mouse.press(mouse_button)
                        sleep(int(self.hold_duration.get()) / 1000)
                        mouse.release(mouse_button)
                    sleep(click_interval + random.uniform(0, int(self.random_time_offset.get()) / 1000)
                          if self.random_time_offset_enabled else click_interval)
                    if self.random_mouse_offset_enabled.get():
                        mouse.move(-x, -y, absolute=False)
        exit()

    def change_hotkey(self, buttons_frame):
        new_hotkey = []
        used_modifiers = []
        buttons_frame.change_hotkey_button.configure(text='Press any key...')
        hotkey_created = False

        def callback(key):
            nonlocal hotkey_created
            if key.name not in keyboard.all_modifiers:
                new_hotkey.append(key.name)
                hotkey_created = True
                return
            if key.name not in used_modifiers:
                new_hotkey.append(key.name)
                used_modifiers.append(key.name)

        keyboard.hook(callback)

        def wait_for_callback():
            while not hotkey_created:
                sleep(0.01)
            keyboard.unhook(callback)
            hotkey = '+'.join(new_hotkey)
            keyboard.remove_hotkey(self.hotkey.get())
            self.hotkey.set(hotkey)
            keyboard.add_hotkey(self.hotkey.get(), lambda: self.start_clicking(buttons_frame))
            buttons_frame.change_hotkey_button.configure(text='Change Hotkey')

            buttons_frame.start_button.configure(text=f"Start: {self.hotkey.get().replace('+', '-').title()}")
            buttons_frame.stop_button.configure(text=f"Stop: {self.hotkey.get().replace('+', '-').title()}")

            exit()

        threading.Thread(target=wait_for_callback, daemon=True).start()

    @staticmethod
    def validate(variable) -> None:
        variable_text = variable.get()
        for letter in variable_text:
            if not letter.isdigit():
                variable_text = variable_text.replace(letter, '')
            variable.set(variable_text)


class MainFrame(ctk.CTkFrame):
    def __init__(self, master, interval_variables, dropdown_variable, advanced_options_vars):
        super().__init__(master)
        self.pack(expand=True, fill='both', padx=5, pady=5)

        self.info_frame = MainFrameInfoFrame(self, dropdown_variable, advanced_options_vars)
        self.interval_frame = IntervalFrame(self, interval_variables)


class MainFrameInfoFrame(ctk.CTkFrame):
    def __init__(self, master, dropdown_variable, advanced_options_vars):
        super().__init__(master, fg_color='transparent')
        self.pack(expand=True, fill='x')

        self.description_label = ctk.CTkLabel(self, text='Click Interval:')
        self.description_label.pack(side='left', padx=10)

        self.advanced_options = ctk.CTkButton(
            self, text='>>', width=40, command=lambda: AdvancedOptions(advanced_options_vars)
        )
        self.advanced_options.pack(side='right', padx=5, pady=10)

        self.drop_menu = ctk.CTkOptionMenu(self, values=['Left', 'Right', 'Middle'], variable=dropdown_variable)
        self.drop_menu.pack(side='right', padx=5, pady=10)

        self.drop_menu_label = ctk.CTkLabel(self, text='Mouse Button:')
        self.drop_menu_label.pack(side='right', padx=5, pady=10)


class IntervalFrame(ctk.CTkFrame):
    def __init__(self, master, interval_variables):
        super().__init__(master, fg_color='transparent')
        self.pack(expand=True, fill='x', padx=5)

        self.label_ms = IntervalFrameLabel(self, text='Ms:')
        self.entry_ms = IntervalFrameEntry(self, interval_variables[0], width=60)

        self.label_sec = IntervalFrameLabel(self, text='Sec:')
        self.entry_sec = IntervalFrameEntry(self, interval_variables[1], width=60)

        self.label_min = IntervalFrameLabel(self, text='Min:')
        self.entry_min = IntervalFrameEntry(self, interval_variables[2], width=60)

        self.label_hr = IntervalFrameLabel(self, text='Hr:')
        self.entry_hr = IntervalFrameEntry(self, interval_variables[3], width=60)


class IntervalFrameEntry(ctk.CTkEntry):
    def __init__(self, master, interval_variable, *, width):
        super().__init__(master, textvariable=interval_variable, width=width)
        self.pack(side='left', expand=True, fill='x', padx=5, pady=5)


class IntervalFrameLabel(ctk.CTkLabel):
    def __init__(self, master, *, text):
        super().__init__(master, text=text, )
        self.pack(side='left', expand=True, fill='x', padx=5, pady=5)


class ButtonsFrame(ctk.CTkFrame):
    def __init__(self, master, button_funcs, hotkey_variable):
        super().__init__(master, fg_color='transparent')
        self.pack(expand=True, fill='y', padx=5, pady=5)

        self.start_button = ctk.CTkButton(
            self,
            text=f"Start: {hotkey_variable.get().replace('+', '-').title()}",
            command=lambda: button_funcs[0](self)
        )
        self.start_button.pack(side='left', expand=True, padx=5)

        self.stop_button = ctk.CTkButton(
            self,
            text=f"Stop: {hotkey_variable.get().replace('+', '-').title()}",
            state='disabled',
            command=lambda: button_funcs[1](self)
        )
        self.stop_button.pack(side='left', expand=True, padx=5)

        self.change_hotkey_button = ctk.CTkButton(
            self,
            text='Change Hotkey',
            command=lambda: button_funcs[2](self)
        )
        self.change_hotkey_button.pack(side='left', expand=True, padx=5)

        keyboard.add_hotkey((hotkey_variable.get()), lambda: button_funcs[0](self))


class InfoFrame(ctk.CTkFrame):
    def __init__(self, master, super_mode_variable):
        super().__init__(master, fg_color='transparent')
        self.pack(fill='x', padx=10, pady=5)
        self.killswitch_label = ctk.CTkLabel(self, text='Killswitch: Ctrl+Shift+K')
        self.killswitch_label.pack(side='left')

        self.super_mode_switch = ctk.CTkSwitch(self, text='Super Mode', variable=super_mode_variable)
        self.super_mode_switch.pack(side='right', padx=5)


class AdvancedOptions(ctk.CTkToplevel):
    def __init__(self, advanced_options_vars):
        super().__init__()
        self.title("Advanced Options")
        self.grab_set()
        self.geometry(
            f"500x300"
            f"+{int(self.winfo_screenwidth() / 2 - 500 / 2)}"
            f"+{int(self.winfo_screenheight() / 2 - 300 / 2)}"
        )
        self.resizable(False, False)

        self.rowconfigure((0, 1, 2), weight=3, uniform='a')
        self.columnconfigure((0, 1), weight=1, uniform='a')

        self.random_time_offset_enabled = advanced_options_vars[0]
        self.random_time_offset = advanced_options_vars[1]

        self.random_mouse_offset_enabled = advanced_options_vars[2]
        self.random_mouse_offset_x = advanced_options_vars[3]
        self.random_mouse_offset_y = advanced_options_vars[4]

        self.click_type = advanced_options_vars[5]
        self.hold_duration = advanced_options_vars[6]

        self.repeat_option = advanced_options_vars[7]
        self.repeat_value = advanced_options_vars[8]

        self.killswitch_hotkey = advanced_options_vars[9]

        self.appearence = ctk.StringVar(value='System')
        self.theme = ctk.StringVar(value='Blue')

        TimeOffset(self, self.random_time_offset_enabled, self.random_time_offset)
        MouseOffset(self, self.random_mouse_offset_enabled, (self.random_mouse_offset_x, self.random_mouse_offset_y))
        ClickType(self, self.click_type, self.hold_duration)
        RepeatOptions(self, self.repeat_option, self.repeat_value)
        KillSwitch(self, self.killswitch_hotkey)
        ChangeTheme(self, self.appearence, self.theme)

    @staticmethod
    def validate(variable) -> None:
        variable_text = variable.get()
        for letter in variable_text:
            if not letter.isdigit():
                variable_text = variable_text.replace(letter, '')
            variable.set(variable_text)


class TimeOffset(ctk.CTkFrame):
    def __init__(self, master, random_time_offest_enabled, random_time_offest):
        super().__init__(master)
        self.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.switch = ctk.CTkSwitch(self, text='Random Time Offset', variable=random_time_offest_enabled)
        self.switch.place(relx=0.05, rely=0.1)

        self.label = ctk.CTkLabel(self, text='Milliseconds')
        self.label.place(relx=0.05, rely=0.55)

        self.entry = ctk.CTkEntry(self, width=60, textvariable=random_time_offest)
        self.entry.place(relx=0.4, rely=0.55)


class MouseOffset(ctk.CTkFrame):
    def __init__(self, master, random_mouse_offset_enabled, variables):
        super().__init__(master)
        self.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.switch = ctk.CTkSwitch(self, text='Random Mouse Offset', variable=random_mouse_offset_enabled)
        self.switch.place(relx=0.05, rely=0.1)

        self.x = ctk.CTkLabel(self, text='X:')
        self.x.place(relx=0.05, rely=0.55)

        self.x_entry = ctk.CTkEntry(self, width=60, textvariable=variables[0])
        self.x_entry.place(relx=0.15, rely=0.55)

        self.y = ctk.CTkLabel(self, text='Y:')
        self.y.place(relx=0.45, rely=0.55)

        self.y_entry = ctk.CTkEntry(self, width=60, textvariable=variables[1])
        self.y_entry.place(relx=0.55, rely=0.55)


class ClickType(ctk.CTkFrame):
    def __init__(self, master, click_type, hold_duration):
        super().__init__(master)
        self.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.label = ctk.CTkLabel(self, text='Click Type:')
        self.label.place(relx=0.05, rely=0.1)

        self.option_menu = ctk.CTkOptionMenu(self, values=['Single', 'Double'], width=135, variable=click_type)
        self.option_menu.place(relx=0.37, rely=0.1)

        self.hold_label = ctk.CTkLabel(self, text='Hold duration (ms):')
        self.hold_label.place(relx=0.05, rely=0.55)

        self.hold_entry = ctk.CTkEntry(self, width=60, textvariable=hold_duration)
        self.hold_entry.place(relx=0.6, rely=0.55)


class RepeatOptions(ctk.CTkFrame):
    def __init__(self, master, repeat_option, repeat_value):
        super().__init__(master)
        self.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

        self.label = ctk.CTkLabel(self, text='Repeat Options:')
        self.label.place(relx=0.05, rely=0.1)

        self.toggle = ctk.CTkRadioButton(self, text='Toggle', variable=repeat_option, value='Toggle')
        self.toggle.place(relx=0.05, rely=0.55)

        self.repeat = ctk.CTkRadioButton(self, text='Repeat', variable=repeat_option, value='Repeat')
        self.repeat.place(relx=0.4, rely=0.55)

        self.entry = ctk.CTkEntry(self, width=50, textvariable=repeat_value)
        self.entry.place(relx=0.75, rely=0.53)


class KillSwitch(ctk.CTkFrame):
    def __init__(self, master, killswitch_hotkey):
        super().__init__(master)
        self.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.change_kill_switch_hotkey = ctk.CTkButton(self, text='Change KillSwitch Hotkey')
        self.change_kill_switch_hotkey.place(relx=0.5, rely=0.15, anchor='n')
        self.killswitch_hotkey = ctk.CTkLabel(self, textvariable=killswitch_hotkey)
        self.killswitch_hotkey.place(relx=0.5, rely=0.6, anchor='n')


class ChangeTheme(ctk.CTkFrame):
    def __init__(self, master, appearence, theme):
        super().__init__(master)
        self.grid(row=2, column=1, padx=10, pady=10, sticky='nsew')

        self.appearence_label = ctk.CTkLabel(self, text='Appearence:')
        self.appearence_label.place(relx=0.05, rely=0.1)

        self.appearence_menu = ctk.CTkOptionMenu(
            self, values=['Light', 'Dark', 'System'], width=126, variable=appearence
        )
        self.appearence_menu.place(relx=0.4, rely=0.1)

        self.theme_label = ctk.CTkLabel(self, text='Theme:')
        self.theme_label.place(relx=0.05, rely=0.55)

        self.theme_menu = ctk.CTkOptionMenu(
            self, values=['Blue', 'Green', 'Red', 'Grey', 'Cyan', 'Purple'], width=126, variable=theme
        )
        self.theme_menu.place(relx=0.4, rely=0.55)


app = App()
