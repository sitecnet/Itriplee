# -*- coding: utf-8 -*-

from odoo import models, fields, api

class movimientos(models.Model):
    _name = 'itriplee.movimientos'
    _rec_name = 'name'

    def _default_fecha(self):
        return fields.Date.context_today(self)
    
    name = fields.Char(string='ID de Movimiento', readonly=True, index=True,
                       default=lambda self: ('New'))
    estado = fields.Selection([
        ("programada","Programada"),
        ("solicitada","Solicitada"),
        ("recibida","Recibida"),
        ("atrasada","Atrasada"),
        ("cancelada","Cancelada"),
        ("surtida","Surtida"),
        ("retornada","Refacciones retornadas"),
        ], 'Estado del movimiento', default='programada')
    tipo = fields.Selection([
        ("entrada","Entrada"),
        ("salida","Salida"),
        ("apartado","Apartado"),
        ("stock","Cantidad Inicial")
        ], 'Tipo de Movimiento')
    documento = fields.Char('Documento de entrada')
    fecha = fields.Date('Fecha', default=_default_fecha)
    productos = fields.One2many('itriplee.movimientos.linea', 'movimiento_id', string='Cantidades', ondelete='cascade')
    series = fields.One2many('itriplee.movimientos.series', 'name', string='Series')
    servicio = fields.Many2one('itriplee.servicio', 'Servicio', ondelete='cascade')
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('movimientos') or ('New')
        res = super(movimientos, self).create(vals)
        return res

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

    def _default_fecha(self):
        return fields.Date.context_today(self)
    productos = fields.One2many('itriplee.movimientos.linea.transient', 'productow', string='Cantidades', ondelete='cascade')
    estado = fields.Selection([
        ("programada","Programada"),
        ("solicitada","Solicitada"),
        ("recibida","Recibida"),
        ("atrasada","Atrasada"),
        ("cancelada","Cancelada"),
        ("retornada","Refacciones retornadas"),
        ("surtida","Surtida"),
        ], 'Estado del movimiento', default='programada')
    fecha = fields.Date('Fecha', default=_default_fecha)
    salientes = fields.One2many('itriplee.movimientos.linea.transient', 'salientes', string='Equipos por Salir', ondelete='cascade')

    @api.model    
    def default_get(self, fields):        
        rec = super(SeriesWizard, self).default_get(fields)
        product_line = []
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids')) 
        self.update({'estado' : active_obj.estado})
        for producto in active_obj.productos:
            product_line.append((0, 0, {
            'movimiento_id': producto.movimiento_id.id,
            'cantidad': producto.cantidad,
            'producto': producto.producto.id,
            'series': producto.series.ids,
            'seriesdisponibles': producto.seriesdisponibles.id,
            }))
            rec['productos'] = product_line        
        return rec
        
    @api.multi
    def button_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        for rec in active_obj:
            rec.estado = 'recibida'
        for line in self.productos:
            total = line.producto.cantidad + line.cantidad
            line.producto.update({
                'cantidad': total
            })         
            for record in line.series:                
                vals = {
                    'name': record.name,
                    'estado': 'disponible',
                    'producto': line.producto.id,
                    'documento': active_obj.documento,
                    'movimiento_entrada': line.movimiento_id.id
                }
                self.env['itriplee.stock.series'].create(vals)
               # if line.producto.id == line.producto.id:   #Colocar bien el filtro                 
                #    active_obj.productos.write({'series': [
                 #       (0, 0, {'name': record.name}),
                  #  ]})

    @api.multi
    def button_surtir_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        for rec in active_obj:
            rec.estado = 'surtida'
            rec.servicio.estado_refacciones = 'surtida'
        for line in self.productos:
            disponible = line.producto.cantidad - line.cantidad
            reservado = line.producto.reservado + line.cantidad
            serie = line.producto
            line.producto.update({
                'cantidad': disponible,
                'reservado': reservado,
            })
            line.seriesdisponibles.update({
                'estado': 'reservado',
            })
            for prod in active_obj.productos:
                if serie == prod.producto:
                    prod.update(
                    {'seriesdisponibles': line.seriesdisponibles})
            

    @api.multi
    def button_retornar1_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        regresadas = []
        recs = []
        self.estado = 'retornada'        
        for rec in active_obj:
            rec.servicio.estado_refacciones = 'regresadas'
        for line in self.productos:
            if line.regresar == True:
                disponible = line.producto.cantidad + line.cantidad
                reservado = line.producto.reservado - line.cantidad
                line.producto.update({
                    'cantidad': disponible,
                    'reservado': reservado,
                })
                line.seriesdisponibles.update({
                    'estado': 'disponible',
                }) 
                regresadas.append((0, 0, {
                    'producto': line.producto.id,
                    'cantidad': 1,
                    'seriesdisponibles': line.seriesdisponibles.id
                    }))
                vals = {
                'estado': 'solicitada',
                'tipo': 'entrada',
                'fecha': self.fecha,
                'productos': regresadas,
                } 
                rec.env['itriplee.movimientos'].create(vals)
            else:
                self.salientes.write({
                    'producto': line.producto.id,
                    'cantidad': 1,
                    'seriesdisponibles': line.seriesdisponibles.id
                    })
            return   
        return {"type": "set_scrollTop"}
            
    def button_retornar2_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        salidas = []
        for line in self.salientes:
            pass

class lineasWizard(models.TransientModel):
    _name = 'itriplee.movimientos.linea.transient'

    productow = fields.Many2one('itriplee.series.wizard', string='Movimiento')
    salientes = fields.Many2one('itriplee.series.wizard', string='Productos por Salir')
    cantidad = fields.Integer('Cantidad')
    producto = fields.Many2one('itriplee.catalogo')
    movimiento_id = fields.Many2one('itriplee.movimientos', string='Movimiento')
    series = fields.One2many('itriplee.movimientos.series.transient', 'movimiento', string='Series')
    seriesdisponibles = fields.Many2one('itriplee.stock.series', string='Series')
    regresar = fields.Boolean('Regresar al almacen', default=False)
    tipo_salida = fields.Selection([
                    ("venta","Venta"),
                    ("garantia","Garantia"),
                    ], 'Tipo de Salida')
    serie_nueva = fields.Char('Serie de remplazo')
    factura = fields.Char('Factura de Salida')

class lineas_movimientos(models.Model):
    _name = 'itriplee.movimientos.linea'
    _rec_name = 'movimiento_id'

    movimiento_id = fields.Many2one('itriplee.movimientos', string='Movimiento')
    cantidad = fields.Integer('Cantidad')
    producto = fields.Many2one('itriplee.catalogo')
    series = fields.One2many('itriplee.movimientos.series', 'movimiento', string='name', ondelete='cascade')
    seriesdisponibles = fields.Many2one('itriplee.stock.series', string='Series')
    estado_refaccion = fields.Selection([
                    ("nueva","Nueva"),
                    ("reparada","Reparada"),
                    ], 'De Preferencia')     
        

class lineas_movimientos_series(models.Model):
    _name = 'itriplee.movimientos.series'

    name = fields.Char('Serie', ondelete='cascade')
    movimiento = fields.Many2one('itriplee.movimientos.linea', ondelete='cascade')

class seriesWizard(models.TransientModel):
    _name = 'itriplee.movimientos.series.transient'

    name = fields.Char('Serie', ondelete='cascade')
    movimiento = fields.Many2one('itriplee.movimientos.linea.transient', ondelete='cascade')