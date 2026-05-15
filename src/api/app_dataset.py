# -*- coding:utf-8 -*-
"""
@author:llj
@date
@
"""
from parse_docx import parse_docx_content
import pandas as pd
from doc_to_docx import doc_to_docx
from fastapi import APIRouter
from parse_docx_ssxz import parse_content_ssxz
import os
import datetime


from src.utils.call_llm import call_llm_no_stream
from src.utils.common import hash_id, extract_dates
from src.utils.insert_table import insert_data_mysql



dataset_router = APIRouter(prefix="/dataset", tags=["dataset"])

def get_all_files(path):
    files = []
    # 遍历目录树
    print(os.walk(path))
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            # 构建完整路径并添加到列表中
            full_path = os.path.join(dirpath, filename)
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


# 抽取试验任务数据集
@dataset_router.post("/syrw")
async def extract_syrw(file_path: dict):
    path = file_path["file_path"]
    if os.path.isdir(path):
        path_lst = get_all_files(path)
    else:
        path_lst = [path]
    path_lst = trans_path(path_lst, "大纲")
    print(path_lst)
    resulst_data = []
    for one_path in path_lst:
        basename = os.path.basename(one_path)
        try:
            content = parse_docx_content(one_path)
            template = "我会给你一段内容，你需要从内容中帮我提取出所有的文档标题、任务编号、试验性质、试验目的、试验时间、试验对象、试验地点。不需要总结概括，文档标题为xxx试验大纲，其中xxx一般代表被试装备名称，即被试装备名称一般会包含在文档标题中，试验对象为被试装备名称，试验时间为试验时间和地点章节下的试验时间信息，试验地点为试验时间和地点章节下的试验地点信息，输出结果为一个固定格式的可解析的json，不需要其他额外信息，示例如下：{'文档标题':'xxx','任务编号':'xxx','试验性质':'xxx'}。内容如下：\n" + content
            bszb = call_llm_no_stream(template).replace("json","").replace("```","").strip()
            print(bszb)
            bszb_json = ast.literal_eval(bszb)     # 将llm大模型返回的字符串转换成字典，字符串->字典。
            bszb_json["数据来源"] = basename
            bszb_json["记录时间"] = ""
            print(content[:200])
            date_lst = extract_dates(content[:200])
            if len(date_lst) > 0:
                bszb_json['记录时间'] = date_lst[0]
            print(bszb_json)
            result_tmp = []
            # 创建一个datetime 对象（例如当前时间）
            current_time = datetime.datetime.now()
            # 蒋datetime转换为字符串格式（MYSQL DATETIME 格式）
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            # 如果bszb_json里key有"文档标题"那么相应的值赋给wdbt，如果没有那么就赋值为""
            wdbt = bszb_json["文档标题"] if "文档标题" in bszb_json else ""
            rwbh = bszb_json["任务编号"] if "任务编号" in bszb_json else ""
            syxz = bszb_json["试验性质"] if "试验性质" in bszb_json else ""
            symd = bszb_json["试验目的"] if "试验目的" in bszb_json else ""
            sysj = bszb_json["试验时间"] if "试验时间" in bszb_json else ""
            sydx = bszb_json["试验对象"] if "试验对象" in bszb_json else ""
            sycj = bszb_json["试验地点"] if "试验地点" in bszb_json else ""
            tmp_id = hash_id(str([wdbt, rwbh]))
            # 变量值插入到result_tmp列表中
            result_tmp.append([tmp_id,wdbt,rwbh,syxz,symd,sysj,bszb_json["记录时间"],basename, formatted_time])
            insert_data_mysql("试验任务",result_tmp)
            tmp_result = {"docx_name":basename,"content": []}
            keys = ["文档标题","任务编号","试验性质","试验目的","试验时间","试验对象","试验场景","记录时间"]
            # values 列表（list）有索引
            values = [wdbt,rwbh,syxz,symd,sysj,sydx,sycj,bszb_json["记录时间"]]
            tmp_dic_lst = []
            for index, x in enumerate(keys):
                # keys[index],values[index]输出的是索引对应的值不是索引本身。输出索引本身是"index": index
                tmp_dic_lst.append({"name": keys[index],"value": values[index]})
            # 字典列表 tmp_dic_lst 添加到 tmp_result["content"] 中
            tmp_result["content"].append(tmp_dic_lst)
            resulst_data.append(tmp_result)

        except Exception as e:
            print(e)
    return {"code":0,"status":"success","data":resulst_data}



