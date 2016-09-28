#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import re
import os

from jinja2 import Environment, PackageLoader


class Variable(object):
    PRIMITIVE_TYPES = ['String', 'Int', 'Double', 'Bool', 'UInt', 'Float', 'Character']

    def __init__(self, property_name, property_type, property_key):
        self.property_name = property_name
        self.property_type = property_type.replace("?", "")
        self.property_key = property_key

    def if_block(self):
        var_type = 'AnyObject' if self.is_custom_type() else self.property_type

        if self.is_custom_type() and self.is_list_type():
            var_type = '[AnyObject]'

        return "if let {}Val = representation.valueForKeyPath(\"{}\") as? {}".format(
            self.property_name, self.property_key, var_type
        )

    def then_block(self):
        property_value = "{}Val".format(self.property_name)

        if self.is_custom_type():
            if self.is_list_type():
                property_value = "{}Val.map({{ {}(response, representation: $0) }})".format(self.property_name, re.sub("\[|\]", "", self.property_type))
            else:
                property_value = "{}(response, representation: {}Val)".format(
                    self.property_type, self.property_name
                )

        return "self.{} = {}".format(self.property_name, property_value)

    def is_custom_type(self):
        property_type = self.property_type.replace("]", "").replace("[", "")
        return not any([property_type == primitive_type for primitive_type in Variable.PRIMITIVE_TYPES])

    def is_list_type(self):
        return self.property_type.find("]") != -1 and self.property_type.find("[") != -1


def get_var_list(model_file_contents):
    r"""get_var_list returns the public properties from a Swift file in a tuple list

    >>> model_file_contents = 'import Foundation\npublic class TestSerializer: JSONEncodable {\n    public var anInt: Int?\n    public var aString: String?\n   public var truthyValue: Bool?\n    public var customType: CustomType?\n    public var customTypeList: [CustomType]?\n}'
    >>> get_var_list(model_file_contents)
    [('anInt', 'Int?'), ('aString', 'String?'), ('truthyValue', 'Bool?'), ('customType', 'CustomType?'), ('customTypeList', '[CustomType]?')]
    """
    raw_vars = re.findall("public var .*$", model_file_contents, re.MULTILINE)
    processed_vars = [re.sub('public var ', '', raw_var) for raw_var in raw_vars]
    tuple_vars = [(var[0], var[1]) for var in map(lambda x: x.split(': '), processed_vars)]

    return tuple_vars


def get_json_to_object_map(model_file_contents):
    r"""get_json_to_object_map returns the map of JSON properties to object properties

    >>> model_file_contents = 'import Foundation\npublic class TestSerializer: JSONEncodable {\n    func encodeToJSON() -> AnyObject {\n        var nillableDictionary = [String:AnyObject?]()\n        nillableDictionary["an_int"] = self.anInt\n        nillableDictionary["a_string"] = self.aString\n        nillableDictionary["a_bool"] = self.aBool\n        nillableDictionary["custom_type"] = self.customType?.encodeToJSON()\n        nillableDictionary["custom_type_list"] = self.customTypeList?.encodeToJSON()\n    }\n}'
    >>> get_json_to_object_map(model_file_contents)
    [('anInt', 'an_int'), ('aString', 'a_string'), ('aBool', 'a_bool'), ('customType', 'custom_type'), ('customTypeList', 'custom_type_list')]
    """
    raw_assignments = re.findall('nillableDictionary\[.*\] = .*$', model_file_contents, re.MULTILINE)
    processed = [re.sub('nillableDictionary\["|"\]|\?\.encodeToJSON\(\)', "", assignment) for assignment in raw_assignments]

    return [(var[1], var[0]) for var in map(lambda x: x.split(" = self."), processed)]

def get_variable_list(model_file_contents):
    json_object_map = dict(get_json_to_object_map(model_file_contents))
    var_types = dict(get_var_list(model_file_contents))
    assert set(json_object_map.keys()) == set(var_types.keys())

    var_list = []
    for key in json_object_map.keys():
        var_list.append(Variable(property_name=key, property_type=var_types[key], property_key=json_object_map[key]))

    return var_list


