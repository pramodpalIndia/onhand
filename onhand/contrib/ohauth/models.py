from django.db import models

from onhand.management.models import Role


class AccessLevel(models.Model):
    accs_code = models.CharField(primary_key=True, max_length=1, verbose_name='Access')
    accs_desc = models.CharField(max_length=20, verbose_name='description')

    def __str__(self):
        return "%s (%s)" % (self.accs_desc, self.accs_code)

    class Meta:
        db_table = 'oh_access_level'
        verbose_name = ("access_level")
        verbose_name_plural = "access_levels"


class OhFunction(models.Model):
    func_id = models.CharField(primary_key=True,max_length=60, db_column='func_id', verbose_name='function')
    func_name = models.CharField(max_length=60, db_column='func_name', verbose_name='description')

    def __str__(self):
        return "%s (%s)" % (self.func_name, self.func_id)

    class Meta:
        db_table = 'oh_function'
        verbose_name = ("oh_function")
        verbose_name_plural = "oh_functions"


class FunctionRoleAccessLevel(models.Model):
    func = models.ForeignKey(OhFunction, models.DO_NOTHING, db_column='func_id',verbose_name='Function')
    role_code = models.ForeignKey(Role, models.DO_NOTHING, db_column='role_code',verbose_name='Role')
    accs_code = models.ForeignKey(AccessLevel, models.DO_NOTHING, db_column='accs_code',verbose_name='Access')

    def __str__(self):
        return "%s (%s / %s )" % (self.func_name, self.role_code, self.accs_code)

    class Meta:
        db_table = 'oh_function_role_access_level'
        verbose_name = ("function_role_access_level")
        verbose_name_plural = "function_role_access_levels"
        unique_together = (('func', 'role_code', 'accs_code'),)
