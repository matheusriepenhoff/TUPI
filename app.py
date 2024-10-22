from flask import Flask, render_template, request, redirect
import pandas as pd
import os
import math

app = Flask(__name__)

# Caminho do arquivo Excel
data_file = "pacientes.xlsx"

# Lista de Comorbidades
comorbidades_list = [
    "Dislipidemia",
    "AVC",
    "Demência",
    "Acamado",
    "DPOC",
    "Nefropatia",
    "Hepatopatia",
    "Hipotireoidismo",
    "Polifarmácia"
]

# Função para carregar dados existentes
def carregar_dados():
    if os.path.exists(data_file):
        pacientes_df = pd.read_excel(data_file, engine='openpyxl')
        print(f"Arquivo {data_file} carregado com sucesso.")

        # Remover colunas desnecessárias
        colunas_para_remover = ['Score 2', 'Pontuação']
        for coluna in colunas_para_remover:
            if coluna in pacientes_df.columns:
                pacientes_df = pacientes_df.drop(columns=[coluna])
                print(f"Coluna '{coluna}' removida.")

        # Garantir que todas as comorbidades estejam presentes
        for comorbidade in comorbidades_list:
            if comorbidade not in pacientes_df.columns:
                pacientes_df[comorbidade] = 'Não'

        # Garantir que os campos 'Visitado' e 'Internação Recente' estejam presentes
        if 'Visitado' in pacientes_df.columns:
            pacientes_df['Visitado'] = pacientes_df['Visitado'].fillna(False).astype(bool)
        else:
            pacientes_df['Visitado'] = False

        if 'Internação Recente' in pacientes_df.columns:
            pacientes_df['Internação Recente'] = pacientes_df['Internação Recente'].fillna('Não')
        else:
            pacientes_df['Internação Recente'] = 'Não'

        # Garantir que a coluna 'Medicamentos' esteja presente
        if 'Medicamentos' not in pacientes_df.columns:
            pacientes_df['Medicamentos'] = ''

        # Garantir que as colunas numéricas estejam no tipo correto
        num_cols = ['Idade', 'Colesterol Total', 'HDL', 'Pressão Sistólica', 'Creatinina Sérica', 'Score Framingham', 'CKD-EPI', 'Risco Total']
        for col in num_cols:
            if col in pacientes_df.columns:
                pacientes_df[col] = pd.to_numeric(pacientes_df[col], errors='coerce').fillna(0)
            else:
                pacientes_df[col] = 0

        print("Dados carregados e processados.")
    else:
        pacientes_df = pd.DataFrame(columns=[
            'Nome', 'CNS', 'Idade', 'Sexo', 'Diabetes', 'Hipertensão', 'Colesterol Total', 'HDL',
            'Pressão Sistólica', 'Tratamento Hipertensão', 'Creatinina Sérica', 'Fumante',
            'Internação Recente', 'Medicamentos', 'CKD-EPI', 'Classificação CKD-EPI',
            'Score Framingham', 'Classificação Framingham', 'Risco Total', 'Visitado'
        ])
        # Adicionar colunas para comorbidades
        for comorbidade in comorbidades_list:
            pacientes_df[comorbidade] = 'Não'
        print(f"Arquivo {data_file} não encontrado. DataFrame vazio criado.")
    return pacientes_df

# Carregar dados existentes, se disponível
pacientes_df = carregar_dados()

