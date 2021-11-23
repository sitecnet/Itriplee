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

#class LibraryLoanWizard(models.TransientModel):
#    _name = 'library.loan.wizard'
#    member_id = fields.Many2one('library.member', string='Member')
#    book_ids = fields.Many2many('library.book', string='Books')

#    @api.multi
#    def button_recibir(self):
#        return {
#            'name': "Close Support Ticket",
#            'type': 'ir.actions.act_window',
#            'view_type': 'form',
#            'view_mode': 'form',
#            'res_model': 'website.support.ticket.close',
#            'context': {'default_ticket_id': self.id},
#            'target': 'new'
#        }



class lineas_movimientos(models.Model):
    _name = 'itriplee.movimientos.linea'
    _rec_name = 'movimiento_id'

    @api.model
    def _default_values(self):
        terms = []
        for rec in self:
            values = {}
            values['documento'] = rec.movimiento_id.documento
            values['producto'] = rec.producto
            values['movimiento_id'] = rec.movimiento_id.name
            terms.append((0, 0, values))
        return terms

    movimiento_id = fields.Many2one('itriplee.movimientos', string='Movimiento')
    cantidad = fields.Char('Cantidad')
    producto = fields.Many2one('itriplee.catalogo')
    series = fields.One2many('itriplee.stock.series',
                              'producto',
                              string='Serie de entrada', default=_default_values)
