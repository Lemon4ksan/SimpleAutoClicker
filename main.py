import random

import customtkinter as ctk
import keyboard
import threading
import mouse
import ctypes
from time import sleep
from advanced_options import AdvancedOptions


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
        self.random_time_offset = ctk.IntVar(value=0)

        self.random_mouse_offset_enabled = ctk.BooleanVar(value=False)
        self.random_mouse_offset_x = ctk.IntVar(value=0)
        self.random_mouse_offset_y = ctk.IntVar(value=0)

        self.click_type = ctk.StringVar(value='Single')
        self.hold_duration = ctk.IntVar(value=0)

        self.repeat_option = ctk.StringVar(value='Toggle')
        self.repeat_value = ctk.IntVar(value=0)

        self.killswitch_hotkey = ctk.StringVar(value='Ctrl+Shift+K')

        self.appearence = ctk.StringVar(value='System')
        self.theme = ctk.StringVar(value='Blue')

        MainFrame(
            self,
            (self.interval_ms, self.interval_s, self.interval_min, self.interval_hr),
            self.button,
            self.update_variable
        )
        ButtonsFrame(self, (self.start_clicking, self.stop_clicking, self.change_hotkey), self.hotkey)
        InfoFrame(self, self.super_mode)

        keyboard.add_hotkey('Ctrl+Shift+k', self.destroy)

        self.new_window = AdvancedOptions(self.update_variable)
        self.new_window.withdraw()

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
            args=(self.get_interval_sum(), self.button.get()),
            daemon=True
        ).start()

    def stop_clicking(self, buttons_frame) -> None:
        self.stop_main_thread = True
        keyboard.remove_hotkey(self.hotkey.get())
        buttons_frame.start_button.configure(state='enabled')
        buttons_frame.stop_button.configure(state='disabled')
        keyboard.add_hotkey(self.hotkey.get(), lambda: self.start_clicking(buttons_frame))

    def clicking_thread(self, click_interval: float | int, button) -> None:
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
            while not self.stop_main_thread:
                if self.random_mouse_offset_enabled:
                    x = random.randint(-self.random_mouse_offset_x.get(), self.random_mouse_offset_x.get())
                    y = random.randint(-self.random_mouse_offset_y.get(), self.random_mouse_offset_y.get())
                    mouse.move(x, y, absolute=False)
                mouse.press(mouse_button)
                mouse.release(mouse_button)
                sleep(click_interval + random.uniform(0, self.random_time_offset.get() / 1000)
                      if self.random_time_offset_enabled else click_interval)
                if self.random_mouse_offset_enabled:
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

    def update_variable(self, variable, variable_name):
        match variable_name:
            case 'random_time_offset_enabled':
                self.random_time_offset_enabled.set(variable.get())
            case 'random_time_offset':
                self.random_time_offset.set(variable.get())
            case 'random_mouse_offset_enabled':
                self.random_time_offset_enabled.set(variable.get())
            case 'random_mouse_offset_x':
                self.random_mouse_offset_x.set(variable.get())
            case 'random_mouse_offset_y':
                self.random_mouse_offset_y.set(variable.get())
            case 'click_type':
                self.click_type.set(variable.get())
            case 'hold_duration':
                self.hold_duration.set(variable.get())
            case 'repeat_option':
                self.repeat_option.set(variable.get())
            case 'repeat_value':
                self.repeat_value.set(variable.get())
            case 'killswitch_hotkey':
                print(variable.get())
            case _:
                print('Error' + str(variable.get()))
        print(variable.get())

    @staticmethod
    def validate(variable) -> None:
        variable_text = variable.get()
        for letter in variable_text:
            if not letter.isdigit():
                variable_text = variable_text.replace(letter, '')
            variable.set(variable_text)


class MainFrame(ctk.CTkFrame):
    def __init__(self, master, interval_variables, dropdown_variable, update_func):
        super().__init__(master)
        self.pack(expand=True, fill='both', padx=5, pady=5)

        self.info_frame = MainFrameInfoFrame(self, dropdown_variable, update_func)
        self.interval_frame = IntervalFrame(self, interval_variables)


class MainFrameInfoFrame(ctk.CTkFrame):
    def __init__(self, master, dropdown_variable, update_func):
        super().__init__(master, fg_color='transparent')
        self.pack(expand=True, fill='x')

        self.description_label = ctk.CTkLabel(self, text='Click Interval:')
        self.description_label.pack(side='left', padx=10)

        self.advanced_options = ctk.CTkButton(
            self, text='>>', width=40, command=lambda: AdvancedOptions(update_func=update_func)
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


app = App()
