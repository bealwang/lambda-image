try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def load_xml_file(filename):
    tree = ET.ElementTree(file=filename)
    root = tree.getroot()
    result = []
    for package in root.iter("package"):
        item = package.attrib
        for function in package.iter("function"):
            item.update(function.attrib)
            para = []
            for param in function.iter("param"):
                para.append(param.text)
            item.update(dict(param = para))
        result.append(item)
    return result

def get_function(pname, resource):
    fun = filter(lambda x:x.get('pname') == pname,resource)[0]
    return pname+"."+fun.get('fname')


if __name__=='__main__':
    result = load_xml_file("./lambdaimage.xml")
    print get_function("reg",result)
