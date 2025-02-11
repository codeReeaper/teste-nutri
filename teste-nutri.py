import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF

# Criar banco de dados SQLite
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    peso REAL,
    altura REAL,
    imc REAL,
    data TEXT
)
""")
conn.commit()

# Função para calcular IMC e salvar no banco
def calcular_imc():
    try:
        nome = entry_nome.get().strip()
        peso = float(entry_peso.get())
        altura = float(entry_altura.get())

        if not nome:
            messagebox.showerror("Erro", "Por favor, insira um nome válido.")
            return

        imc = peso / (altura ** 2)
        categoria = (
            "Abaixo do peso" if imc < 18.5 else
            "Peso normal" if imc < 24.9 else
            "Sobrepeso" if imc < 29.9 else
            "Obesidade"
        )

        resultado_label.config(text=f"IMC: {imc:.2f}\nCategoria: {categoria}")

        # Salvar no banco de dados
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO usuarios (nome, peso, altura, imc, data) VALUES (?, ?, ?, ?, ?)",
                       (nome, peso, altura, imc, data_atual))
        conn.commit()

        atualizar_grafico(nome)

    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira valores válidos para peso e altura.")

# Função para gerar PDF com recomendações personalizadas
def gerar_pdf():
    nome = entry_nome.get().strip()
    if not nome:
        messagebox.showerror("Erro", "Por favor, insira um nome válido.")
        return

    peso = float(entry_peso.get())
    altura = float(entry_altura.get())
    imc = peso / (altura ** 2)

    pasta_usuario = os.path.join(os.getcwd(), "Usuarios", nome)
    os.makedirs(pasta_usuario, exist_ok=True)
    caminho_pdf = os.path.join(pasta_usuario, f"relatorio_{nome}.pdf")

    recomendacao = (
        "Para ganhar massa, aumente a ingestão de proteínas e pratique musculação."
        if imc < 18.5 else
        "Mantenha uma alimentação equilibrada e exercícios moderados para se manter saudável."
        if imc < 24.9 else
        "Reduza o consumo de calorias e aumente atividades aeróbicas para perder peso."
    )

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Relatório de Saúde e Nutrição", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Nome: {nome}", ln=True)
    pdf.cell(200, 10, f"Peso: {peso} kg", ln=True)
    pdf.cell(200, 10, f"Altura: {altura} m", ln=True)
    pdf.cell(200, 10, f"IMC: {imc:.2f}", ln=True)
    pdf.cell(200, 10, f"Recomendação: {recomendacao}", ln=True)

    pdf.output(caminho_pdf)
    messagebox.showinfo("PDF Gerado!", f"Relatório salvo em:\n{caminho_pdf}")

# Função para atualizar o gráfico de IMC no histórico
def atualizar_grafico(nome):
    cursor.execute("SELECT data, imc FROM usuarios WHERE nome = ? ORDER BY data", (nome,))
    dados = cursor.fetchall()

    if not dados:
        return

    datas = [d[0] for d in dados]
    imcs = [d[1] for d in dados]

    ax.clear()
    ax.plot(datas, imcs, marker="o", linestyle="-", color="blue")
    ax.set_title(f"Evolução do IMC de {nome}")
    ax.set_xlabel("Data")
    ax.set_ylabel("IMC")
    ax.grid(True)
    canvas.draw()

# Criando a janela principal
root = tk.Tk()
root.title("Calculadora de IMC")
root.geometry("600x500")
root.resizable(False, False)

# Criando um Notebook (abas de navegação)
notebook = ttk.Notebook(root)
notebook.pack(pady=10, fill="both", expand=True)

# Criando as abas
aba_inicio = ttk.Frame(notebook)
aba_historico = ttk.Frame(notebook)
aba_config = ttk.Frame(notebook)

notebook.add(aba_inicio, text="Início")
notebook.add(aba_historico, text="Histórico")
notebook.add(aba_config, text="Configurações")

# Layout da Aba Início
ttk.Label(aba_inicio, text="Nome:").pack(pady=2)
entry_nome = ttk.Entry(aba_inicio)
entry_nome.pack(pady=2)

ttk.Label(aba_inicio, text="Peso (kg):").pack(pady=2)
entry_peso = ttk.Entry(aba_inicio)
entry_peso.pack(pady=2)

ttk.Label(aba_inicio, text="Altura (m):").pack(pady=2)
entry_altura = ttk.Entry(aba_inicio)
entry_altura.pack(pady=2)

botao_calcular = ttk.Button(aba_inicio, text="Calcular IMC", command=calcular_imc)
botao_calcular.pack(pady=10)

resultado_label = ttk.Label(aba_inicio, text="IMC: -\nCategoria: -", font=("Arial", 12, "bold"))
resultado_label.pack(pady=5)

botao_pdf = ttk.Button(aba_inicio, text="Gerar PDF", command=gerar_pdf)
botao_pdf.pack(pady=10)

# Aba Histórico - Gráfico
ttk.Label(aba_historico, text="Histórico de IMC").pack(pady=5)
fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=aba_historico)
canvas.get_tk_widget().pack()

# Aba Configurações (ainda será implementada)
ttk.Label(aba_config, text="Configurações do Aplicativo (Em breve)").pack(pady=20)

# Rodando o app
root.mainloop()
