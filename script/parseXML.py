import collections
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def load_xml_file(filename):
    tree = ET.ElementTree(file=filename)
    root = tree.getroot()
    result = []
    for package in root.iter("package"):
        item = collections.OrderedDict(package.attrib)
        for function in package.iter("function"):
            item.update(collections.OrderedDict(function.attrib))
            para = []
            for param in function.iter("param"):
                para.append(param.text)
            item.update(collections.OrderedDict(param = para))
        result.append(item)
    return result

def get_function(index, resource):
    fun_dict = resource[index]
    fun = fun_dict.get('pname') + "." + fun_dict.get('fname')
    para = fun_dict.get('param')
    return fun, para


if __name__=='__main__':
    result = load_xml_file("./lambdaimage.xml")
    fun, para = get_function(2, result)
    print fun
    print para
