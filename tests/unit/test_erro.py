from app.schemas.erro import ErroCalculo, ErrorResponse, ErrorDetail

def test_erro_calculo_to_error_detail():
    err = ErroCalculo(codigo="TEST_CODE", mensagem="Mensagem de teste", campo="vazao")
    detail = err.to_error_detail()
    assert detail.codigo == "TEST_CODE"
    assert detail.mensagem == "Mensagem de teste"
    assert detail.campo == "vazao"

    resp = ErrorResponse(erros=[detail])
    assert resp.status == "ERRO"
    assert resp.erros[0].codigo == "TEST_CODE"
