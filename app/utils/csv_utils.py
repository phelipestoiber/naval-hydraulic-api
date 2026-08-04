from app.schemas.erro import ErrorDetail

def validar_e_parsear_csv_curva(conteudo_bytes: bytes) -> tuple[list[dict[str, float | None]], list[ErrorDetail]]:
    """
    Valida e parseia um arquivo CSV contendo a curva HxQ da bomba segundo as 10 regras do Schema D2.
    Header esperado: Q_m3h,H_m,eta_pct,NPSH_m
    """
    erros: list[ErrorDetail] = []
    dados: list[dict[str, float | None]] = []

    if not conteudo_bytes or len(conteudo_bytes.strip()) == 0:
        erros.append(ErrorDetail(
            campo="arquivo_csv",
            mensagem="Arquivo CSV vazio ou inválido.",
            codigo="CURVA_CSV_ARQUIVO_INVALIDO"
        ))
        return (dados, erros)

    # Regra 10: UTF-8 encoding
    try:
        texto = conteudo_bytes.decode('utf-8')
    except UnicodeDecodeError:
        erros.append(ErrorDetail(
            campo="arquivo_csv",
            mensagem="Encoding do arquivo CSV deve ser UTF-8.",
            codigo="CURVA_CSV_ENCODING_INVALIDO"
        ))
        return (dados, erros)

    linhas_brutas = texto.splitlines()
    linhas_validas = []

    # Regra 9: Linhas com '#' são comentários
    for idx, linha in enumerate(linhas_brutas, start=1):
        l = linha.strip()
        if l and not l.startswith('#'):
            linhas_validas.append((idx, l))

    if not linhas_validas:
        erros.append(ErrorDetail(
            campo="arquivo_csv",
            mensagem="Arquivo CSV vazio ou contendo apenas comentários.",
            codigo="CURVA_CSV_ARQUIVO_INVALIDO"
        ))
        return (dados, erros)

    # Regra 1 e 2: Header
    idx_header, linha_header = linhas_validas[0]
    colunas_header = [c.strip() for c in linha_header.split(',')]

    if "Q_m3h" not in colunas_header or "H_m" not in colunas_header:
        erros.append(ErrorDetail(
            campo="header",
            mensagem="Header do CSV deve conter obrigatoriamente as colunas 'Q_m3h' e 'H_m'.",
            codigo="CURVA_CSV_HEADER_INVALIDO"
        ))
        return (dados, erros)

    pos_q = colunas_header.index("Q_m3h")
    pos_h = colunas_header.index("H_m")
    pos_eta = colunas_header.index("eta_pct") if "eta_pct" in colunas_header else None
    pos_npsh = colunas_header.index("NPSH_m") if "NPSH_m" in colunas_header else None

    linhas_dados = linhas_validas[1:]

    # Regra 4 e 5: Mínimo 3 pontos, Máximo 50 pontos
    if len(linhas_dados) < 3:
        erros.append(ErrorDetail(
            campo="linhas",
            mensagem=f"A curva deve conter no mínimo 3 pontos (fornecidos: {len(linhas_dados)}).",
            codigo="CURVA_CSV_PONTOS_INSUFICIENTES"
        ))
        return (dados, erros)

    if len(linhas_dados) > 50:
        erros.append(ErrorDetail(
            campo="linhas",
            mensagem=f"A curva deve conter no máximo 50 pontos (fornecidos: {len(linhas_dados)}).",
            codigo="CURVA_CSV_PONTOS_EXCEDIDOS"
        ))
        return (dados, erros)

    q_anteriores = []
    h_anteriores = []

    for num_linha, linha in linhas_dados:
        # Checar se contem virgula decimal em números não delimitadores
        partes = linha.split(',')

        if len(partes) < len(colunas_header):
            erros.append(ErrorDetail(
                campo=f"linha_{num_linha}",
                mensagem=f"Linha {num_linha}: quantidade de colunas menor que o header.",
                codigo="CURVA_CSV_FORMATO_INVALIDO"
            ))
            continue

        # Regra 3: Decimal com ponto (não vírgula)
        # Se houver mais partes do que colunas no header, provavelmente foi usada vírgula decimal
        if len(partes) > len(colunas_header):
            erros.append(ErrorDetail(
                campo=f"linha_{num_linha}",
                mensagem=f"Linha {num_linha}: o formato de decimal deve utilizar ponto ('.') e não vírgula (',').",
                codigo="CURVA_CSV_FORMATO_DECIMAL"
            ))
            continue

        str_q = partes[pos_q].strip()
        str_h = partes[pos_h].strip()

        # Regra 8: Valor ausente em coluna obrigatória
        if not str_q or not str_h:
            erros.append(ErrorDetail(
                campo=f"linha_{num_linha}",
                mensagem=f"Linha {num_linha}: valor ausente em coluna obrigatória (Q_m3h ou H_m).",
                codigo="CURVA_CSV_VALOR_AUSENTE"
            ))
            continue

        try:
            q_val = float(str_q)
            h_val = float(str_h)
        except ValueError:
            erros.append(ErrorDetail(
                campo=f"linha_{num_linha}",
                mensagem=f"Linha {num_linha}: formato numérico inválido (use ponto como decimal).",
                codigo="CURVA_CSV_FORMATO_DECIMAL"
            ))
            continue

        eta_val = None
        if pos_eta is not None and pos_eta < len(partes) and partes[pos_eta].strip():
            try:
                eta_val = float(partes[pos_eta].strip())
            except ValueError:
                erros.append(ErrorDetail(
                    campo=f"linha_{num_linha}_eta_pct",
                    mensagem=f"Linha {num_linha}: valor inválido para eta_pct.",
                    codigo="CURVA_CSV_FORMATO_DECIMAL"
                ))

        npsh_val = None
        if pos_npsh is not None and pos_npsh < len(partes) and partes[pos_npsh].strip():
            try:
                npsh_val = float(partes[pos_npsh].strip())
            except ValueError:
                erros.append(ErrorDetail(
                    campo=f"linha_{num_linha}_NPSH_m",
                    mensagem=f"Linha {num_linha}: valor inválido para NPSH_m.",
                    codigo="CURVA_CSV_FORMATO_DECIMAL"
                ))

        q_anteriores.append(q_val)
        h_anteriores.append(h_val)

        dados.append({
            "Q_m3h": q_val,
            "H_m": h_val,
            "eta_pct": eta_val,
            "NPSH_m": npsh_val
        })

    if erros:
        return ([], erros)

    # Regra 6: Q monotonicamente crescente
    for i in range(1, len(q_anteriores)):
        if q_anteriores[i] <= q_anteriores[i - 1]:
            erros.append(ErrorDetail(
                campo="Q_m3h",
                mensagem="Vazão Q_m3h deve ser monotonicamente crescente.",
                codigo="CURVA_CSV_Q_NAO_CRESCENTE"
            ))
            return ([], erros)

    # Regra 7: H monotonicamente decrescente
    for i in range(1, len(h_anteriores)):
        if h_anteriores[i] >= h_anteriores[i - 1]:
            erros.append(ErrorDetail(
                campo="H_m",
                mensagem="Altura manométrica H_m deve ser monotonicamente decrescente.",
                codigo="CURVA_CSV_H_INVALIDO"
            ))
            return ([], erros)

    return (dados, erros)
