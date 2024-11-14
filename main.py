import os
import sys
import time
import threading
import webbrowser
from app import app

class ApplicationManager:
    def __init__(self):
        self.port = 8080
        self.host = '127.0.0.1'
        self.url = f'http://{self.host}:{self.port}'
        self.server_thread = None
        self.is_running = False

    def check_port_available(self):
        """Verifica se a porta está disponível"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((self.host, self.port))
            sock.close()
            return True
        except:
            sock.close()
            return False

    def start_server(self):
        """Inicia o servidor Flask"""
        try:
            app.run(host=self.host, port=self.port, debug=False, threaded=True)
        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")
            self.is_running = False

    def open_browser(self):
        """Abre o navegador após verificar se o servidor está pronto"""
        time.sleep(2)  # Espera 2 segundos para o servidor iniciar
        try:
            webbrowser.open(self.url)
            print(f"Navegador aberto em {self.url}")
            return True
        except Exception as e:
            print(f"Erro ao abrir navegador: {e}")
            print(f"Por favor, acesse manualmente: {self.url}")
            return False

    def run(self):
        """Inicia a aplicação"""
        try:
            # Verifica porta
            if not self.check_port_available():
                print(f"Porta {self.port} está em uso. Tentando próxima porta...")
                self.port += 1
                self.url = f'http://{self.host}:{self.port}'
                if not self.check_port_available():
                    print("Não foi possível encontrar uma porta disponível.")
                    return False

            # Inicia o servidor em uma thread separada
            self.is_running = True
            server_thread = threading.Thread(target=self.start_server)
            server_thread.daemon = True
            server_thread.start()

            # Abre o navegador
            self.open_browser()

            print("\nServidor rodando. Pressione Ctrl+C para encerrar...")
            
            # Mantém a aplicação rodando
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nEncerrando aplicação...")
            return True
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return False

def main():
    app_manager = ApplicationManager()
    success = app_manager.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()