# 抽取试验方案数据集
@dataset_router.post("/syfa")
async def extract_syfa(file_path: dict):
    path = file_path["file_path"]
    if os.path.isdir(path):
        path_lst = get_all_files(path)
    else:
        path_lst = [path]
    path_lst = trans_path(path_lst, "总体方案")
    print(path_lst)
    resulst_data = []
    for one_path in path_lst:
        try:
            basename = os.path.basename(one_path)
            content = parse_docx_content(one_path)
            template = "我会给你一段内容，你需要从内容中帮我提取文档标题、试验任务背景、被试装备简介、作战对象分析、试验总体思路、试验保障需求、安全风险分析、有关问题说明的相关内容。其中文档标题为xxx总体方案，如果某个字段没有相关信息则取值为'',不需要总结概括，输出结果为一个固定格式可解析的json，不需要其他额外信息，示例如下：{'文档标题':'xxx','试验任务背景':'xxx'}。内容如下： \n" + content
            bszb_json = call_llm_no_stream(template).replace("json", "").replace("```", "").strip()
            print(bszb_json)
            print(len(bszb_json))
            bszb_json = ast.literal_eval(bszb_json)
            title = bszb_json["文档标题"] if "文档标题" in bszb_json else ""
            sybj = bszb_json["试验任务背景"] if "试验任务背景" in bszb_json else ""
            bszb = bszb_json["被试装备简介"] if "被试装备简介" in bszb_json else ""
            zzxd = bszb_json["作战对象分析"] if "作战对象分析" in bszb_json else ""
            syfa = bszb_json["试验总体思路"] if "试验总体思路" in bszb_json else ""
            sybz = bszb_json["试验保障需求"] if "试验保障需求" in bszb_json else ""
            aqfx = bszb_json["试验保障需求"] if "安全风险分析" in bszb_json else ""
            wtsm = bszb_json["有关问题说明"] if "有关问题说明" in bszb_json else ""

            #抽取记录时间
            print(content[:200])
            record_time = ""
            date_lst = extract_dates(content[:200])
            if len(date_lst) > 0:
                record_time = date_lst[0]
            # 创建一个datetime对象（例如当前时间）
            current_time = datetime.datetime.now()
            # 蒋datetime 转换为字符串格式（MYSQL DATATIME格式）
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            tmp_id = hash_id(str([basename, title]))
            result_tmp = []
            result_tmp.append([tmp_id, title, sybj, bszb, zzxd, syfa, sybz, aqfx, wtsm, record_time, basename, formatted_time])

            insert_data_mysql("试验方案",result_tmp)
            tmp_result = {"docx_name":basename,"content": []}
            keys = ["文档标题","试验背景","被试装备概况","作战想定与作战对象分析","试验方案设计","试验保障需求","安全风险分析","有关问题说明","记录时间"]
            vaules = [title, sybj, bszb, zzxd, syfa, sybz, aqfx, wtsm, record_time]
            tmp_dic_lst = []
            for index, x in enumerate(keys):
                tmp_dic_lst.append({"name": keys[index],"value": vaules[index]})
            tmp_result["content"].append(tmp_dic_lst)
            resulst_data.append(tmp_result)

        except Exception as e:
            print(e)

    return {"code":0,"status":"success","data":resulst_data}





# 抽取作战场景数据集excel
@dataset_router.post("/zzcj-excel")
async def extract_zzcj_excel(file_path: dict):
    path = file_path["file_path"]
    if os.path.isdir(path):
        path_lst = get_all_files(path)
    else:
        path_lst = [path]
    print(path_lst)
    resulst_data = []
    import pandas as pd
    df_data = pd.read_excel(path_lst[0])
    name_lst = list(df_data["试验名称"])
    content_lst = list(df_data["作战场景"])

    for index, one_path in enumerate(name_lst):
        try:
            basename = one_path
            tmp_result = {"docx_name":basename,"content": []}

            content= content_lst[index]
            template = "我会给你一段内容，你需要从内容中帮我提取所有的作战目的、作战目标、参战力量、敌方装备、作战范围的相关内容。如果某个字段没有相关信息则其取值为'',输出结果为一个固定格式的可解析的json数组，不需要其他额外信息，示例如下：[{'作战目的':'xxx','作战目标':''}]。内容如下： \n" + content
            bszb = call_llm_no_stream(template).replace("json", "").replace("```", "").strip()
            print(bszb)
            bszb_json_lst = ast.literal_eval(bszb)
            record = ""
            print(content[:200])
            date_lst = extract_dates(content[:200])
            if len(date_lst) > 0:
                record = date_lst[0]

            result_tmp = []
            #创建一个datetime对象（例如当前时间）
            current_time = datetime.datetime.now()
            # 蒋datetime转换为字符串格式（MYSQL DATETIME格式）
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

            for bszb_json in bszb_json_lst:

                wdbt = one_path
                zzmd = bszb_json["作战目的"] if "作战目的" in bszb_json else ""
                zzmb = bszb_json["作战目标"] if "作战目标" in bszb_json else ""
                czll = bszb_json["参战力量"] if "参战力量" in bszb_json else ""
                dfzb = bszb_json["敌方装备"] if "敌方装备" in bszb_json else ""
                zzfw = bszb_json["作战范围"] if "作战范围" in bszb_json else ""
                if zzmb == "" and zzmb == "":
                    continue
                syxm = "复杂电磁环境适应性"
                tmp_id = hash_id(str([wdbt, zzmd]))
                result_tmp.append([tmp_id, wdbt, zzmd, zzmb, czll, dfzb, zzfw, syxm, record, os.path.basename(path_lst[0]), formatted_time])
                tmp_dic_lst = []
                keys = ["文档标题", "作战目的", "作战目标", "参战力量", "敌方装备", "作战范围", "试验项目"]
                vaules = [wdbt, zzmd, zzmb, czll, dfzb, zzfw]
                for index, x in enumerate(keys):
                    tmp_dic_lst.append({"name": keys[index],"value": vaules[index]})
                tmp_result["content"].append(tmp_dic_lst)

            resulst_data.append(tmp_result)
            insert_data_mysql("作战场景",result_tmp)
        except Exception as e:
            print(e)
    return {"code":0,"status":"success","data":resulst_data}


