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
    productos = fields.One2many('itriplee.movimientos.linea', 'movimiento_id', string='Cantidades', ondelete='cascade')
    series = fields.One2many('itriplee.movimientos.series', 'name', string='Series')

    @api.multi
    def button_recibir(self):
        for rec in self:
            rec.estado = 'recibida'
        for line in self.productos:
            total = line.producto.cantidad + line.cantidad
            line.producto.update({
                'cantidad': total
            })
            for productos in line.series:
                vals = {
                    'name': productos.name,
                    'estado': 'disponible',
                    'producto': line.producto.id,
                    'documento': self.documento,
                    'movimiento_entrada': line.movimiento_id.id
                }        
                self.env['itriplee.stock.series'].create(vals)

class SeriesWizard(models.TransientModel):
    _name = 'itriplee.series.wizard'

    productos = fields.One2many('itriplee.movimientos.linea', 'movimiento_id', string='Cantidades', ondelete='cascade')

    @api.model    
    def default_get(self, fields):        
        rec = super(SeriesWizard, self).default_get(fields)        
        product_line = []        
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))        
        for line in active_obj:            
            product_line.append((0, 0, {                            
            'cantidad': line.cantidad,
            'producto': line.producto.id,     
            }))        
            rec['productos'] = product_line        
            return rec    

class lineas_movimientos(models.Model):
    _name = 'itriplee.movimientos.linea'
    _rec_name = 'movimiento_id'

    movimiento_id = fields.Many2one('itriplee.movimientos', string='Movimiento')
    cantidad = fields.Integer('Cantidad')
    producto = fields.Many2one('itriplee.catalogo')
    series = fields.One2many('itriplee.movimientos.series', 'movimiento', string='name', ondelete='cascade')

class lineas_movimientos_series(models.Model):
    _name = 'itriplee.movimientos.series'

    name = fields.Char('Serie', ondelete='cascade')
    movimiento = fields.Many2one('itriplee.movimientos.linea', ondelete='cascade')