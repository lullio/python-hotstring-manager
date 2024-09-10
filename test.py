import ast

code = "import datetime; result = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')"  # Exemplo de código

try:
    # Verifica se o código é sintaticamente válido
    ast.parse(code)
    
    # Executa o código se for válido
    exec_globals = {}
    exec_locals = {}
    exec(code, exec_globals, exec_locals)
    
    # Retorna o resultado, assumindo que a variável 'result' está definida
    result = exec_locals.get('result', 'Nenhum resultado encontrado.')
    print(result)
    
except SyntaxError:
    # Código inválido, não faz nada
    pass