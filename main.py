import customtkinter as ctk
import random
import keyboard
import threading
import mouse
import ctypes
import os
from time import sleep

BASE_DIR = os.path.dirname(__file__)

fg_colors = {
    'Default': '#1c72b1',
    'Green': '#15a336',
    'Red': '#ab150a',
    'Grey': '#a3a2a2',
    'Cyan': '#0dacba',
    'Purple': '#a12dc2'
}
hover_colors = {
    'Default': '#144870',
    'Green': '#167014',
    'Red': '#701c14',
    'Grey': '#6b6b6b',
    'Cyan': '#146d70',
    'Purple': '#5c1470'
}
dropdown_hover_colors = {
    'Default': '#203a4f',
    'Green': '#204f28',
    'Red': '#4f2020',
    'Grey': '#4f4e4e',
    'Cyan': '#204e4f',
    'Purple': '#4b204f'
}


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title('Simple Auto Clicker')
        self.geometry(
            f"450x200"
            f"+{int(self.winfo_screenwidth() / 2 - 450 / 2)}"
            f"+{int(self.winfo_screenheight() / 2 - 250 / 2)}"
        )
        self.iconbitmap(os.path.join(BASE_DIR, r'./App.ico'))
        self.resizable(False, False)

        self.stop_main_thread = False

        self.interval_ms = ctk.StringVar(value='100')
        self.interval_s = ctk.StringVar(value='0')
        self.interval_min = ctk.StringVar(value='0')
        self.interval_hr = ctk.StringVar(value='0')

        self.interval_ms.trace('w', lambda x, y, z: self.validate(self.interval_ms))
        self.interval_s.trace('w', lambda x, y, z: self.validate(self.interval_s))
        self.interval_min.trace('w', lambda x, y, z: self.validate(self.interval_min))
        self.interval_hr.trace('w', lambda x, y, z: self.validate(self.interval_hr))

        self.mouse_button = ctk.StringVar(value='Left')
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
        self.theme = ctk.StringVar(value='Default')

        self.random_time_offset.trace('w', lambda x, y, z: self.validate(self.random_time_offset))
        self.random_mouse_offset_x.trace('w', lambda x, y, z: self.validate(self.random_mouse_offset_x))
        self.random_mouse_offset_y.trace('w', lambda x, y, z: self.validate(self.random_mouse_offset_y))
        self.hold_duration.trace('w', lambda x, y, z: self.validate(self.hold_duration))
        self.repeat_value.trace('w', lambda x, y, z: self.validate(self.repeat_value))
        self.appearence.trace('w', lambda x, y, z: ctk.set_appearance_mode(self.appearence.get().lower()))
        self.theme.trace('w', lambda x, y, z: self.change_theme())

        self.main_frame = MainFrame(self)
        self.buttons_frame = ButtonsFrame(self)
        self.info_frame = InfoFrame(self)

        keyboard.add_hotkey('Ctrl+Shift+K', self.destroy)

    def get_interval_sum(self) -> float | int:
        return (self.normalize(self.interval_ms) * 0.001
                + self.normalize(self.interval_s)
                + self.normalize(self.interval_min) * 60
                + self.normalize(self.interval_hr) * 3600)

    def start_clicking(self) -> None:
        self.stop_main_thread = False

        keyboard.remove_hotkey(self.hotkey.get())

        self.buttons_frame.start_button.configure(state='disabled')
        self.buttons_frame.stop_button.configure(state='enabled')

        keyboard.add_hotkey(self.hotkey.get(), self.stop_clicking)

        threading.Thread(
            target=self.clicking_thread,
            daemon=True
        ).start()

    def stop_clicking(self) -> None:
        self.stop_main_thread = True

        keyboard.remove_hotkey(self.hotkey.get())

        self.buttons_frame.start_button.configure(state='enabled')
        self.buttons_frame.stop_button.configure(state='disabled')

        keyboard.add_hotkey(self.hotkey.get(), self.start_clicking)

    def clicking_thread(self) -> None:

        if self.super_mode.get():
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            # Directly calling system to click even faster (really unstable)
            # Ignores all preferences for speed performance
            # 0x201 - LEFTBUTTONDOWN
            # 0x202 - LEFTBUTTONUP
            while not self.stop_main_thread:
                user32.mouse_event(0x201, 0, 0, 0, 0)
                user32.mouse_event(0x202, 0, 0, 0, 0)
            exit()

        mouse_button = self.mouse_button.get().lower()
        click_interval = self.get_interval_sum()

        if self.repeat_option.get() == 'Repeat':
            self.repeat_clicking(mouse_button, click_interval)
        else:
            self.toggle_clicking(mouse_button, click_interval)

        exit()

    def repeat_clicking(self, mouse_button, click_interval) -> None:
        repeat_amount = int(self.repeat_value.get())
        while not self.stop_main_thread and repeat_amount > 0:

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

            sleep(
                click_interval + random.uniform(0, int(self.random_time_offset.get()) / 1000)
                if self.random_time_offset_enabled else click_interval
            )

            if self.random_mouse_offset_enabled:
                mouse.move(-x, -y, absolute=False)

            repeat_amount -= 1

        self.stop_clicking()

    def toggle_clicking(self, mouse_button, click_interval) -> None:
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

    def change_hotkey(self) -> None:
        keyboard.remove_hotkey(self.hotkey.get())
        hotkey_created = False
        new_hotkey = []
        used_modifiers = []
        self.buttons_frame.change_hotkey_button.configure(text='Press any key...')

        def callback(key) -> None:
            nonlocal hotkey_created
            if key.name not in keyboard.all_modifiers:
                new_hotkey.append(key.name)
                hotkey_created = True
                return
            if key.name not in used_modifiers:
                new_hotkey.append(key.name)
                used_modifiers.append(key.name)

        keyboard.hook(callback)

        def wait_for_callback() -> None:
            while not hotkey_created:
                sleep(0.01)
            keyboard.unhook(callback)
            hotkey = '+'.join(new_hotkey)

            self.hotkey.set(hotkey)
            keyboard.add_hotkey(self.hotkey.get(), self.start_clicking)

            self.buttons_frame.change_hotkey_button.configure(text='Change Hotkey')

            self.buttons_frame.start_button.configure(text=f"Start: {self.hotkey.get().replace('+', '-').title()}")
            self.buttons_frame.stop_button.configure(text=f"Stop: {self.hotkey.get().replace('+', '-').title()}")

            exit()

        threading.Thread(target=wait_for_callback, daemon=True).start()

    def change_theme(self) -> None:
        fg_color = fg_colors[self.theme.get()]
        hover_color = hover_colors[self.theme.get()]
        dropdown_hover_color = dropdown_hover_colors[self.theme.get()]

        self.main_frame.info_frame.advanced_options.configure(fg_color=fg_color, hover_color=hover_color)
        self.main_frame.info_frame.dropdown.configure(
            fg_color=fg_color, button_color=hover_color, button_hover_color=dropdown_hover_color
        )

        self.buttons_frame.start_button.configure(fg_color=fg_color, hover_color=hover_color)
        self.buttons_frame.stop_button.configure(fg_color=fg_color, hover_color=hover_color)
        self.buttons_frame.change_hotkey_button.configure(fg_color=fg_color, hover_color=hover_color)

        self.info_frame.super_mode_switch.configure(progress_color=hover_color)

    @staticmethod
    def normalize(variable: ctk.StringVar) -> int:
        if variable.get() == '':
            return 0
        return int(variable.get())

    @staticmethod
    def validate(variable: ctk.StringVar) -> None:
        # Should be used in entry traces
        variable_text = variable.get()
        for letter in variable_text:
            if not letter.isdigit():
                variable_text = variable_text.replace(letter, '')
            variable.set(variable_text)


