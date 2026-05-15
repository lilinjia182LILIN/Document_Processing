import os
import win32com.client
import pythoncom
from docx import Document
import tempfile
import time


def doc_to_docx(doc_path):
    """
    使用Microsoft Word应用程序将.doc或.wps文件转换为.docx格式

    Args:
        doc_path (str): 源文件路径（.doc或.wps格式）

    Returns:
        str: 转换后的.docx文件路径，如果转换失败返回空字符串
    """
    try:
        # 检查源文件是否存在
        if not os.path.exists(doc_path):
            print(f"源文件不存在: {doc_path}")
            return ""

        # 生成输出文件路径
        output_path = os.path.splitext(doc_path)[0] + ".docx"

        # 如果输出文件已存在，先删除
        if os.path.exists(output_path):
            os.remove(output_path)

        # 初始化COM（需要在主线程中）
        pythoncom.CoInitialize()

        # 创建Word应用程序实例
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False  # 不显示Word界面
        word.DisplayAlerts = False  # 不显示警告

        try:
            # 打开文档
            doc = word.Documents.Open(doc_path)

            # 保存为docx格式
            doc.SaveAs2(output_path, FileFormat=16)  # 16表示docx格式

            # 关闭文档
            doc.Close()

            print(f"成功转换: {doc_path} -> {output_path}")
            return output_path

        except Exception as e:
            print(f"转换过程中出错: {str(e)}")
            return ""

        finally:
            # 退出Word应用程序
            word.Quit()
            pythoncom.CoUninitialize()

    except Exception as e:
        print(f"初始化过程中出错: {str(e)}")
        return ""


# 如果没有win32com，可以使用以下备选方案
def doc_to_docx_fallback(doc_path):
    """
    备选方案：使用系统关联程序打开并提示用户手动保存
    """
    try:
        import subprocess
        import platform

        # 使用系统默认程序打开文件
        if platform.system() == "Windows":
            os.startfile(doc_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(("open", doc_path))
        else:  # Linux
            subprocess.call(("xdg-open", doc_path))

        print(f"请手动打开文件并另存为.docx格式: {doc_path}")
        return ""

    except Exception as e:
        print(f"无法打开文件: {str(e)}")
        return ""


# 测试函数

#if __name__ == "__main__":
#    # 测试您的文件
#    test_file = r"C:\Users\李灵佳\Desktop\2.doc"

#    # 首先尝试使用Word自动转换
#    result = doc_to_docx(test_file)

#    if not result:
#        print("自动转换失败，尝试备选方案")
#        result = doc_to_docx_fallback(test_file)

#    if result:
#        print(f"转换成功！输出文件: {result}")
#    else:
#        print("转换失败")


if __name__ == '__main__':
    doc_to_docx(r"C:\Users\李灵佳\Desktop\2.doc")



