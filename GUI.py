import tkinter as tk
from Driver_USB import InterruptTable, DeviceDriverTable, DeviceControlBlock, USBDriver, IOManager, IOOPeration

class USBGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("USB Simulator GUI")

        self.interrupt_table = InterruptTable()
        self.driver_table = DeviceDriverTable()
        self.usb_dcb = DeviceControlBlock(1, "USB", 128)
        self.usb_driver = USBDriver(self.usb_dcb, self.interrupt_table)
        self.driver_table.register_driver(self.usb_dcb.device_id, self.usb_driver)
        self.io_manager = IOManager(self.driver_table)
        self.io_manager.start()

        tk.Button(master, text="Conectar USB", command=self.connect_usb).pack(pady=5)
        tk.Button(master, text="Desconectar USB", command=self.disconnect_usb).pack(pady=5)
        tk.Button(master, text="Operación Lectura", command=self.read_op).pack(pady=5)
        tk.Button(master, text="Operación Escritura", command=self.write_op).pack(pady=5)
        tk.Button(master, text="Salir", command=self.exit_app).pack(pady=5)

    def connect_usb(self):
        self.interrupt_table.trigger_interrupt("USB_INSERT")

    def disconnect_usb(self):
        self.interrupt_table.trigger_interrupt("USB_REMOVE")

    def read_op(self):
        self.io_manager.add_io_operation(self.usb_dcb.device_id, IOOPeration("READ", 100, "GUI_Process"))

    def write_op(self):
        self.io_manager.add_io_operation(self.usb_dcb.device_id, IOOPeration("WRITE", 200, "GUI_Process"))

    def exit_app(self):
        self.io_manager.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = USBGUI(root)
    root.mainloop()