class MainFrame(ctk.CTkFrame):
    def __init__(self, master: App):
        super().__init__(master)
        self.pack(expand=True, fill='both', padx=5, pady=5)

        self.info_frame = MainFrameInfoFrame(self, master)
        self.interval_frame = IntervalFrame(self, master)


class MainFrameInfoFrame(ctk.CTkFrame):
    def __init__(self, master, root: App):
        super().__init__(master, fg_color='transparent')
        self.pack(expand=True, fill='x')

        self.description = ctk.CTkLabel(self, text='Click Interval:')
        self.description.pack(side='left', padx=10)

        self.advanced_options = ctk.CTkButton(
            self,
            text='>>',
            width=40,
            command=lambda: AdvancedOptions(root),
            fg_color=fg_colors[root.theme.get()],
            hover_color=hover_colors[root.theme.get()]
        )
        self.advanced_options.pack(side='right', padx=5, pady=10)

        self.dropdown = ctk.CTkOptionMenu(
            self,
            values=['Left', 'Right', 'Middle'],
            variable=root.mouse_button,
            fg_color=fg_colors[root.theme.get()],
            button_color=hover_colors[root.theme.get()],
            button_hover_color=dropdown_hover_colors[root.theme.get()])
        self.dropdown.pack(side='right', padx=5, pady=10)

        self.dropdown_label = ctk.CTkLabel(self, text='Mouse Button:')
        self.dropdown_label.pack(side='right', padx=5, pady=10)


