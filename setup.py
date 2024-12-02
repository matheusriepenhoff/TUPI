"""
Script de instalação do sistema
"""
import os
from app import create_initial_excel, SYSTEM_PATH, DATA_PATH, BACKUP_PATH, LOG_PATH

def main():
    print("Iniciando instalação do Sistema de Gestão de Pacientes...")
    
    # Cria diretórios necessários
    directories = [SYSTEM_PATH, DATA_PATH, BACKUP_PATH, LOG_PATH]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Diretório criado: {directory}")
    
    # Cria arquivo Excel inicial
    if create_initial_excel():
        print("Arquivo Excel inicial criado com sucesso!")
    
    print("\nInstalação concluída!")
    print("\nInformações importantes:")
    print(f"1. Seus dados serão salvos em: {DATA_PATH}")
    print(f"2. Backups automáticos serão feitos em: {BACKUP_PATH}")
    print(f"3. Logs do sistema estarão em: {LOG_PATH}")
    
    print("\nPara iniciar o sistema, execute o arquivo main.py")

if __name__ == "__main__":
    main()