@app.route('/')
def index():
    # Ordenar pacientes: não visitados primeiro, depois visitados, ambos por risco total decrescente
    pacientes_df['Visitado'] = pacientes_df['Visitado'].fillna(False).astype(bool)
    pacientes_ordenados = pacientes_df.sort_values(by=['Visitado', 'Risco Total'], ascending=[True, False]).reset_index(drop=True)
    return render_template('index.html', pacientes=pacientes_ordenados.to_dict(orient='records'), comorbidades=comorbidades_list)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        try:
            campos_necessarios = [
                'nome', 'cns', 'idade', 'sexo', 'diabetes', 'hipertensao',
                'colesterol_total', 'hdl', 'pressao_sistolica', 'tratamento_hipertensao',
                'creatinina_serica', 'fumante', 'internacao_recente'
            ]

            # Verificar se todos os campos obrigatórios estão presentes
            for campo in campos_necessarios:
                if campo not in request.form or not request.form.get(campo):
                    return f"Erro: Campo ausente ou inválido - {campo}", 400

            # Criar o dicionário do novo paciente
            novo_paciente = {
                'Nome': request.form['nome'],
                'CNS': request.form['cns'],
                'Idade': int(request.form['idade']),
                'Sexo': request.form['sexo'],
                'Diabetes': request.form['diabetes'],
                'Hipertensão': request.form['hipertensao'],
                'Colesterol Total': float(request.form['colesterol_total']),
                'HDL': float(request.form['hdl']),
                'Pressão Sistólica': float(request.form['pressao_sistolica']),
                'Tratamento Hipertensão': request.form['tratamento_hipertensao'],
                'Creatinina Sérica': float(request.form['creatinina_serica']),
                'Fumante': request.form['fumante'],
                'Internação Recente': request.form['internacao_recente'],
                'Medicamentos': request.form.get('medicamentos', ''),
                'Visitado': False
            }

            # Processar Comorbidades
            for comorbidade in comorbidades_list:
                if comorbidade in request.form.getlist('comorbidades'):
                    novo_paciente[comorbidade] = 'Sim'
                else:
                    novo_paciente[comorbidade] = 'Não'

        except ValueError as e:
            return f"Erro: Valor inválido - {str(e)}", 400

        # Validar dados do paciente
        if not validar_paciente(novo_paciente):
            return "Erro: Dados do paciente inválidos", 400

        # Calcular o Score de Framingham
        novo_paciente['Score Framingham'] = calcular_score_framingham(novo_paciente)
        novo_paciente['Classificação Framingham'] = classificar_framingham(novo_paciente['Score Framingham'])

        # Calcular o CKD-EPI
        novo_paciente['CKD-EPI'] = calcular_ckd_epi(novo_paciente)
        novo_paciente['Classificação CKD-EPI'] = classificar_ckd_epi(novo_paciente['CKD-EPI'])

        # Calcular o risco total considerando comorbidades, idade e internação recente
        novo_paciente['Risco Total'] = calcular_risco_total(novo_paciente)

        # Adicionar novo paciente ao DataFrame usando pd.concat()
        global pacientes_df
        novo_paciente_df = pd.DataFrame([novo_paciente])
        pacientes_df = pd.concat([pacientes_df, novo_paciente_df], ignore_index=True)

        salvar_dados()
        return redirect('/')
    return render_template('adicionar.html', comorbidades=comorbidades_list)

@app.route('/remover/<int:paciente_id>', methods=['POST'])
def remover(paciente_id):
    global pacientes_df
    if 0 <= paciente_id < len(pacientes_df):
        pacientes_df = pacientes_df.drop(paciente_id).reset_index(drop=True)
        salvar_dados()
    return redirect('/')

@app.route('/marcar_visitado/<int:paciente_id>', methods=['POST'])
def marcar_visitado(paciente_id):
    global pacientes_df
    if 0 <= paciente_id < len(pacientes_df):
        pacientes_df.at[paciente_id, 'Visitado'] = True
        salvar_dados()
    return redirect('/')

@app.route('/editar/<int:paciente_id>', methods=['GET', 'POST'])
def editar(paciente_id):
    global pacientes_df
    if paciente_id < 0 or paciente_id >= len(pacientes_df):
        return "Paciente não encontrado.", 404

    paciente = pacientes_df.iloc[paciente_id].to_dict()

    if request.method == 'POST':
        try:
            campos_necessarios = [
                'nome', 'cns', 'idade', 'sexo', 'diabetes', 'hipertensao',
                'colesterol_total', 'hdl', 'pressao_sistolica', 'tratamento_hipertensao',
                'creatinina_serica', 'fumante', 'internacao_recente'
            ]

            # Verificar se todos os campos obrigatórios estão presentes
            for campo in campos_necessarios:
                if campo not in request.form or not request.form.get(campo):
                    return f"Erro: Campo ausente ou inválido - {campo}", 400

            # Atualizar os dados do paciente
            pacientes_df.at[paciente_id, 'Nome'] = request.form['nome']
            pacientes_df.at[paciente_id, 'CNS'] = request.form['cns']
            pacientes_df.at[paciente_id, 'Idade'] = int(request.form['idade'])
            pacientes_df.at[paciente_id, 'Sexo'] = request.form['sexo']
            pacientes_df.at[paciente_id, 'Diabetes'] = request.form['diabetes']
            pacientes_df.at[paciente_id, 'Hipertensão'] = request.form['hipertensao']
            pacientes_df.at[paciente_id, 'Colesterol Total'] = float(request.form['colesterol_total'])
            pacientes_df.at[paciente_id, 'HDL'] = float(request.form['hdl'])
            pacientes_df.at[paciente_id, 'Pressão Sistólica'] = float(request.form['pressao_sistolica'])
            pacientes_df.at[paciente_id, 'Tratamento Hipertensão'] = request.form['tratamento_hipertensao']
            pacientes_df.at[paciente_id, 'Creatinina Sérica'] = float(request.form['creatinina_serica'])
            pacientes_df.at[paciente_id, 'Fumante'] = request.form['fumante']
            pacientes_df.at[paciente_id, 'Internação Recente'] = request.form['internacao_recente']
            pacientes_df.at[paciente_id, 'Medicamentos'] = request.form.get('medicamentos', '')

            # Processar Comorbidades
            for comorbidade in comorbidades_list:
                if comorbidade in request.form.getlist('comorbidades'):
                    pacientes_df.at[paciente_id, comorbidade] = 'Sim'
                else:
                    pacientes_df.at[paciente_id, comorbidade] = 'Não'

        except ValueError as e:
            return f"Erro: Valor inválido - {str(e)}", 400

        # Validar dados do paciente
        if not validar_paciente(pacientes_df.iloc[paciente_id].to_dict()):
            return "Erro: Dados do paciente inválidos", 400

        # Recalcular Scores
        pacientes_df.at[paciente_id, 'Score Framingham'] = calcular_score_framingham(pacientes_df.iloc[paciente_id].to_dict())
        pacientes_df.at[paciente_id, 'Classificação Framingham'] = classificar_framingham(pacientes_df.at[paciente_id, 'Score Framingham'])

        pacientes_df.at[paciente_id, 'CKD-EPI'] = calcular_ckd_epi(pacientes_df.iloc[paciente_id].to_dict())
        pacientes_df.at[paciente_id, 'Classificação CKD-EPI'] = classificar_ckd_epi(pacientes_df.at[paciente_id, 'CKD-EPI'])

        pacientes_df.at[paciente_id, 'Risco Total'] = calcular_risco_total(pacientes_df.iloc[paciente_id].to_dict())

        salvar_dados()
        return redirect('/')

    return render_template('editar.html', paciente=paciente, paciente_id=paciente_id, comorbidades=comorbidades_list)