class IntervalFrame(ctk.CTkFrame):
    def __init__(self, master, root: App):
        super().__init__(master, fg_color='transparent')
        self.pack(expand=True, fill='x', padx=5)

        self.label_ms = IntervalFrameLabel(self, text='Ms:')
        self.entry_ms = IntervalFrameEntry(self, root.interval_ms, width=60)

        self.label_sec = IntervalFrameLabel(self, text='Sec:')
        self.entry_sec = IntervalFrameEntry(self, root.interval_s, width=60)

        self.label_min = IntervalFrameLabel(self, text='Min:')
        self.entry_min = IntervalFrameEntry(self, root.interval_min, width=60)

        self.label_hr = IntervalFrameLabel(self, text='Hr:')
        self.entry_hr = IntervalFrameEntry(self, root.interval_hr, width=60)


class IntervalFrameEntry(ctk.CTkEntry):
    def __init__(self, master, interval_variable, *, width):
        super().__init__(master, textvariable=interval_variable, width=width)
        self.pack(side='left', expand=True, fill='x', padx=5, pady=5)


class IntervalFrameLabel(ctk.CTkLabel):
    def __init__(self, master, *, text):
        super().__init__(master, text=text, )
        self.pack(side='left', expand=True, fill='x', padx=5, pady=5)


class ButtonsFrame(ctk.CTkFrame):
    def __init__(self, master: App):
        super().__init__(master, fg_color='transparent')
        self.pack(expand=True, fill='y', padx=5, pady=5)

        self.start_button = ctk.CTkButton(
            self,
            text=f"Start: {master.hotkey.get().replace('+', '-').title()}",
            command=lambda: master.start_clicking(),
            fg_color=fg_colors[master.theme.get()],
            hover_color=hover_colors[master.theme.get()]
        )
        self.start_button.pack(side='left', expand=True, padx=5)

        self.stop_button = ctk.CTkButton(
            self,
            text=f"Stop: {master.hotkey.get().replace('+', '-').title()}",
            state='disabled',
            command=lambda: master.stop_clicking(),
            fg_color=fg_colors[master.theme.get()],
            hover_color=hover_colors[master.theme.get()]
        )
        self.stop_button.pack(side='left', expand=True, padx=5)

        self.change_hotkey_button = ctk.CTkButton(
            self,
            text='Change Hotkey',
            command=lambda: master.change_hotkey(),
            fg_color=fg_colors[master.theme.get()],
            hover_color=hover_colors[master.theme.get()]
        )
        self.change_hotkey_button.pack(side='left', expand=True, padx=5)

        keyboard.add_hotkey((master.hotkey.get()), master.start_clicking)


class InfoFrame(ctk.CTkFrame):
    def __init__(self, master: App):
        super().__init__(master, fg_color='transparent')
        self.pack(fill='x', padx=10, pady=5)
        self.killswitch_label = ctk.CTkLabel(
            self,
            text=f'Killswitch: {master.killswitch_hotkey.get().replace('+', '-').title()}'
        )
        self.killswitch_label.pack(side='left')

        self.super_mode_switch = ctk.CTkSwitch(self, text='Super Mode', variable=master.super_mode)
        self.super_mode_switch.pack(side='right', padx=5)


