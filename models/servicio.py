# -*- coding: utf-8 -*-

from odoo import models, fields, api

AVAILABLE_PRIORITIES = [
    ('1', 'Critico'),
    ('2', 'Alta'),
    ('3', 'Normal'),
    ('4', 'Baja'),
    ('5', 'Informativo'),
]

AVAILABLE_STATES = [

    ('confirmar', 'Confirmar'),
    ('por asignar', 'Por asignar'),
    ('asignado', 'Asignado'),
    ('pendiente', 'Pendiente'),
    ('terminado', 'Terminado'),
    ('cancelado', 'Cancelado'),
    ('calificado', 'Calificado'),
]


class servicio(models.Model):
    _name = 'itriplee.servicio'
    _rec_name = 'cliente'

    cliente = fields.Many2one('res.partner', 'Cliente', required=True)
    visita = fields.Datetime('Visita Programada', required=True)
    tipo_visita = fields.Selection([
    	("Ordinaria","Ordinaria"),
    	("Extraordinaria","Extraordinaria")],
    	 'Tipo de Visita')
    ubicacion = fields.Selection([
    	("Local","Local"),
    	("Foraneo","Foraneo")],
    	 'Local o Foraneo')
    prioridad = fields.Selection(AVAILABLE_PRIORITIES, 'Prioridad')
    estado = fields.Selection(AVAILABLE_STATES, 'Status')
    estado_equipo = fields.Selection([
    	("Garantia","Garantia"),
    	("Poliza","Poliza"),
    	("Sin Garantia","Fuera de Garantia"),
    	("Variado","Variado")],
    	 'Estado del Equipo')
    tecnico = fields.Many2one('res.users', 'Tecnico') #, domain=lambda self: [("groups_id", "=", self.env.ref("itriplee.servicios_grupo_base").id)]
    vendedor = fields.Many2one('res.users', 'Vendedor')# , domain=lambda self: [("groups_id", "=", self.env.ref("itriplee.cotizaciones_grupo_general").id)]
    reinsidencia = fields.Boolean('Es reinsidencia?')
    modelo_transicion = fields.Char('Modelo Version anterior')
    garantia_asociada = fields.Many2one('itriplee.garantias', 'Garantias')
    poliza_asociada = fields.Many2one('itriplee.polizas', 'Polizas')
    equipos = fields.One2many('itriplee.equipos', 'name', 'Equipos', ondelete='cascade')
    observaciones = fields.Text('Observaciones del equipo')
    razon_cancelacion = fields.Text('Razon de Cancelación')
    falla = fields.Text('Falla Reportada')
    responsable = fields.Selection([
    	("Cliente","Cliente"),
    	("Almacen","Almacen"),
    	("Administracion","Administracion"),
    	("Proveedor","Proveedor"),
    	("Tecnico","Tecnico"),
    	("Otro","Otro")], 
    	'Responsable Actual')
    resultado = fields.Text('Resultado del Reporte')
    comentarios = fields.Text('Comentarios del Técnico')
    firma = fields.Binary('Firma del Cliente')
    firma1 = fields.Binary('Firma del Cliente')
# Falta implementar la calificacion