#type_keyword: ""

# 抽取试验细则数据集
def extract_syxz(file_path: dict):
    path = file_path["file_path"]
    if os.path.isdir(path):
        path_lst = get_all_files(path)
    else:
        path_lst = [path]
    path_lst = trans_path(path_lst, type_keyword="")
    print(path_lst)
    resulst_data = []
    for one_path in path_lst:
        try:
            basename = os.path.basename(one_path)
            # basename = "_".join(basename.split("_")[1:])
            content, syxm_content_str = parse_content_ssxz(one_path)
            template = "我会给你一段内容，你需要从内容中帮我提取出所有的文档标题、试验任务名称、试验代号、试验地点、试验时间、被试装备、参试装备的相关信息。不需要总结概括，其中文档标题为xxx实施细则，xxx一般代表被试装备，被试装备和参数装备都只需要输出相关的装备名称即可，如果包含多个装备则用','分割开，输出结果为一个固定格式的可解析的json，不需要其他额外信息，示例如下：{'文档标题':'xxx','试验任务名称':'xxx','试验代号':'xxx'}。内容如下：\n" + content
            bszb = call_llm_no_stream(template).replace("json", "").replace("```", "").strip()
            print(bszb)
            bszb_json = ast.literal_eval(bszb)
            bszb_json["试验步骤"] = syxm_content_str

            bszb_json["记录时间"] = ""
            print(content[:200])
            date_lst = extract_dates(content[:200])
            if len(date_lst) > 0:
                bszb_json["记录时间"] = date_lst[0]
            print(bszb_json)
            result_tmp = []
            # 创建一个datetime 对象（例如当前时间）
            current_time = datetime.datetime.now()
            # 将datetime转换为字符串格式（MYSQL DATETIME 格式）
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            wdbt = bszb_json["文档标题"] if "文档标题" in bszb_json else ""
            rwmc = bszb_json["试验任务名称"] if "试验任务名称" in bszb_json else ""
            sydh = bszb_json["试验代号"] if "试验代号" in bszb_json else ""
            sydd = bszb_json["试验地点"] if "试验地点" in bszb_json else ""
            sysj = bszb_json["试验时间"] if "试验时间" in bszb_json else ""
            bszb = bszb_json["被试装备"] if "被试装备" in bszb_json else ""
            cszb = bszb_json["参试装备"] if "参试装备" in bszb_json else ""
            tmp_id = hash_id(str([wdbt, rwmc, sydh]))

            result_tmp.append([tmp_id, wdbt, rwmc, sydh, rwmc, sydd, sysj, bszb, cszb, syxm_content_str, bszb_json["记录时间"], basename, formatted_time])

            insert_data_mysql("试验细则",result_tmp)
            tmp_result = {"docx_name":basename,"content": []}
            keys = ["文档标题", "试验任务名称", "试验代号", "试验地点", "试验时间", "被试装备", "参试装备", "试验步骤"]
            vaules = [wdbt, rwmc, sydh, sydd, sysj, bszb, cszb, syxm_content_str]
            tmp_dic_lst = []
            for index, x in enumerate(keys):
                tmp_dic_lst.append({"name": keys[index],"value": vaules[index]})
            tmp_result["content"].append(tmp_dic_lst)
            resulst_data.append(tmp_result)

        except Exception as e:
            print(e)

    return {"code":0,"status":"success","data":resulst_data}






































































