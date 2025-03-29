import time
from collections import deque
from InternalMemoryDevice import InternalMemoryDevice
from RemovableMemoryDevice import RemovableMemoryDevice
from KeyboardDevice import KeyboardDriverSimulator


class DeviceDriverSimulator:
    """
    Simula un sistema operativo que gestiona dispositivos, operaciones de entrada/salida (E/S),
    interrupciones y una memoria RAM limitada.
    """

    class Device:
        """Representa un dispositivo físico en el sistema."""
        def __init__(self, name):
            self.name = name        # Nombre del dispositivo (e.g., Printer)
            self.busy = False       # Estado del dispositivo (ocupado o libre)
            self.buffer = ""        # Buffer interno del dispositivo

    class IORequest:
        """Representa una solicitud de E/S por parte de un proceso de usuario."""
        def __init__(self, device_id, operation, data=""):
            self.device_id = device_id  # Índice del dispositivo objetivo
            self.operation = operation  # Tipo de operación: "read" o "write"
            self.data = data            # Datos a escribir (solo si es write)

    class RAMManager:
        """Simula una gestión básica de memoria RAM limitada."""
        def __init__(self, size):
            self.size = size
            self.used = 0

        def allocate(self, amount):
            """Solicita una cantidad de memoria. Si no hay suficiente, retorna False."""
            if self.used + amount > self.size:
                print(f"[RAM] Error: Not enough memory to allocate {amount} bytes.")
                return False
            self.used += amount
            print(f"[RAM] Allocated {amount} bytes. Used: {self.used}/{self.size}")
            return True

        def free(self, amount):
            """Libera una cantidad de memoria previamente asignada."""
            self.used = max(0, self.used - amount)
            print(f"[RAM] Freed {amount} bytes. Used: {self.used}/{self.size}")

    def __init__(self, ram_size=1024, buffer_size=128, queue_size=10):
        self.BUFFER_SIZE = buffer_size
        self.IO_QUEUE_SIZE = queue_size
        self.devices = [
            InternalMemoryDevice("SSD", capacity=2048),
            RemovableMemoryDevice("USB Stick", capacity=1024),
            KeyboardDriverSimulator("Keyboard")
        ]
        self.io_queue = deque(maxlen=queue_size)
        self.ram = self.RAMManager(ram_size)

    def enqueue_io(self, device_id, operation, data=""):
        """Agrega una solicitud de E/S a la cola."""
        if len(self.io_queue) >= self.IO_QUEUE_SIZE:
            print("[SPOOLING] I/O queue is full. Request delayed.")
            return
        request = self.IORequest(device_id, operation, data)
        self.io_queue.append(request)
        print(f"[QUEUE] Enqueued {operation.upper()} on {self.devices[device_id].name}")

    def handle_io(self):
        """Procesa la siguiente solicitud de E/S en la cola."""
        if not self.io_queue:
            print("[QUEUE] No pending I/O operations.")
            return

        req = self.io_queue.popleft()
        dev = self.devices[req.device_id]

        if dev.busy:
            print(f"[BLOCKED] {dev.name} is busy. Re-enqueueing request.")
            self.enqueue_io(req.device_id, req.operation, req.data)
            return

        self._device_driver(dev, req)
        self._interrupt_handler(dev)

    def _device_driver(self, dev, req):
        """Simula la ejecución de un controlador de dispositivo (driver)."""
        dev.busy = True
        if req.operation == "write":
            dev.buffer = req.data[:self.BUFFER_SIZE]
            if self.ram.allocate(len(dev.buffer)):
                print(f"[DEVICE] {dev.name} writing: {dev.buffer}")
        elif req.operation == "read":
            dev.buffer = "Simulated input"
            if self.ram.allocate(len(dev.buffer)):
                print(f"[DEVICE] {dev.name} reading: {dev.buffer}")
        else:
            print(f"[ERROR] Unknown operation: {req.operation}")

    def _interrupt_handler(self, dev):
        """Simula un manejador de interrupciones."""
        print(f"[INTERRUPT] Operation completed on {dev.name}.")
        self.ram.free(len(dev.buffer))
        dev.buffer = ""
        dev.busy = False

    def run(self, delay=1):
        """Ejecuta el simulador procesando las solicitudes de la cola."""
        while self.io_queue:
            self.handle_io()
            time.sleep(delay)

    def status_report(self):
        """Muestra un resumen del estado actual del sistema."""
        print("\n=== DEVICE STATUS ===")
        for i, dev in enumerate(self.devices):
            state = "Busy" if dev.busy else "Idle"
            print(f"{i}. {dev.name}: {state}")
        print(f"[RAM] Usage: {self.ram.used}/{self.ram.size} bytes")
        print(f"[QUEUE] Pending: {len(self.io_queue)}\n")


if __name__ == "__main__":
    simulator = DeviceDriverSimulator()

    print("=== Simulación de Dispositivos ===")
    while True:
        print("\nSeleccione un dispositivo:")
        for i, device in enumerate(simulator.devices, start=1):
            print(f"{i}. {device.name}")
        print("4. Salir")

        choice = input("Ingrese el número del dispositivo: ")
        if choice == "4":
            print("Saliendo del programa...")
            break

        if choice not in ["1", "2", "3"]:
            print("Opción inválida. Intente nuevamente.")
            continue

        device_id = int(choice) - 1
        print(f"\nSeleccionado: {simulator.devices[device_id].name}")
        print("1. Leer")
        print("2. Escribir")
        print("3. Estado del dispositivo")
        print("4. Volver al menú principal")

        action = input("Seleccione una acción: ")
        match action:
            case "1":  # Leer
                simulator.enqueue_io(device_id, "read")
            case "2":  # Escribir
                data = input("Ingrese los datos a escribir: ")
                simulator.enqueue_io(device_id, "write", data)
            case "3":  # Estado del dispositivo
                simulator.status_report()
            case "4":  # Volver al menú principal
                continue
            case _:  # Opción inválida
                print("Opción inválida. Intente nuevamente.")

        simulator.run()