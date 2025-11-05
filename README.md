# T2: Morphing Geométrico de Objetos 3D

Trabalho T2 da disciplina de **Computação Gráfica** (2025/2 - Turma 31) da Escola Politécnica - PUCRS.

* **Professores:** Profª. Soraia Raupp Musse, Prof. Gabriel Fonseca Silva
* **Autores:** [Luísa Kirsch Silva Zarth e Rosana Schreiner Budant]

---

## 🎯 Objetivo do Projeto

O objetivo deste trabalho é implementar um sistema para geração de objetos poliédricos baseado em *morphing* geométrico. O sistema lê dois objetos 3D a partir de arquivos `.obj` e realiza uma animação de transformação (interpolação linear) entre eles.

## ✨ Funcionalidades Implementadas

* **Carregamento de Objetos:** O sistema carrega dois arquivos `.obj` (com malhas triangulares) e os exibe em janelas separadas.
* **Visualização Múltipla:** São utilizadas três janelas `freeglut`:
    1.  Janela 1: Exibe o objeto de origem.
    2.  Janela 2: Exibe o objeto de destino.
    3.  Janela 3: Exibe a animação do *morphing* (aberta sob demanda).
* **Associação de Faces:** Implementa a associação de faces (triângulos) entre os dois objetos para permitir a interpolação, mesmo quando o número de faces é diferente.
* **Animação Controlável:** A animação de *morphing* pode ser iniciada e pausada pelo usuário em tempo real.
* **Renderização:** Os objetos são renderizados com iluminação 3D (ambiente, difusa e especular), modo sólido (`GL_FILL`) e *wireframe* para melhor visualização da topologia.
* **⭐ Extra (0.5):** A animação do *morphing* é sincronizada com uma música de fundo (`beatles.mp3`). A música toca quando a animação é iniciada (**ESPAÇO**) e pausa quando a animação é pausada (**ESPAÇO** novamente).

## 💻 Tecnologias Utilizadas

* **Python 3**
* **PyOpenGL** (para renderização e interface com OpenGL)
* **freeglut** (para gerenciamento de janelas, contexto e eventos)
* **Pygame** (utilizado especificamente o módulo `pygame.mixer` para o áudio)

## 🚀 Como Executar

**1. Instalação das Dependências:**

Certifique-se de ter as bibliotecas necessárias instaladas:

```bash
pip install PyOpenGL PyOpenGL-accelerate pygame