import random
import time
import threading
from collections import OrderedDict

class InternalMemoryDevice:
    """
    Simulación avanzada de un dispositivo de memoria interna (SSD o RAM persistente).
    Maneja bloques de memoria, errores, caché LRU y latencia realista.
    """
    def __init__(self, name="SSD Interno", capacity=4096, block_size=256, cache_size=4):
        self.name = name
        self.block_size = block_size
        self.total_blocks = capacity // block_size
        self.storage = [""] * self.total_blocks
        self.block_state = ["free"] * self.total_blocks
        self.lock = threading.Lock()

        # Simulación de caché con LRU
        self.cache = OrderedDict()
        self.cache_size = cache_size

        # Probabilidad de error simulada (por bloque)
        self.failure_chance = 0.05  # 5%

        print(f"[INIT] {self.name} initialized with {self.total_blocks} blocks.")

    def simulate_latency(self, min_ms=10, max_ms=100):
        """Simula latencia del dispositivo en ms."""
        delay = random.uniform(min_ms, max_ms) / 1000.0
        time.sleep(delay)

    def simulate_failure(self):
        """Simula un posible fallo de hardware."""
        return random.random() < self.failure_chance

    def write_block(self, block_num, data):
        """
        Escribe datos en un bloque específico.

        Args:
            block_num (int): Número del bloque.
            data (str): Datos a escribir.

        Returns:
            bool: True si tuvo éxito, False si hubo error simulado.
        """
        with self.lock:
            self.simulate_latency()

            if block_num >= self.total_blocks:
                print(f"[ERROR] {self.name}: Block {block_num} out of range.")
                return False

            if self.simulate_failure():
                print(f"[FAILURE] {self.name}: Write failure on block {block_num}!")
                return False

            self.storage[block_num] = data[:self.block_size]
            self.block_state[block_num] = "used"

            # Actualizar caché
            self._update_cache(block_num, data[:self.block_size])

            print(f"[WRITE] {self.name}: Block {block_num} <- '{data[:30]}...'")
            return True

    def read_block(self, block_num):
        """
        Lee los datos de un bloque específico.

        Args:
            block_num (int): Número del bloque.

        Returns:
            str: Contenido del bloque o mensaje de error.
        """
        with self.lock:
            self.simulate_latency()

            if block_num >= self.total_blocks:
                print(f"[ERROR] {self.name}: Block {block_num} out of range.")
                return ""

            if self.simulate_failure():
                print(f"[FAILURE] {self.name}: Read failure on block {block_num}!")
                return "[BLOCK READ FAILURE]"

            # Intentar lectura desde caché
            if block_num in self.cache:
                data = self.cache[block_num]
                print(f"[CACHE HIT] {self.name}: Block {block_num} -> '{data[:30]}...'")
                self.cache.move_to_end(block_num)
                return data

            # Si no está en caché, leer de almacenamiento y guardar en caché
            data = self.storage[block_num]
            self._update_cache(block_num, data)
            print(f"[READ] {self.name}: Block {block_num} -> '{data[:30]}...'")
            return data

    def _update_cache(self, block_num, data):
        """Mantiene la caché LRU al día."""
        if block_num in self.cache:
            self.cache.move_to_end(block_num)
        else:
            if len(self.cache) >= self.cache_size:
                evicted = self.cache.popitem(last=False)
                print(f"[CACHE EVICT] {self.name}: Block {evicted[0]}")
            self.cache[block_num] = data

    def status(self):
        """Muestra un resumen del estado de la memoria."""
        used = self.block_state.count("used")
        print(f"\n[{self.name}] STATUS")
        print(f"Blocks used: {used}/{self.total_blocks}")
        print(f"Cache: {[k for k in self.cache.keys()]}\n")