def salvar_dados():
    # Salvar o DataFrame para o Excel
    pacientes_df_copy = pacientes_df.copy()

    # Garantir que as comorbidades sejam 'Sim' ou 'Não' nas colunas separadas
    # Já estão separadas, então não é necessário serializar

    # Garantir que o campo Visitado seja booleano
    pacientes_df_copy['Visitado'] = pacientes_df_copy['Visitado'].astype(bool)

    # Salvar no Excel
    pacientes_df_copy.to_excel(data_file, index=False, engine='openpyxl')
    print(f"Dados salvos em {data_file}. Total de pacientes: {len(pacientes_df)}")

def validar_paciente(paciente):
    # Validação básica dos dados do paciente
    if not paciente['Nome'] or not paciente['CNS']:
        return False
    if paciente['Sexo'] not in ['Masculino', 'Feminino']:
        return False
    if paciente['Internação Recente'] not in ['Sim', 'Não']:
        return False
    # Removemos o limite de idade
    try:
        idade = int(paciente['Idade'])
        if idade < 0 or idade > 120:
            return False
    except ValueError:
        return False
    # Adicione outras regras de validação conforme necessário
    return True

def calcular_score_framingham(paciente):
    idade = paciente['Idade']
    if idade < 30:
        return 0  # Não calcula para menores de 30
    elif idade > 79:
        idade = 79  # Usa 79 como idade máxima

    # Coeficientes β
    coef = {}
    col_tot = paciente['Colesterol Total']
    hdl = paciente['HDL']
    pas = paciente['Pressão Sistólica']
    trat_hipertensao = 1 if paciente['Tratamento Hipertensão'] == 'Sim' else 0
    fumante = 1 if paciente['Fumante'] == 'Sim' else 0

    try:
        ln_idade = math.log(idade)
        ln_col_tot = math.log(col_tot)
        ln_hdl = math.log(hdl)
        ln_pas = math.log(pas)
    except ValueError:
        return 0  # Retorna 0 se ocorrer erro matemático

    sexo = paciente['Sexo']

    if sexo == 'Masculino':
        coef = {
            'ln_idade': 52.00961,
            'ln_col_tot': 20.014077,
            'ln_hdl': -0.905964,
            'ln_pas': 1.305784,
            'trat_hipertensao': 0.241549,
            'fumante': 12.096316,
            'ln_idade_ln_col_tot': -4.605038,
            'ln_idade_fumante': -2.84367,
            'ln_idade_quadrado': -2.93323,
            'constante': -172.300168
        }

        calculo = (coef['ln_idade'] * ln_idade +
                   coef['ln_col_tot'] * ln_col_tot +
                   coef['ln_hdl'] * ln_hdl +
                   coef['ln_pas'] * ln_pas +
                   coef['trat_hipertensao'] * trat_hipertensao +
                   coef['fumante'] * fumante +
                   coef['ln_idade_ln_col_tot'] * ln_idade * ln_col_tot +
                   coef['ln_idade_fumante'] * ln_idade * fumante +
                   coef['ln_idade_quadrado'] * ln_idade ** 2 +
                   coef['constante'])

        risco = 1 - (0.9402 ** math.exp(calculo))
        risco_percentual = risco * 100
        return risco_percentual

    elif sexo == 'Feminino':
        coef = {
            'ln_idade': 31.764001,
            'ln_col_tot': 22.465206,
            'ln_hdl': -1.187731,
            'ln_pas': 2.552905,
            'trat_hipertensao': 0.420251,
            'fumante': 13.07543,
            'ln_idade_ln_col_tot': -5.060998,
            'ln_idade_fumante': -2.996945,
            'constante': -146.5933061
        }

        calculo = (coef['ln_idade'] * ln_idade +
                   coef['ln_col_tot'] * ln_col_tot +
                   coef['ln_hdl'] * ln_hdl +
                   coef['ln_pas'] * ln_pas +
                   coef['trat_hipertensao'] * trat_hipertensao +
                   coef['fumante'] * fumante +
                   coef['ln_idade_ln_col_tot'] * ln_idade * ln_col_tot +
                   coef['ln_idade_fumante'] * ln_idade * fumante +
                   coef['constante'])

        risco = 1 - (0.98767 ** math.exp(calculo))
        risco_percentual = risco * 100
        return risco_percentual

    else:
        return 0

