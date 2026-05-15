import os
import win32com.client
import pythoncom

def get_all_files(path):
    files = []
    # 遍历目录树
    print(os.walk(path))
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            # 构建完整路径并添加到列表中
            full_path = os.path.join(dirpath, filename)    #os.path.join 自动使用当前操作系统正确的路径分隔符
            files.append(full_path)
            print(full_path)
    return files

def trans_path(path_lst,type_keyword):
    result_lst = []
    print(len(path_lst))
    for index,path in enumerate(path_lst):
        print(index)
        basename = os.path.basename(path)
        if basename.startswith("~$"):
            continue
        if type_keyword in basename:
            if path.endswith(".docx"):
                if path not in result_lst:
                    result_lst.append(path)
            elif path.endswith(".doc") or path.endswith(".wps"):
                tmp_path = doc_to_docx(path)
                if tmp_path == "":
                    print("====error file====",path)
                    continue
                elif tmp_path not in result_lst:
                    result_lst.append(tmp_path)
                os.remove(path)
    return result_lst


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


def extract_syrw(file_path: dict):
    path = file_path["file_path"]
    if os.path.isdir(path):
        path_lst = get_all_files(path)
    else:
        path_lst = [path]
    path_lst = trans_path(path_lst, "大纲")
    print(path_lst)

if __name__ == "__main__":
    file_info = {"file_path": r'C:\Users\李灵佳\Desktop\新建文件夹'}
    extract_syrw(file_info)