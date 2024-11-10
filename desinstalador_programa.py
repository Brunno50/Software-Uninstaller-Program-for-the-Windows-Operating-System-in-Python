import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

def get_installed_programs():
    # Obtém a lista de programas instalados usando PowerShell
    command = r'powershell "Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion, EstimatedSize"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    lines = result.stdout.splitlines()[3:]  # Ignora as 3 primeiras linhas do PowerShell

    # Filtra e estrutura os dados dos programas instalados
    programs = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            size = parts[-1]
            version = parts[-2]
            name = " ".join(parts[:-2])

            # Verifica se o tamanho é um número antes de converter para evitar erro
            try:
                size_in_mb = f"{int(size) / 1024:.2f} MB"
            except ValueError:
                size_in_mb = "Desconhecido"  # Define como desconhecido se não puder converter para número

            programs.append((name.strip(), version.strip(), size_in_mb))
        elif len(parts) == 2:
            programs.append((parts[0].strip(), parts[1].strip(), "Desconhecido"))
        elif parts:
            programs.append((parts[0].strip(), "", "Desconhecido"))
    return programs

def uninstall_program(program_name):
    try:
        # Executa o comando de desinstalação usando o nome do programa
        command = f'powershell "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Where-Object {{$_.DisplayName -eq \'{program_name}\'}} | ForEach-Object {{$_.UninstallString}}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.stdout.strip():
            uninstall_command = result.stdout.strip()
            subprocess.run(uninstall_command, shell=True)
            messagebox.showinfo("Desinstalação", f"{program_name} desinstalado com sucesso.")
        else:
            messagebox.showerror("Erro", f"Não foi possível encontrar o comando de desinstalação para {program_name}.")
        
        # Atualiza a lista de programas após a desinstalação
        tree.delete(*tree.get_children())
        load_programs()
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def load_programs():
    programs = get_installed_programs()
    for program, version, size in programs:
        tree.insert("", tk.END, values=(program, version, size))

# Interface Gráfica com Tkinter
root = tk.Tk()
root.title("Programas e Recursos")
root.geometry("700x400")

# Configuração das cores no estilo modo noturno do Telegram com texto azul
root.configure(bg="#2A2F32")  # Fundo escuro
telegram_blue = "#0088cc"  # Cor azul do Telegram
style = ttk.Style(root)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#2A2F32", foreground=telegram_blue)  # Texto azul para o cabeçalho
style.configure("Treeview", font=("Segoe UI", 10), background="#212529", fieldbackground="#2A2F32", foreground=telegram_blue)  # Texto azul na tabela
style.map("Treeview.Heading", background=[('active', '#212529')])  # Fundo do cabeçalho quando ativo

# Frame para conter o Treeview e a Scrollbar
frame = tk.Frame(root, bg="#2A2F32")
frame.pack(fill="both", expand=True, pady=10)

# Tabela Treeview para listar os programas, versões e tamanhos
tree = ttk.Treeview(frame, columns=("Nome", "Versão", "Tamanho"), show="headings")
tree.heading("Nome", text="Nome")
tree.heading("Versão", text="Versão")
tree.heading("Tamanho", text="Tamanho")
tree.column("Nome", anchor="w", width=400)
tree.column("Versão", anchor="center", width=100)
tree.column("Tamanho", anchor="center", width=100)
tree.pack(side="left", fill="both", expand=True)

# Configuração da Scrollbar personalizada
scrollbar = tk.Scrollbar(frame, orient="vertical", command=tree.yview, bg="#2A2F32", troughcolor="#2A2F32", activebackground="#3B4A54")
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# Botão para desinstalar o programa selecionado com texto azul
def on_uninstall():
    selected_item = tree.selection()
    if selected_item:
        selected_program = tree.item(selected_item, "values")[0]
        response = messagebox.askyesno("Confirmação", f"Tem certeza que deseja desinstalar {selected_program}?")
        if response:
            uninstall_program(selected_program)

button = tk.Button(root, text="Desinstalar Programa Selecionado", command=on_uninstall, font=("Segoe UI", 10, "bold"), bg="#3B4A54", fg=telegram_blue, activebackground="#212529", activeforeground=telegram_blue)
button.pack(pady=10)

# Carregar a lista de programas ao iniciar
load_programs()

root.mainloop()
