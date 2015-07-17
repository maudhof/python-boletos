# coding: utf-8
__author__ = 'mauricio'


from boletos.bancos.cef import BoletoCEF
from boletos.bancos.common import modulo11_0, modulo11_1, modulo10
from boletos.render import render_to_pdf, render_to_png, render_to_jpg
from datetime import date
from decimal import Decimal
import unittest
import os
import logging


logging.basicConfig(
    level=logging.NOTSET,
    #format="%(asctime)-15s %(clientip)s %(user)-8s %(message)s"
)



CAIXA_BOLETO = {
    'valor_documento': 25.00,
    'nosso_numero': "72191010",
    'numero_documento': "00001",
    'data_vencimento': date(2015, 5, 7),
    'cedente': 'Diario de Sorocaba Jornal e Editora LTDA',
    'cedente_agencia': '0356',
    'cedente_conta': '005507',
    'instrucoes': u"""
    Cobrar multa de 2% após o vencimento.
    Não receber após 30 dias da data de vencimento.
    """,
    'demonstrativo': u"""
    Teste Teste  Teste Teste Teste Teste Teste Teste
    """,
    'sacado': u"""
    Cliente
    Av. Paulista, 10 - Centro - São Paulo - CEP 00001-010
    """,
}



CODIGO_DE_BARRAS = '10499642100000025000055077000200040721910101'
#                       |-> DV = 1


class BoletoCaixaValidationTest(unittest.TestCase):

    def setUp(self):
        self.boleto = BoletoCEF(**CAIXA_BOLETO)

    def test_valor_digitavel(self):

        self.assertEqual(self.boleto.valor_digitavel, '0000002500')

    def test_cedente_agencia_codigo(self):

        logging.info('**** test_cedente_agencia_codigo ****')

        self.assertEquals(
            self.boleto.cedente_agencia,
            CAIXA_BOLETO['cedente_agencia']
        )

        self.assertEquals(
            self.boleto.cedente_conta,
            CAIXA_BOLETO['cedente_conta']
        )

        dv = str(modulo11_0(self.boleto.cedente_conta))

        valor = [
            self.boleto.cedente_agencia,
            '/',
            self.boleto.cedente_conta,
            '-',
            dv
        ]

        logging.info(''.join(valor))

        self.assertEqual(self.boleto.cedente_agencia_codigo, ''.join(valor))

    def test_nosso_numero(self):

        valor = [
            self.boleto.TipoCobranca,
            self.boleto.EmissaoBoleto,
            self.boleto.nosso_numero.zfill(15),
        ]

        dv = str(modulo11_0(''.join(valor)))

        valor.append('-')
        valor.append(dv)

        self.assertEqual(''.join(valor), self.boleto.nosso_numero_formatado)

    def test_codigo_barras(self):

        logging.debug('CODIGO_DE_BARRAS: ' + CODIGO_DE_BARRAS)
        logging.debug('boleto.codigo_barras: ' + self.boleto.codigo_barras)


        self.assertEqual(len(CODIGO_DE_BARRAS), 44)

        self.assertEqual(len(self.boleto.codigo_barras), 44)

        self.assertEqual(CODIGO_DE_BARRAS, self.boleto.codigo_barras)

    def test_linha_digitavel(self):

        logging.debug("***** TEST_LINHA_DIGITAVEL *****")

        logging.debug("\tCODIGO_DE_BARRAS: " + CODIGO_DE_BARRAS)

        blk_1 = '%s%s' % (CODIGO_DE_BARRAS[:4], CODIGO_DE_BARRAS[19:24])
        blk_1 += str(modulo10(blk_1))
        logging.debug("\ttest blk_1: " + blk_1)

        blk_2 = CODIGO_DE_BARRAS[24:34]
        blk_2 += str(modulo10(blk_2))
        logging.debug("\ttest blk_2: " + blk_2)

        blk_3 = CODIGO_DE_BARRAS[34:44]
        blk_3 += str(modulo10(blk_3))
        logging.debug("\ttest blk_3: " + blk_3)

        blk_4 = CODIGO_DE_BARRAS[4]
        logging.debug("\ttest blk_4: " + blk_4)

        blk_5 = '%s%s' % (CODIGO_DE_BARRAS[5:9], CODIGO_DE_BARRAS[9:19])
        logging.debug("\ttest blk_5: " + blk_5)

        linha_digitavel = '%s.%s %s.%s %s.%s %s %s' % (
            blk_1[:5], blk_1[5:],
            blk_2[:5], blk_2[5:],
            blk_3[:5], blk_3[5:],
            blk_4,
            blk_5
        )

        logging.debug("\ttest linha_digitavel: " + linha_digitavel)

        self.assertEqual(linha_digitavel, self.boleto.linha_digitavel)




class RenderTest(object):
    def _test_render(self, method, filename):
        fmt_filename = filename % self.boleto.__class__.__name__
        with open(fmt_filename, 'wb') as f:
            f.write(method(self.boleto).getvalue())

    def test_render_to_pdf(self):
        self._test_render(render_to_pdf, '/tmp/%s-cef-test.pdf')

    def test_render_to_png(self):
        self._test_render(render_to_png, '/tmp/%s-cef-test.png')

    def test_render_to_jpg(self):
        self._test_render(render_to_jpg, '/tmp/%s-cef-test.jpg')


class BoletoCaixaRenderTest(RenderTest, unittest.TestCase):
    def setUp(self):
        self.boleto = BoletoCEF(**CAIXA_BOLETO)




if __name__ == '__main__':
    unittest.main()
