import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.section import CT_SectPr
from docx.text.paragraph import Paragraph
from docx.table import _Cell, Table


def parse_docx_content(filepath):
    content_str = ""
    file = docx.Document(filepath)   # 读取文档（创建一个对象）
    bodys = file.element.body   # 对应Word文档中 <w:body> 标签的内容
    #print(type(bodys))  # 该对象的xml类型
    #print(bodys.xml) # 该对象具体内容(xml格式)


    for i, child in enumerate(bodys, 1):
        if child.tag.endswith('p'):  #段落`/w:document/w:body/w:p`
            para = Paragraph(child, file.part)    # file.part 类似字典里的目录提供索引包含全局信息，不提供具体内容，具体内容由child提供
            if not para.text.strip(): continue
            para_text = para.text
        elif child.tag.endswith('tbl'):  # 表格`/w:document/w:body/w:tbl`
            tbl = Table(child, CT_Tbl)   # CT_Tbl类型确认
            table_matrix = []
            for row in tbl.rows:             # 编历表格每一行
                tmp_table_row = []
                for cell in row.cells:       # 遍历当前行的每一个单元格
                    # print(cell.text)
                    tmp_table_row.append(str(cell.text))  # 遍历的每一个单元格内容放到tmp_table_row里
                table_matrix.append(tmp_table_row)    # 遍历的当前行放在table_matrix里
            para_text = str(table_matrix)     #  将整个表格转换为字符串格式
        content_str += (para_text+"\n")   # 将段落文本或表格文本添加到总内容字符串中，并加上换行符
    # print(content_str)
    print(len(content_str))

    content_str = content_str.split("附录A\n")[0].strip("附录1\n")[0]
    # 开头有个附件1 部发 （2020） 584号附件1 这种跳过
    if len(content_str.split("附件1\n")[0]) > 1000:
        content_str = content_str.split("附件1\n")[0]
    if len(content_str)>50000:
        content_str = content_str[:49000]
    # print(content_str)
    print(len(content_str))


    return content_str

if __name__ == "__main__":
    filepath = r"C:\Users\李灵佳\Desktop\1.docx"
    parse_docx_content(filepath)


