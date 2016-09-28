import Foundation


public class ExampleClass: JSONEncodable {

    public var aString: String?
    public var aBool: Bool?
    public var anInt: Int?
    public var customType: CustomType?
    public var customTypeList: [CustomType]?

    public init() {}

    // MARK: JSONEncodable
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
