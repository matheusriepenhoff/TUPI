# Sistema de Gerenciamento de Pacientes com Flask

Este é um sistema de gerenciamento de pacientes desenvolvido em Python, utilizando o framework **Flask**. O aplicativo permite adicionar pacientes, calcular pontuações de risco com base em diversas métricas médicas e priorizar visitas domiciliares de acordo com o risco total. O sistema armazena os dados dos pacientes em um arquivo Excel e oferece uma interface web simples e amigável para interação.

## Sumário

1. [Funcionalidades](#funcionalidades)
2. [Tecnologias Utilizadas](#tecnologias-utilizadas)
3. [Pré-requisitos](#pré-requisitos)
4. [Instalação](#instalação)
5. [Uso](#uso)
6. [Estrutura do Projeto](#estrutura-do-projeto)
7. [Cálculo de Risco Total](#cálculo-de-risco-total)
8. [Considerações de Segurança](#considerações-de-segurança)
9. [Contribuição](#contribuição)
10. [Licença](#licença)
11. [Agradecimentos](#agradecimentos)
12. [Contato](#contato)

## Funcionalidades

- **Adicionar Pacientes**: Permite adicionar novos pacientes com informações detalhadas, incluindo dados pessoais e métricas médicas.
- **Cálculo de Pontuações**:
  - **Escore de Framingham**: Calcula o risco cardiovascular baseado no estudo de Framingham.
  - **CKD-EPI**: Calcula a taxa de filtração glomerular estimada para avaliar a função renal.
  - **Risco Total**: Calcula uma pontuação total de risco considerando idade, comorbidades, internação recente e as pontuações de Framingham e CKD-EPI.
- **Priorização de Visitas**: Lista os pacientes ordenados pelo risco total, priorizando aqueles que ainda não foram visitados.
- **Marcar como Visitado**: Permite marcar pacientes como visitados, atualizando sua prioridade na lista.
- **Remover Pacientes**: Possibilidade de remover pacientes da lista conforme necessário.
- **Interface Web Amigável**: Interface simples e responsiva para facilitar a interação.
- **Armazenamento em Excel**: Dados dos pacientes são armazenados em um arquivo Excel (`pacientes.xlsx`).
- **Backup Automático**: Criação de backups automáticos dos dados antes de cada salvamento.
- **Validações de Formulário**: Validações no frontend e backend para garantir a integridade dos dados.

## Tecnologias Utilizadas

- **Python 3.10 ou superior**
- **Flask**: Framework web para Python.
- **Pandas**: Biblioteca para manipulação de dados.
- **OpenPyXL**: Biblioteca para trabalhar com arquivos Excel.
- **Gunicorn**: Servidor WSGI para implantação em produção.
- **HTML5**, **CSS3** e **JavaScript**: Para a interface web.
- **Bootstrap**: Para estilos responsivos e componentes visuais.

## Pré-requisitos

- **Python 3.10 ou superior** instalado no sistema.
- **Pip** (gerenciador de pacotes do Python).
- **Git** (para clonar o repositório, opcional).

## Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/matheusriepenhoff/TUPI.git
```

### 2. Navegar até o Diretório do Projeto

```bash
cd TUPI
```

### 3. Criar um Ambiente Virtual (Opcional, mas Recomendado)

```bash
python -m venv venv
```

### 4. Ativar o Ambiente Virtual

- **Windows**:

  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux**:

  ```bash
  source venv/bin/activate
  ```

### 5. Instalar as Dependências

```bash
pip install -r requirements.txt
```

## Uso

### Executar o Aplicativo Localmente

#### Iniciar o servidor Flask

```bash
python main.py
```

### Acessar o Aplicativo no Navegador

Abra o navegador e acesse:

```
http://localhost:8080
```

### Funcionalidades Principais

- **Adicionar Paciente**: Clique em "Adicionar Paciente" e preencha o formulário com as informações do paciente.
- **Lista de Pacientes**: Visualize a lista de pacientes, ordenada por prioridade de risco.
- **Marcar como Visitado**: Marque pacientes como visitados para atualizar suas prioridades.
- **Remover Paciente**: Remova pacientes da lista conforme necessário.

## Estrutura do Projeto

```plaintext
TUPI/
├── app.py                   # Código principal da aplicação Flask
├── main.py                  # Script de inicialização do sistema
├── requirements.txt         # Lista de dependências do Python
├── Procfile                 # Arquivo para implantação no Heroku
├── runtime.txt              # Especifica a versão do Python para o Heroku
├── README.md                # Este arquivo
├── .gitignore               # Arquivos e pastas ignorados pelo Git
├── templates/               # Pasta com os templates HTML
│   ├── index.html           # Template da página principal
│   ├── adicionar.html       # Template do formulário de adição
│   ├── editar.html          # Template do formulário de edição
│   ├── base.html            # Template base com estrutura comum
│   └── error.html           # Template para páginas de erro
└── static/                  # Arquivos estáticos (CSS, JS)
    ├── css/
    │   ├── main.css         # Estilos globais e componentes
    │   └── forms.css        # Estilos específicos para formulários
    └── js/
        ├── main.js          # Funcionalidades principais e inicialização
        └── validation.js    # Validações de formulários
```

**Estrutura de Diretórios Gerados pelo Sistema:**

```plaintext
%USERPROFILE%/Documents/Sistema_Pacientes/
├── dados/                   # Armazena o arquivo Excel com os dados dos pacientes
├── backup/                  # Armazena backups automáticos dos dados
└── logs/                    # Armazena logs do sistema
```

## Cálculo de Risco Total

O **Risco Total** é calculado com base nos seguintes fatores:

### Pontuação por Idade

- **≥ 80 anos**: 3 pontos
- **70-79 anos**: 2 pontos
- **60-69 anos**: 1 ponto
- **< 60 anos**: 0 pontos

### Comorbidades

- **Cada comorbidade**: 2 pontos

### Escore de Framingham

- **Alto**: 3 pontos
- **Moderado**: 2 pontos
- **Baixo**: 1 ponto

### CKD-EPI (Função Renal)

- **Estágio V**: 3 pontos
- **Estágio IV**: 2 pontos
- **Estágio III**: 1 ponto
- **Estágios I e II**: 0 pontos

### Internação Recente

- **Sim**: 3 pontos
- **Não**: 0 pontos

**Nota:** Pacientes **não visitados** são priorizados na lista. O risco total determina a ordem de prioridade para visitas domiciliares.

## Considerações de Segurança

- **Dados Sensíveis**: O aplicativo lida com informações pessoais de pacientes. Certifique-se de proteger esses dados e cumprir as leis e regulamentações de privacidade aplicáveis.
- **Arquivo `pacientes.xlsx`**: Este arquivo contém os dados dos pacientes e não deve ser compartilhado publicamente ou enviado para repositórios online.
- **`.gitignore`**: O arquivo `.gitignore` está configurado para ignorar `pacientes.xlsx` e outras pastas sensíveis.
- **Uso Responsável**: Este aplicativo é um protótipo e não deve ser usado em ambientes de produção sem implementações adequadas de segurança e conformidade legal.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir **issues** para relatar bugs ou solicitar melhorias, e **pull requests** para propor alterações.

### Passos para Contribuir

1. **Faça um fork** deste repositório.

2. **Crie uma branch** para sua feature ou correção:

   ```bash
   git checkout -b minha-nova-feature
   ```

3. **Faça o commit** das suas alterações:

   ```bash
   git commit -m "Adiciona nova funcionalidade X"
   ```

4. **Envie para o branch remoto**:

   ```bash
   git push origin minha-nova-feature
   ```

5. **Abra um Pull Request** no GitHub.

## Licença

Este projeto está licenciado sob a licença **MIT** - consulte o arquivo [LICENSE](LICENSE) para detalhes.

## Agradecimentos

- **Flask**: Framework web que facilitou o desenvolvimento deste aplicativo.
- **Pandas** e **OpenPyXL**: Bibliotecas essenciais para manipulação de dados e arquivos Excel.
- **Comunidade Python**: Pelos inúmeros recursos e suporte disponíveis.

## Contato

Para dúvidas ou sugestões, entre em contato:

- **Nome**: Matheus Jurgen Riepenhoff
- **Email**: [jurgen.riepenhoff@gmail.com](mailto:jurgen.riepenhoff@gmail.com)
- **GitHub**: [github.com/matheusriepenhoff](https://github.com/matheusriepenhoff)

---