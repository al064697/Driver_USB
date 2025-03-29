import threading
import time
import keyboard  # pip install keyboard
from collections import deque
from DeviceDriverSimulator import DeviceDriverSimulator

class KeyboardDriverSimulator(DeviceDriverSimulator.Device):
    """
    Simula un driver de teclado con interrupciones, buffer de entrada,
    y captura de eventos de tecla (presionar y soltar).
    """
    def __init__(self, name="Keyboard", buffer_size=20):
        super().__init__(name)
        self.buffer = deque(maxlen=buffer_size)
        self.running = False
        self.lock = threading.Lock()

    def _keyboard_interrupt(self, event):
        """
        Función manejadora de interrupciones. Se activa en cada evento de teclado.

        Args:
            event: Evento de tecla (tecla presionada o soltada)
        """
        with self.lock:
            self.buffer.append({
                "key": event.name,
                "event_type": event.event_type,  # 'down' o 'up'
                "timestamp": time.time()
            })
            print(f"[INTERRUPT] {event.event_type.upper()} - '{event.name}'")

    def start(self):
        """Inicia la simulación del driver y captura de eventos."""
        self.running = True
        keyboard.hook(self._keyboard_interrupt)
        print("[KEYBOARD DRIVER] Listening to keyboard. Press ESC to stop.")
        
        try:
            while self.running:
                if keyboard.is_pressed('esc'):
                    self.running = False
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.running = False
        finally:
            keyboard.unhook_all()
            print("[KEYBOARD DRIVER] Stopped.")

    def read_buffer(self):
        """Simula la lectura del buffer desde el sistema operativo."""
        with self.lock:
            while self.buffer:
                entry = self.buffer.popleft()
                print(f"[READ] {entry['event_type'].upper()} '{entry['key']}' at {entry['timestamp']}")

# --- Simulación en ejecución separada ---

def os_reader(driver):
    """Simula el sistema operativo leyendo del driver de teclado."""
    while driver.running:
        driver.read_buffer()
        time.sleep(1)  # Simula latencia del sistema

if __name__ == "__main__":
    driver = KeyboardDriverSimulator()

    # Hilo para el lector del SO
    reader_thread = threading.Thread(target=os_reader, args=(driver,), daemon=True)

    # Inicia hilo del lector
    reader_thread.start()

    # Ejecuta el driver
    driver.start()