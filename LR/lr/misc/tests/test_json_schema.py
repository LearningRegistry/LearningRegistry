from jsonschema import validate, Draft3Validator, ValidationError
from lr.schema.validate import LRDraft3Validator
from unittest import TestCase
from urllib import urlopen
import copy, glob, os, re, uuid
import logging, json

log = logging.getLogger(__name__)

sample = json.loads('''{
    "X_resource_data": {
        "activity": {
            "content": "A resource found at http://www.phschool.com/iText/math/sample_chapter/Ch02/02-01/PH_Alg1_ch02-01_Obj1.html was matched to the academic content standard with ID http://purl.org/ASN/resources/S1000E0F by a member of the Brokers of Expertise Standards Matching Group on August 7, 2010",
            "verb": {
                "action": "matched",
                "date": "2010-08-07",
                "context": {
                    "description": "Brokers of Expertise resource management page",
                    "id": "http://www.myboe.org/go/resource/13338",
                    "objectType": "LMS"
                }
            },
            "actor": {
                "url": "http://myboe.org/go/groups/standards_matchers",
                "displayName": "Brokers of Expertise Standards Matching Group",
                "objectType": "group"
            },
            "related": [{
                "content": "Know and understand that equals multiplied by equals are equal.",
                "id": "http://purl.org/ASN/resources/S1000E0F",
                "objectType": "academic standard"
            }],
            "object": {
                "id": "http://www.phschool.com/iText/math/sample_chapter/Ch02/02-01/PH_Alg1_ch02-01_Obj1.html"
            }
        }
    },
    "doc_type": "resource_data",
    "resource_locator": "http://www.phschool.com/iText/math/sample_chapter/Ch02/02-01/PH_Alg1_ch02-01_Obj1.html",
    "update_timestamp": "2012-02-28T09:18:55.826272Z",
    "digital_signature": {
        "key_location": ["http://keyserver.pgp.com/vkd/DownloadKey.event?keyid=0x7DA1E3E28AF74166"],
        "signing_method": "LR-PGP.1.0",
        "signature": "xxxx"
    },
    "keys": ["U.S. Constitution", "Dance", "standards alignment", "Psychology", "Health & Physical Education", "English-Language Arts", "Physical Education", "California Academic Content Standards", "Equations and Inequalities", "Calculus", "Weather, Climate & Atmosphere", "Economics", "Music", "Geometry", "Vocabulary & Spelling", "Grammar", "World History", "Visual Arts & Performing Arts", "Addition & Subtraction", "Physics", "Sociology", "Religion", "American Democracy", "Career & Technical Ed", "Writing Strategies", "Measurement & Geometry", "Area & Volume", "Data Analysis, Statistics, and Probability", "Number Sense", "United States History", "Technology", "Algebra & Functions", "Earth & Space Science", "Grade 12", "Grade 11", "Grade Pre-K", "Chemistry", "Grade 10", "English Language Development", "Literature", "Injury Prevention & Safety", "Health Education", "Foreign Languages", "History-Social Science", "Mathematics", "Time", "Reading strategies", "Personal and Community Health", "Ecology & Ecosystems", "Measurement, Tools, and Data Analysis", "Geography", "Parts of a Whole (Fractions, Decimals & Percent)", "Grade K", "Electives", "Life Sciences", "Oral Presentations", "Reading Comprehension", "Family & Adult Literacy", "Science", "Theatre", "Grade 9", "Grade 7", "Literary Analysis", "Visual Arts", "Grade 8", "Grade 5", "Grade 6", "Grade 3", "Christianity", "Grade 4", "Grade 1", "Arts, Media, & Entertainment", "Grade 2", "Growth, Development & Aging", "Humanities", "Measurement & Tools", "Sports and Competition"],
    "TOS": {
        "submission_attribution": "Copyright 2011 California Department of Education: CC-BY-3.0",
        "submission_TOS": "http://creativecommons.org/licenses/by/3.0/"
    },
    "resource_data_type": "paradata",
    "payload_placement": "inline",
    "payload_schema": ["LR Paradata 1.0"],
    "node_timestamp": "2012-02-28T09:18:55.826272Z",
    "doc_version": "0.23.0",
    "create_timestamp": "2012-02-28T09:18:55.826272Z",
    "active": true,
    "publishing_node": "3b7ea975ac0f4c2c89a62268be6cbb03",
    "doc_ID": "0001969949d64402b7a2a6e7c7fd29f2",
    "identity": {
        "signer": "Brokers of Expertise",
        "submitter": "Brokers of Expertise",
        "submitter_type": "agent"
    },"payload_locator": "http://foo.com"
}''')


# class TestCaseFiles():
#     def __init__(self):
#         files = [
#             "file:lr/tests/data/validation/v_0_23_resource_data.json"
#         ]

#     def next(self):
#         for f in files:
#             log.info("Case File: %s" % f)
#             yield eval(urlopen(f).read())

