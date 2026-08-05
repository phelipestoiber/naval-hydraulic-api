import pytest
from app.utils.csv_utils import validar_e_parsear_csv_curva

def test_csv_utils_10_casos_schema_d2():
    """T1.9 — csv_utils: 10 casos do schema D2"""
    # 1. CSV Válido
    csv_valido = "Q_m3h,H_m,eta_pct,NPSH_m\n0,42,0,1.5\n50,40,60,2.5\n100,36,79,3.2\n"
    dados, erros = validar_e_parsear_csv_curva(csv_valido.encode('utf-8'))
    assert len(erros) == 0
    assert len(dados) == 3
    assert dados[0]["Q_m3h"] == 0.0
    assert dados[0]["H_m"] == 42.0
    assert dados[0]["eta_pct"] == 0.0
    assert dados[0]["NPSH_m"] == 1.5

    # 2. Header incorreto
    csv_header_errado = "Vazao,Altura\n0,42\n50,40\n100,36\n"
    _, erros = validar_e_parsear_csv_curva(csv_header_errado.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_HEADER_INVALIDO" for e in erros)

    # 3. Pontos insuficientes (< 3)
    csv_poucos_pontos = "Q_m3h,H_m\n0,42\n50,40\n"
    _, erros = validar_e_parsear_csv_curva(csv_poucos_pontos.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_PONTOS_INSUFICIENTES" for e in erros)

    # 4. Q não crescente
    csv_q_decrescente = "Q_m3h,H_m\n0,42\n100,40\n50,36\n"
    _, erros = validar_e_parsear_csv_curva(csv_q_decrescente.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_Q_NAO_CRESCENTE" for e in erros)

    # 5. H crescente
    csv_h_crescente = "Q_m3h,H_m\n0,42\n50,45\n100,36\n"
    _, erros = validar_e_parsear_csv_curva(csv_h_crescente.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_H_INVALIDO" for e in erros)

    # 6. Decimal vírgula
    csv_decimal_virgula = "Q_m3h,H_m\n0,42\n50,5,40\n100,36\n"
    _, erros = validar_e_parsear_csv_curva(csv_decimal_virgula.encode('utf-8'))
    assert any(e.codigo in ("CURVA_CSV_FORMATO_DECIMAL", "CURVA_CSV_HEADER_INVALIDO", "CURVA_CSV_FORMATO_INVALIDO") for e in erros)

    # 7. Pontos excedidos (> 50)
    linhas = ["Q_m3h,H_m"]
    for i in range(52):
        linhas.append(f"{i},{100-i}")
    csv_muitos_pontos = "\n".join(linhas)
    _, erros = validar_e_parsear_csv_curva(csv_muitos_pontos.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_PONTOS_EXCEDIDOS" for e in erros)

    # 8. Arquivo vazio ou apenas comentários
    csv_vazio = ""
    _, erros = validar_e_parsear_csv_curva(csv_vazio.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_ARQUIVO_INVALIDO" for e in erros)

    csv_comentarios = "# comentario 1\n# comentario 2\n"
    _, erros = validar_e_parsear_csv_curva(csv_comentarios.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_ARQUIVO_INVALIDO" for e in erros)

    # 9. Encoding inválido
    bytes_invalid_utf8 = b'\x80\x81\x82'
    _, erros = validar_e_parsear_csv_curva(bytes_invalid_utf8)
    assert any(e.codigo == "CURVA_CSV_ENCODING_INVALIDO" for e in erros)

    # 10. Valor ausente em coluna obrigatória (H_m)
    csv_valor_ausente = "Q_m3h,H_m\n0,42\n50,\n100,36\n"
    _, erros = validar_e_parsear_csv_curva(csv_valor_ausente.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_VALOR_AUSENTE" for e in erros)

    # 11. Erros extras de parse (colunas ausentes, eta/npsh/Q/H inválidos)
    csv_colunas_faltando = "Q_m3h,H_m,eta_pct\n0\n50,40\n100,36\n"
    _, erros = validar_e_parsear_csv_curva(csv_colunas_faltando.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_FORMATO_INVALIDO" for e in erros)

    csv_q_texto = "Q_m3h,H_m\n0,42\ntexto,40\n100,36\n"
    _, erros = validar_e_parsear_csv_curva(csv_q_texto.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_FORMATO_DECIMAL" for e in erros)

    csv_eta_invalido = "Q_m3h,H_m,eta_pct,NPSH_m\n0,42,abc,1.5\n50,40,60,xyz\n100,36,79,3.2\n"
    _, erros = validar_e_parsear_csv_curva(csv_eta_invalido.encode('utf-8'))
    assert any(e.codigo == "CURVA_CSV_FORMATO_DECIMAL" for e in erros)
