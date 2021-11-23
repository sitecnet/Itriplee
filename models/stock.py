# -*- coding: utf-8 -*-

from odoo import models, fields, api


AVAILABLE_STATES = [
    ('disponible', 'Disponible'),
    ('reservado', 'Reservado'),
    ('garantia', 'En Garantia'),
    ('Instalado', 'Instalado'),
    ]

class stock(models.Model):
    _inherit = 'itriplee.catalogo'

    cantidad = fields.Integer('Cantidad Disponible')
    reservado = fields.Integer('Cantidad Reservada')
    #programado = fields.Integer('Cantidad', required=True) visualizar el stock entrante
    #atrasado = fields.Integer('Cantidad', required=True) visualizar el stock entrante
    almacen = fields.Many2one('itriplee.almacen', string='Almacen')
    minimo = fields.Integer('Cantidad Minima')
    cb =  fields.Char('Codigo de Barras')
    series =  fields.One2many('itriplee.stock.series', 'producto', string='Numeros de Serie')


class series(models.Model):
    _name = 'itriplee.stock.series'
    _rec_name = 'name'

    name = fields.Char('Numero de Serie')
    estado = fields.Selection(AVAILABLE_STATES, 'Estado', default='reservado')
    producto = fields.Many2one('itriplee.catalogo',) #hay que hacerlo automatico
    reparado = fields.Boolean('Reparada', default=False)
    documento = fields.Char('No. de documento de entrada')
    movimiento_entrada = fields.Many2one('itriplee.movimientos', 'No. de documento de entrada')
    #servicio = fields.Many2one()
    #movimientos = fields.Many2many('itriplee.movimientos.linea',
     #                         'movimiento_series_rel',
      #                        'series_id',
       #                       'movimientos_id',
        #                      string='Movimientos de Producto')


    

