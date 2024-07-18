import customtkinter as ctk


class AdvancedOptions(ctk.CTkToplevel):
    def __init__(self, update_func):
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

        self.random_time_offset_enabled = ctk.BooleanVar(value=False)
        self.random_time_offset = ctk.StringVar(value='0')

        self.random_mouse_offset_enabled = ctk.BooleanVar(value=False)
        self.random_mouse_offset_x = ctk.StringVar(value='0')
        self.random_mouse_offset_y = ctk.StringVar(value='0')

        self.click_type = ctk.StringVar(value='Single')
        self.hold_duration = ctk.IntVar(value=0)

        self.repeat_option = ctk.StringVar(value='Toggle')
        self.repeat_value = ctk.IntVar(value=0)

        self.killswitch_hotkey = ctk.StringVar(value='Ctrl+Shift+K')

        self.appearence = ctk.StringVar(value='System')
        self.theme = ctk.StringVar(value='Blue')

        self.random_time_offset_enabled.trace(
            'w',
            callback=lambda name, y, z: update_func(self.random_time_offset_enabled, 'random_time_offset_enabled')
        )
        self.random_time_offset.trace(
            'w',
            callback=lambda name, y, z: update_func(self.random_time_offset, 'random_time_offset')
        )
        self.random_mouse_offset_enabled.trace(
            'w',
            callback=lambda name, y, z: update_func(self.random_mouse_offset_enabled, 'random_mouse_offset_enabled')
        )
        self.random_mouse_offset_x.trace(
            'w',
            callback=lambda name, y, z: update_func(self.random_mouse_offset_x, 'random_mouse_offset_x')
        )
        self.random_mouse_offset_y.trace(
            'w',
            callback=lambda name, y, z: update_func(self.random_mouse_offset_y, 'random_mouse_offset_y')
        )
        self.click_type.trace(
            'w',
            callback=lambda name, y, z: update_func(self.click_type, 'click_type')
        )
        self.hold_duration.trace(
            'w',
            callback=lambda name, y, z: update_func(self.hold_duration, 'hold_duration')
        )
        self.repeat_option.trace(
            'w',
            callback=lambda name, y, z: update_func(self.repeat_option, 'repeat_option')
        )
        self.repeat_value.trace(
            'w',
            callback=lambda name, y, z: update_func(self.repeat_value, 'repeat_value')
        )
        self.killswitch_hotkey.trace(
            'w',
            callback=lambda name, y, z: update_func(self.killswitch_hotkey, 'killswitch_hotkey')
        )

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

        self.hold_label = ctk.CTkLabel(self, text='Hold dureation (ms):')
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


if __name__ == '__main__':
    AdvancedOptions().mainloop()
