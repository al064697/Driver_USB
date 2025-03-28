"""
El programa simula un sistema que maneja la conexión y desconexión de dispositivos USB,
procesa operaciones de E/S mediante un hilo y muestra como se registran y manejan interrupciones para esos eventos
"""

import time, random, threading
from queue import Queue

"""
1. Clases de soporte: Representaciones de la "Tabla de Control de Dispositivos,
la Tabla de Manejadores, la Tabla de Interrupciones y la Cola de Operaciones de E/S
"""

class DeviceControlBlock: 
    """
    Simula la información de la Tabla de Control de Dispositivos
    Contiene metadatos sobre el dispositivo
    """
    def __init__(self, device_id, device_name, capacity_gb):
        self.device_id = device_id
        self.device_name = device_name
        self.capacity_gb = capacity_gb
        self.is_connected = True # Indica el estado del dispositivo

        
    def __str__(self):
        return f"[DCB] {self.device_name} (ID: {self.device_id} - Capacidad: {self.capacity_gb} GB)"
        
class InterruptTable: 
    """
    Simula una Tabla de Interrupciones.
    En un SO real, aquí se mapean rutinas de servicio a interrupciones. 
    En esta simulación solo registramos eventos y disparamos callbacks
    """
    def __init__(self): 
        self.interrupt_handlers = {}
    
    def register_interrupt_handler(self, interrupt_type, handler): 
        self.interrupt_handlers[interrupt_type] = handler

    def trigger_interrupt(self, interrupt_type, *args, **kwards): 
        """
        Llama a la función handler asociada al tipo de interrupción.
        """    
        if interrupt_type in self.interrupt_handlers:
            self.interrupt_handlers[interrupt_type](*args, **kwards)
        else: 
            print(f"[INTERRUPT] No se encontró un manejador para la interrupción {interrupt_type}")

class IOOPeration: 
    """
    Representa una operación de E/S en la Cola de Operaciones de E/S. 
    Tiene un un tipo (LECTURA/ESCRITURA), un tamaño de datos y un identificador de proceso.
    """
    def __init__(self, operation_type, data_size_mb, process_name):
        self.operation_type = operation_type
        self.data_size_mb = data_size_mb
        self.process_name = process_name

    def __str__(self):
        return (f"[IOOperation] Tipo: {self.operation_type},"
                f" Tamaño: {self.data_size_mb} MB,"
                f" Proceso: {self.process_name}")


"""
2. Driver de Dispositivo para USB
"""

class USBDriver: 
    """
    Simula un Manejador de Dispositivo específico para USB. 
    Se encarga de procesar operaciones de lectura y escritura, así como de
    interactuar con la Tabla de Interrupciones.
    """
    def __init__(self, device_control_block, interrupt_table):
        self.dcb = device_control_block
        self.interrupt_table = interrupt_table
        self.transfer_rate_mb_s = 30.0 # Velocidad de transferencia en MB/s

        # Se registran rutinas de interrupción específicas
        self.interrupt_table.register_interrupt_handler("USB_INSERT", self.on_usb_insert)
        self.interrupt_table.register_interrupt_handler("USB_REMOVE", self.on_usb_remove)

    def on_usb_insert(self): 
        print(f"[USB] Dispositivo {self.dcb.device_name} conectado")
        self.dcb.is_connected = True

    def on_usb_remove(self):
        print(f"[USB] Dispositivo {self.dcb.device_name} desconectado")
        self.dcb.is_connected = False
        
    def perform_operation(self, io_operation):
        if not self.dcb.is_connected:
            print(f"[USBDriver] ERROR: Dispositivo {self.dcb.device_name} no conectado")
            return
        
        try:
            print(f"[USBDriver] Iniciando operación de {io_operation} en {self.dcb.device_name}")
            transfer_time = io_operation.data_size_mb / self.transfer_rate_mb_s
            time.sleep(transfer_time)
            print(f"[USBDriver] Operación finalizada en {self.dcb.device_name}. Tiempo: {transfer_time:.2f} s\n")

        except OSError as e:
            print(f"[USBDriver] ERROR: No se pudo completar la operación. Detalle: {e}")

