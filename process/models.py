# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from django_permanent.models import PermanentModel
from process.helpers import region_hash
# Create your models here.

class Train_Parameter(PermanentModel):
    xmin = models.DecimalField('最小延迟指数', max_digits=10, decimal_places=4, default=None)
    xmax = models.DecimalField('最大延迟指数', max_digits=10, decimal_places=4, default=None)
    ymin = models.IntegerField('最小APP举报数', default=None)
    ymax = models.IntegerField('最大APP举报数', default=None)
    zmin = models.IntegerField('最小APP事故数', default=None)
    zmax = models.IntegerField('最大APP事故数', default=None)
    wmin = models.IntegerField('最小122事故数', default=None)
    wmax = models.IntegerField('最大122事故数', default=None)
    cx = models.DecimalField('c1', max_digits=10, decimal_places=4, default=None)
    cy = models.DecimalField('c2', max_digits=10, decimal_places=4, default=None)
    cz = models.DecimalField('c3', max_digits=10, decimal_places=4, default=None)
    cw = models.DecimalField('c4', max_digits=10, decimal_places=4, default=None)
    a = models.DecimalField('a', max_digits=10, decimal_places=4, default=None)
    b = models.DecimalField('b', max_digits=10, decimal_places=4, default=None)
    create_time = models.DateTimeField('时间')
    comment = models.TextField('备注', default='train')
    def __unicode__(self):
        return u'时间:'+ str(self.create_time) + u',备注:'+ str(self.comment) + u',最小延迟指数:' + str(self.xmin) + u',最大延迟指数:' + str(self.xmax) + u',最小APP举报数:' + str(self.ymin) + u'最大APP举报数:'\
               + str(self.ymax) + u',最小APP事故数:' + str(self.zmin) + u'最大APP事故数:' + str(self.zmax) + u'最小122事故数:' + str(self.wmin) \
               + u',最大122事故数:' + str(self.wmax) + ',cx:' + str(self.cx) + ',cy:' + str(self.cy) + ',cz:' + str(self.cz) + ',cw:' + str(self.cw) \
               + ',a:' + str(self.a) + ',b:' + str(self.b) + '\n'

class Prediction_Info(PermanentModel):
    PCAx = models.DecimalField('延迟指数PCA', max_digits=10, decimal_places=4, default=None)
    PCAy = models.DecimalField('APP举报PCA', max_digits=10, decimal_places=4, default=None)
    PCAz = models.DecimalField('APP事故PCA', max_digits=10, decimal_places=4, default=None)
    PCAw = models.DecimalField('122事故PCA', max_digits=10, decimal_places=4, default=None)
    expect_police = models.IntegerField('预估警力', default=None)
    real_police = models.IntegerField('实际警力', default=None)
    create_time = models.DateTimeField('时间')

    def __unicode(self):
        return 'PCAx:' + str(self.PCAx) + ',PCAy:' + str(self.PCAy) + 'PCAz:' + str(self.PCAz) + 'PCAw:' + str(self.PCAw) + 'u预估警力:'+ \
               str(self.expect_police) + u',实际警力:' + str(self.real_police) + u',时间:' + str(self.create_time) + '\n'