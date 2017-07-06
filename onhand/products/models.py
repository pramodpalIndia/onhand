from __future__ import unicode_literals
from django.db import models
from ..management.models import Basis

class ProductType(models.Model):
    prdt_code = models.CharField(primary_key=True, max_length=6, verbose_name=('producttype'))
    prdt_desc = models.CharField(max_length=60, verbose_name=('description'))
    prdt_is_fulfill_manual = models.CharField(max_length=1, verbose_name=('fulfillmentmanual'))
    # prdt_is_fulfill_recurring = models.CharField(max_length=1, verbose_name=('fulfillmentrecurring'))

    def __str__(self):
        return "%s (%s)" % (self.prdt_desc, self.prdt_code)

    class Meta:
        db_table = 'oh_product_type'
        verbose_name = "producttype"
        verbose_name_plural = "ProductTypes"


class Product(models.Model):
    prod_code = models.CharField(primary_key=True, max_length=6, verbose_name=('code'))
    prod_name = models.CharField(max_length=60, verbose_name=('name'))
    prod_desc = models.CharField(max_length=60, blank=True, null=True, verbose_name=('description'))
    prdt_code = models.ForeignKey(ProductType, models.DO_NOTHING, db_column='prdt_code', verbose_name=('producttype'))
    # prod_is_auto_renew = models.CharField(max_length=1, verbose_name=('autorenew'))


    def __str__(self):
        return "%s (%s)" % (self.prod_name, self.prod_code)

    class Meta:
        db_table = 'oh_product'
        verbose_name = ("product")
        verbose_name_plural = "Products"


class ProductBasis(models.Model):
    prdb_id = models.AutoField(primary_key=True, verbose_name=('id'))
    basi_code = models.ForeignKey(Basis, models.DO_NOTHING, db_column='basi_code', verbose_name=('basis'))
    prod_code = models.ForeignKey(Product, models.DO_NOTHING, db_column='prod_code', verbose_name=('product'))
    prdb_is_active = models.CharField(max_length=1, verbose_name=('active'),default='Y')
    prdb_list_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=('price'))


    def __str__(self):
        return "%s (%s / %s)" % (self.prod_code, self.basi_code, self.prdb_list_price)

    class Meta:
        db_table = 'oh_product_basis'
        verbose_name = ("productbasis")
        verbose_name_plural = "Productsbasis"


class Discount(models.Model):
    disc_code = models.CharField(primary_key=True, max_length=20, verbose_name=('code'))
    disc_desc = models.CharField(max_length=60, verbose_name=('description'))
    disc_percent = models.DecimalField(max_digits=8, decimal_places=5, verbose_name=('percentage'))

    def __str__(self):
        return "%s (%s / discount %s %)" % (self.disc_desc, self.disc_code, self.disc_percent)

    class Meta:
        db_table = 'oh_discount'
        verbose_name = ("discount")
        verbose_name_plural = "Discounts"

class ProductDiscount(models.Model):
    pdis_id = models.AutoField(primary_key=True, verbose_name=('id'))
    prdb_id = models.ForeignKey(ProductBasis, models.DO_NOTHING, db_column='prdb_id', verbose_name=('productbasis'))
    pdis_name = models.CharField(max_length=60, verbose_name=('description'))
    disc_code = models.ForeignKey(Discount, models.DO_NOTHING, db_column='disc_code', verbose_name=('discount'))
    pdis_start_date = models.DateField(blank=True, null=True, verbose_name=('startdate'))
    pdis_end_date = models.DateField(blank=True, null=True, verbose_name=('enddate'))

    def __str__(self):
        return "%s (%s discount %s )" % (self.pdis_name, self.prdb_id, self.disc_code)

    class Meta:
        db_table = 'oh_product_discount'
        verbose_name = ("productdiscount")
        verbose_name_plural = "ProductDiscounts"
