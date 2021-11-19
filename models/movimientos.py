# -*- coding: utf-8 -*-

from odoo import models, fields, api

class movimientos(models.Model):
    _name = 'itriplee.movimientos'
    _rec_name = 'name'
    
    name = fields.Char('Numero automatico consecutivo')
    estado = fields.Selection([
        ("solicitada","Programada"),
        ("recibida","Recibida"),
        ("atrasada","Atrasada"),
        ("cancelada","Cancelada"),
        ], 'Estado del movimiento', default='solicitada')
    tipo = fields.Selection([
        ("entrada","Entrada"),
        ("salida","Salida"),
        ("apartado","Apartado"),
        ("stock","Cantidad Inicial")
        ], 'Tipo de Movimiento')
    documento = fields.Char('Documento de entrada')
    fecha = fields.Date('Fecha de Movimiento')
    productos = fields.One2many('itriplee.movimientos.linea', 'producto', string='Productos')

    @api.model
    def button_recibir(self, vals):
        for linea in self.productos:
            vals = {
            'name': linea.series.name,
            'producto': linea.producto.id,
            'documento': self.documento
            }
            self.env['itriplee.stock.series'].create(vals)



class lineas_movimientos(models.Model):
    _name = 'itriplee.movimientos.linea'
    _rec_name = 'movimiento_id'

    movimiento_id = fields.Many2one('itriplee.movimientos', string='Movimiento')
    cantidad = fields.Char('Cantidad')
    producto = fields.Many2one('itriplee.catalogo')
    series = fields.Many2many('itriplee.stock.series',
                              'movimiento_series_rel',
                              'movimientos_id',
                              'series_id',
                              string='Serie de entrada')
