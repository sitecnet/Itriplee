# -*- coding: utf-8 -*-

from odoo import models, fields, api

class almacen(models.Model):
    _name = 'itriplee.almacen'
    _rec_name = 'name'

    AVAILABLE_STATES = [

        ('Disponible', 'Disponible'),
        ('No Disponible', 'No Disponible'),
        ('Reparado', 'Reparado'),
        ('En Garantia', 'En Garantia'),
        ('Instalado', 'Instalado'),
    ]
########Campos De sistema##############
    name = fields.Char(string='Refaccion', required=True)
    marca = fields.Many2one('itriplee.marca', string='Marca')
    estado = fields.Selection(AVAILABLE_STATES, 'Status', string='Estado', default='Disponible')
    tipo_equipo = fields.Many2one('itriplee.tipo', string='Tipo de Equipo')

domain="[('tipo_equipo', '=', 'Refacción')]"