# coding:utf-8
import xlwt


def outer(data=[[]], filename="", sheet_name="sheet 1"):
    '''
    输出到xls文件
    :param data: 输出的数据，该数据为二位数组
    :param filename: 输出文件名称
    :param sheet_name: 表名字
    :return: 无返回值
    '''

    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet(sheet_name)
    for row_index, lines in enumerate(data):
        for col_index, line in enumerate(lines):
            sheet.write(row_index, col_index, line)
    wbk.save(filename)

