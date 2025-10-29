from visualizacao import inicializar_janelas
from morphing import carregar_objetos

def main():
    print("Carregando objetos...")
    carregar_objetos()
    print("Objetos carregados e normalizados!")

    print("\nControles da janela de Morphing:")
    print("SPACE - Play/Pause animação")
    print("R - Reset (volta para t=0)")
    print("Q - Sair")

    inicializar_janelas()

if __name__ == "__main__":
    main()
