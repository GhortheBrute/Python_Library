from python_library import create_app

app = create_app()

# Bloco de execução
if __name__ == '__main__':
    # Habilitamos o 'debug=True'
    # Isso faz o servidor reiniciar automaticamente quando você salvar o arquivo.
    app.run(debug=True)