class TestJSONSchemaValidation(TestCase):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)


    @classmethod
    def setUpClass(self):
        self.abstract_resource_data = json.load(open("lr/schema/abstract_resource_data.json"));
        self.abstract_linked_resource_data = json.load(open("lr/schema/abstract_linked_resource_data.json"));
        self.abstract_inline_resource_data = json.load(open("lr/schema/abstract_inline_resource_data.json"));

        self.v_0_23_resource_data = json.load(open("lr/schema/v_0_23/resource_data.json"));
        self.v_0_23_inline_resource_data = json.load(open("lr/schema/v_0_23/inline_resource_data.json"));
        self.v_0_23_linked_resource_data = json.load(open("lr/schema/v_0_23/linked_resource_data.json"));

        self.v_0_49_resource_data = json.load(open("lr/schema/v_0_49/resource_data.json"));
        self.v_0_49_inline_resource_data = json.load(open("lr/schema/v_0_49/inline_resource_data.json"));
        self.v_0_49_linked_resource_data = json.load(open("lr/schema/v_0_49/linked_resource_data.json"));
        self.v_0_49_deleted_resource_data = json.load(open("lr/schema/v_0_49/deleted_resource_data.json"));



    def test_validate_schemas(self):
        LRDraft3Validator.check_schema(self.abstract_resource_data)
        LRDraft3Validator.check_schema(self.abstract_linked_resource_data)
        LRDraft3Validator.check_schema(self.abstract_inline_resource_data)
        
        LRDraft3Validator.check_schema(self.v_0_23_resource_data)
        LRDraft3Validator.check_schema(self.v_0_23_inline_resource_data)
        LRDraft3Validator.check_schema(self.v_0_23_linked_resource_data)

        LRDraft3Validator.check_schema(self.v_0_49_resource_data)
        LRDraft3Validator.check_schema(self.v_0_49_inline_resource_data)
        LRDraft3Validator.check_schema(self.v_0_49_linked_resource_data)
        LRDraft3Validator.check_schema(self.v_0_49_deleted_resource_data)


    # def test_check_paradata(self):
    #     v = Draft3Validator(self.v_0_23_resource_data)
    #     for error in v.iter_errors(sample):
    #         # pass 
    #         print error



    # def test_misc(self):
    #     s = {
    #         "disallow":[{
    #             "type": "object",
    #             "properties": {
    #                 "payoad_locator" : { "type": ["number","any"]  }
    #             }
    #         }]
    #     }
    #     v = Draft3Validator(self.v_0_23_resource_data)
    #     for error in v.iter_errors({"payload_locator": 1}):
    #         pass 
    #         # print error



def make_case(schema, data, valid, cls):    
    def test_case(self):
        try:
            if valid:
                validate(data, schema, cls=cls)
            else:
                with self.assertRaises(ValidationError):
                    validate(data, schema, cls=cls)
        except Exception as e:
            print "VALID: %r\n" % valid
            print "DATA: %s\n" % repr(data)
            raise e
    return test_case



def load_json_cases(test_dir):
    def add_test_methods(test_class):
        test_num = 0;
        for filename in glob.iglob(os.path.join(test_dir, "*.json")):
            validating, _ = os.path.splitext(os.path.basename(filename))

            with open(filename) as test_file:
                data = json.load(test_file)

                for case in data:
                    for test in case["tests"]:
                        tdata = {}
                        if "default_data" in case:
                            tdata = copy.deepcopy(case["default_data"])
                            tdata.update(test["data"])
                        else:
                            tdata = test["data"]


                        if "rm_data" in test:
                            # print test["description"]
                            for rm in test["rm_data"]:
                                if rm in tdata:
                                    del tdata[rm]


                        a_test = make_case(
                            case["schema"],
                            tdata,
                            test["valid"],
                            test_class.validator_class,
                        )

                        test_name = "test_%s_%s_%s__%s" % (
                            validating,
                            re.sub(r"[\W ]+", "_", case["description"]),
                            re.sub(r"[\W ]+", "_", test["description"]),
                            uuid.uuid1().hex
                        )

                        
                        test_name = test_name.encode("utf-8")
                        a_test.__name__ = test_name

                        setattr(test_class, test_name, a_test)
                        test_num += 1

                        print "Test #%d: %s" % (test_num, test_name)

        return test_class
    return add_test_methods



@load_json_cases("lr/tests/data/validation/")
class TestLRJSONSchemaResourceData(TestCase):
    validator_class = LRDraft3Validator

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)


    # def setUp(self):
    #     self.test_cases = TestCaseFiles()


    # def test_file(self):
    #     for case_file in test_case.next():
    #         for case in case_file:
    #             log.info("Test Case: %s" % case["description"])
    #             schema  = json.load(urlopen(case["schema"]))

    #             for test in case["tests"]:
    #                 log.info("Test description: %s" % test["description"])
    #                 validator = Draft3Validator(schema)
    #                 assert test["valid"] == validator.is_valid(test["data"]), "Failed Test"
                    # for error in v.iter_errors()




