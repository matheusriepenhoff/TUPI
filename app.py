from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
import math
import sys
import logging
from datetime import datetime
import shutil
from threading import Timer
import time
import traceback

try:
    import psutil
except ImportError:
    psutil = None
    print("psutil não instalado. Algumas funcionalidades podem estar limitadas.")

# Configuração dos diretórios
DOCUMENTS_PATH = os.path.join(os.path.expanduser("~"), "Documents")
SYSTEM_PATH = os.path.join(DOCUMENTS_PATH, "Sistema_Pacientes")
DATA_PATH = os.path.join(SYSTEM_PATH, "dados")
BACKUP_PATH = os.path.join(SYSTEM_PATH, "backup")
LOG_PATH = os.path.join(SYSTEM_PATH, "logs")
EXCEL_FILE = os.path.join(DATA_PATH, "pacientes.xlsx")

# Criar estrutura de diretórios
for path in [SYSTEM_PATH, DATA_PATH, BACKUP_PATH, LOG_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Diretório criado: {path}")

# Configuração de logging
log_file = os.path.join(LOG_PATH, f'sistema_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

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

def cleanup_process():
    """Limpa processos ao fechar"""
    if psutil:
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            for child in children:
                child.terminate()
            current_process.terminate()
        except:
            pass

def get_base_path():
    """Retorna o caminho base da aplicação"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Configuração do Flask
base_path = get_base_path()
app = Flask(__name__,
            template_folder=os.path.join(base_path, 'templates'),
            static_folder=os.path.join(base_path, 'static'))

app.secret_key = 'chave_secreta_do_sistema_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['DEBUG'] = False
def safe_float_conversion(value, default=0.0):
    """Converte valor para float de forma segura"""
    try:
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)
    except (ValueError, TypeError):
        return default

def create_initial_excel():
    """Cria o arquivo Excel inicial com todas as colunas necessárias"""
    try:
        if os.path.exists(EXCEL_FILE):
            return True

        columns = [
            'Nome', 'CNS', 'Idade', 'Sexo', 'Diabetes', 'Hipertensão',
            'Colesterol Total', 'HDL', 'Pressão Sistólica', 
            'Tratamento Hipertensão', 'Creatinina Sérica', 'Fumante',
            'Internação Recente', 'Medicamentos', 'Score Framingham',
            'Classificação Framingham', 'CKD-EPI', 'Classificação CKD-EPI',
            'Risco Total', 'Visitado', 'Data Visita'  # Adicionado Data Visita
        ] + comorbidades_list

        df_inicial = pd.DataFrame(columns=columns)

        dtypes = {
            'Nome': str,
            'CNS': str,
            'Idade': 'Int64',
            'Sexo': str,
            'Diabetes': str,
            'Hipertensão': str,
            'Colesterol Total': 'float64',
            'HDL': 'float64',
            'Pressão Sistólica': 'float64',
            'Tratamento Hipertensão': str,
            'Creatinina Sérica': 'float64',
            'Fumante': str,
            'Internação Recente': str,
            'Medicamentos': str,
            'Score Framingham': 'float64',
            'Classificação Framingham': str,
            'CKD-EPI': 'float64',
            'Classificação CKD-EPI': str,
            'Risco Total': 'float64',
            'Visitado': bool
        }

        for comorbidade in comorbidades_list:
            dtypes[comorbidade] = str

        for col, dtype in dtypes.items():
            df_inicial[col] = df_inicial[col].astype(dtype)

        df_inicial.to_excel(EXCEL_FILE, index=False)
        logging.info(f"Arquivo Excel inicial criado: {EXCEL_FILE}")
        return True

    except Exception as e:
        logging.error(f"Erro ao criar arquivo Excel inicial: {e}")
        return False

def create_backup():
    """Cria backup do arquivo Excel"""
    try:
        if os.path.exists(EXCEL_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_PATH, f"pacientes_backup_{timestamp}.xlsx")
            shutil.copy2(EXCEL_FILE, backup_file)
            logging.info(f"Backup criado: {backup_file}")
            
            # Mantém apenas os últimos 5 backups
            backups = sorted([f for f in os.listdir(BACKUP_PATH) if f.startswith("pacientes_backup_")])
            while len(backups) > 5:
                os.remove(os.path.join(BACKUP_PATH, backups.pop(0)))
            return True
    except Exception as e:
        logging.error(f"Erro ao criar backup: {e}")
        return False

def load_data():
    """Carrega os dados do arquivo Excel"""
    try:
        if not os.path.exists(EXCEL_FILE):
            if not create_initial_excel():
                raise Exception("Falha ao criar arquivo Excel inicial")
        
        df = pd.read_excel(EXCEL_FILE)
        logging.info(f"Dados carregados: {len(df)} registros")

        # Verifica e corrige tipos de dados
        dtypes = {
            'Nome': str,
            'CNS': str,
            'Idade': 'Int64',
            'Sexo': str,
            'Diabetes': str,
            'Hipertensão': str,
            'Colesterol Total': 'float64',
            'HDL': 'float64',
            'Pressão Sistólica': 'float64',
            'Tratamento Hipertensão': str,
            'Creatinina Sérica': 'float64',
            'Fumante': str,
            'Internação Recente': str,
            'Medicamentos': str,
            'Score Framingham': 'float64',
            'Classificação Framingham': str,
            'CKD-EPI': 'float64',
            'Classificação CKD-EPI': str,
            'Risco Total': 'float64',
            'Visitado': bool
        }

        for comorbidade in comorbidades_list:
            dtypes[comorbidade] = str

        # Converte e limpa dados numéricos
        numeric_columns = ['Colesterol Total', 'HDL', 'Pressão Sistólica', 'Creatinina Sérica']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

        # Aplica tipos de dados
        for col, dtype in dtypes.items():
            if col not in df.columns:
                if dtype == bool:
                    df[col] = False
                elif dtype == 'float64':
                    df[col] = 0.0
                elif dtype == 'Int64':
                    df[col] = 0
                else:
                    df[col] = ''
            df[col] = df[col].astype(dtype)

        return df

    except Exception as e:
        logging.error(f"Erro ao carregar dados: {e}\n{traceback.format_exc()}")
        return pd.DataFrame(columns=list(dtypes.keys()))

def save_data():
    """Salva os dados no arquivo Excel"""
    try:
        create_backup()
        df.to_excel(EXCEL_FILE, index=False)
        logging.info(f"Dados salvos com sucesso: {len(df)} registros")
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}\n{traceback.format_exc()}")
        return False
def calcular_framingham(paciente):
    """Calcula o score de Framingham"""
    try:
        idade = min(paciente['Idade'], 79)
        if idade < 30:
            return 0

        colesterol = float(paciente['Colesterol Total'])
        hdl = float(paciente['HDL'])
        pas = float(paciente['Pressão Sistólica'])
        fumante = paciente['Fumante'] == 'Sim'
        diabetico = paciente['Diabetes'] == 'Sim'

        pontos = 0
        if paciente['Sexo'] == 'Masculino':
            # Idade
            if idade >= 60: pontos += 3
            elif idade >= 50: pontos += 2
            elif idade >= 40: pontos += 1

            # Colesterol
            if colesterol >= 280: pontos += 3
            elif colesterol >= 240: pontos += 2
            elif colesterol >= 200: pontos += 1

            # HDL
            if hdl < 35: pontos += 2
            elif hdl < 45: pontos += 1
            elif hdl >= 60: pontos -= 1

            # Pressão Sistólica
            if pas >= 160: pontos += 3
            elif pas >= 140: pontos += 2
            elif pas >= 130: pontos += 1

            if fumante: pontos += 2
            if diabetico: pontos += 2

            risco = 2 ** (pontos - 7)
        else:  # Feminino
            # Idade
            if idade >= 60: pontos += 4
            elif idade >= 50: pontos += 3
            elif idade >= 40: pontos += 2

            # Colesterol
            if colesterol >= 280: pontos += 3
            elif colesterol >= 240: pontos += 2
            elif colesterol >= 200: pontos += 1

            # HDL
            if hdl < 35: pontos += 2
            elif hdl < 45: pontos += 1
            elif hdl >= 60: pontos -= 1

            # Pressão Sistólica
            if pas >= 160: pontos += 3
            elif pas >= 140: pontos += 2
            elif pas >= 130: pontos += 1

            if fumante: pontos += 2
            if diabetico: pontos += 2

            risco = 2 ** (pontos - 8.5)

        return round(min(risco * 100, 100), 1)

    except Exception as e:
        logging.error(f"Erro no cálculo de Framingham: {e}")
        return 0

def classificar_framingham(score):
    """Classifica o risco baseado no score de Framingham"""
    if score < 10:
        return "Baixo"
    elif score < 20:
        return "Moderado"
    else:
        return "Alto"

def calcular_ckd_epi(paciente):
    """Calcula o CKD-EPI"""
    try:
        idade = float(paciente['Idade'])
        creatinina = float(paciente['Creatinina Sérica'])
        
        if paciente['Sexo'] == 'Feminino':
            k = 0.7
            a = -0.329
            fator = 1.018
        else:
            k = 0.9
            a = -0.411
            fator = 1

        if creatinina <= k:
            ckd = 141 * ((creatinina/k)**a) * (0.993**idade) * fator
        else:
            ckd = 141 * ((creatinina/k)**(-1.209)) * (0.993**idade) * fator

        return round(max(min(ckd, 200), 0), 1)

    except Exception as e:
        logging.error(f"Erro no cálculo de CKD-EPI: {e}")
        return 0

def classificar_ckd_epi(valor):
    """Classifica o estágio da DRC baseado no valor do CKD-EPI"""
    if valor >= 90:
        return "Estágio 1"
    elif valor >= 60:
        return "Estágio 2"
    elif valor >= 45:
        return "Estágio 3A"
    elif valor >= 30:
        return "Estágio 3B"
    elif valor >= 15:
        return "Estágio 4"
    else:
        return "Estágio 5"

def calcular_risco_total(paciente):
    """Calcula o risco total do paciente"""
    try:
        risco = 0

        # Idade
        idade = paciente['Idade']
        if idade >= 80:
            risco += 3
        elif idade >= 70:
            risco += 2
        elif idade >= 60:
            risco += 1

        # Comorbidades
        for comorbidade in comorbidades_list:
            if paciente.get(comorbidade) == 'Sim':
                risco += 2

        # Framingham
        framingham = paciente.get('Score Framingham', 0)
        if framingham >= 20:
            risco += 3
        elif framingham >= 10:
            risco += 2
        elif framingham > 0:
            risco += 1

        # CKD-EPI
        ckd_epi = paciente.get('CKD-EPI', 0)
        if ckd_epi < 15:
            risco += 3
        elif ckd_epi < 30:
            risco += 2
        elif ckd_epi < 60:
            risco += 1

        # Internação recente
        if paciente.get('Internação Recente') == 'Sim':
            risco += 3

        return risco

    except Exception as e:
        logging.error(f"Erro no cálculo de risco total: {e}")
        return 0
def process_form_data(form):
    """Processa e valida os dados do formulário"""
    try:
        logging.info(f"Processando formulário: {dict(form)}")
        
        # Basic validations
        nome = form.get('nome', '').strip()
        cns = form.get('cns', '').strip()
        
        if not nome or len(nome) < 3:
            raise ValueError("Nome inválido (mínimo 3 caracteres)")
        if not cns.isdigit() or len(cns) != 15:
            raise ValueError("CNS deve conter exatamente 15 dígitos")
            
        # Create patient dict with validated data
        paciente = {
            'Nome': nome,
            'CNS': cns,
            'Idade': int(form.get('idade', 0)),
            'Sexo': form.get('sexo'),
            'Diabetes': form['diabetes'],
            'Hipertensão': form['hipertensao'],
            'Tratamento Hipertensão': form['tratamento_hipertensao'],
            'Fumante': form['fumante'],
            'Internação Recente': form['internacao_recente'],
            'Medicamentos': form.get('medicamentos', '').strip(),
            'Visitado': False
        }
        
        # Process numeric values
        paciente['Colesterol Total'] = safe_float_conversion(form.get('colesterol_total'))
        paciente['HDL'] = safe_float_conversion(form.get('hdl'))
        paciente['Pressão Sistólica'] = safe_float_conversion(form['pressao_sistolica'])
        paciente['Creatinina Sérica'] = safe_float_conversion(form['creatinina_serica'])

        # Validações
        if not paciente['Nome'] or len(paciente['Nome']) < 3:
            raise ValueError("Nome inválido (mínimo 3 caracteres)")

        if not paciente['CNS'].isdigit() or len(paciente['CNS']) != 15:
            raise ValueError("CNS deve conter exatamente 15 dígitos")

        if not 0 <= paciente['Idade'] <= 120:
            raise ValueError("Idade deve estar entre 0 e 120 anos")

        if not 0 <= paciente['Colesterol Total'] <= 1000:
            raise ValueError("Colesterol Total deve estar entre 0 e 1000 mg/dL")

        if not 0 <= paciente['HDL'] <= 200:
            raise ValueError("HDL deve estar entre 0 e 200 mg/dL")

        if paciente['HDL'] > paciente['Colesterol Total']:
            raise ValueError("HDL não pode ser maior que o Colesterol Total")

        if not 0 <= paciente['Pressão Sistólica'] <= 300:
            raise ValueError("Pressão Sistólica deve estar entre 0 e 300 mmHg")

        if not 0 <= paciente['Creatinina Sérica'] <= 20:
            raise ValueError("Creatinina Sérica deve estar entre 0 e 20 mg/dL")

        # Processa comorbidades
        comorbidades_selecionadas = request.form.getlist('comorbidades')
        for comorbidade in comorbidades_list:
            paciente[comorbidade] = 'Sim' if comorbidade in comorbidades_selecionadas else 'Não'

        # Calcula scores
        paciente['Score Framingham'] = calcular_framingham(paciente)
        paciente['Classificação Framingham'] = classificar_framingham(paciente['Score Framingham'])
        paciente['CKD-EPI'] = calcular_ckd_epi(paciente)
        paciente['Classificação CKD-EPI'] = classificar_ckd_epi(paciente['CKD-EPI'])
        paciente['Risco Total'] = calcular_risco_total(paciente)

        logging.info(f"Dados processados com sucesso: {paciente}")
        return paciente
        
    except Exception as e:
        logging.error(f"Erro ao processar dados: {e}\n{traceback.format_exc()}")
        raise
    # Carrega dados iniciais
print("Inicializando sistema...")
create_initial_excel()
df = load_data()

# Rotas da aplicação
@app.route('/')
def index():
    """Retorna a lista de pacientes ordenada por visitado, risco e data da última visita"""
    pacientes = []
    if 'df' in globals() and not df.empty:
        # Se todos foram visitados, ordena por risco e data da última visita
        if df['Visitado'].all():
            df_ordenado = df.sort_values(
                by=['Risco Total', 'Data Visita'], 
                ascending=[False, True]
            )
        else:
            # Comportamento original: não visitados primeiro, depois por risco
            df_ordenado = df.sort_values(
                by=['Visitado', 'Risco Total'], 
                ascending=[True, False]
            )
            
        pacientes = df_ordenado.to_dict('records')
        paciente_ids = df_ordenado.index.tolist()  # Adiciona esta linha
    
    return render_template('index.html', 
                         pacientes=pacientes,
                         paciente_id=paciente_ids,  # Modifica esta linha
                         comorbidades=comorbidades_list)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    global df
    if request.method == 'POST':
        try:
            # Log dos dados recebidos
            logging.info(f"Dados do formulário recebidos: {dict(request.form)}")
            
            # Validação inicial dos campos obrigatórios
            required_fields = ['nome', 'cns', 'idade', 'sexo', 'diabetes', 
                              'hipertensao', 'tratamento_hipertensao', 'fumante',
                              'internacao_recente', 'colesterol_total', 'hdl',
                              'pressao_sistolica', 'creatinina_serica']
            
            for field in required_fields:
                if field not in request.form or not request.form[field]:
                    flash(f'Campo obrigatório não preenchido: {field}', 'error')
                    return render_template('adicionar.html', comorbidades=comorbidades_list)

            novo_paciente = process_form_data(request.form)
            if novo_paciente:
                df = pd.concat([df, pd.DataFrame([novo_paciente])], ignore_index=True)
                if save_data():
                    flash('Paciente adicionado com sucesso!', 'success')
                    return redirect(url_for('index'))
                flash('Erro ao salvar os dados', 'error')
            else:
                flash('Dados inválidos', 'error')
        except Exception as e:
            logging.error(f"Erro ao adicionar paciente: {e}\n{traceback.format_exc()}")
            flash(f'Erro ao adicionar paciente: {str(e)}', 'error')
    
    return render_template('adicionar.html', comorbidades=comorbidades_list)

@app.route('/editar/<int:paciente_id>', methods=['GET', 'POST'])
def editar(paciente_id):
    global df
    try:
        if paciente_id >= len(df):
            flash('Paciente não encontrado', 'error')
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            logging.info(f"Editando paciente {paciente_id}: {dict(request.form)}")
            
            # Validate required fields
            required_fields = ['nome', 'cns', 'idade', 'sexo', 'diabetes', 
                              'hipertensao', 'tratamento_hipertensao', 'fumante',
                              'internacao_recente', 'colesterol_total', 'hdl',
                              'pressao_sistolica', 'creatinina_serica']
            
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    flash(f'Campo obrigatório não preenchido: {field}', 'error')
                    return render_template('editar.html', 
                                        paciente=df.iloc[paciente_id].to_dict(),
                                        paciente_id=paciente_id,
                                        comorbidades=comorbidades_list)

            dados_atualizados = process_form_data(request.form)
            if dados_atualizados:
                for key, value in dados_atualizados.items():
                    df.at[paciente_id, key] = value
                if save_data():
                    flash('Paciente atualizado com sucesso!', 'success')
                    return redirect(url_for('index'))
                flash('Erro ao salvar as alterações', 'error')
            else:
                flash('Dados inválidos', 'error')
                
        return render_template('editar.html',
                             paciente=df.iloc[paciente_id].to_dict(),
                             paciente_id=paciente_id,
                             comorbidades=comorbidades_list)
                             
    except Exception as e:
        logging.error(f"Erro ao editar paciente: {e}\n{traceback.format_exc()}")
        flash(f'Erro ao editar paciente: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/remover/<int:paciente_id>', methods=['POST'])
def remover(paciente_id):
    global df
    try:
        if 0 <= paciente_id < len(df):
            df = df.drop(paciente_id).reset_index(drop=True)
            if save_data():
                flash('Paciente removido com sucesso!', 'success')
            else:
                flash('Erro ao salvar alterações', 'error')
        else:
            flash('Paciente não encontrado', 'error')
    except Exception as e:
        logging.error(f"Erro ao remover paciente: {e}\n{traceback.format_exc()}")
        flash(f'Erro ao remover paciente: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/marcar_visitado/<int:paciente_id>', methods=['POST'])
def marcar_visitado(paciente_id):
    """Marca um paciente como visitado"""
    global df
    try:
        # Verifica se o paciente existe
        if paciente_id in df.index:  # Modifica esta linha
            # Atualiza apenas o campo 'Visitado'
            df.at[paciente_id, 'Visitado'] = True
            df.at[paciente_id, 'Data Visita'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if save_data():
                flash('Visita registrada com sucesso!', 'success')
                logging.info(f"Paciente {paciente_id} marcado como visitado")
            else:
                flash('Erro ao salvar alterações', 'error')
                logging.error(f"Erro ao salvar status de visita do paciente {paciente_id}")
        else:
            flash('Paciente não encontrado', 'error')
            logging.warning(f"Tentativa de marcar visita em paciente inexistente: {paciente_id}")
        
    except Exception as e:
        logging.error(f"Erro ao marcar visita: {e}\n{traceback.format_exc()}")
        flash('Erro ao registrar visita', 'error')
    
    return redirect(url_for('index'))

# Rotas de erro
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error="Página não encontrada",
                         message="A página que você está procurando não existe."), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Erro interno do servidor: {error}\n{traceback.format_exc()}")
    return render_template('error.html',
                         error="Erro Interno",
                         message="Ocorreu um erro interno no servidor."), 500

@app.errorhandler(400)
def bad_request_error(error):
    logging.error(f"Erro de requisição inválida: {error}\n{traceback.format_exc()}")
    return render_template('error.html',
                         error="Requisição Inválida",
                         message="Os dados enviados são inválidos ou estão em formato incorreto."), 400

# Inicialização do aplicativo
if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='127.0.0.1', port=port, debug=False)
    except Exception as e:
        logging.critical(f"Erro fatal ao iniciar aplicação: {e}\n{traceback.format_exc()}")
        print(f"Erro fatal: {e}")
        cleanup_process()
        sys.exit(1)
