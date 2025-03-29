from DeviceDriverSimulator import DeviceDriverSimulator
import time
import random
from collections import deque

class RemovableMemoryDevice(DeviceDriverSimulator.Device):
    """
    Simula un dispositivo de almacenamiento extraíble como una memoria USB.
    Soporta operaciones de bloque, inserción/extracción y latencia de acceso.
    """
    def __init__(self, name="USB Stick", capacity=1024, block_size=128):
        super().__init__(name)
        self.capacity = capacity  # Capacidad total en bytes
        self.block_size = block_size
        self.total_blocks = capacity // block_size
        self.storage = [""] * self.total_blocks
        self.inserted = True
        self.block_state = ["free"] * self.total_blocks
        self.failure_chance = 0.03  # 3% de fallo en operación simulada

    def simulate_latency(self, min_ms=20, max_ms=200):
        """Simula latencia de hardware."""
        delay = random.uniform(min_ms, max_ms) / 1000.0
        time.sleep(delay)

    def simulate_failure(self):
        """Simula error de lectura/escritura aleatorio."""
        return random.random() < self.failure_chance

    def eject(self):
        """Extrae la memoria USB de forma segura."""
        self.inserted = False
        print(f"[REMOVABLE] {self.name} has been safely removed.")

    def insert(self):
        """Inserta o reconecta la memoria USB."""
        self.inserted = True
        print(f"[REMOVABLE] {self.name} inserted.")

    def write_block(self, block_num, data):
        """Escribe datos en un bloque específico si está insertado."""
        if not self.inserted:
            print(f"[ERROR] {self.name} not inserted.")
            return False
        if block_num >= self.total_blocks:
            print(f"[ERROR] {self.name}: Block {block_num} out of range.")
            return False
        self.simulate_latency()
        if self.simulate_failure():
            print(f"[FAILURE] {self.name}: Write failure on block {block_num}!")
            return False
        self.storage[block_num] = data[:self.block_size]
        self.block_state[block_num] = "used"
        print(f"[WRITE] {self.name}: Block {block_num} <- '{data[:30]}...'")
        return True

    def read_block(self, block_num):
        """Lee datos de un bloque específico si está insertado."""
        if not self.inserted:
            print(f"[ERROR] {self.name} not inserted.")
            return ""
        if block_num >= self.total_blocks:
            print(f"[ERROR] {self.name}: Block {block_num} out of range.")
            return ""
        self.simulate_latency()
        if self.simulate_failure():
            print(f"[FAILURE] {self.name}: Read failure on block {block_num}!")
            return "[READ FAILURE]"
        data = self.storage[block_num]
        print(f"[READ] {self.name}: Block {block_num} -> '{data[:30]}...'")
        return data

    def status(self):
        """Muestra información del dispositivo."""
        used = self.block_state.count("used")
        print(f"[{self.name}] Status: {used}/{self.total_blocks} blocks used.")