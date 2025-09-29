import tkinter as tk
from tkinter import messagebox, ttk
import random
from multiprocessing import Process, Queue
import threading

def has_pair(numbers):
    return len(numbers) != len(set(numbers))

def run_simulation_worker(n, m, q):
    pair_count = 0
    for _ in range(m):
        numbers = [random.randint(1, 365) for _ in range(n)]
        if has_pair(numbers):
            pair_count += 1
    q.put(pair_count)

def run_simulation():
    try:
        N = int(entry_n.get())
        M = int(entry_m.get())
        
        if N < 1 or M < 1:
            messagebox.showerror("Ошибка", "N и M должны быть положительными числами!")
            return
        if N > 365:
            messagebox.showerror("Ошибка", "N не может превышать 365!")
            return

        progress_bar["value"] = 0
        result_label.config(text="Моделирование выполняется...")
        root.update()

        num_processes = min(8, M)
        batch = M // num_processes
        processes = []
        queue = Queue()

        for i in range(num_processes):
            m_chunk = batch if i < num_processes - 1 else M - batch * (num_processes - 1)
            p = Process(target=run_simulation_worker, args=(N, m_chunk, queue))
            processes.append(p)
            p.start()

        def monitor():
            collected = 0
            total_pairs = 0
            while collected < num_processes:
                result = queue.get()
                total_pairs += result
                collected += 1
                progress_bar["value"] = (collected / num_processes) * 100
                root.update()
            result_label.config(text=f"Случаев с парами: {total_pairs} из {M}")
            log_text.insert(tk.END, f"Результат: {total_pairs} пар из {M} итераций\n")
            log_text.see(tk.END)

        threading.Thread(target=monitor, daemon=True).start()

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите целые числа для N и M!")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Парадокс дней рождения (многопроцессный)")
    root.geometry("400x400")

    tk.Label(root, text="Введите N (количество чисел):").pack(pady=5)
    entry_n = tk.Entry(root)
    entry_n.pack()

    tk.Label(root, text="Введите M (количество повторений):").pack(pady=5)
    entry_m = tk.Entry(root)
    entry_m.pack()

    tk.Button(root, text="Запустить моделирование", command=lambda: threading.Thread(target=run_simulation, daemon=True).start()).pack(pady=10)

    progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
    progress_bar.pack(pady=10)

    result_label = tk.Label(root, text="Результат появится здесь")
    result_label.pack(pady=10)

    tk.Label(root, text="История результатов:").pack()
    log_text = tk.Text(root, height=8, width=40)
    log_text.pack(pady=5)
    scrollbar = tk.Scrollbar(root, command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)

    root.mainloop()
