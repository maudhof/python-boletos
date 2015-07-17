# coding: utf-8

__author__ = 'maudhof@gmail.com'

from common import Boleto, modulo10, modulo11_0, modulo11_1
import logging

class BoletoCEF(Boleto):
    banco = '104'

    carteira = 'SR'

    local_pagamento = u"PREFERENCIALMENTE NAS CASAS LOTÉRICAS ATÉ O VALOR LIMITE"

    TipoCobranca = '2' #1 = Registrada, 2 = Sem Registro

    EmissaoBoleto = '4' #4 = BEneficiario

    # cedente_operacao = '003'

    def __init__(self, *args, **kwargs):

        if 'cedente_operacao' in kwargs:
            # self.cedente_operacao = kwargs.pop('cedente_operacao')
            kwargs.pop('cedente_operacao')

        super(BoletoCEF, self).__init__(*args, **kwargs)

    def _cedente_agencia_codigo(self, formatado):

        #code = [
        #    self.cedente_agencia.zfill(4)[:4],
        #    self.cedente_operacao.zfill(3)[:3],
        #    self.cedente_conta.zfill(8)[:8],
        #]

        codigo_beneficiario = self.cedente_conta.zfill(6)[:6]

        code = [
            self.cedente_agencia.zfill(4)[:4],
            codigo_beneficiario,
            modulo11_0(codigo_beneficiario)
        ]

        if not formatado:
            return ''.join(code)

        #code.append(self._modulo11(''.join(code)))

        #return '%s.%s.%s-%s' % tuple(code)
        return '%s/%s-%s' % tuple(code)

    @property
    def nosso_numero_formatado(self):

        #self.prefixo_nosso_numero = str(self.prefixo_nosso_numero).ljust(2, '0')

        output = ''.join([
            self.TipoCobranca,
            self.EmissaoBoleto,
            self.nosso_numero.zfill(15)  #ja vem com 15 posicoes
        ])

        return '%s-%s' % (output, modulo11_0(output))

    @property
    def cedente_agencia_codigo(self):
        return self._cedente_agencia_codigo(True)

    @property
    def banco_dv(self):
        return "%s-%s" % (
            self.banco,
            modulo11_0(self.banco)
        )

    @property
    def codigo_barras(self):

        logging.debug("***** cria codigo_barras *****")

        codigo_beneficiario = str(self.cedente_conta).zfill(6)[:6]

        logging.debug('\tcodigo_beneficiario: ' + codigo_beneficiario)

        nosso_numero =  str(self.nosso_numero.zfill(15)[:15])

        logging.debug('\tnosso_numero: ' + nosso_numero)

        dv_nosso_numero = str(modulo11_0(''.join([
            self.TipoCobranca,
            self.EmissaoBoleto,
            nosso_numero
        ])))

        logging.debug('\tdv_nosso_numero: ' + dv_nosso_numero)

        barcode = [  # tam   descricao
                     self.banco,                                  # 3 - banco
                     self.moeda,                                  # 1 - código da moeda (9) real
                                                                  # 1
                     str(self.fator_vencimento).zfill(4),         # 4 - fator vencimento
                     self.valor_digitavel,                        # 10 - valor documento
                     codigo_beneficiario,                         # 6  - codigo beneficiario
                     str(modulo11_0(codigo_beneficiario)),        # 1  - DV codigo beneficiario
                     nosso_numero[:3],                            # 3  - nosso numero posicao 3 a 5
                     self.TipoCobranca,                           # 1  - TipoCobranca
                     nosso_numero[3:6],                           # 3  - nosso numero posicao 6 a 8
                     self.EmissaoBoleto,                          # 1  - EmissaoBoleto
                     nosso_numero[6:],                            # 9  - nosso numero posicao 9 a final
                     dv_nosso_numero                              # 1  - dv_nosso_numero
        ]

        dv = str(modulo11_1(''.join(barcode)))

        barcode.insert(2, dv)

        logging.info(barcode)

        return ''.join(barcode)

    @property
    def linha_digitavel(self):

        barcode = self.codigo_barras

        ####################################
        ### bloco 1                      ###
        ####################################
        blk_1 = [barcode[:4], barcode[19:24]]
        dv = str(modulo10(''.join(blk_1)))
        blk_1.append(dv)
        blk_1 = ''.join(blk_1)

        ####################################
        ### bloco 2                      ###
        ####################################
        blk_2 = barcode[24:33]
        dv = str(modulo10(blk_2))
        blk_2 = '%s%s' % (blk_2, dv)

        ####################################
        ### bloco 3                      ###
        ####################################
        blk_3 = barcode[34:43]
        dv = str(modulo10(blk_3))
        blk_3 = '%s%s' % (blk_3, dv)

        ####################################
        ### bloco 4                      ###
        ####################################
        blk_4 = barcode[4]

        ####################################
        ### bloco 5                      ###
        ####################################
        blk_5 = ''.join([barcode[5:9], barcode[9:19]])

        return "%s.%s %s.%s %s.%s %s %s" % (
            blk_1[:5],
            blk_1[5:],
            blk_2[:5],
            blk_2[5:],
            blk_3[:5],
            blk_3[5:],
            blk_4,
            blk_5
        )

    # def _modulo11(self, num):
    #     resultado = self.__modulo_11_base__(num)
    #     if resultado > 9:
    #         return 0
    #     return resultado

