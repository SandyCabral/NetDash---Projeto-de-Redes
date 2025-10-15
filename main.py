import tkinter as tk
from tkinter import ttk
import subprocess
import platform
import re
import time
import statistics
import threading  # Importamos a biblioteca de threading


# ==============================================================================
#  MOTOR DE MONITORAMENTO (Nosso código anterior, sem alterações)
# ==============================================================================

def ping_target(target):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', target]
    encoding = 'cp850' if platform.system().lower() == 'windows' else 'utf-8'

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=5, check=True, encoding=encoding
        )
        match = re.search(r"(?:tempo|time)=([\d.]+)\s?ms", result.stdout)
        if match:
            return float(match.group(1))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return None


# ==============================================================================
#  INTERFACE GRÁFICA (Agora com as funções dos botões)
# ==============================================================================

class NetDashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetDash - Monitor de Rede")
        self.root.geometry("400x250")

        self.is_monitoring = False
        self.monitor_thread = None

        # --- Widgets da Interface (código anterior) ---
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))

        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)
        ttk.Label(input_frame, text="Alvo (IP ou domínio):").pack(side=tk.LEFT, padx=(0, 10))
        self.target_entry = ttk.Entry(input_frame)
        self.target_entry.pack(fill=tk.X, expand=True)
        self.target_entry.insert(0, "8.8.8.8")

        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # Conectamos os botões a novas funções
        self.start_button = ttk.Button(control_frame, text="Iniciar", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.stop_button = ttk.Button(control_frame, text="Parar", state=tk.DISABLED, command=self.stop_monitoring)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        results_frame = ttk.Frame(self.root, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(results_frame, text="Resultados", style="Header.TLabel").grid(row=0, column=0, columnspan=2,
                                                                                sticky="w")
        ttk.Label(results_frame, text="Latência Atual:").grid(row=1, column=0, sticky="w", pady=5)
        self.latency_label = ttk.Label(results_frame, text="N/A")
        self.latency_label.grid(row=1, column=1, sticky="w", pady=5)
        ttk.Label(results_frame, text="Média de Latência:").grid(row=2, column=0, sticky="w", pady=5)
        self.average_label = ttk.Label(results_frame, text="N/A")
        self.average_label.grid(row=2, column=1, sticky="w", pady=5)
        ttk.Label(results_frame, text="Jitter:").grid(row=3, column=0, sticky="w", pady=5)
        self.jitter_label = ttk.Label(results_frame, text="N/A")
        self.jitter_label.grid(row=3, column=1, sticky="w", pady=5)

        # Garante que a thread de monitoramento pare ao fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_monitoring(self):
        self.is_monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        target = self.target_entry.get()
        # Criamos e iniciamos a thread para não travar a interface
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, args=(target,))
        self.monitor_thread.daemon = True  # Permite que a thread feche com o programa
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.latency_label.config(text="N/A")
        self.average_label.config(text="N/A")
        self.jitter_label.config(text="N/A")

    def monitoring_loop(self, target):
        latencies = []
        while self.is_monitoring:
            latency = ping_target(target)
            if latency is not None and self.is_monitoring:
                latencies.append(latency)
                latencies = latencies[-30:]

                latest = latencies[-1]
                average = statistics.mean(latencies)
                jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0

                # Atualiza os textos da interface
                self.latency_label.config(text=f"{latest:.2f} ms")
                self.average_label.config(text=f"{average:.2f} ms")
                self.jitter_label.config(text=f"{jitter:.2f} ms")
            else:
                self.latency_label.config(text="Falha")

            time.sleep(1)

    def on_closing(self):
        self.is_monitoring = False
        self.root.destroy()


# ==============================================================================
#  PONTO DE ENTRADA DO PROGRAMA
# ==============================================================================
if __name__ == "__main__":
    main_window = tk.Tk()
    app = NetDashApp(main_window)
    main_window.mainloop()