class AdvancedOptions(ctk.CTkToplevel):
    def __init__(self, root: App):
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

        self.root = root

        self.root.theme.trace('w', lambda x, y, z: self.change_theme())

        self.time_offset = TimeOffset(self)
        self.mouse_offset = MouseOffset(self)
        self.click_type = ClickType(self)
        self.repeat_options = RepeatOptions(self)
        self.killswitch = KillSwitch(self)
        self.theme = Theme(self)

    def change_killswitch_hotkey(self, buttons_frame):
        keyboard.remove_hotkey(self.root.killswitch_hotkey.get())
        hotkey_created = False
        new_hotkey = []
        used_modifiers = []
        buttons_frame.change_killswitch_hotkey.configure(text='Press any key...')

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

            self.root.killswitch_hotkey.set(hotkey)
            keyboard.add_hotkey(self.root.killswitch_hotkey.get(), self.root.destroy)

            buttons_frame.change_killswitch_hotkey.configure(text='Change KillSwitch Hotkey')
            buttons_frame.killswitch_hotkey.configure(
                text=f"{self.root.killswitch_hotkey.get().replace('+', '-').title()}"
            )
            self.root.info_frame.killswitch_label.configure(text=f'Killswitch: {hotkey.replace('+', '-').title()}')
            exit()

        threading.Thread(target=wait_for_callback, daemon=True).start()

    def change_theme(self):
        fg_color = fg_colors[self.root.theme.get()]
        hover_color = hover_colors[self.root.theme.get()]
        dropdown_hover_color = dropdown_hover_colors[self.root.theme.get()]

        self.time_offset.switch.configure(progress_color=hover_color)

        self.mouse_offset.switch.configure(progress_color=hover_color)

        self.click_type.option_menu.configure(
            fg_color=fg_color, button_color=hover_color, button_hover_color=dropdown_hover_color
        )

        self.repeat_options.toggle.configure(fg_color=fg_color, hover_color=hover_color)
        self.repeat_options.repeat.configure(fg_color=fg_color, hover_color=hover_color)

        self.killswitch.change_killswitch_hotkey.configure(fg_color=fg_color, hover_color=hover_color)

        self.theme.appearence_menu.configure(
            fg_color=fg_color, button_color=hover_color, button_hover_color=dropdown_hover_color
        )
        self.theme.theme_menu.configure(
            fg_color=fg_color, button_color=hover_color, button_hover_color=dropdown_hover_color
        )

class TimeOffset(ctk.CTkFrame):
    def __init__(self, master: AdvancedOptions):
        super().__init__(master)
        self.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.switch = ctk.CTkSwitch(
            self,
            text='Random Time Offset',
            variable=master.root.random_time_offset_enabled,
            progress_color=hover_colors[master.root.theme.get()]
        )
        self.switch.place(relx=0.05, rely=0.1)

        self.label = ctk.CTkLabel(self, text='Milliseconds')
        self.label.place(relx=0.05, rely=0.55)

        self.entry = ctk.CTkEntry(self, width=60, textvariable=master.root.random_time_offset)
        self.entry.place(relx=0.4, rely=0.55)


class MouseOffset(ctk.CTkFrame):
    def __init__(self, master: AdvancedOptions):
        super().__init__(master)
        self.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.switch = ctk.CTkSwitch(
            self,
            text='Random Mouse Offset',
            variable=master.root.random_mouse_offset_enabled,
            progress_color=hover_colors[master.root.theme.get()]
        )
        self.switch.place(relx=0.05, rely=0.1)

        self.x = ctk.CTkLabel(self, text='X:')
        self.x.place(relx=0.05, rely=0.55)

        self.x_entry = ctk.CTkEntry(self, width=60, textvariable=master.root.random_mouse_offset_x)
        self.x_entry.place(relx=0.15, rely=0.55)

        self.y = ctk.CTkLabel(self, text='Y:')
        self.y.place(relx=0.45, rely=0.55)

        self.y_entry = ctk.CTkEntry(self, width=60, textvariable=master.root.random_mouse_offset_y)
        self.y_entry.place(relx=0.55, rely=0.55)


