from parse_outline_level import parse_docx_level_entry


def generate_numbering(data):
    numbering = [0]    #用于记录各级编号，初始为 [0]
    result = []

    for item in data:
        level = item['level']
        text = item['text']
        content = item['content']


        # 更新编号
        if level <= len(numbering):
            numbering[level - 1] += 1
            for i in range(level, len(numbering)):
                numbering[i] = 0
        else:
            # 如果level超出当前编号长度，补零
            for i in range(len(numbering), level):
                numbering.append(0)
            numbering[level - 1] += 1

        # 生成编号字符串
        numbering_str = ".".join(str(num) for num in numbering[:level])

        # 更新 text 字段
        item['text'] = f"{numbering_str} {text}"

        result.append(item)

    return result



def parse_content_ssxz(path):
    result_lst, begin_text = parse_docx_level_entry(path)
    # 过滤
    result_filter = []
    for x in result_lst:
        if "目  录" in x ["text"]:
            continue
        elif "附录" in x["text"] or "附件" in x ["text"]:
            break
        else:
            result_filter.append(x)

    # 本身内容包含序号的就不用生成序号了
    if not result_filter[0]["text"][0].isdigit():
        result_filter = generate_numbering(result_filter)

    # for i in result_filter:
    #       print(i)
    #       print("----")

    result_str = ""
    syxm_content_str = ""
    parse_syxm_flag = False
    for i in result_filter:
        if any(keyword in i["text"] for keyword in ["试验项目", "试验方法"]):
            parse_syxm_flag = True
        if parse_syxm_flag == True:
            if i["content"] == "":
                syxm_content_str += (i['text'] + "\n")
            else:
                syxm_content_str += (i['text'] + "\n" + i['content'].strip() + "\n")
        else:
            if i["content"] == "":
                result_str += (i['text'] + "\n")
            else:
                result_str += (i['text'] + "\n" + i['content'].strip() + "\n")

    result_str = begin_text + result_str
    # print(result_str)
    print(len(result_str))
    print(len(syxm_content_str))

    return syxm_content_str, result_str


if __name__ == '__main__':
    parse_content_ssxz(r"C:\Users\总体技术中心\Desktop\RCD213A车载GPS干扰站性能鉴定试验实施细则.docx")










