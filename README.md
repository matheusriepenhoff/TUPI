Sistema de Gerenciamento de Pacientes com Flask
Este é um sistema de gerenciamento de pacientes desenvolvido em Python usando o framework Flask. O aplicativo permite adicionar pacientes, calcular pontuações de risco com base em diversas métricas médicas e priorizar visitas domiciliares de acordo com o risco total. O sistema armazena os dados dos pacientes em um arquivo Excel e oferece uma interface web simples para interação.

Sumário

1) Funcionalidades
2) Tecnologias Utilizadas
3) Pré-requisitos
4) Instalação
5) Uso
6) Estrutura do Projeto
7) Cálculo de Risco Total
8) Considerações de Segurança
9) Contribuição
10) Licença
11) Agradecimentos

1) Funcionalidades
Adicionar Pacientes: Permite adicionar novos pacientes com informações detalhadas, incluindo dados pessoais e métricas médicas.
Cálculo de Pontuações:
Escore de Framingham: Calcula o risco cardiovascular baseado no estudo de Framingham.
CKD-EPI: Calcula a taxa de filtração glomerular estimada para avaliar a função renal.
Risco Total: Calcula uma pontuação total de risco considerando idade, comorbidades, internação recente e as pontuações de Framingham e CKD-EPI.
Priorização de Visitas: Lista os pacientes ordenados pelo risco total, priorizando aqueles que ainda não foram visitados.
Marcar como Visitado: Permite marcar pacientes como visitados, atualizando sua prioridade na lista.
Remover Pacientes: Possibilidade de remover pacientes da lista.
Interface Web Amigável: Interface simples e responsiva para facilitar a interação.
Armazenamento em Excel: Dados dos pacientes são armazenados em um arquivo Excel (pacientes.xlsx).

2) Tecnologias Utilizadas
Python 3.13.0
Flask: Framework web para Python.
Pandas: Biblioteca para manipulação de dados.
OpenPyXL: Biblioteca para trabalhar com arquivos Excel.
Gunicorn: Servidor WSGI para implantação em produção.
HTML/CSS: Para a interface web.

3) Pré-requisitos
Python 3.13.0 instalado no sistema.
Pip (gerenciador de pacotes do Python).
Git (para clonar o repositório, opcional).

3.1) Instalação
Clonar o Repositório
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
Substitua SEU_USUARIO e SEU_REPOSITORIO pelo seu nome de usuário e nome do repositório no GitHub.

3.2) Navegar até o Diretório do Projeto
cd SEU_REPOSITORIO

3.3) Criar um Ambiente Virtual (Opcional, mas Recomendado)
python -m venv venv

3.4) Ativar o ambiente virtual:

3.4.1) Windows:
venv\Scripts\activate

3.4.2) macOS/Linux:
source venv/bin/activate

4) Instalar as Dependências
pip install -r requirements.txt


5) Uso
Executar o Aplicativo Localmente
Iniciar o Servidor Flask
python app.py
Acessar o Aplicativo no Navegador
Abra o navegador e acesse:
http://localhost:8080

5.1) Funcionalidades Principais
Adicionar Paciente: Clique em "Adicionar Paciente" e preencha o formulário com as informações do paciente.
Lista de Pacientes: Visualize a lista de pacientes, ordenada por prioridade de risco.
Marcar como Visitado: Marque pacientes como visitados para atualizar suas prioridades.
Remover Paciente: Remova pacientes da lista conforme necessário.

6) Estrutura do Projeto
TUPI/
│
├── app.py                # Código principal da aplicação Flask
├── requirements.txt      # Lista de dependências do Python
├── Procfile              # Arquivo para implantação no Heroku
├── runtime.txt           # Especifica a versão do Python para o Heroku
├── README.md             # Este arquivo
├── .gitignore            # Arquivos e pastas ignorados pelo Git
└── templates/            # Pasta com os templates HTML
    ├── index.html        # Template da página principal
    └── adicionar.html    # Template do formulário de adição

7) Cálculo de Risco Total
O Risco Total é calculado com base nos seguintes fatores:

Idade:
≥ 80 anos: 3 pontos
70-79 anos: 2 pontos
60-69 anos: 1 ponto
< 60 anos: 0 pontos

Comorbidades: Cada comorbidade adiciona 2 pontos.
Escore de Framingham:
Alto: 3 pontos
Moderado: 2 pontos
Baixo: 1 ponto

CKD-EPI:
Estágio V: 3 pontos
Estágio IV: 2 pontos
Estágio III: 1 ponto
Estágios I e II: 0 pontos

Internação Recente:
Sim: 3 pontos
Não: 0 pontos
Nota: Pacientes não visitados são priorizados na lista. O risco total determina a ordem de prioridade para visitas domiciliares.

8) Considerações de Segurança
Dados Sensíveis: O aplicativo lida com informações pessoais de pacientes. Certifique-se de proteger esses dados e cumprir as leis e regulamentações de privacidade aplicáveis.
Arquivo pacientes.xlsx: Este arquivo contém os dados dos pacientes e não deve ser compartilhado publicamente ou enviado para repositórios online.
.gitignore: O arquivo .gitignore está configurado para ignorar pacientes.xlsx e outras pastas sensíveis.
Uso Responsável: Este aplicativo é um protótipo e não deve ser usado em ambientes de produção sem implementações adequadas de segurança e conformidade legal.

9) Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues para relatar bugs ou solicitar melhorias, e pull requests para propor alterações.

9.1) Passos para Contribuir
Fork este repositório.

9.2) Crie uma branch para sua feature ou correção:
git checkout -b minha-nova-feature

9.3) Faça o commit das suas alterações:
git commit -m "Adiciona nova funcionalidade X"

9.4) Envie para o branch remoto:
git push origin minha-nova-feature

9.5) Abra um Pull Request no GitHub.

10) Licença
Este projeto está licenciado sob a licença MIT - consulte o arquivo LICENSE para detalhes.

11) Agradecimentos
Flask: Framework web que facilitou o desenvolvimento deste aplicativo.
Pandas e OpenPyXL: Bibliotecas essenciais para manipulação de dados e arquivos Excel.
Comunidade Python: Pelos inúmeros recursos e suporte disponíveis.

12) Contato
Para dúvidas ou sugestões, entre em contato:

Nome: Matheus Jurgen Riepenhoff
Email: jurgen.riepenhoff@gmail.com
GitHub: https://github.com/matheusriepenhoff