"""
3. Tabla de Manejadores de Dispositivos
"""
class DeviceDriverTable: 
    """
    Representa la tabla de drivers registrados en el sistema.
    Aquí registramos y buscamos los drivers por device_id. 
    """
    def __init__(self):
        # Diccionario: device_id -> instancia de USBDriver (u otro driver)
        self.drivers = {}

    def register_driver(self, device_id, driver_instance): 
        self.drivers[device_id] = driver_instance

    def get_driver(self, device_id): 
        return self.drivers.get(device_id, None)
    
"""
4. Sistema o Gerente de E/S que maneja la cola de operaciones
"""
class IOManager(threading.Thread): 
    """
    Hilo que se encarga de procesar la cola de operaciones de E/S.
    Toma operaciones en orden FIFO y las delega al driver correspondiente.
    """
    def __init__(self, driver_table): 
        super().__init__()
        self.daemon = True
        self.driver_table = driver_table
        self.operation_queue = Queue()
        self.running = True

    def run(self): 
        """
        Bucle principal: procesa operaciones de E/S encoladas.
        """
        while self.running: 
            try: 
                # Obtiene la siguiente operación (bloquea si no hay nada en la cola)
                device_id, io_op = self.operation_queue.get(timeout = 1)
                driver = self.driver_table.get_driver(device_id)
                if driver is not None:
                    driver.perform_operation(io_op)
                else: 
                    print(f"[IOManager] No hay driver registrado para device_id = {device_id}")
                self.operation_queue.task_done()
            except: 
                # Si no hay operaciones en 1 segundo, se repite el bucle
                pass

    def stop(self): 
        self.running = False

    def add_io_operation(self, device_id, io_operation): 
        """
        Agrega una operación de E/S a la cola. 
        """
        self.operation_queue.put((device_id, io_operation))

if __name__ == "__main__": 
    # 1. Crear la Tabla de Interrupciones
    interrupt_table = InterruptTable()

    # 2. Crear la Tabla de Drivers
    driver_table = DeviceDriverTable() 

    # 3. Crear el Device Control Block para la USB
    usb_dcb = DeviceControlBlock (
        device_id = 1, 
        device_name = "USB", 
        capacity_gb = 128
    )

    # 4. Crear el Driver del USB
    usb_driver = USBDriver(device_control_block = usb_dcb, interrupt_table = interrupt_table)
    driver_table.register_driver(usb_dcb.device_id, usb_driver)

    # 5. Iniciar el "IOManager (hilo que gestiona la cola de operaciones)"
    io_manager = IOManager(driver_table)
    io_manager.start()

    # 6. Simular eventos de conexión y operaciones de E/S
    interrupt_table.trigger_interrupt("USB_INSERT") # Simula la conexión de un dispositivo USB

    #Agregar varias operaciones de E/S
    io_ops = [
        IOOPeration("WRITE", 200, "Process A"), # Escribe 200 MB
        IOOPeration("READ", 50, "Process B"), # Lee 50 MB
        IOOPeration("WRITE", 100, "Process C"), # Escribe 100 MB
        IOOPeration("READ", 150, "Process D"), # Lee 150 MB
    ]

    for op in io_ops:
        io_manager.add_io_operation(usb_dcb.device_id, op)
        # Pequeña pausa para simular tiempos diferentes en llegada de solicitudes
        time.sleep(random.uniform(0.5, 1.5))

        # Se espera a que terminen la mayoría de operaciones
        time.sleep(3)

        # 7. Simular una "expulsión forzada" del USB (en medio de las operaciones) para ver el comportamiento
        interrupt_table.trigger_interrupt("USB_REMOVE ")

        # Intentar una nueva operación de escritura después de la expulsión
        io_manager.add_io_operation(usb_dcb.device_id, IOOPeration("WRITE", 300, "Process E"))

        # Esperar unos segundos apra observar los mensajes
        time.sleep(5)

        # 8. Finalizar el hilo de E/S y cerrar el programa
        io_manager.stop()
        print("[MAIN] Simulación finalizada.")