class ClickType(ctk.CTkFrame):
    def __init__(self, master: AdvancedOptions):
        super().__init__(master)
        self.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.description = ctk.CTkLabel(self, text='Click Type:')
        self.description.place(relx=0.05, rely=0.1)

        self.option_menu = ctk.CTkOptionMenu(
            self,
            values=['Single', 'Double'],
            width=135,
            variable=master.root.click_type,
            fg_color=fg_colors[master.root.theme.get()],
            button_color=hover_colors[master.root.theme.get()],
            button_hover_color=dropdown_hover_colors[master.root.theme.get()]
        )
        self.option_menu.place(relx=0.37, rely=0.1)

        self.hold_label = ctk.CTkLabel(
            self, text='Hold duration (ms):'
        )
        self.hold_label.place(relx=0.05, rely=0.55)

        self.hold_entry = ctk.CTkEntry(
            self,
            width=60,
            textvariable=master.root.hold_duration
        )
        self.hold_entry.place(relx=0.6, rely=0.55)


class RepeatOptions(ctk.CTkFrame):
    def __init__(self, master: AdvancedOptions):
        super().__init__(master)
        self.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

        self.description = ctk.CTkLabel(self, text='Repeat Options:')
        self.description.place(relx=0.05, rely=0.1)

        self.toggle = ctk.CTkRadioButton(
            self,
            text='Toggle',
            variable=master.root.repeat_option,
            value='Toggle',
            fg_color=fg_colors[master.root.theme.get()],
            hover_color=hover_colors[master.root.theme.get()]
        )
        self.toggle.place(relx=0.05, rely=0.55)

        self.repeat = ctk.CTkRadioButton(
            self,
            text='Repeat',
            variable=master.root.repeat_option,
            value='Repeat',
            fg_color=fg_colors[master.root.theme.get()],
            hover_color=hover_colors[master.root.theme.get()]
        )
        self.repeat.place(relx=0.4, rely=0.55)

        self.entry = ctk.CTkEntry(self, width=50, textvariable=master.root.repeat_value)
        self.entry.place(relx=0.75, rely=0.53)


class KillSwitch(ctk.CTkFrame):
    def __init__(self, master: AdvancedOptions):
        super().__init__(master)
        self.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.change_killswitch_hotkey = ctk.CTkButton(
            self,
            text='Change KillSwitch Hotkey',
            command=lambda: master.change_killswitch_hotkey(self),
            fg_color=fg_colors[master.root.theme.get()],
            hover_color=hover_colors[master.root.theme.get()]
        )
        self.change_killswitch_hotkey.place(relx=0.5, rely=0.15, anchor='n')

        self.killswitch_hotkey = ctk.CTkLabel(
            self,
            text=f"{master.root.killswitch_hotkey.get().replace('+', '-').title()}"
        )
        self.killswitch_hotkey.place(relx=0.5, rely=0.6, anchor='n')


class Theme(ctk.CTkFrame):
    def __init__(self, master: AdvancedOptions):
        super().__init__(master)
        self.grid(row=2, column=1, padx=10, pady=10, sticky='nsew')

        self.description = ctk.CTkLabel(self, text='Appearence:')
        self.description.place(relx=0.05, rely=0.1)

        self.appearence_menu = ctk.CTkOptionMenu(
            self,
            values=['Light', 'Dark', 'System'],
            width=126,
            variable=master.root.appearence,
            fg_color=fg_colors[master.root.theme.get()],
            button_color=hover_colors[master.root.theme.get()],
            button_hover_color=dropdown_hover_colors[master.root.theme.get()]
        )
        self.appearence_menu.place(relx=0.4, rely=0.1)

        self.theme_label = ctk.CTkLabel(self, text='Theme:')
        self.theme_label.place(relx=0.05, rely=0.55)

        self.theme_menu = ctk.CTkOptionMenu(
            self,
            values=['Default', 'Green', 'Red', 'Grey', 'Cyan', 'Purple'],
            width=126,
            variable=master.root.theme,
            fg_color=fg_colors[master.root.theme.get()],
            button_color=hover_colors[master.root.theme.get()],
            button_hover_color=dropdown_hover_colors[master.root.theme.get()]
        )
        self.theme_menu.place(relx=0.4, rely=0.55)


app = App()
app.mainloop()
