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
        ("entregadas","Refacciones entregadas"),
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
    movimiento = fields.Many2one('itriplee.movimientos', 'Proviene de', ondelete='cascade')
    comentarios = fields.Text('comentarios')
    
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
        ("entregadas","Entregadas"),
        ], 'Estado del movimiento', default='programada')
    fecha = fields.Date('Fecha', default=_default_fecha)
    salientes = fields.One2many('itriplee.movimientos.linea.transient', 'productow', string='Equipos por Salir', ondelete='cascade', domain=[('regresar','=',False)])

    @api.model    
    def default_get(self, fields):        
        rec = super(SeriesWizard, self).default_get(fields)
        product_line = []
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids')) 
        self.write({'estado' : active_obj.estado})
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
                'estado': 'recibida',
                'tipo': 'entrada',
                'fecha': self.fecha,
                'productos': regresadas,
                } 
                rec.env['itriplee.movimientos'].create(vals)
            else:
                pass
            return {"type": "set_scrollTop"}
            
    def button_retornar2_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        salidas = []
        entradas = []
        for line in self.salientes:
            salida = line.producto.reservado - line.cantidad
            line.producto.update({
                'reservado': salida
                }) 
            if line.tipo_salida == 'garantia':
                garantia = line.producto.garantias + line.cantidad
                line.producto.update({
                'garantias': garantia
                })
                line.seriesdisponibles.update({
                'estado': 'instalado',
                'movimiento_salida': active_obj.id
                }) 
            elif line.tipo_salida == 'venta':
                venta = line.producto.vendidos + line.cantidad
                line.producto.update({
                'vendidos': venta
                }) 
                line.seriesdisponibles.update({
                'estado': 'vendida',
                'movimiento_salida': active_obj.id,
                'documento_salida': line.factura
                })# Aqui acaban los movimientos directo al inventario del producto
            else:
                pass
            salidas.append((0, 0, {
                    'producto': line.producto.id,
                    'cantidad': 1,
                    'seriesdisponibles': line.seriesdisponibles.id
                    }))
            vals = {
                'estado': 'entregadas',
                'tipo': 'salida',
                'fecha': self.fecha,
                'movimiento': active_obj.id,
                'productos': salidas,
                } 
            self.env['itriplee.movimientos'].create(vals)# Aqui acaba la creación de los movimientos de salida
            if line.serie_nueva != False and line.tipo_salida == 'garantia':
                for reg in self.salientes:
                    total2 = line.producto.reservado + line.cantidad
                    line.producto.update({
                    'reservado': total2
                    })
                    vals2 = {
                    'name': reg.serie_nueva,
                    'reparado': True,
                    'estado': 'garantia',
                    'producto': line.producto.id,
                    'documento': active_obj.servicio.name,
                    'movimiento_entrada': line.movimiento_id.id,
                    }
                nuevo = self.env['itriplee.stock.series'].create(vals2)                    
                entradas.append((0, 0, {
                    'producto': line.producto.id,
                    'cantidad': 1,
                    'seriesdisponibles': nuevo.id
                    }))
                vals3 = {
                    'estado': 'solicitada',
                    'tipo': 'entrada',
                    'fecha': self.fecha,
                    'movimiento': active_obj.name,
                    'productos': salidas,
                    }
                self.env['itriplee.movimientos'].create(vals3)
                line.seriesdisponibles.update({
                'remplazo': nuevo.id
                })
                return nuevo
            elif line.serie_nueva == False and line.tipo_salida == 'garantia':
                line.seriesdisponibles.update({
                'definitivo': True
                })
                active_obj.write({
                    'comentarios' : 'no se trajo pieza de remplazo por equipo de garantia'
                    })


            



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