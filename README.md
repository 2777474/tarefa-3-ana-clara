# Jogo da Forca

Aplicacao grafica do Jogo da Forca desenvolvida em Python com Tkinter.

## Funcionalidades

- Display das letras ocultas.
- Teclado virtual com letras de A a Z e suporte ao teclado fisico.
- Boneco desenhado em ate seis etapas de erro.
- Contador de tentativas restantes.
- Mensagens de vitoria, derrota e desistência.
- Botoes Novo Jogo, Desistir e Dicas.
- Palavras carregadas aleatoriamente de `palavras.txt`.
- Validacao de letras ja tentadas.
- Dicas que revelam uma letra ainda escondida.
- Estatisticas persistentes de vitorias e derrotas em `estatisticas.json`.

## Requisitos

- Windows com Python 3 instalado.
- Tkinter (normalmente incluido na instalacao padrao do Python).

## Executando

No terminal, dentro da pasta do projeto:

```powershell
py -3 forca_gui.py
```

## Testes

```powershell
py -3 -m unittest -v test_forca_gui.py
```

## Arquivos

- `forca_gui.py`: codigo da interface e regras do jogo.
- `palavras.txt`: banco com mais de 50 palavras.
- `estatisticas.json`: criado automaticamente ao concluir a primeira partida.
- `test_forca_gui.py`: testes das funcoes principais.
- Interface pronta para uso no Windows com Python e Tkinter.