def classificar_framingham(risco):
    if risco < 10:
        return "Baixo (<10%)"
    elif 10 <= risco <= 20:
        return "Moderado (10-20%)"
    else:
        return "Alto (>20%)"

def calcular_ckd_epi(paciente):
    # Fórmula CKD-EPI 2021
    creatinina = paciente['Creatinina Sérica']
    idade = paciente['Idade']
    sexo = paciente['Sexo']

    if sexo == 'Masculino':
        if creatinina <= 0.9:
            A = 0.9
            B = -0.302
        else:
            A = 0.9
            B = -1.2
        multiplicador_sexo = 1
    elif sexo == 'Feminino':
        if creatinina <= 0.7:
            A = 0.7
            B = -0.241
        else:
            A = 0.7
            B = -1.2
        multiplicador_sexo = 1.012
    else:
        return 0

    ckdepi = 142 * ((creatinina / A) ** B) * (0.9938 ** idade) * multiplicador_sexo
    return ckdepi

def classificar_ckd_epi(ckdepi):
    if ckdepi >= 90:
        return "Estágio I (Normal ou Aumentado)"
    elif 60 <= ckdepi < 90:
        return "Estágio II (Redução Discreta)"
    elif 45 <= ckdepi < 60:
        return "Estágio IIIa (Redução Discreta-Moderada)"
    elif 30 <= ckdepi < 45:
        return "Estágio IIIb (Redução Moderada-Grave)"
    elif 15 <= ckdepi < 30:
        return "Estágio IV (Redução Grave)"
    else:
        return "Estágio V (Fase Terminal)"

def calcular_risco_total(paciente):
    # Pontuação por idade
    idade = paciente['Idade']
    if idade >= 80:
        idade_pontos = 3
    elif 70 <= idade < 80:
        idade_pontos = 2
    elif 60 <= idade < 70:
        idade_pontos = 1
    else:
        idade_pontos = 0

    # Pontuação por comorbidades
    comorbidades_sim = sum(1 for comorbidade in comorbidades_list if paciente.get(comorbidade) == 'Sim')
    comorbidade_pontos = comorbidades_sim * 2  # Cada comorbidade vale 2 pontos

    # Pontuação do Framingham
    classificacao_framingham = paciente['Classificação Framingham']
    if "Alto" in classificacao_framingham:
        framingham_pontos = 3
    elif "Moderado" in classificacao_framingham:
        framingham_pontos = 2
    else:
        framingham_pontos = 1

    # Pontuação do CKD-EPI
    classificacao_ckd = paciente['Classificação CKD-EPI']
    if "Estágio V" in classificacao_ckd:
        ckdepi_pontos = 3
    elif "Estágio IV" in classificacao_ckd:
        ckdepi_pontos = 2
    elif "Estágio III" in classificacao_ckd:
        ckdepi_pontos = 1
    else:
        ckdepi_pontos = 0

    # Pontuação por internação recente
    if paciente['Internação Recente'] == 'Sim':
        internacao_pontos = 3  # Você pode ajustar este valor conforme necessário
    else:
        internacao_pontos = 0

    # Risco Total
    risco_total = comorbidade_pontos + idade_pontos + framingham_pontos + ckdepi_pontos + internacao_pontos

    return risco_total

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
