from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PrintingCustomOrder(models.Model):
    """
    This class represents a custom print order.
    Each instance is a row in the database.
    """
    
    # This is the technical name Odoo uses in the database
    _name = 'printing.custom.order'
    _description = 'Custom Print Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # === BASIC FIELDS ===
    # These are like columns in an Excel sheet
    
    name = fields.Char(
        string='Order Reference',  # Label shown in the interface
        required=True,  # This field is mandatory
        copy=False,  # Don't copy this when duplicating
        readonly=True,  # Can't edit manually
        default='New'  # Default value
    )
    
    customer_id = fields.Many2one(
        'res.partner',  # Links to the Customer/Partner table
        string='Customer',
        required=True,
        domain=[('customer_rank', '>', 0)]  # Only show customers, not suppliers
    )
    
    product_id = fields.Many2one(
        'product.product',  # Links to the Product table
        string='Base Product',
        required=True,
        help='Select the base 3D product to customize'
    )
    
    # === CUSTOMIZATION OPTIONS ===
    
    custom_text = fields.Char(
        string='Custom Text',
        help='Text to print on the product (max 50 characters)',
        size=50
    )
    
    custom_color = fields.Selection([
        ('white', 'White'),
        ('black', 'Black'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('custom', 'Custom Color')
    ], string='Color', default='white')
    
    custom_color_code = fields.Char(
        string='Custom Color Code',
        help='Hex color code (e.g., #FF5733)'
    )
    
    size = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('xlarge', 'Extra Large')
    ], string='Size', default='medium')
    
    design_file = fields.Binary(
        string='Design File',
        help='Upload your custom design (PNG, JPG, STL)'
    )
    
    design_filename = fields.Char(string='Filename')
    
    # === PRICING ===
    
    base_price = fields.Float(
        string='Base Price',
        related='product_id.list_price',  # Gets price from product
        readonly=True
    )
    
    customization_fee = fields.Float(
        string='Customization Fee',
        compute='_compute_customization_fee',  # Calculated automatically
        store=True  # Save to database
    )
    
    total_price = fields.Float(
        string='Total Price',
        compute='_compute_total_price',
        store=True
    )
    
    quantity = fields.Integer(
        string='Quantity',
        default=1,
        required=True
    )
    
    # === WORKFLOW & STATUS ===
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('production', 'In Production'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Special Instructions')
    
    # === COMPUTED FIELDS ===
    # These fields calculate their value automatically
    
    @api.depends('custom_text', 'design_file', 'size')
    def _compute_customization_fee(self):
        """
        Calculate extra fees based on customization options.
        The @api.depends decorator means: recalculate when these fields change.
        """
        for order in self:
            fee = 0.0
            
            # Add fee if custom text is provided
            if order.custom_text:
                fee += 5.0
            
            # Add fee if design file is uploaded
            if order.design_file:
                fee += 10.0
            
            # Add fee based on size
            size_fees = {
                'small': 0.0,
                'medium': 5.0,
                'large': 10.0,
                'xlarge': 15.0
            }
            fee += size_fees.get(order.size, 0.0)
            
            order.customization_fee = fee
    
    @api.depends('base_price', 'customization_fee', 'quantity')
    def _compute_total_price(self):
        """Calculate total price: (base + customization) * quantity"""
        for order in self:
            order.total_price = (order.base_price + order.customization_fee) * order.quantity
    
    # === VALIDATION ===
    
    @api.constrains('quantity')
    def _check_quantity(self):
        """Make sure quantity is positive"""
        for order in self:
            if order.quantity <= 0:
                raise ValidationError('Quantity must be greater than 0!')
    
    @api.constrains('custom_text')
    def _check_custom_text_length(self):
        """Limit custom text to 50 characters"""
        for order in self:
            if order.custom_text and len(order.custom_text) > 50:
                raise ValidationError('Custom text cannot exceed 50 characters!')
    
    # === BUSINESS LOGIC (Button Actions) ===
    
    @api.model
    def create(self, vals):
        """
        Override create method to generate automatic order reference.
        This runs when creating a new record.
        """
        if vals.get('name', 'New') == 'New':
            # Generate sequence: PRINT/001, PRINT/002, etc.
            vals['name'] = self.env['ir.sequence'].next_by_code('printing.custom.order') or 'New'
        return super(PrintingCustomOrder, self).create(vals)
    
    def action_confirm(self):
        """Confirm the order (button action)"""
        self.write({'state': 'confirmed'})
        return True
    
    def action_start_production(self):
        """Start production (button action)"""
        self.write({'state': 'production'})
        return True
    
    def action_mark_done(self):
        """Mark as done (button action)"""
        self.write({'state': 'done'})
        return True
    
    def action_cancel(self):
        """Cancel the order (button action)"""
        self.write({'state': 'cancel'})
        return True
    
    def action_reset_to_draft(self):
        """Reset to draft (button action)"""
        self.write({'state': 'draft'})
        return True