def generate_protocol_method(model_file_contents):
    r"""generate_protocol_method generates a protocol to make the class conform to ResponseObjectSerializable
    Reference: https://gist.github.com/jpotts18/e39ee74de84ae094b270

    >>> model_file_contents = 'import Foundation\npublic class TestSerializer: JSONEncodable {\n    public var anInt: Int?\n    public var aString: String?\n   public var aBool: Bool?\n    func encodeToJSON() -> AnyObject {\n        var nillableDictionary = [String:AnyObject?]()\n        nillableDictionary["an_int"] = self.anInt\n        nillableDictionary["a_string"] = self.aString\n        nillableDictionary["a_bool"] = self.aBool\n    }\n}'
    >>> print(generate_protocol_method(model_file_contents))
    required public init?(response: NSHTTPURLResponse, representation: AnyObject) {
            if let aBoolVal = representation.valueForKeyPath("a_bool") as? Bool {
                self.aBool = aBoolVal
            }
            if let anIntVal = representation.valueForKeyPath("an_int") as? Int {
                self.anInt = anIntVal
            }
            if let aStringVal = representation.valueForKeyPath("a_string") as? String {
                self.aString = aStringVal
            }
        }
    """
    env = Environment(loader=PackageLoader('parse_model', 'templates'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('init.swift')
    variable_list = sorted(get_variable_list(model_file_contents), key=lambda x: x.property_type)

    return template.render(var_list=variable_list)


def generate_serializable_class(filename):
    r"""generate_serializable_class reads in a file, then generates a class which conforms to ResponseObjectSerializable
    Reference: https://gist.github.com/jpotts18/e39ee74de84ae094b270

    >>> print(generate_serializable_class('example.swift'))
    //
    // example.swift
    //
    // Generated by swagger-codegen, made Alamofire compatible by Alamoswagger
    //
    <BLANKLINE>
    import Foundation
    <BLANKLINE>
    <BLANKLINE>
    public class ExampleClass: ResponseObjectSerializable {
    <BLANKLINE>
        public var aBool: Bool?
        public var customType: CustomType?
        public var anInt: Int?
        public var aString: String?
        public var customTypeList: [CustomType]?
    <BLANKLINE>
        public init() {}
    <BLANKLINE>
        required public init?(response: NSHTTPURLResponse, representation: AnyObject) {
            if let aBoolVal = representation.valueForKeyPath("a_bool") as? Bool {
                self.aBool = aBoolVal
            }
            if let customTypeVal = representation.valueForKeyPath("custom_type") as? AnyObject {
                self.customType = CustomType(response, representation: customTypeVal)
            }
            if let anIntVal = representation.valueForKeyPath("an_int") as? Int {
                self.anInt = anIntVal
            }
            if let aStringVal = representation.valueForKeyPath("a_string") as? String {
                self.aString = aStringVal
            }
            if let customTypeListVal = representation.valueForKeyPath("custom_type_list") as? [AnyObject] {
                self.customTypeList = customTypeListVal.map({ CustomType(response, representation: $0) })
            }
        }
    <BLANKLINE>
        func encodeToJSON() -> AnyObject {
            var nillableDictionary = [String:AnyObject?]()
            nillableDictionary["a_string"] = self.aString
            nillableDictionary["a_bool"] = self.aBool
            nillableDictionary["an_int"] = self.anInt
            nillableDictionary["custom_type"] = self.customType?.encodeToJSON()
            nillableDictionary["custom_type_list"] = self.customTypeList?.encodeToJSON()
            let dictionary: [String:AnyObject] = APIHelper.rejectNil(nillableDictionary) ?? [:]
            return dictionary
        }
    }
    """
    assert type(filename) == str, "The filename should be a string"

    with open(filename, 'r') as input_file:
        model_file_contents = input_file.read()

    variable_list = sorted(get_variable_list(model_file_contents), key=lambda x: x.property_type)
    assert variable_list, "Couldn't find a list of public vars in the file %s" % (filename)

    class_line = re.findall("public class .*\:",model_file_contents, re.MULTILINE)
    assert class_line and len(class_line) > 0, "Couldn't find a class name in the file %s" % (filename)
    class_name = re.sub("public class |\:", "", class_line[0])

    comments = "//\n// %s\n//\n// Generated by swagger-codegen, made Alamofire compatible by Alamoswagger\n//" % (os.path.basename(filename))

    import_list = re.findall("^import .*$", model_file_contents, re.MULTILINE)
    if import_list and len(import_list) > 0:
        imports = '\n'.join(import_list)

    json_method_match = re.search("func encodeToJSON[\s\S]+return dictionary\s+}", model_file_contents, re.MULTILINE)
    assert json_method_match, "There should be an encodeToJSON method in the generated file"

    json_method = model_file_contents[json_method_match.start():json_method_match.end()]
    assert json_method, "There was a problem with the match indices: Start {} End {}".format(json_method_match.start(), json_method_match.end())

    required_init_method = generate_protocol_method(model_file_contents)
    assert required_init_method, "This method is required and couldn't be generated"

    env = Environment(loader=PackageLoader('parse_model', 'templates'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('responseobject.swift')

    return template.render(header=comments, imports=imports, var_list=variable_list, required_init_method=required_init_method, encode_to_json_method=json_method, classname=class_name)
