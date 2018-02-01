#-*- coding:utf-8 -*-
'''
Description:
    此脚本用于绘制CDF 累计概率图
============================
@author:hbs
@date:2018-1-28
@version:1.0
============================
@update:提高脚本的复用性，修复了基本绘图的一个bug
@version:1.1
'''
import numpy as np
from matplotlib import pyplot as plt
import warnings


class CDFDrawer:
    def __init__(self, variance_type="discrete"):
        '''
        传入的有变量的类型，默认是离散型变量，即discrete；
                         如果是连续型变量，则为continuous。
        :param variance_type: 变量类型
        '''
        self.vt = variance_type

    def discrete_data(self, variance_value, distribution_seq=None):
        '''如果变量是离散型变量需要用到这一方法传数据
        :param variance_value: 实验得到的离散型变量的所有的值。
        :param distribution_seq: 离散型变量的分布列，默认是空，不指定则会认为是均匀概率。
        '''
        variance_value = np.array(variance_value)
        values = np.sort(np.unique(variance_value))
        test_num = variance_value.size
        #如果不指定则认为是均匀分布
        if distribution_seq == None:
            distribution_seq = np.ones(values.size) / test_num
        #样本频数*概率值 求取传入的每种自变量对应的概率值，替换概率分布列表中相应的值
        for i in range(values.size):
            val = values[i]
            distribution_seq[i] = distribution_seq[i] * (variance_value == val).sum()
        return values, test_num, distribution_seq

    def contiunous_data(self, variance_value, distribution_seq=None, distribution_func=None,**kwargs):
        '''如果变量是连续型变量则需要使用该方法获取到数据
        :param variance_value: 实验得到的连续型变量所有的结果。
        :param distribution_seq: 可以直接传入样本点的分布列
        :param distribution_func: 概率分布函数，如果不指定，默认为None，即各点的概率相等。
                                  根据自变量值求概率密度，请将自变量x作为函数的第一个参数。
        '''
        variance_value = np.array(variance_value)
        #首先将变量的值去除重复并由小到大排序
        values = np.sort(np.unique(variance_value))
        #获取到样本的总数
        test_num = variance_value.shape[0]
        #假设没有传入计算好的样本点分布列
        distribution = np.zeros(values.size)
        if distribution_seq == None:
            if distribution_func == None:   #此时默认各样本点呈均匀分布
                uniform_probability = 1.0 / test_num
                for i in range(values.size):
                    val = values[i]
                    distribution[i] = uniform_probability * (variance_value == val).sum()

            else:                           #此时用户传入计算概率的方法
                for i in range(values.size):
                    probability = distribution_func(values[i], **kwargs)
                    val = values[i]
                    distribution[i] = probability * (variance_value == val).sum()
        #如果传入了分布列
        else:
            for i in range(values.size):
                val = values[i]
                distribution[i] = distribution_seq[i] * (variance_value == val).sum()

        return values, test_num, distribution

    def create_plots(self, vals, distribution_seq):
        '''根据传来的数据结果，得到画图需要的点集。
        :param variance_value: 变量值最后作为横坐标的点。
        :param distribution_seq: 各个坐标点对应的概率值。
        '''
        x_plots = vals
        y_plots = np.cumsum(distribution_seq)

        return x_plots,y_plots

    def cdf_graph(self, x_plots, y_plots, x_label, y_label, line_color, line_style, x_range, y_range, graph_title, label, fig_name):
        '''根据传入的点画出cdf图
        :param x_plots: 横坐标x点集
        :param y_plots: 纵坐标y点集
        :param x_label: 横坐标的名称
        :param y_label: 纵坐标的名称
        :param line_color: 线的颜色
        :param line_style: 线的形式，注意需要遵循 matplotlib的2D图的线型标准
        :param x_range: 设定横坐标的左值和右值，传入一个列表
        :param y_range: 传入纵坐标的左值和右值，传入一个列表，默认0~1的区间（因为是概率）
        :param graph_title: 给图片设置一个标题
        :param label: 图示/图例内容
        :param fig_name: 图片保存的文件名
        '''
        fig = plt.figure(figsize=(4, 4))
        plt.xlim(x_range[0], x_range[1])
        plt.ylim(y_range[0], y_range[1])

        plt.plot(x_plots, y_plots, color=line_color, linestyle=line_style, label=label)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.legend()

        plt.title(graph_title)

        fig.savefig(fig_name)

    def main(self, variance_value, x_label, y_label, line_color, line_style, x_range="auto", y_range=[0,1], graph_title=None, distribution_seq=None, distribution_func=None, label=None, fig_name="cdf.jpg", **kwargs):
        if self.vt == "discrete":
            variance_value, test_num, distribution_seq = self.discrete_data(variance_value, distribution_seq)
        elif self.vt == "continuous":
            variance_value, test_num, distribution_seq = self.contiunous_data(variance_value, distribution_seq, distribution_func, **kwargs)
        else:
            raise ValueError("invalid input of variance type")
        x_plots, y_plots = self.create_plots(variance_value, distribution_seq)
        if x_range == "auto":
            if x_plots[0] > 0:
                x_start = 0
            else:
                x_start = x_plots[0]
            x_range=[x_start, x_plots[-1]]
        self.cdf_graph(x_plots, y_plots, x_label, y_label, line_color, line_style, x_range, y_range, graph_title, label, fig_name)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    x = np.random.rand(100)
    x2 = np.random.randn(100)
    # print(x)
    c = CDFDrawer("continuous")
    c.main(x, "score", "probability", "b-", [0,1.1], [0,1.3])
    c.main(x2, "score", "probability", "b-", [0,1.1], [0,1.3])